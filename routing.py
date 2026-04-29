"""
routing.py — Safe route recommendation for AsthmaSafe Melbourne.

Given start + end coordinates, runs a LOCAL Dijkstra on an OpenStreetMap
walk/drive graph (no external routing API), produces up to 3 candidate
routes, then scores each on (distance + dust + pollen exposure) to
return the best one.

Designed to be imported by api.py and exposed via /api/safe-route.

Scoring model (lower = safer):
    composite_score = w_dist * dist_norm
                    + w_dust * dust_norm
                    + w_pollen * pollen_norm

All three components are normalised 0-100 across the candidate routes,
so the comparison is *relative* — even a "bad" route gets some routes
scoring near 0 if it's the least bad option.

Path planning:
    Routes are computed locally via networkx.shortest_path on an
    OSM-derived graph loaded once from disk (data/melbourne_walk.graphml
    or melbourne_drive.graphml). Build these once with scripts/build_graph.py.
    No external HTTP calls during routing.
"""

import math
from datetime import datetime

import networkx as nx
import osmnx as ox

# ============================================================
# CONFIG
# ============================================================

# Pre-built OSM graph. Run scripts/build_graph.py once to generate.
# All profiles use the walk graph — AsthmaSafe targets pedestrian routing
# for asthmatic users. Driving is supported syntactically for API
# compatibility but uses the same graph (driving profile mostly affects
# the speed used to estimate duration).
GRAPH_PATHS = {
    'walking': 'data/melbourne_walk.graphml',
    'cycling': 'data/melbourne_walk.graphml',
    'driving': 'data/melbourne_walk.graphml',
}

# Average travel speeds (m/s), used to estimate duration from path length
# since OSM edges don't carry reliable speed limits for walking/cycling.
SPEEDS_MPS = {
    'walking': 1.4,   # ~5 km/h
    'cycling': 4.2,   # ~15 km/h
    'driving': 11.0,  # ~40 km/h, urban
}

# How often to sample points along a route for exposure scoring.
# 50m strikes a balance: short routes get ~10 samples, long routes ~50.
ROUTE_SAMPLE_INTERVAL_M = 50

# Radius around each sample point to look for nearby permits / trees.
# Dust travels further than pollen direct exposure.
DUST_SAMPLE_RADIUS_M = 200
POLLEN_SAMPLE_RADIUS_M = 30

# Default scoring weights (sum to 1.0).
# Distance gets the largest weight because users care most about not detouring;
# dust + pollen split the rest. User can override via ?weights= param.
DEFAULT_WEIGHTS = {
    'distance': 0.40,
    'dust':     0.30,
    'pollen':   0.30,
}

# Cap on detour: routes more than this much longer than the shortest are
# discarded even if they have lower exposure. Stops the algorithm from
# suggesting absurd 5km detours to avoid 1 plane tree.
MAX_DETOUR_RATIO = 1.5  # i.e. "no route can be more than 50% longer than the shortest"

# How many alternative routes to attempt to generate.
DEFAULT_ALTERNATIVES = 3

# Two routes are considered "the same" if they share more than this fraction
# of their nodes. Filters out near-duplicate alternatives.
ROUTE_SIMILARITY_THRESHOLD = 0.85

# Pollen seasons by month (Southern Hemisphere)
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


# ============================================================
# GRAPH LOADING (lazy + cached)
# ============================================================
_GRAPH_CACHE = {}

def get_graph(profile='walking'):
    """
    Lazy-load the OSM graph for the requested profile from disk.
    Cached after first call so subsequent requests are instant.

    Raises FileNotFoundError if the graph hasn't been built yet —
    in that case, run scripts/build_graph.py first.
    """
    if profile not in GRAPH_PATHS:
        raise ValueError(f"Unknown profile: {profile!r}. "
                         f"Must be one of {list(GRAPH_PATHS)}.")

    path = GRAPH_PATHS[profile]
    if path in _GRAPH_CACHE:
        return _GRAPH_CACHE[path]

    G = ox.load_graphml(path)
    _GRAPH_CACHE[path] = G
    return G


# ============================================================
# GEOMETRY HELPERS
# ============================================================
def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance between two lat/lon points, in meters."""
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sample_route_points(geojson_coordinates, interval_m=ROUTE_SAMPLE_INTERVAL_M):
    """
    Walk a GeoJSON LineString and emit (lat, lon) sample points roughly
    `interval_m` meters apart. Always includes the start and end.

    Args:
        geojson_coordinates: list of [lon, lat] pairs
        interval_m: target spacing between samples

    Returns: list of (lat, lon) tuples
    """
    if not geojson_coordinates or len(geojson_coordinates) < 2:
        return []

    samples = []
    accumulated = 0.0
    # Coordinates come in [lon, lat] — flip immediately for clarity
    pts = [(c[1], c[0]) for c in geojson_coordinates]
    samples.append(pts[0])

    for i in range(1, len(pts)):
        seg_len = haversine_m(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1])
        if seg_len <= 0:
            continue
        # Walk along this segment, dropping a sample every interval_m
        next_threshold = interval_m - accumulated
        while next_threshold <= seg_len:
            t = next_threshold / seg_len
            lat = pts[i-1][0] + (pts[i][0] - pts[i-1][0]) * t
            lon = pts[i-1][1] + (pts[i][1] - pts[i-1][1]) * t
            samples.append((lat, lon))
            next_threshold += interval_m
        accumulated = (accumulated + seg_len) % interval_m

    # Always include the actual endpoint
    if samples[-1] != pts[-1]:
        samples.append(pts[-1])
    return samples


def bbox_around_points(points, padding_m):
    """
    Compute a (min_lat, max_lat, min_lon, max_lon) bounding box that contains
    all `points` plus `padding_m` meters of buffer on all sides.

    Used to do a single SQL query for ALL trees/permits along a route at once,
    instead of one query per sample point (would be ~50 queries per route).
    """
    if not points:
        return None
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    # Roughly: 1 degree latitude = 111km, 1 degree lon @ -37° = ~88km
    lat_pad = padding_m / 111000
    lon_pad = padding_m / (111000 * math.cos(math.radians(sum(lats) / len(lats))))
    return (min(lats) - lat_pad, max(lats) + lat_pad,
            min(lons) - lon_pad, max(lons) + lon_pad)


# ============================================================
# LOCAL ROUTE PLANNING (replaces OSRM)
# ============================================================
_SIMPLE_GRAPH_CACHE = {}

def _to_simple_digraph(G):
    """
    Collapse a MultiDiGraph (osmnx default) into a simple DiGraph by keeping
    only the shortest parallel edge between each pair of nodes. Required for
    networkx.shortest_simple_paths (Yen's algorithm), which doesn't support
    multi-edges. Cached per-graph so we only do this once.
    """
    cache_key = id(G)
    if cache_key in _SIMPLE_GRAPH_CACHE:
        return _SIMPLE_GRAPH_CACHE[cache_key]

    H = nx.DiGraph()
    H.add_nodes_from(G.nodes(data=True))
    for u, v, data in G.edges(data=True):
        length = data.get('length', 0.0)
        if H.has_edge(u, v):
            if length < H[u][v]['length']:
                H[u][v]['length'] = length
        else:
            H.add_edge(u, v, length=length)
    _SIMPLE_GRAPH_CACHE[cache_key] = H
    return H


def _path_to_route_dict(G, node_path, speed_mps):
    """
    Convert a NetworkX node-id path → a dict shaped like an OSRM route.
    Keeps the rest of the pipeline (sampling, scoring) unchanged.

    NOTE on multi-edges: OSMnx returns a MultiDiGraph because two nodes can
    be connected by multiple parallel ways (e.g. a road + an adjacent path).
    For length we take the minimum across parallel edges, which matches what
    nx.shortest_path used internally when picking this path.
    """
    coords = []  # GeoJSON [lon, lat]
    total_length = 0.0

    for i, node in enumerate(node_path):
        coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        if i > 0:
            edge_data = G.get_edge_data(node_path[i-1], node)
            # MultiDiGraph: edge_data is {key: attrs}; pick min-length parallel edge
            length = min(d.get('length', 0.0) for d in edge_data.values())
            total_length += length

    return {
        'geometry': {'type': 'LineString', 'coordinates': coords},
        'distance': total_length,
        'duration': total_length / speed_mps,
        '_node_path': node_path,  # internal — stripped before returning to client
    }


def _routes_are_distinct(path_a, path_b, threshold=ROUTE_SIMILARITY_THRESHOLD):
    """
    Return True if two node paths differ on more than (1-threshold) of their
    combined node set. Yen's algorithm tends to produce alternatives that
    differ by only one or two nodes — we want genuinely different routes.
    """
    a = set(path_a)
    b = set(path_b)
    if not a or not b:
        return True
    overlap = len(a & b) / max(len(a), len(b))
    return overlap < threshold


def _penalised_alternatives(G, primary_path, dest_orig, num_alternatives,
                            penalty_factor=3.0):
    """
    Generate alternative paths via edge-penalty method.

    For each alternative wanted, multiply the lengths of edges already used
    by previous paths by `penalty_factor`, then re-run Dijkstra. The
    penalty discourages reuse, forcing genuinely different routes.

    This is much faster than Yen's algorithm (one extra Dijkstra per
    alternative vs. O(path_len) Dijkstras per Yen iteration), and on
    MultiDiGraph it works directly without the simple-graph conversion.

    Args:
        G: the OSM graph (MultiDiGraph)
        primary_path: node list of the already-found shortest path
        dest_orig: tuple (orig_node, dest_node)
        num_alternatives: how many alternatives to attempt
        penalty_factor: multiplier applied to penalised edges (>1)

    Returns: list of node-lists, each a distinct alternative path
    """
    orig, dest = dest_orig
    alternatives = []
    penalised_pairs = set()  # (u, v) edges that have been penalised at least once

    # Mark the primary path's edges as penalised
    for i in range(len(primary_path) - 1):
        penalised_pairs.add((primary_path[i], primary_path[i + 1]))

    # Custom weight function: returns penalised length if the (u, v) pair is
    # in the penalised set, else regular length. Multi-edge: take min length.
    def penalised_weight(u, v, edge_data):
        length = min(d.get('length', 0.0) for d in edge_data.values())
        if (u, v) in penalised_pairs:
            return length * penalty_factor
        return length

    accepted_paths = [primary_path]

    for _ in range(num_alternatives):
        try:
            path = nx.shortest_path(G, orig, dest, weight=penalised_weight)
        except nx.NetworkXNoPath:
            break

        # Skip if we've already got this exact path (penalty wasn't enough
        # to push the algorithm off it — happens on tightly-constrained graphs)
        if any(path == p for p in accepted_paths):
            # Bump penalty for next iteration to try harder
            for i in range(len(path) - 1):
                penalised_pairs.add((path[i], path[i + 1]))
            continue

        # Check distinctness vs. all previously accepted paths
        if all(_routes_are_distinct(path, p) for p in accepted_paths):
            alternatives.append(path)
            accepted_paths.append(path)

        # Add this path's edges to the penalty set so the next iteration
        # is pushed away from both the primary AND this alternative
        for i in range(len(path) - 1):
            penalised_pairs.add((path[i], path[i + 1]))

    return alternatives


def fetch_routes(start_lat, start_lon, end_lat, end_lon,
                 profile='walking', alternatives=DEFAULT_ALTERNATIVES,
                 timeout=None):
    """
    Compute candidate routes locally using OSM graph + Dijkstra.

    Primary route uses pure shortest-path. Alternatives are produced via the
    edge-penalty method: each alternative re-runs Dijkstra after multiplying
    previously-used edges by a penalty factor, forcing new routes.

    Drop-in replacement for the previous OSRM-backed version: returns a list
    of dicts with the same shape ({'geometry', 'distance', 'duration'}) so
    nothing downstream needs to change.

    Args:
        profile: 'walking', 'driving', or 'cycling'
        alternatives: how many distinct routes to attempt to return
        timeout: ignored (kept for API compatibility with the old OSRM signature)

    Returns: list of route dicts (1 to `alternatives` items)
    Raises:
        FileNotFoundError if graph hasn't been built
        RuntimeError if no path exists between start and end
    """
    G = get_graph(profile)
    speed_mps = SPEEDS_MPS[profile]

    # Snap user-supplied coordinates to the nearest graph node.
    orig = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)

    if orig == dest:
        raise RuntimeError(
            "Start and end snap to the same graph node — points are too close "
            "together or both fell on the same intersection."
        )

    # Primary route: plain shortest path by length.
    try:
        primary = nx.shortest_path(G, orig, dest, weight='length')
    except nx.NetworkXNoPath:
        raise RuntimeError(
            f"No path found between ({start_lat}, {start_lon}) and "
            f"({end_lat}, {end_lon}) on the {profile} graph."
        )

    routes_out = [_path_to_route_dict(G, primary, speed_mps)]

    if alternatives <= 1:
        return routes_out

    # Generate alternatives via edge-penalty method (fast, MultiDiGraph-native)
    alt_paths = _penalised_alternatives(
        G, primary, (orig, dest),
        num_alternatives=alternatives - 1,
    )
    for path in alt_paths:
        routes_out.append(_path_to_route_dict(G, path, speed_mps))

    return routes_out


# ============================================================
# EXPOSURE SCORING
# ============================================================
def query_permits_in_bbox(db_conn, bbox, query_date):
    """
    Fetch all active building permits whose suburb-center falls within the bbox.

    NOTE: building_permits in our DB doesn't have per-permit lat/lon (only
    suburb names). We approximate each permit's location by its suburb centroid.
    This is a known limitation — see SUBURB_COORDS in api.py.

    Returns: list of dicts {lat, lon, cost, suburb}
    """
    min_lat, max_lat, min_lon, max_lon = bbox

    # Suburb centroids — must match api.py SUBURB_COORDS keys
    SUBURB_COORDS = {
        'Melbourne':       (-37.8136, 144.9631),
        'Southbank':       (-37.8230, 144.9650),
        'Docklands':       (-37.8145, 144.9460),
        'Carlton':         (-37.8000, 144.9670),
        'North Melbourne': (-37.7990, 144.9430),
        'West Melbourne':  (-37.8080, 144.9380),
        'East Melbourne':  (-37.8160, 144.9870),
        'Parkville':       (-37.7860, 144.9550),
        'Kensington':      (-37.7940, 144.9260),
        'South Yarra':     (-37.8380, 144.9930),
    }
    relevant_suburbs = [
        name for name, (lat, lon) in SUBURB_COORDS.items()
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    ]
    if not relevant_suburbs:
        return []

    placeholders = ','.join(['%s'] * len(relevant_suburbs))
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT suburb, COUNT(*) AS cnt, COALESCE(SUM(estimated_cost), 0) AS total_cost
        FROM building_permits
        WHERE suburb IN ({placeholders})
          AND issue_date <= %s
          AND completed_by_date >= %s
        GROUP BY suburb
    """, (*relevant_suburbs, query_date, query_date))
    permits = []
    for row in cursor.fetchall():
        lat, lon = SUBURB_COORDS[row['suburb']]
        permits.append({
            'lat': lat,
            'lon': lon,
            'cost': float(row['total_cost']),
            'count': int(row['cnt']),
            'suburb': row['suburb'],
        })
    cursor.close()
    return permits


def query_allergenic_trees_in_bbox(db_conn, bbox, current_month):
    """
    Fetch only trees that are (a) currently in pollen season AND
    (b) inside the route bbox. One query, returns possibly thousands of rows.
    """
    active_genera = POLLEN_SEASONS.get(current_month, [])
    if not active_genera:
        return []  # off-season → no pollen exposure at all

    min_lat, max_lat, min_lon, max_lon = bbox
    placeholders = ','.join(['%s'] * len(active_genera))
    cursor = db_conn.cursor(dictionary=True)
    try:
        cursor.execute(f"""
            SELECT lat, lon, genus, allergen_weight, pollen_factor
            FROM urban_trees
            WHERE is_allergenic = TRUE
              AND genus IN ({placeholders})
              AND lat BETWEEN %s AND %s
              AND lon BETWEEN %s AND %s
        """, (*active_genera, min_lat, max_lat, min_lon, max_lon))
        return cursor.fetchall()
    except Exception as e:
        # Table doesn't exist yet — degrade gracefully, no pollen scoring
        print(f"  urban_trees query failed: {e}")
        return []
    finally:
        cursor.close()


def score_dust_exposure(samples, permits):
    """
    For each sample point, sum (permit_cost / distance²) over all permits
    within DUST_SAMPLE_RADIUS_M. Inverse-square reflects how dust concentration
    falls off with distance.

    Returns a dimensionless number; relative ordering across routes is what matters.
    """
    if not permits:
        return 0.0
    total = 0.0
    for slat, slon in samples:
        for p in permits:
            d = haversine_m(slat, slon, p['lat'], p['lon'])
            if d <= DUST_SAMPLE_RADIUS_M:
                # Inverse-square with floor of 10m to avoid blowup at zero distance
                effective_d = max(d, 10)
                # Cost in millions × 1/(d/100)² gives reasonable magnitude
                total += (p['cost'] / 1e6) / ((effective_d / 100) ** 2)
    return total


def score_pollen_exposure(samples, trees):
    """
    For each sample point, sum (allergen_weight × pollen_factor) over all
    nearby in-season trees. Pollen is more localised than dust so we use a
    smaller radius and don't apply distance-decay (presence within 30m matters).
    """
    if not trees:
        return 0.0
    total = 0.0
    for slat, slon in samples:
        for t in trees:
            d = haversine_m(slat, slon, float(t['lat']), float(t['lon']))
            if d <= POLLEN_SAMPLE_RADIUS_M:
                weight = float(t['allergen_weight'])
                pf = float(t['pollen_factor'])
                total += weight * pf
    return total


def normalise_scores(values, min_relative_spread=0.05):
    """
    Convert raw scores → 0-100 range, where lowest = 0 (best) and highest = 100 (worst).

    Key fix vs naive minmax: if max and min are within `min_relative_spread`
    of each other (5% by default), treat all values as equivalent and return 0.
    Otherwise the algorithm would amplify trivial 0.04% differences into a
    full 100-point spread, hijacking the composite score.

    Args:
        values: list of raw scores
        min_relative_spread: minimum (max-min)/max ratio required for the spread
                             to be considered meaningful. Below this threshold,
                             all values get score 0 (no penalty).
    """
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [0.0] * len(values)
    # If the relative spread is too small, the routes are effectively equivalent
    # on this dimension — don't manufacture artificial differentiation.
    if hi > 0 and (hi - lo) / hi < min_relative_spread:
        return [0.0] * len(values)
    return [100.0 * (v - lo) / (hi - lo) for v in values]


# ============================================================
# MAIN ORCHESTRATION
# ============================================================
def find_safe_route(start_lat, start_lon, end_lat, end_lon, db_conn,
                    profile='walking', weights=None, query_date=None):
    """
    Top-level entry point. Computes alternatives locally, scores each,
    returns ranked list.

    Args:
        db_conn: live MySQL connection (caller manages lifecycle)
        profile: 'walking', 'driving', or 'cycling'
        weights: dict like {'distance': 0.4, 'dust': 0.3, 'pollen': 0.3}
                 None → use DEFAULT_WEIGHTS
        query_date: 'YYYY-MM-DD' string for permit query, defaults to today

    Returns: dict with 'recommended', 'alternatives', 'metadata'
    """
    weights = weights or DEFAULT_WEIGHTS
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month

    # 1. Compute candidate routes locally on the OSM graph
    routes = fetch_routes(start_lat, start_lon, end_lat, end_lon, profile=profile)
    if not routes:
        raise RuntimeError("Local router returned no routes")

    # 2. Filter out routes that are absurdly longer than the shortest
    shortest_dist = min(r['distance'] for r in routes)
    routes = [r for r in routes if r['distance'] <= shortest_dist * MAX_DETOUR_RATIO]

    # 3. Sample each route, build a global bbox, query all permits/trees ONCE
    all_samples = []
    per_route_samples = []
    for r in routes:
        samples = sample_route_points(r['geometry']['coordinates'])
        per_route_samples.append(samples)
        all_samples.extend(samples)

    if not all_samples:
        raise RuntimeError("Could not sample route geometry")

    # Pad bbox by the larger of the two radii so edge sample points have full lookups
    bbox = bbox_around_points(all_samples, padding_m=max(DUST_SAMPLE_RADIUS_M,
                                                          POLLEN_SAMPLE_RADIUS_M))

    permits = query_permits_in_bbox(db_conn, bbox, query_date)
    trees = query_allergenic_trees_in_bbox(db_conn, bbox, current_month)

    # 4. Score each route
    raw_scores = []
    for samples in per_route_samples:
        dust = score_dust_exposure(samples, permits)
        pollen = score_pollen_exposure(samples, trees)
        raw_scores.append({'dust': dust, 'pollen': pollen})

    distances = [r['distance'] for r in routes]
    durations = [r['duration'] for r in routes]
    # Distance: tighter threshold — even 2% difference is user-perceivable
    dist_norm = normalise_scores(distances, min_relative_spread=0.02)
    # Dust/pollen: 5% threshold — micro-differences in raw exposure are noise
    dust_norm = normalise_scores([s['dust'] for s in raw_scores], min_relative_spread=0.05)
    pollen_norm = normalise_scores([s['pollen'] for s in raw_scores], min_relative_spread=0.05)

    # 5. Composite score (lower = better)
    scored_routes = []
    for i, r in enumerate(routes):
        composite = (weights['distance'] * dist_norm[i]
                     + weights['dust'] * dust_norm[i]
                     + weights['pollen'] * pollen_norm[i])
        scored_routes.append({
            'geometry': r['geometry'],
            'distance_m': round(r['distance']),
            'duration_s': round(r['duration']),
            'duration_min': round(r['duration'] / 60, 1),
            'scores': {
                'composite': round(composite, 1),
                'distance_norm': round(dist_norm[i], 1),
                'dust_norm': round(dust_norm[i], 1),
                'pollen_norm': round(pollen_norm[i], 1),
                'raw_dust': round(raw_scores[i]['dust'], 2),
                'raw_pollen': round(raw_scores[i]['pollen'], 2),
            },
            'sample_count': len(per_route_samples[i]),
        })

    # 6. Rank: best = lowest composite
    scored_routes.sort(key=lambda x: x['scores']['composite'])

    return {
        'recommended': scored_routes[0],
        'alternatives': scored_routes[1:],
        'metadata': {
            'profile': profile,
            'query_date': query_date,
            'pollen_season': POLLEN_SEASONS.get(current_month, []),
            'weights': weights,
            'permits_found': len(permits),
            'trees_found': len(trees),
            'routes_evaluated': len(scored_routes),
            'router': 'local-osm-dijkstra',
        }
    }


# ============================================================
# NATIVE HEALTH-AWARE ROUTING
# ============================================================
# Unlike find_safe_route (which post-hoc scores k pre-computed shortest paths),
# this runs a single Dijkstra where the edge cost ITSELF includes dust/pollen
# exposure. This means the algorithm can take detours of any shape — not just
# pick from k near-shortest candidates — and is the conceptual differentiator
# from commercial routing APIs that only optimise for distance/time.
#
# Edge cost model:
#     cost(u, v) = length(u, v) * (1 + alpha * dust(midpoint)
#                                    + beta  * pollen(midpoint))
#
# alpha and beta are "exposure penalties": a value of 1.0 means "1 unit of
# normalised exposure feels like doubling the edge length". They're tuneable;
# defaults below are calibrated so that on a typical 1km route the algorithm
# will accept ~10-20% extra distance to avoid the worst hotspots.

# Default exposure penalty multipliers. Tune these based on demo behaviour.
NATIVE_DUST_ALPHA = 1.0
NATIVE_POLLEN_BETA = 0.8

# Buffer (meters) around the straight-line bbox between origin and destination
# when pre-fetching permits/trees. Needs to be generous because the path can
# detour significantly to avoid exposure. 1km is enough for inner-city walks.
NATIVE_BBOX_BUFFER_M = 1000


def _build_exposure_lookup(permits, trees, dust_radius_m=DUST_SAMPLE_RADIUS_M,
                           pollen_radius_m=POLLEN_SAMPLE_RADIUS_M):
    """
    Returns a closure that, given a (lat, lon) midpoint, computes raw
    dust + pollen exposure at that point. Reuses the same physics as
    score_dust_exposure / score_pollen_exposure but for a single point.

    Pulled out so we don't allocate a tiny lambda on every edge evaluation.
    """
    def exposure_at(lat, lon):
        dust = 0.0
        for p in permits:
            d = haversine_m(lat, lon, p['lat'], p['lon'])
            if d <= dust_radius_m:
                effective_d = max(d, 10)
                dust += (p['cost'] / 1e6) / ((effective_d / 100) ** 2)

        pollen = 0.0
        for t in trees:
            d = haversine_m(lat, lon, float(t['lat']), float(t['lon']))
            if d <= pollen_radius_m:
                pollen += float(t['allergen_weight']) * float(t['pollen_factor'])

        return dust, pollen
    return exposure_at


def _normalise_exposure_for_edges(G, exposure_at, sample_n=200):
    """
    Estimate typical exposure magnitudes by sampling random edges across the
    graph, so we can rescale dust/pollen into a [0, ~1] band before applying
    alpha/beta. Without this, raw dust scores can be orders of magnitude
    different from raw pollen scores, and one will dominate.

    Returns (dust_scale, pollen_scale) — the ~95th percentile of each, which
    we'll use as the divisor.
    """
    import random
    nodes = list(G.nodes)
    if len(nodes) < 2:
        return 1.0, 1.0

    # Sample random edges; small N is fine because we only want rough magnitude
    dust_vals = []
    pollen_vals = []
    edges = list(G.edges)
    sampled = random.sample(edges, min(sample_n, len(edges)))
    for u, v, *_ in sampled:
        midlat = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
        midlon = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
        d, p = exposure_at(midlat, midlon)
        dust_vals.append(d)
        pollen_vals.append(p)

    # 95th percentile, with a floor of 1.0 to avoid divide-by-tiny when most
    # of the bbox has zero exposure (off-season pollen, no permits, etc).
    def p95(vals):
        if not vals:
            return 1.0
        s = sorted(vals)
        idx = int(len(s) * 0.95)
        return max(s[min(idx, len(s) - 1)], 1.0)

    return p95(dust_vals), p95(pollen_vals)


def find_safe_route_native(start_lat, start_lon, end_lat, end_lon, db_conn,
                            profile='walking', query_date=None,
                            alpha=NATIVE_DUST_ALPHA,
                            beta=NATIVE_POLLEN_BETA):
    """
    Single-pass health-aware shortest path. The edge weight function bakes
    dust + pollen exposure directly into Dijkstra's cost, so the resulting
    path is genuinely optimised for combined distance + exposure rather than
    being one of k near-shortest candidates re-ranked after the fact.

    Args:
        db_conn: live MySQL connection
        profile: 'walking' / 'cycling' / 'driving'
        query_date: 'YYYY-MM-DD' for permit/season lookup, defaults to today
        alpha: dust penalty multiplier. Higher → bigger detours to avoid dust.
        beta:  pollen penalty multiplier. Same idea.

    Returns: dict with same shape as find_safe_route's 'recommended' field,
             plus a 'baseline_shortest' for the pure-distance comparison and
             a 'metadata' block.
    """
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month

    G = get_graph(profile)
    speed_mps = SPEEDS_MPS[profile]

    # Snap endpoints to graph nodes
    orig = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
    if orig == dest:
        raise RuntimeError(
            "Start and end snap to the same graph node — points are too close."
        )

    # Pre-fetch all permits/trees in a generous bbox covering the OD pair.
    # We can't sample the path first (chicken-and-egg with edge weights), so
    # we just buffer the straight-line bbox.
    od_bbox = bbox_around_points(
        [(start_lat, start_lon), (end_lat, end_lon)],
        padding_m=NATIVE_BBOX_BUFFER_M,
    )
    permits = query_permits_in_bbox(db_conn, od_bbox, query_date)
    trees = query_allergenic_trees_in_bbox(db_conn, od_bbox, current_month)

    exposure_at = _build_exposure_lookup(permits, trees)
    dust_scale, pollen_scale = _normalise_exposure_for_edges(G, exposure_at)

    # The edge weight callback — invoked once per edge during Dijkstra.
    # NetworkX passes (u, v, edge_attr_dict) for MultiDiGraph; the third arg
    # is the dict-of-keyed-attrs for parallel edges. Pick min-length parallel.
    def edge_cost(u, v, edge_data):
        # edge_data: {0: {length, ...}, 1: {...}, ...}
        d_attrs = min(edge_data.values(), key=lambda d: d.get('length', float('inf')))
        length = d_attrs.get('length', 0.0)
        if length <= 0:
            return 0.0

        midlat = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
        midlon = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
        dust, pollen = exposure_at(midlat, midlon)

        # Normalised penalty in [0, ~1] band, then scaled by alpha/beta
        penalty = alpha * (dust / dust_scale) + beta * (pollen / pollen_scale)
        return length * (1 + penalty)

    # Run Dijkstra with the cost-aware weight
    try:
        safe_path = nx.shortest_path(G, orig, dest, weight=edge_cost)
    except nx.NetworkXNoPath:
        raise RuntimeError(
            f"No path between ({start_lat},{start_lon}) and ({end_lat},{end_lon})"
        )

    # Also compute the pure-distance baseline so we can show what the user
    # *would* have walked through — this is the comparison story.
    baseline_path = nx.shortest_path(G, orig, dest, weight='length')

    # Score both paths by sampling, just like find_safe_route would. This gives
    # us numbers comparable to the post-hoc method.
    safe_route_dict = _path_to_route_dict(G, safe_path, speed_mps)
    baseline_route_dict = _path_to_route_dict(G, baseline_path, speed_mps)

    safe_samples = sample_route_points(safe_route_dict['geometry']['coordinates'])
    baseline_samples = sample_route_points(baseline_route_dict['geometry']['coordinates'])

    safe_dust = score_dust_exposure(safe_samples, permits)
    safe_pollen = score_pollen_exposure(safe_samples, trees)
    base_dust = score_dust_exposure(baseline_samples, permits)
    base_pollen = score_pollen_exposure(baseline_samples, trees)

    def shape(route_dict, samples, dust, pollen):
        return {
            'geometry': route_dict['geometry'],
            'distance_m': round(route_dict['distance']),
            'duration_s': round(route_dict['duration']),
            'duration_min': round(route_dict['duration'] / 60, 1),
            'scores': {
                'raw_dust': round(dust, 2),
                'raw_pollen': round(pollen, 2),
            },
            'sample_count': len(samples),
        }

    safe_out = shape(safe_route_dict, safe_samples, safe_dust, safe_pollen)
    baseline_out = shape(baseline_route_dict, baseline_samples, base_dust, base_pollen)

    # Did the cost-aware path actually deviate?
    is_same_path = (safe_path == baseline_path)

    return {
        'recommended': safe_out,
        'baseline_shortest': baseline_out,
        'is_same_path': is_same_path,
        'metadata': {
            'profile': profile,
            'query_date': query_date,
            'pollen_season': POLLEN_SEASONS.get(current_month, []),
            'permits_found': len(permits),
            'trees_found': len(trees),
            'router': 'local-osm-dijkstra-native',
            'alpha_dust': alpha,
            'beta_pollen': beta,
            'dust_scale': round(dust_scale, 4),
            'pollen_scale': round(pollen_scale, 4),
        }
    }


# ============================================================
# POLLEN LEVEL AT A POINT (for /api/pollen-level)
# ============================================================
def get_pollen_level(lat, lon, db_conn, radius_m=300, query_date=None):
    """
    Compute pollen risk level at a single point — for the "current pollen
    levels" user story. Returns Low / Moderate / High plus a human-readable
    explanation.

    Args:
        lat, lon: query location
        db_conn: live MySQL connection
        radius_m: how far around the point to look for trees (default 300m)
        query_date: 'YYYY-MM-DD' for season lookup, defaults to today

    Returns: dict with level, score, active_genera, dominant_species,
             tree_count, explanation, advice
    """
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month
    active_genera = POLLEN_SEASONS.get(current_month, [])

    # Off-season: short-circuit
    if not active_genera:
        return {
            'level': 'Low',
            'score': 0,
            'active_genera': [],
            'dominant_species': [],
            'tree_count_in_radius': 0,
            'explanation': 'No tree species are currently in pollen season at this time of year.',
            'advice': 'Outdoor pollen exposure from trees is minimal. Routine precautions are sufficient.',
            'query_date': query_date,
            'radius_m': radius_m,
        }

    # Bounding box query for speed
    lat_pad = radius_m / 111000
    lon_pad = radius_m / (111000 * math.cos(math.radians(lat)))
    bbox = (lat - lat_pad, lat + lat_pad, lon - lon_pad, lon + lon_pad)

    placeholders = ','.join(['%s'] * len(active_genera))
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute(f"""
        SELECT lat, lon, genus, common_name, scientific_name,
               allergen_weight, pollen_factor
        FROM urban_trees
        WHERE is_allergenic = TRUE
          AND genus IN ({placeholders})
          AND lat BETWEEN %s AND %s
          AND lon BETWEEN %s AND %s
    """, (*active_genera, bbox[0], bbox[1], bbox[2], bbox[3]))
    candidate_trees = cursor.fetchall()
    cursor.close()

    # Filter by actual radius (haversine, not just bbox)
    nearby_trees = []
    total_score = 0.0
    genus_counts = {}
    for t in candidate_trees:
        d = haversine_m(lat, lon, float(t['lat']), float(t['lon']))
        if d <= radius_m:
            # Weight by 1/distance so closer trees count more, with a 10m floor
            distance_weight = max(10, d) ** -1 * 100
            contribution = (float(t['allergen_weight'])
                           * float(t['pollen_factor'])
                           * distance_weight)
            total_score += contribution
            nearby_trees.append({**t, 'distance_m': d})
            genus_counts[t['genus']] = genus_counts.get(t['genus'], 0) + 1

    # Map score to Low / Moderate / High using empirically reasonable thresholds.
    # These come from manually checking typical urban contexts:
    #   - quiet residential street (3-5 small trees within 300m): score < 50
    #   - moderate plane-lined avenue: 50-200
    #   - dense central avenue (Royal Parade-like): > 200
    if total_score < 50:
        level = 'Low'
        advice = 'Pollen exposure here is low. Routine precautions are sufficient.'
    elif total_score < 200:
        level = 'Moderate'
        advice = 'Some allergenic trees are nearby. Consider taking medication before extended outdoor activity, especially in the morning.'
    else:
        level = 'High'
        advice = 'High pollen exposure expected. Avoid lingering in the area, keep windows closed, and consider antihistamines before going out.'

    # Find dominant species (top 3 by count)
    top_genera = sorted(genus_counts.items(), key=lambda x: -x[1])[:3]
    dominant_species = [
        {'genus': g, 'count': c} for g, c in top_genera
    ]

    # Build human-readable explanation
    if not nearby_trees:
        explanation = (
            f"While {len(active_genera)} tree species are in pollen season this month, "
            f"none were found within {radius_m}m of this location."
        )
    else:
        lead_genus, lead_count = top_genera[0]
        # Pretty-print common name from the most-represented genus
        lead_common = next(
            (t['common_name'] for t in nearby_trees if t['genus'] == lead_genus),
            lead_genus.title()
        )
        explanation = (
            f"{len(nearby_trees)} allergenic trees in pollen season are within {radius_m}m. "
            f"The most common is {lead_common} ({lead_count} trees)."
        )

    return {
        'level': level,
        'score': round(total_score, 1),
        'active_genera': active_genera,
        'dominant_species': dominant_species,
        'tree_count_in_radius': len(nearby_trees),
        'explanation': explanation,
        'advice': advice,
        'query_date': query_date,
        'radius_m': radius_m,
    }


# ============================================================
# ROUTE COMPARISON (for /api/route-compare)
# ============================================================
def compare_routes(start_lat, start_lon, end_lat, end_lon, db_conn,
                   profile='walking', query_date=None):
    """
    Side-by-side comparison of "safest route" vs "shortest route".
    Used by the route-comparison user story — lets users see the trade-off
    explicitly rather than blindly trusting the algorithm.

    Returns a dict with 'recommended', 'shortest', and 'comparison' fields.
    The 'comparison' summarises the trade-off in plain numbers + percentages.
    """
    # Reuse find_safe_route to do the heavy lifting
    result = find_safe_route(start_lat, start_lon, end_lat, end_lon,
                             db_conn=db_conn, profile=profile,
                             query_date=query_date)

    # Identify the shortest route — it's whichever route has the smallest distance.
    # Compare by Python object identity, NOT by distance_m, because two distinct
    # routes can coincidentally share a distance value.
    all_routes = [result['recommended']] + result['alternatives']
    shortest = min(all_routes, key=lambda r: r['distance_m'])
    recommended = result['recommended']

    # If recommended and shortest are literally the same dict, no trade-off
    is_same_route = (shortest is recommended)

    if is_same_route:
        comparison = {
            'is_same_route': True,
            'message': 'The recommended route is also the shortest route — no trade-off needed.',
        }
    else:
        d_extra_m = recommended['distance_m'] - shortest['distance_m']
        d_extra_min = round(recommended['duration_min'] - shortest['duration_min'], 1)
        d_pct = round(100 * d_extra_m / shortest['distance_m'], 1)

        # Pollen difference
        rec_pollen = recommended['scores']['raw_pollen']
        short_pollen = shortest['scores']['raw_pollen']
        if short_pollen > 0:
            pollen_pct_reduction = round(100 * (short_pollen - rec_pollen) / short_pollen, 1)
        else:
            pollen_pct_reduction = 0

        # Dust difference
        rec_dust = recommended['scores']['raw_dust']
        short_dust = shortest['scores']['raw_dust']
        if short_dust > 0:
            dust_pct_reduction = round(100 * (short_dust - rec_dust) / short_dust, 1)
        else:
            dust_pct_reduction = 0

        comparison = {
            'is_same_route': False,
            'extra_distance_m': d_extra_m,
            'extra_duration_min': d_extra_min,
            'extra_distance_pct': d_pct,
            'pollen_reduction_pct': pollen_pct_reduction,
            'dust_reduction_pct': dust_pct_reduction,
            'message': _build_tradeoff_message(d_extra_m, d_extra_min,
                                                pollen_pct_reduction,
                                                dust_pct_reduction),
        }

    return {
        'recommended': recommended,
        'shortest': shortest,
        'comparison': comparison,
        'metadata': result['metadata'],
    }


def _build_tradeoff_message(extra_m, extra_min, pollen_pct, dust_pct):
    """Generate a one-sentence summary of the trade-off."""
    parts = []
    if pollen_pct > 5:
        parts.append(f"{pollen_pct}% less pollen")
    if dust_pct > 5:
        parts.append(f"{dust_pct}% less dust")
    if not parts:
        return f"Recommended adds {extra_min} min ({extra_m}m) without significant exposure reduction."
    benefits = " and ".join(parts)

    # Distance & time framing — handle the case where the longer route
    # is paradoxically faster (OSM ETA reflects road type / signals)
    if extra_min > 0.5:
        time_phrase = f"takes {extra_min} min longer"
    elif extra_min < -0.5:
        time_phrase = f"is actually {abs(extra_min)} min faster"
    else:
        time_phrase = "takes about the same time"

    if extra_m > 50:
        return f"Recommended {time_phrase} ({extra_m}m extra distance) for {benefits}."
    elif extra_m < -50:
        return f"Recommended {time_phrase} ({abs(extra_m)}m shorter) for {benefits}."
    else:
        return f"Recommended {time_phrase} for {benefits}."