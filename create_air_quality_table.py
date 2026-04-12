import pandas as pd
import requests
import time

# ============================================================
# CONFIG
# ============================================================
INPUT_FILE = "geocoded_permits_sample_200.csv"
OUTPUT_FILE = "table2_air_quality.csv"

# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv(INPUT_FILE)

# keep rows with valid coordinates only
df = df[df["lat"].notna() & df["lon"].notna()].copy()

# make sure lat/lon are numeric
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
df = df[df["lat"].notna() & df["lon"].notna()].copy()

# remove duplicate coordinate pairs
df_coords = df[["lat", "lon"]].drop_duplicates().copy()

print("Coordinate pairs selected:", len(df_coords))

# ============================================================
# API FUNCTION
# ============================================================
def get_air_quality(lat, lon):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "us_aqi,pm10,pm2_5"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})

        return {
            "timestamp": current.get("time"),
            "pm10": current.get("pm10"),
            "pm2_5": current.get("pm2_5"),
            "aqi": current.get("us_aqi")
        }

    except Exception as e:
        print(f"API error for ({lat}, {lon}): {e}")
        return {
            "timestamp": None,
            "pm10": None,
            "pm2_5": None,
            "aqi": None
        }

# ============================================================
# CALL API
# ============================================================
results = []

for i, row in enumerate(df_coords.itertuples(index=False), start=1):
    lat = row.lat
    lon = row.lon

    aq = get_air_quality(lat, lon)

    results.append({
        "timestamp": aq["timestamp"],
        "latitude": lat,
        "longitude": lon,
        "pm10": aq["pm10"],
        "pm2_5": aq["pm2_5"],
        "aqi": aq["aqi"],
        "source": "Open-Meteo"
    })
    

    print(
        f"[{i}/{len(df_coords)}] "
        f"lat={lat}, lon={lon}, time={aq['timestamp']}, "
        f"pm10={aq['pm10']}, pm2_5={aq['pm2_5']}, aqi={aq['aqi']}"
    )

    time.sleep(1)

# ============================================================
# SAVE TABLE 2
# ============================================================
table2 = pd.DataFrame(results)
table2.to_csv(OUTPUT_FILE, index=False)

print("Table 2 saved:", OUTPUT_FILE)
print("Rows in Table 2:", len(table2))
print(table2.head())

