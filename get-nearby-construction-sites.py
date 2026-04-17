import os
import json
import math
import pymysql

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ.get("DB_PORT", "3306"))
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ.get("DB_NAME", "construction_db")
DB_TABLE = os.environ.get("DB_TABLE", "table1_construction_sites_clean")

# Supported City of Melbourne suburbs
SUBURB_CENTERS = {
    "Carlton": (-37.8000, 144.9670),
    "Docklands": (-37.8145, 144.9460),
    "East Melbourne": (-37.8160, 144.9870),
    "Kensington": (-37.7940, 144.9260),
    "Melbourne": (-37.8136, 144.9631),
    "North Melbourne": (-37.7990, 144.9430),
    "Parkville": (-37.7860, 144.9550),
    "South Yarra": (-37.8380, 144.9930),
    "Southbank": (-37.8230, 144.9650),
    "West Melbourne": (-37.8080, 144.9380),
}

COVERAGE_KM = float(os.environ.get("COVERAGE_KM", "6"))
DEFAULT_RADIUS_M = int(os.environ.get("DEFAULT_RADIUS_M", "1500"))
MIN_RADIUS_M = 100
MAX_RADIUS_M = 5000


def resp(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, default=str),
    }


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def nearest_supported_suburb(lat, lon):
    nearest = None
    min_km = 10**9
    for name, (slat, slon) in SUBURB_CENTERS.items():
        d = haversine_km(lat, lon, slat, slon)
        if d < min_km:
            min_km = d
            nearest = name
    return nearest, min_km


def in_city_of_melbourne(lat, lon):
    nearest, min_km = nearest_supported_suburb(lat, lon)
    return min_km <= COVERAGE_KM, nearest, round(min_km, 2)


def normalize_suburb_name(raw):
    if not raw:
        return None
    s = raw.strip().lower()
    for official in SUBURB_CENTERS.keys():
        if official.lower() == s:
            return official
    return None


def parse_inputs(event):
    qs = event.get("queryStringParameters") or {}

    radius_m = int(qs.get("radius", DEFAULT_RADIUS_M))
    radius_m = max(MIN_RADIUS_M, min(radius_m, MAX_RADIUS_M))

    # Mode A: coordinates
    if "lat" in qs and "lon" in qs:
        return {
            "mode": "coords",
            "lat": float(qs["lat"]),
            "lon": float(qs["lon"]),
            "selectedSuburb": None,
            "radiusM": radius_m,
        }

    # Mode B: selected suburb
    if "suburb" in qs:
        suburb = normalize_suburb_name(qs.get("suburb"))
        if not suburb:
            return {"error": "Unsupported suburb."}
        lat, lon = SUBURB_CENTERS[suburb]
        return {
            "mode": "suburb",
            "lat": lat,
            "lon": lon,
            "selectedSuburb": suburb,
            "radiusM": radius_m,
        }

    return {"error": "Either (lat, lon) or suburb is required."}


def build_query():
    # AC rules:
    # - issued within last 24 months
    # - no recorded completion date
    # - nearest first
    # - max 5
    # + deduplicate by address
    return f"""
        SELECT
          MIN(site_id) AS site_id,
          address,
          MIN(latitude) AS latitude,
          MIN(longitude) AS longitude,
          MIN(distance_m) AS distance_m
        FROM (
          SELECT
            site_id,
            address,
            latitude,
            longitude,
            (
              6371000 * ACOS(
                COS(RADIANS(%s)) * COS(RADIANS(latitude)) *
                COS(RADIANS(longitude) - RADIANS(%s)) +
                SIN(RADIANS(%s)) * SIN(RADIANS(latitude))
              )
            ) AS distance_m
          FROM {DB_TABLE}
          WHERE latitude IS NOT NULL
            AND longitude IS NOT NULL
            AND DATE(start_date) >= DATE_SUB(CURDATE(), INTERVAL 24 MONTH)
            AND (end_date IS NULL OR TRIM(CAST(end_date AS CHAR)) = '')
        ) t
        WHERE distance_m <= %s
        GROUP BY address
        ORDER BY distance_m ASC
        LIMIT 5
    """

def query_sites(lat, lon, radius_m):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(build_query(), (lat, lon, lat, radius_m))
            return cur.fetchall()
    finally:
        conn.close()


def to_payload(rows):
    # UI requirement: only show address (distance kept for ordering/debug)
    sites = []
    for r in rows:
        sites.append(
            {
                "siteId": str(r.get("site_id", "")),
                "address": r.get("address", ""),
                "distanceM": int(round(float(r["distance_m"]))),
                "lat": float(r["latitude"]) if r.get("latitude") is not None else None,
                "lon": float(r["longitude"]) if r.get("longitude") is not None else None,
            }
        )
    return sites


def handler(event, context):
    try:
        parsed = parse_inputs(event)
        if "error" in parsed:
            return resp(400, {"ok": False, "message": parsed["error"]})

        lat = parsed["lat"]
        lon = parsed["lon"]
        mode = parsed["mode"]
        selected_suburb = parsed["selectedSuburb"]
        radius_m = parsed["radiusM"]

        # Coverage check only for realtime coordinates
        if mode == "coords":
            in_cov, nearest_suburb, nearest_km = in_city_of_melbourne(lat, lon)
            if not in_cov:
                return resp(
                    200,
                    {
                        "ok": True,
                        "inCoverage": False,
                        "message": "You are currently outside the City of Melbourne coverage area.",
                        "nearestSupportedSuburb": nearest_suburb,
                        "distanceToCoverageKm": nearest_km,
                        "count": 0,
                        "sites": [],
                    },
                )
        else:
            nearest_suburb = selected_suburb
            nearest_km = 0.0

        rows = query_sites(lat, lon, radius_m)
        sites = to_payload(rows)

        return resp(
            200,
            {
                "ok": True,
                "inCoverage": True,
                "queryMode": mode,
                "selectedSuburb": selected_suburb,
                "nearestSupportedSuburb": nearest_suburb,
                "distanceToCoverageKm": nearest_km,
                "radiusM": radius_m,
                "count": len(sites),
                "sites": sites,
            },
        )

    except ValueError:
        return resp(400, {"ok": False, "message": "Invalid lat/lon/radius format."})
    except Exception as e:
        return resp(500, {"ok": False, "message": str(e)})


# Compatible with both handler settings:
# - lambda_function.handler
# - lambda_function.lambda_handler
lambda_handler = handler
