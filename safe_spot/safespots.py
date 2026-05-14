"""
safespots.py - AsthmaSafe Melbourne SafeSpots Finder
=====================================================
Given an origin (lat/lon) and a search radius, return nearby child-friendly
outdoor places (parks, playgrounds, libraries, childcare centres) each
scored 0-100 on asthma-safety.

The score combines four risk factors measured within 200m of each place:
  1. Construction activity (from building_permits)
  2. Traffic intensity     (from traffic_points)
  3. Vehicle emission      (from traffic_points.emission_index)
  4. Air quality           (from air_quality_points)

Each place comes back with a plain-English explanation, so guardians can
see *why* a spot scored the way it did without reading sensor numbers.

Public entry points:
  list_safe_spots(origin_lat, origin_lon, radius_m, db_conn,
                  category=None, sort_by='score')
  geocode_place(query)   # Photon wrapper, returns (lat, lon, display_name)
"""

import math
import re
import time
import requests

# ============================================================
# Tunable constants — change these and the whole scoring shifts.
# Keep them named so the explanation strings stay honest.
# ============================================================

# How close a risk source has to be to count against a place.
# Different risks have different effective ranges, calibrated from real data:
#   - Construction dust is near-field. Stays within 200m of the site.
#   - Vehicle traffic / emissions waft further AND SCATS sites are spaced
#     200-500m apart, so a tight 200m radius misses most places. 400m
#     reliably catches 1-3 SCATS sites in CBD.
#   - Pollen is even more localised than dust — trees release pollen that
#     drops within meters of the tree. 50m is tight but generous; most
#     park visitors are within 50m of dozens of trees.
CONSTRUCTION_RADIUS_M = 200
TRAFFIC_RADIUS_M      = 400
POLLEN_RADIUS_M       = 50
# Legacy name still used by a few helpers — kept for compat.
RISK_RADIUS_M = CONSTRUCTION_RADIUS_M

# Saturation thresholds: anything at or above this value contributes the
# max risk (1.0). Calibrated from observed Melbourne CBD distributions
# rather than guessed.
#
# Traffic: Melbourne CBD arterials carry 15k-50k vehicles/day routinely.
# 40k is the realistic threshold for "very busy arterial".
#
# Emission: scales with traffic. 8000 lets a normal busy road sit around
# 0.6, not 1.0.
#
# Pollen: chosen so a moderate avenue lined with allergenic trees
# (~5-10 trees x allergen_weight 2 x pollen_factor 2 = 20-40) sits in the
# mid range, while a heavily-planted street (Royal Parade with mature
# plane trees) saturates.
#
# Dust score: built from active_permits * estimated_cost (millions) *
# wind_factor. Calibrated so a single small permit doesn't move the
# needle but a large active build site nearby is meaningful.
# Dust score: built from active_permits * estimated_cost (millions) *
# sqrt-decay-by-distance * wind_factor. After re-calibration with real
# CBD data:
#   - 1 small building 100m away: score ~ 1
#   - 5 mid-size buildings spread within 200m: score ~ 15
#   - dense CBD block (30+ permits, mixed sizes): score ~ 80-150
# Saturation at 80 means "dense CBD construction zone" hits max risk,
# everything below scales linearly.
CONSTRUCTION_SATURATION = 80
TRAFFIC_SATURATION      = 40000
EMISSION_SATURATION     = 8000
POLLEN_SATURATION       = 80
PM25_SATURATION         = 35       # μg/m³, WHO 24-hour interim target

# Neutral values used when we can't measure a risk factor. CRITICAL:
# do NOT default missing data to 0 (= "no risk"), or places in data-poor
# zones get falsely awarded high scores. Use a mid-range value (~0.3)
# so missing data neither helps nor crushes a place's ranking.
PM25_NEUTRAL    = 0.30
TRAFFIC_NEUTRAL = 0.30    # used when no SCATS site within TRAFFIC_RADIUS_M

# Risk weights — must sum to 1.0.
# 5 dimensions of roughly equal importance, with slight preference for
# construction dust (most direct asthma trigger for kids).
RISK_WEIGHTS = {
    'construction': 0.22,
    'traffic':      0.20,
    'emission':     0.20,
    'air_quality':  0.18,
    'pollen':       0.20,
}

# Pollen seasons (Southern Hemisphere) — copied from routing.py to keep
# safespots.py self-contained. Genera in season for the given month
# contribute to the pollen score; others don't.
POLLEN_SEASONS = {
    7:  ['cupressus'],
    8:  ['cupressus', 'betula', 'fraxinus', 'ulmus', 'acacia'],
    9:  ['platanus', 'betula', 'quercus', 'fraxinus', 'ulmus', 'cupressus', 'acacia'],
    10: ['platanus', 'betula', 'quercus', 'olea', 'fraxinus', 'eucalyptus'],
    11: ['platanus', 'quercus', 'olea', 'eucalyptus'],
    12: ['olea', 'eucalyptus'],
    1:  ['eucalyptus'],
    2:  ['eucalyptus'],
}

# Wind factor model for dust dispersion. Same intuition as the XGBoost
# Lambda but linear and explicable: low wind = dust accumulates near the
# source = high risk; high wind disperses it. Calibration:
#   wind 0 m/s  -> factor 1.2 (worst case, dead air)
#   wind 2 m/s  -> factor 1.0 (typical CBD condition, baseline)
#   wind 5 m/s  -> factor 0.6
#   wind 10 m/s -> factor 0.3
WIND_FACTOR_BASE = 1.2
WIND_FACTOR_DECAY = 0.09

# Categories we consider "safe-spot" candidates. Maps DB enum -> display label.
PLACE_CATEGORIES = {
    'playground': 'Playground',
    'park':       'Park',
    'library':    'Library',
    'childcare':  'Childcare Centre',
    'landmark':   'Public Place',
}


# ============================================================
# Geometry
# ============================================================

def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance in metres."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bbox_around(lat, lon, radius_m):
    """
    Quick lat/lon bounding box for a circular radius. Used as a coarse SQL
    pre-filter before the exact haversine check, so we don't ST_Distance every
    row in the table.
    """
    # ~111,320 m per degree of latitude everywhere
    dlat = radius_m / 111320.0
    # longitude degrees shrink with latitude
    dlon = radius_m / (111320.0 * math.cos(math.radians(lat)))
    return (lat - dlat, lat + dlat, lon - dlon, lon + dlon)


# ============================================================
# Geocoding (Photon)
# ============================================================

# Same UA trick you used in routing.py — Photon's public instance 403s
# generic clients.
_PHOTON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; AsthmaSafe/1.0)',
    'Accept': 'application/json',
}

def geocode_place(query, bias_lat=-37.8136, bias_lon=144.9631):
    """
    Resolve a free-text place name to (lat, lon, display_name).
    Biased toward Melbourne CBD so 'Carlton Gardens' picks ours, not
    one in another country.

    Returns (None, None, None) on failure rather than raising — caller
    should surface a friendly error.
    """
    if not query or not query.strip():
        return None, None, None

    url = 'https://photon.komoot.io/api/'
    params = {
        'q': query.strip(),
        'limit': 1,
        'lat': bias_lat,
        'lon': bias_lon,
    }
    try:
        resp = requests.get(url, params=params, headers=_PHOTON_HEADERS, timeout=8)
        if resp.status_code != 200:
            return None, None, None
        data = resp.json()
        features = data.get('features') or []
        if not features:
            return None, None, None
        f = features[0]
        lon, lat = f['geometry']['coordinates']  # Photon: [lon, lat]
        props = f.get('properties', {})
        # Build a readable display name from whatever Photon gave us
        parts = [props.get('name'), props.get('street'),
                 props.get('city') or props.get('locality'),
                 props.get('state'), props.get('country')]
        display = ', '.join([p for p in parts if p])
        return lat, lon, display or query.strip()
    except Exception as e:
        print(f"[safespots] geocode error for {query!r}: {e}")
        return None, None, None


# ============================================================
# Database queries — all radius-bounded
# ============================================================

def _places_in_radius(cursor, lat, lon, radius_m, categories=None):
    """
    Fetch candidate places from safe_places within a bounding box, then
    exact-filter by haversine. Returns rows with computed distance_m.
    """
    s, n, w, e = bbox_around(lat, lon, radius_m)

    sql = """
        SELECT id, name, category, lat, lon, address
        FROM safe_places
        WHERE lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """
    params = [s, n, w, e]

    if categories:
        placeholders = ','.join(['%s'] * len(categories))
        sql += f" AND category IN ({placeholders})"
        params.extend(categories)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    out = []
    for r in rows:
        d = haversine_m(lat, lon, r['lat'], r['lon'])
        if d <= radius_m:
            r['distance_m'] = round(d)
            out.append(r)
    return out


def _dust_score_for_place(cursor, lat, lon, radius_m, query_date,
                          wind_speed_ms=None):
    """
    Compute a construction dust score based on the XGBoost Lambda's
    feature logic (which writes to dust_risk_log, but currently empty).

    Components:
      active_permits      : count of DISTINCT geocoded sites within radius
      total_cost_millions : sum of estimated_cost (millions), capped
      wind_factor         : higher wind = more dispersion = less local risk
                            taken from latest weather_data, or 1.0 if none

    Returns a dict so we can show both the score AND the human-readable
    breakdown (count + dominant building cost), not just one number.

    Important: same de-dup logic as before — one building can have many
    permits but is one construction site for dust purposes.
    """
    s, n, w, e = bbox_around(lat, lon, radius_m)
    cursor.execute("""
        SELECT lat, lon, MAX(estimated_cost) AS max_cost,
               COUNT(*) AS permit_count
        FROM building_permits
        WHERE lat IS NOT NULL AND lon IS NOT NULL
          AND lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
          AND issue_date <= %s
          AND completed_by_date >= %s
        GROUP BY lat, lon
    """, (s, n, w, e, query_date, query_date))

    # Cost is in $, convert to $M. Cap individual buildings at $50M
    # so one mega-project doesn't single-handedly saturate the score.
    sites = []
    for row in cursor.fetchall():
        d = haversine_m(lat, lon, row['lat'], row['lon'])
        if d > radius_m:
            continue
        cost_m = min(float(row['max_cost'] or 0) / 1_000_000, 50.0)
        sites.append({
            'distance_m': d,
            'cost_m':     cost_m,
            'permit_count': int(row['permit_count']),
        })

    if not sites:
        return {
            'score':                0.0,
            'active_sites':         0,
            'total_cost_millions':  0.0,
            'wind_factor':          1.0,
        }

    # Score = sum of (cost_m * inverse_distance_factor) where the
    # factor stays meaningful even for far sites within the radius.
    # The old linear decay (1 - d/r) made sites near the edge contribute
    # ~0, so 34 spread-out construction sites looked harmless. Real
    # dust doesn't work that way: a building 180m away still produces
    # measurable dust at your location.
    #
    # New: floor distance at 30m (one block) so very close sites don't
    # blow up, and use sqrt decay so the contribution drops gradually.
    raw_score = 0.0
    for site in sites:
        effective_d = max(site['distance_m'], 30)
        # decay: 1.0 at 30m, ~0.4 at 200m, fairly graceful
        decay = (30 / effective_d) ** 0.5
        raw_score += site['cost_m'] * decay

    # Wind correction: if we have a wind_speed reading, scale the score.
    wind_factor = (
        max(0.2, WIND_FACTOR_BASE - WIND_FACTOR_DECAY * wind_speed_ms)
        if wind_speed_ms is not None else 1.0
    )

    return {
        'score':               raw_score * wind_factor,
        'active_sites':        len(sites),
        'total_cost_millions': round(sum(s['cost_m'] for s in sites), 1),
        'wind_factor':         round(wind_factor, 2),
    }


def _get_recent_wind_speed(cursor, lat, lon):
    """
    Look up the most recent wind speed from weather_data near the place,
    used for dust dispersion correction. Returns wind speed in m/s, or
    None if no recent reading. Picks the suburb nearest to (lat, lon).
    """
    cursor.execute("""
        SELECT latitude, longitude, wind_speed_ms
        FROM weather_data
        WHERE wind_speed_ms IS NOT NULL
        ORDER BY recorded_at DESC
        LIMIT 100
    """)
    rows = cursor.fetchall()
    if not rows:
        return None

    best = None
    best_d = float('inf')
    for r in rows:
        try:
            d = haversine_m(lat, lon,
                            float(r['latitude']), float(r['longitude']))
        except (TypeError, ValueError):
            continue
        if d < best_d:
            best_d = d
            best = float(r['wind_speed_ms'])
    # Only trust the reading if there's a station within ~5km
    return best if best_d <= 5000 else None


def _traffic_within(cursor, lat, lon, radius_m):
    """
    Return (avg_volume, avg_emission_index) for traffic points within radius.
    Returns (None, None) if no points in range.
    """
    s, n, w, e = bbox_around(lat, lon, radius_m)
    cursor.execute("""
        SELECT lat, lon, daily_volume, emission_index
        FROM traffic_points
        WHERE lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """, (s, n, w, e))

    vols, emissions = [], []
    for row in cursor.fetchall():
        if haversine_m(lat, lon, row['lat'], row['lon']) <= radius_m:
            if row.get('daily_volume') is not None:
                vols.append(float(row['daily_volume']))
            if row.get('emission_index') is not None:
                emissions.append(float(row['emission_index']))

    avg_vol = sum(vols) / len(vols) if vols else None
    avg_em  = sum(emissions) / len(emissions) if emissions else None
    return avg_vol, avg_em


def _nearest_air_quality(cursor, lat, lon, max_radius_m=2000):
    """
    Get PM2.5 from the nearest air-quality reading.

    Strategy (in order of preference):
      1. air_quality_points — real microclimate sensors. Only 3 sites
         live in CBD but very accurate. Try within max_radius_m first.
      2. aqi_data fallback — per-suburb hourly PM2.5/PM10 from a wider
         source. Coverage is 10 CBD suburbs with centroid coordinates,
         so it always returns something within a couple of km in CBD.

    Returns (pm25, source) where source is 'sensor' or 'aqi_suburb' or None.
    Caller logs source so users know the precision level.
    """
    # --- Primary: microclimate sensors -------------------------------
    s, n, w, e = bbox_around(lat, lon, max_radius_m)
    cursor.execute("""
        SELECT lat, lon, pm25
        FROM air_quality_points
        WHERE pm25 IS NOT NULL
          AND lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """, (s, n, w, e))

    best_d, best_pm = float('inf'), None
    for row in cursor.fetchall():
        d = haversine_m(lat, lon, row['lat'], row['lon'])
        if d <= max_radius_m and d < best_d:
            best_d, best_pm = d, float(row['pm25'])
    if best_pm is not None:
        return best_pm, 'sensor'

    # --- Fallback: per-suburb aqi_data -------------------------------
    # Pull the latest reading per suburb (the table has many timestamps),
    # find the suburb whose centroid is closest to the place. Run distance
    # in Python because the table uses DECIMAL types.
    cursor.execute("""
        SELECT suburb, latitude, longitude, pm25
        FROM aqi_data a1
        WHERE pm25 IS NOT NULL
          AND latitude IS NOT NULL
          AND recorded_at = (
              SELECT MAX(recorded_at) FROM aqi_data a2
              WHERE a2.suburb = a1.suburb
          )
    """)
    rows = cursor.fetchall()
    best_d, best_pm = float('inf'), None
    for r in rows:
        try:
            d = haversine_m(lat, lon,
                            float(r['latitude']), float(r['longitude']))
        except (TypeError, ValueError):
            continue
        if d < best_d:
            best_d, best_pm = d, float(r['pm25'])
    if best_pm is not None and best_d <= 5000:
        return best_pm, 'aqi_suburb'

    return None, None


def _pollen_score_within(cursor, lat, lon, radius_m, current_month):
    """
    Sum (allergen_weight * pollen_factor) over all in-season allergenic
    trees within radius. Off-season -> 0 regardless of tree count.

    Returns (score, tree_count, dominant_genus). Dominant genus is the
    most common in-season genus nearby, used in the explanation string.
    """
    active_genera = POLLEN_SEASONS.get(current_month, [])
    if not active_genera:
        return 0.0, 0, None

    s, n, w, e = bbox_around(lat, lon, radius_m)
    placeholders = ','.join(['%s'] * len(active_genera))
    cursor.execute(f"""
        SELECT lat, lon, genus, allergen_weight, pollen_factor
        FROM urban_trees
        WHERE is_allergenic = TRUE
          AND genus IN ({placeholders})
          AND lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """, (*active_genera, s, n, w, e))

    total = 0.0
    count = 0
    genus_counts = {}
    for r in cursor.fetchall():
        d = haversine_m(lat, lon, float(r['lat']), float(r['lon']))
        if d > radius_m:
            continue
        weight = float(r['allergen_weight'])
        factor = float(r['pollen_factor'])
        total += weight * factor
        count += 1
        g = r['genus']
        genus_counts[g] = genus_counts.get(g, 0) + 1

    dominant = max(genus_counts, key=genus_counts.get) if genus_counts else None
    return total, count, dominant


# ============================================================
# Scoring
# ============================================================

def _normalize(value, saturation):
    """Clamp value/saturation into [0, 1]."""
    if value is None:
        return None
    return max(0.0, min(1.0, value / saturation))


def score_place(cursor, place_lat, place_lon, query_date,
                current_month=None):
    """
    Compute a 0-100 safety score for one place and return a dict
    containing the score plus the raw evidence used (for the explanation
    layer).

    5 risk dimensions:
      construction (200m): dust from nearby active building sites,
                           wind-corrected
      traffic      (400m): vehicle volume from SCATS
      emission     (400m): NOx index derived from traffic volume
      air_quality  (2km):  PM2.5 from microclimate sensor or aqi_data
      pollen        (50m): in-season allergenic trees from urban_trees

    current_month is needed for pollen season filtering. If not passed,
    derived from query_date.
    """
    if current_month is None:
        from datetime import datetime
        current_month = datetime.strptime(query_date, '%Y-%m-%d').month

    # Wind for dust dispersion correction
    wind_ms = _get_recent_wind_speed(cursor, place_lat, place_lon)

    # 1. Construction dust (replaces simple count — now cost-weighted +
    #    wind-corrected, mirroring the XGBoost feature logic)
    dust = _dust_score_for_place(
        cursor, place_lat, place_lon, CONSTRUCTION_RADIUS_M,
        query_date, wind_speed_ms=wind_ms,
    )

    # 2. Traffic carries further AND SCATS detectors are spaced 200-500m
    #    apart, so 400m reliably catches nearby roads.
    avg_volume, avg_emission = _traffic_within(
        cursor, place_lat, place_lon, TRAFFIC_RADIUS_M,
    )

    # 3. Air quality with fallback
    pm25, air_source = _nearest_air_quality(cursor, place_lat, place_lon)

    # 4. Pollen (in-season trees, 50m near-field)
    pollen_raw, tree_count, dominant_genus = _pollen_score_within(
        cursor, place_lat, place_lon, POLLEN_RADIUS_M, current_month,
    )

    # Per-factor risk in [0, 1].
    # CRITICAL: when a measurement is missing, do NOT default to 0 (zero
    # risk = free pass). That makes data-sparse locations look safer than
    # they actually are. Use NEUTRAL (~0.3) instead so missing data
    # neither helps nor crushes the score.
    r_construction = _normalize(dust['score'],   CONSTRUCTION_SATURATION) or 0.0
    r_traffic      = (_normalize(avg_volume, TRAFFIC_SATURATION)
                      if avg_volume is not None else TRAFFIC_NEUTRAL)
    r_emission     = (_normalize(avg_emission, EMISSION_SATURATION)
                      if avg_emission is not None else TRAFFIC_NEUTRAL)
    r_air          = (_normalize(pm25, PM25_SATURATION)
                      if pm25 is not None else PM25_NEUTRAL)
    # Pollen off-season is genuinely 0 — different from "data missing",
    # so no neutral fallback. Score 0 means there really is no pollen.
    r_pollen       = _normalize(pollen_raw, POLLEN_SATURATION) or 0.0

    total_risk = (
        RISK_WEIGHTS['construction'] * r_construction +
        RISK_WEIGHTS['traffic']      * r_traffic +
        RISK_WEIGHTS['emission']     * r_emission +
        RISK_WEIGHTS['air_quality']  * r_air +
        RISK_WEIGHTS['pollen']       * r_pollen
    )
    score = round((1.0 - total_risk) * 100)

    return {
        'score': score,
        'risk_breakdown': {
            'construction': round(r_construction, 3),
            'traffic':      round(r_traffic, 3),
            'emission':     round(r_emission, 3),
            'air_quality':  round(r_air, 3),
            'pollen':       round(r_pollen, 3),
        },
        'evidence': {
            # Construction
            'construction_sites':  dust['active_sites'],
            'construction_cost_m': dust['total_cost_millions'],
            'wind_factor':         dust['wind_factor'],
            # Traffic / emission
            'traffic_volume':      int(avg_volume) if avg_volume is not None else None,
            'emission_index':      round(avg_emission, 1) if avg_emission is not None else None,
            # Air quality
            'pm25':                round(pm25, 1) if pm25 is not None else None,
            'air_quality_source':  air_source,
            # Pollen
            'pollen_tree_count':   tree_count,
            'pollen_dominant':     dominant_genus,
            'pollen_in_season':    bool(POLLEN_SEASONS.get(current_month, [])),
        },
    }


# ============================================================
# Explanation — turn the breakdown into plain English
# ============================================================

def explain_score(score, evidence, breakdown):
    """
    Return human-readable bullets + an overall verdict.

    Designed so a guardian can read 3 lines and decide. Avoids units
    where the number alone isn't meaningful to a non-expert.
    """
    highlights = []

    # Construction dust — describe severity from the breakdown (which is
    # the actual scored risk), not from raw site count. Wording matters:
    # if there are 20 sites and we still call it 'low risk', users get
    # confused. So when count is high but risk is low, we say WHY (most
    # are far or small) instead of misleadingly calling them 'small'.
    n = evidence['construction_sites']
    cost = evidence['construction_cost_m']
    construction_risk = breakdown['construction']

    if n == 0:
        highlights.append({'icon': 'good', 'text': 'No active construction sites nearby'})
    elif construction_risk < 0.20:
        # Genuinely low: either few sites OR many sites that are far / small
        if n <= 3:
            highlights.append({'icon': 'good',
                               'text': f'{n} small construction site{"s" if n > 1 else ""} nearby, low dust risk'})
        else:
            # Honest about the count, explain why risk is still low
            highlights.append({'icon': 'good',
                               'text': f'{n} permits nearby but mostly minor work (${cost:.0f}M total) — low dust risk'})
    elif construction_risk < 0.50:
        highlights.append({'icon': 'warn',
                           'text': f'{n} active site{"s" if n > 1 else ""} within 200m '
                                   f'(approx ${cost:.0f}M of work) — some dust possible'})
    elif construction_risk < 0.80:
        highlights.append({'icon': 'bad',
                           'text': f'{n} construction sites within 200m '
                                   f'(approx ${cost:.0f}M of work) — higher dust risk'})
    else:
        # Saturated risk: dense construction zone
        highlights.append({'icon': 'bad',
                           'text': f'Dense construction zone ({n} sites, ${cost:.0f}M of work) '
                                   f'— significant dust exposure expected'})

    # Traffic + emission together (they tell the same story)
    t = breakdown['traffic']
    e = breakdown['emission']
    combined = max(t, e)
    if evidence['traffic_volume'] is None:
        # No traffic data in range — don't fake a finding
        pass
    elif combined < 0.30:
        highlights.append({'icon': 'good', 'text': 'Quiet streets with low vehicle traffic'})
    elif combined < 0.70:
        highlights.append({'icon': 'warn', 'text': 'Moderate vehicle traffic in the area'})
    else:
        highlights.append({'icon': 'bad',  'text': 'Close to busy roads with heavy traffic'})

    # Air quality
    pm = evidence['pm25']
    if pm is None:
        # Silent — telling a parent "no sensor nearby" doesn't help them decide
        pass
    elif pm < 12:
        highlights.append({'icon': 'good', 'text': 'Air quality reading is good'})
    elif pm < 25:
        highlights.append({'icon': 'warn', 'text': 'Air quality is fair'})
    else:
        highlights.append({'icon': 'bad',  'text': 'Air quality is poor — consider a mask or shorter visit'})

    # Pollen — show even when off-season, so users know it was checked.
    pollen_in_season = evidence.get('pollen_in_season', False)
    pollen_count = evidence.get('pollen_tree_count', 0)
    pollen_risk = breakdown.get('pollen', 0)
    dominant = evidence.get('pollen_dominant')
    if not pollen_in_season:
        highlights.append({'icon': 'good',
                           'text': 'Outside tree pollen season — minimal pollen risk'})
    elif pollen_count == 0:
        highlights.append({'icon': 'good', 'text': 'No allergenic trees in season nearby'})
    elif pollen_risk < 0.30:
        highlights.append({'icon': 'good',
                           'text': f'A few in-season {dominant} trees nearby, low pollen risk'})
    elif pollen_risk < 0.70:
        highlights.append({'icon': 'warn',
                           'text': f'{pollen_count} allergenic trees nearby ({dominant} mostly), '
                                   f'moderate pollen exposure'})
    else:
        highlights.append({'icon': 'bad',
                           'text': f'{pollen_count} allergenic trees nearby ({dominant} mostly), '
                                   f'high pollen exposure'})

    # Verdict
    if score >= 75:
        verdict = 'Good for extended outdoor time'
    elif score >= 50:
        verdict = 'OK for a short visit (under an hour)'
    else:
        verdict = 'Consider somewhere else, or visit briefly'

    return highlights, verdict


# ============================================================
# BATCH SCORING — preloads data once, scores all places in memory.
# Used by list_safe_spots() to avoid N+1 queries.
# ============================================================

def _preload_for_batch(cursor, origin_lat, origin_lon, radius_m, query_date):
    """
    One-shot fetch of every dataset we need to score every place in the
    candidate set. Run before the per-place scoring loop.

    Strategy: pad the user-requested bbox by the largest per-place radius
    (TRAFFIC_RADIUS_M = 400m) so every place's 400m search circle is
    contained inside the preloaded data. After that, each place's scoring
    is a pure-Python set of haversine checks — no DB hits at all.

    Returns a context dict consumed by _score_place_from_cache().
    """
    # The places themselves are within `radius_m` of the origin. Each
    # place then looks up to TRAFFIC_RADIUS_M (400m) further out, so
    # the total bbox we need to preload is radius_m + 400m.
    preload_radius = radius_m + max(TRAFFIC_RADIUS_M, CONSTRUCTION_RADIUS_M,
                                    POLLEN_RADIUS_M)
    s, n, w, e = bbox_around(origin_lat, origin_lon, preload_radius)

    # 1. Construction sites (de-duped per building)
    cursor.execute("""
        SELECT lat, lon, MAX(estimated_cost) AS max_cost,
               COUNT(*) AS permit_count
        FROM building_permits
        WHERE lat IS NOT NULL AND lon IS NOT NULL
          AND lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
          AND issue_date <= %s
          AND completed_by_date >= %s
        GROUP BY lat, lon
    """, (s, n, w, e, query_date, query_date))
    permits = [dict(r) for r in cursor.fetchall()]

    # 2. SCATS traffic points
    cursor.execute("""
        SELECT lat, lon, daily_volume, emission_index
        FROM traffic_points
        WHERE lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """, (s, n, w, e))
    traffic = [dict(r) for r in cursor.fetchall()]

    # 3. Air quality — load both tables once, full state of the world.
    # These are tiny (3 sensors + 10 suburbs) so no bbox filter needed.
    cursor.execute("""
        SELECT lat, lon, pm25 FROM air_quality_points WHERE pm25 IS NOT NULL
    """)
    air_sensors = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT suburb, latitude AS lat, longitude AS lon, pm25
        FROM aqi_data a1
        WHERE pm25 IS NOT NULL AND latitude IS NOT NULL
          AND recorded_at = (
              SELECT MAX(recorded_at) FROM aqi_data a2
              WHERE a2.suburb = a1.suburb
          )
    """)
    air_aqi = [dict(r) for r in cursor.fetchall()]

    # 4. Allergenic trees in season (large query — 82k rows — but bbox
    # filter keeps it manageable; CBD slice is ~3-5k trees)
    from datetime import datetime
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month
    active_genera = POLLEN_SEASONS.get(current_month, [])
    trees = []
    if active_genera:
        placeholders = ','.join(['%s'] * len(active_genera))
        cursor.execute(f"""
            SELECT lat, lon, genus, allergen_weight, pollen_factor
            FROM urban_trees
            WHERE is_allergenic = TRUE
              AND genus IN ({placeholders})
              AND lat BETWEEN %s AND %s
              AND lon BETWEEN %s AND %s
        """, (*active_genera, s, n, w, e))
        trees = [dict(r) for r in cursor.fetchall()]

    # 5. Wind speed: one reading, applies to everyone in CBD
    cursor.execute("""
        SELECT latitude, longitude, wind_speed_ms
        FROM weather_data
        WHERE wind_speed_ms IS NOT NULL
        ORDER BY recorded_at DESC
        LIMIT 100
    """)
    wind_rows = list(cursor.fetchall())
    best_wind = None
    best_d = float('inf')
    for r in wind_rows:
        try:
            d = haversine_m(origin_lat, origin_lon,
                            float(r['latitude']), float(r['longitude']))
            if d < best_d:
                best_d = d
                best_wind = float(r['wind_speed_ms'])
        except (TypeError, ValueError):
            continue

    return {
        'permits':       permits,
        'traffic':       traffic,
        'air_sensors':   air_sensors,
        'air_aqi':       air_aqi,
        'trees':         trees,
        'wind_ms':       best_wind,
        'current_month': current_month,
    }


def _score_place_from_cache(place_lat, place_lon, cache):
    """
    Score one place using the preloaded cache instead of querying the DB.

    Same output contract as score_place() — returns
    {'score', 'risk_breakdown', 'evidence'} — so the rest of the pipeline
    (explain_score, list assembly) doesn't change.
    """
    wind_ms = cache['wind_ms']

    # 1. Construction dust — filter cached permits by distance.
    sites = []
    for p in cache['permits']:
        d = haversine_m(place_lat, place_lon, p['lat'], p['lon'])
        if d > CONSTRUCTION_RADIUS_M:
            continue
        cost_m = min(float(p['max_cost'] or 0) / 1_000_000, 50.0)
        sites.append({'distance_m': d, 'cost_m': cost_m})

    if sites:
        raw_score = 0.0
        for site in sites:
            effective_d = max(site['distance_m'], 30)
            decay = (30 / effective_d) ** 0.5
            raw_score += site['cost_m'] * decay
        wind_factor = (
            max(0.2, WIND_FACTOR_BASE - WIND_FACTOR_DECAY * wind_ms)
            if wind_ms is not None else 1.0
        )
        dust = {
            'score':               raw_score * wind_factor,
            'active_sites':        len(sites),
            'total_cost_millions': round(sum(s['cost_m'] for s in sites), 1),
            'wind_factor':         round(wind_factor, 2),
        }
    else:
        dust = {'score': 0.0, 'active_sites': 0,
                'total_cost_millions': 0.0, 'wind_factor': 1.0}

    # 2. Traffic + emission — filter cached SCATS points by distance.
    vols, emissions = [], []
    for t in cache['traffic']:
        d = haversine_m(place_lat, place_lon, t['lat'], t['lon'])
        if d > TRAFFIC_RADIUS_M:
            continue
        if t.get('daily_volume') is not None:
            vols.append(float(t['daily_volume']))
        if t.get('emission_index') is not None:
            emissions.append(float(t['emission_index']))
    avg_volume = sum(vols) / len(vols) if vols else None
    avg_emission = sum(emissions) / len(emissions) if emissions else None

    # 3. Air quality — sensor preferred, then aqi_data fallback.
    pm25 = None
    air_source = None
    best_d = float('inf')
    for a in cache['air_sensors']:
        d = haversine_m(place_lat, place_lon, a['lat'], a['lon'])
        if d <= 2000 and d < best_d:
            best_d = d
            pm25 = float(a['pm25'])
            air_source = 'sensor'
    if pm25 is None:
        best_d = float('inf')
        for a in cache['air_aqi']:
            try:
                d = haversine_m(place_lat, place_lon,
                                float(a['lat']), float(a['lon']))
            except (TypeError, ValueError):
                continue
            if d <= 5000 and d < best_d:
                best_d = d
                pm25 = float(a['pm25'])
                air_source = 'aqi_suburb'

    # 4. Pollen — filter cached in-season trees by distance.
    pollen_raw = 0.0
    tree_count = 0
    genus_counts = {}
    for tr in cache['trees']:
        d = haversine_m(place_lat, place_lon, float(tr['lat']), float(tr['lon']))
        if d > POLLEN_RADIUS_M:
            continue
        weight = float(tr['allergen_weight'])
        factor = float(tr['pollen_factor'])
        pollen_raw += weight * factor
        tree_count += 1
        g = tr['genus']
        genus_counts[g] = genus_counts.get(g, 0) + 1
    dominant_genus = (max(genus_counts, key=genus_counts.get)
                      if genus_counts else None)

    # --- Combine into the standard score_place output shape ----------
    r_construction = _normalize(dust['score'],   CONSTRUCTION_SATURATION) or 0.0
    r_traffic      = (_normalize(avg_volume, TRAFFIC_SATURATION)
                      if avg_volume is not None else TRAFFIC_NEUTRAL)
    r_emission     = (_normalize(avg_emission, EMISSION_SATURATION)
                      if avg_emission is not None else TRAFFIC_NEUTRAL)
    r_air          = (_normalize(pm25, PM25_SATURATION)
                      if pm25 is not None else PM25_NEUTRAL)
    r_pollen       = _normalize(pollen_raw, POLLEN_SATURATION) or 0.0

    total_risk = (
        RISK_WEIGHTS['construction'] * r_construction +
        RISK_WEIGHTS['traffic']      * r_traffic +
        RISK_WEIGHTS['emission']     * r_emission +
        RISK_WEIGHTS['air_quality']  * r_air +
        RISK_WEIGHTS['pollen']       * r_pollen
    )
    score = round((1.0 - total_risk) * 100)

    return {
        'score': score,
        'risk_breakdown': {
            'construction': round(r_construction, 3),
            'traffic':      round(r_traffic, 3),
            'emission':     round(r_emission, 3),
            'air_quality':  round(r_air, 3),
            'pollen':       round(r_pollen, 3),
        },
        'evidence': {
            'construction_sites':  dust['active_sites'],
            'construction_cost_m': dust['total_cost_millions'],
            'wind_factor':         dust['wind_factor'],
            'traffic_volume':      int(avg_volume) if avg_volume is not None else None,
            'emission_index':      round(avg_emission, 1) if avg_emission is not None else None,
            'pm25':                round(pm25, 1) if pm25 is not None else None,
            'air_quality_source':  air_source,
            'pollen_tree_count':   tree_count,
            'pollen_dominant':     dominant_genus,
            'pollen_in_season':    bool(POLLEN_SEASONS.get(cache['current_month'], [])),
        },
    }


# ============================================================
# Public entry point
# ============================================================

def list_safe_spots(origin_lat, origin_lon, radius_m, db_conn,
                    categories=None, sort_by='score', query_date=None,
                    limit=50):
    """
    Main entry. Returns a dict ready to jsonify:

      {
        'origin': {'lat': ..., 'lon': ...},
        'radius_m': ...,
        'count': N,
        'places': [ {name, category, lat, lon, distance_m, safety_score,
                     verdict, highlights, risk_breakdown, evidence}, ... ],
        'methodology': '...',
      }

    sort_by: 'score' (default, high to low) or 'distance' (near to far)
    categories: list of safe_places.category values to include; None = all
    """
    from datetime import datetime
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')

    cursor = db_conn.cursor(dictionary=True)
    try:
        candidates = _places_in_radius(cursor, origin_lat, origin_lon,
                                       radius_m, categories=categories)

        # Preload everything we need ONCE — replaces ~5 queries per place
        # with 5 queries total. On 144 candidates this drops latency from
        # ~25s to ~1-2s.
        cache = _preload_for_batch(cursor, origin_lat, origin_lon,
                                   radius_m, query_date)

        scored = []
        for p in candidates:
            s = _score_place_from_cache(p['lat'], p['lon'], cache)
            highlights, verdict = explain_score(
                s['score'], s['evidence'], s['risk_breakdown'],
            )
            scored.append({
                'id':            p['id'],
                'name':          p['name'],
                'category':      p['category'],
                'category_label': PLACE_CATEGORIES.get(p['category'], p['category']),
                'lat':           p['lat'],
                'lon':           p['lon'],
                'address':       p.get('address'),
                'distance_m':    p['distance_m'],
                'safety_score':  s['score'],
                'verdict':       verdict,
                'highlights':    highlights,
                'risk_breakdown': s['risk_breakdown'],
                'evidence':      s['evidence'],
            })

        # Sort. Tiebreakers are explainable (you can show the user why
        # one place ranked above another) — never opaque hashing.
        #
        # When sorting by score, tied scores fall back to:
        #   1. closer distance wins (less travel = less exposure on the way)
        #   2. category preference: parks > playgrounds > libraries >
        #      childcare > landmarks. Parks are the most open, kid-friendly
        #      outdoor option, so when everything else is identical we
        #      surface them first.
        # If two places match on ALL of (score, distance, category),
        # they're genuinely equivalent — the user sees them next to each
        # other and chooses based on whatever matters to them personally.
        CATEGORY_PRIORITY = {
            'park': 0, 'playground': 1, 'library': 2,
            'childcare': 3, 'landmark': 4,
        }
        if sort_by == 'distance':
            scored.sort(key=lambda x: (
                x['distance_m'],
                -x['safety_score'],
                CATEGORY_PRIORITY.get(x['category'], 99),
            ))
        else:  # 'score'
            scored.sort(key=lambda x: (
                -x['safety_score'],
                x['distance_m'],
                CATEGORY_PRIORITY.get(x['category'], 99),
            ))

        scored = scored[:limit]

        return {
            'origin':   {'lat': origin_lat, 'lon': origin_lon},
            'radius_m': radius_m,
            'count':    len(scored),
            'sort_by':  sort_by,
            'places':   scored,
            'methodology': (
                "Each place is scored 0-100 based on 5 factors near it: "
                "construction dust within 200m, vehicle traffic and emissions "
                "within 400m, the nearest air-quality reading, and allergenic "
                "trees in pollen season within 50m. Higher score = cleaner, "
                "quieter, lower pollen exposure."
            ),
        }
    finally:
        cursor.close()