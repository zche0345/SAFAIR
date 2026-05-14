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

Tiebreaks and explainability:
    When routes tie on composite score, we use explainable tiebreakers
    (shorter distance, faster, less raw exposure) — never opaque hashing.
    Each returned route carries a 'reason' field describing why it was
    ranked where it was. If multiple routes tie on every measurable
    dimension, they go into 'co_recommended' as equally-good options
    rather than being arbitrarily ordered.
"""

import math
from datetime import datetime

import networkx as nx
import osmnx as ox

# ============================================================
# CONFIG
# ============================================================

# Pre-built OSM graph. Run scripts/build_graph.py once to generate.
GRAPH_PATHS = {
    'walking': 'data/melbourne_walk.graphml',
    'cycling': 'data/melbourne_walk.graphml',
    'driving': 'data/melbourne_walk.graphml',
}

SPEEDS_MPS = {
    'walking': 1.4,
    'cycling': 4.2,
    'driving': 11.0,
}

ROUTE_SAMPLE_INTERVAL_M = 50
DUST_SAMPLE_RADIUS_M = 200
POLLEN_SAMPLE_RADIUS_M = 30

DEFAULT_WEIGHTS = {
    'distance': 0.40,
    'dust':     0.30,
    'pollen':   0.30,
}

MAX_DETOUR_RATIO = 1.5
DEFAULT_ALTERNATIVES = 3
ROUTE_SIMILARITY_THRESHOLD = 0.85

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
    R = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def sample_route_points(geojson_coordinates, interval_m=ROUTE_SAMPLE_INTERVAL_M):
    if not geojson_coordinates or len(geojson_coordinates) < 2:
        return []
    samples = []
    accumulated = 0.0
    pts = [(c[1], c[0]) for c in geojson_coordinates]
    samples.append(pts[0])
    for i in range(1, len(pts)):
        seg_len = haversine_m(pts[i-1][0], pts[i-1][1], pts[i][0], pts[i][1])
        if seg_len <= 0:
            continue
        next_threshold = interval_m - accumulated
        while next_threshold <= seg_len:
            t = next_threshold / seg_len
            lat = pts[i-1][0] + (pts[i][0] - pts[i-1][0]) * t
            lon = pts[i-1][1] + (pts[i][1] - pts[i-1][1]) * t
            samples.append((lat, lon))
            next_threshold += interval_m
        accumulated = (accumulated + seg_len) % interval_m
    if samples[-1] != pts[-1]:
        samples.append(pts[-1])
    return samples


def bbox_around_points(points, padding_m):
    if not points:
        return None
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    lat_pad = padding_m / 111000
    lon_pad = padding_m / (111000 * math.cos(math.radians(sum(lats) / len(lats))))
    return (min(lats) - lat_pad, max(lats) + lat_pad,
            min(lons) - lon_pad, max(lons) + lon_pad)


# ============================================================
# LOCAL ROUTE PLANNING
# ============================================================
_SIMPLE_GRAPH_CACHE = {}

def _to_simple_digraph(G):
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
    coords = []
    total_length = 0.0
    for i, node in enumerate(node_path):
        coords.append([G.nodes[node]['x'], G.nodes[node]['y']])
        if i > 0:
            edge_data = G.get_edge_data(node_path[i-1], node)
            length = min(d.get('length', 0.0) for d in edge_data.values())
            total_length += length
    return {
        'geometry': {'type': 'LineString', 'coordinates': coords},
        'distance': total_length,
        'duration': total_length / speed_mps,
        '_node_path': node_path,
    }


def _routes_are_distinct(path_a, path_b, threshold=ROUTE_SIMILARITY_THRESHOLD):
    a = set(path_a)
    b = set(path_b)
    if not a or not b:
        return True
    overlap = len(a & b) / max(len(a), len(b))
    return overlap < threshold


def _penalised_alternatives(G, primary_path, dest_orig, num_alternatives,
                            penalty_factor=3.0):
    orig, dest = dest_orig
    alternatives = []
    penalised_pairs = set()
    for i in range(len(primary_path) - 1):
        penalised_pairs.add((primary_path[i], primary_path[i + 1]))

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
        if any(path == p for p in accepted_paths):
            for i in range(len(path) - 1):
                penalised_pairs.add((path[i], path[i + 1]))
            continue
        if all(_routes_are_distinct(path, p) for p in accepted_paths):
            alternatives.append(path)
            accepted_paths.append(path)
        for i in range(len(path) - 1):
            penalised_pairs.add((path[i], path[i + 1]))
    return alternatives


def fetch_routes(start_lat, start_lon, end_lat, end_lon,
                 profile='walking', alternatives=DEFAULT_ALTERNATIVES,
                 timeout=None):
    G = get_graph(profile)
    speed_mps = SPEEDS_MPS[profile]
    orig = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
    if orig == dest:
        raise RuntimeError(
            "Start and end snap to the same graph node — points are too close "
            "together or both fell on the same intersection."
        )
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
    min_lat, max_lat, min_lon, max_lon = bbox
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
    active_genera = POLLEN_SEASONS.get(current_month, [])
    if not active_genera:
        return []
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
        print(f"  urban_trees query failed: {e}")
        return []
    finally:
        cursor.close()


def score_dust_exposure(samples, permits):
    if not permits:
        return 0.0
    total = 0.0
    for slat, slon in samples:
        for p in permits:
            d = haversine_m(slat, slon, p['lat'], p['lon'])
            if d <= DUST_SAMPLE_RADIUS_M:
                effective_d = max(d, 10)
                total += (p['cost'] / 1e6) / ((effective_d / 100) ** 2)
    return total


def score_pollen_exposure(samples, trees):
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
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return [0.0] * len(values)
    if hi > 0 and (hi - lo) / hi < min_relative_spread:
        return [0.0] * len(values)
    return [100.0 * (v - lo) / (hi - lo) for v in values]


# ============================================================
# TIEBREAK + REASON HELPERS
# ============================================================
# When two routes tie on composite score, we need to either pick one for a
# reason the user can understand, or tell them the routes are equivalent.
# These helpers attach a human-readable 'reason' string to each route.

def _rank_key(r):
    """
    Sort key used to rank scored routes. Every dimension here is something
    the user can be shown as a tiebreak rationale — NO opaque hashing.
    If two routes match on all of these, they're genuinely equivalent
    and end up in co_recommended.
    """
    return (
        r['scores']['composite'],
        r['distance_m'],
        r['duration_s'],
        r['scores']['raw_dust'],
        r['scores']['raw_pollen'],
    )


def _diff_reason(route_a, route_b, is_winner):
    """
    Build a one-sentence comparison of route_a to route_b.
    is_winner=True means route_a beat route_b (used for the top route).
    is_winner=False means route_a is being compared TO winner route_b.
    """
    a_score = route_a['scores']
    b_score = route_b['scores']
    composite_diff = a_score['composite'] - b_score['composite']

    # Case 1: composite scores meaningfully different (>= 0.5)
    if abs(composite_diff) >= 0.5:
        dim_diffs = {
            'distance': abs(a_score['distance_norm'] - b_score['distance_norm']),
            'dust':     abs(a_score['dust_norm']     - b_score['dust_norm']),
            'pollen':   abs(a_score['pollen_norm']   - b_score['pollen_norm']),
        }
        dominant = max(dim_diffs, key=dim_diffs.get)
        if is_winner:
            return f'Best overall balance — particularly strong on {dominant}.'
        this_better = []
        this_worse = []
        for k, label in [('distance_norm', 'shorter distance'),
                         ('dust_norm',     'less dust exposure'),
                         ('pollen_norm',   'less pollen exposure')]:
            if a_score[k] < b_score[k] - 5:
                this_better.append(label)
            elif a_score[k] > b_score[k] + 5:
                this_worse.append(label)
        if this_better and this_worse:
            return (f'Trade-off: {" and ".join(this_better)}, '
                    f'but {" and ".join(this_worse)}.')
        if this_better:
            return f'Better on {" and ".join(this_better)} but worse overall balance.'
        return 'Worse on the overall balance.'

    # Case 2: composite scores essentially tied — explain the tiebreak
    reasons = []
    if abs(route_a['distance_m'] - route_b['distance_m']) >= 20:
        if route_a['distance_m'] < route_b['distance_m']:
            reasons.append(f'{route_b["distance_m"] - route_a["distance_m"]}m shorter')
        else:
            reasons.append(f'{route_a["distance_m"] - route_b["distance_m"]}m longer')
    if abs(route_a['duration_s'] - route_b['duration_s']) >= 30:
        diff_min = round((route_b['duration_s'] - route_a['duration_s']) / 60, 1)
        if diff_min > 0:
            reasons.append(f'{diff_min} min faster')
        else:
            reasons.append(f'{abs(diff_min)} min slower')
    if abs(a_score['raw_dust'] - b_score['raw_dust']) >= 0.1:
        if a_score['raw_dust'] < b_score['raw_dust']:
            reasons.append('slightly less dust')
        else:
            reasons.append('slightly more dust')
    if abs(a_score['raw_pollen'] - b_score['raw_pollen']) >= 0.1:
        if a_score['raw_pollen'] < b_score['raw_pollen']:
            reasons.append('slightly less pollen')
        else:
            reasons.append('slightly more pollen')

    if not reasons:
        if is_winner:
            return 'Tied with other routes — both are equally good choices.'
        return 'Equally good as the recommended route.'

    if is_winner:
        return 'Tied on overall score, picked because it is ' + ' and '.join(reasons) + '.'
    return 'Tied on overall score; this one is ' + ' and '.join(reasons) + '.'


def _attach_ranking_reasons(scored_routes):
    """
    Mutate scored_routes in place, adding a 'reason' field to each route.
    Top route's reason explains how it differs from #2;
    each alternative's reason explains how it differs from #1.
    """
    if not scored_routes:
        return
    top = scored_routes[0]
    if len(scored_routes) == 1:
        top['reason'] = 'Only route found.'
        return
    second = scored_routes[1]
    top['reason'] = _diff_reason(top, second, is_winner=True)
    for r in scored_routes[1:]:
        r['reason'] = _diff_reason(r, top, is_winner=False)


# ============================================================
# MAIN ORCHESTRATION
# ============================================================
def find_safe_route(start_lat, start_lon, end_lat, end_lon, db_conn,
                    profile='walking', weights=None, query_date=None):
    weights = weights or DEFAULT_WEIGHTS
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month

    # 1. Compute candidate routes locally
    routes = fetch_routes(start_lat, start_lon, end_lat, end_lon, profile=profile)
    if not routes:
        raise RuntimeError("Local router returned no routes")

    # 2. Filter out absurd detours
    shortest_dist = min(r['distance'] for r in routes)
    routes = [r for r in routes if r['distance'] <= shortest_dist * MAX_DETOUR_RATIO]

    # 3. Sample + global bbox + one-shot DB query
    all_samples = []
    per_route_samples = []
    for r in routes:
        samples = sample_route_points(r['geometry']['coordinates'])
        per_route_samples.append(samples)
        all_samples.extend(samples)
    if not all_samples:
        raise RuntimeError("Could not sample route geometry")
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
    dist_norm = normalise_scores(distances, min_relative_spread=0.02)
    dust_norm = normalise_scores([s['dust'] for s in raw_scores], min_relative_spread=0.05)
    pollen_norm = normalise_scores([s['pollen'] for s in raw_scores], min_relative_spread=0.05)

    # 5. Composite + scored route dicts
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

    # 6. Rank using explainable tiebreakers
    scored_routes.sort(key=_rank_key)

    # 6b. Attach 'reason' field to every route
    _attach_ranking_reasons(scored_routes)

    # 6c. Detect co-recommended (genuinely tied) routes
    top = scored_routes[0]
    tied_with_top = [r for r in scored_routes[1:] if _rank_key(r) == _rank_key(top)]
    remaining_alternatives = [r for r in scored_routes[1:] if r not in tied_with_top]

    return {
        'recommended': top,
        'co_recommended': tied_with_top,
        'alternatives': remaining_alternatives,
        'metadata': {
            'profile': profile,
            'query_date': query_date,
            'pollen_season': POLLEN_SEASONS.get(current_month, []),
            'weights': weights,
            'permits_found': len(permits),
            'trees_found': len(trees),
            'routes_evaluated': len(scored_routes),
            'router': 'local-osm-dijkstra',
            'has_co_recommended': len(tied_with_top) > 0,
        }
    }


# ============================================================
# NATIVE HEALTH-AWARE ROUTING
# ============================================================
NATIVE_DUST_ALPHA = 1.0
NATIVE_POLLEN_BETA = 0.8
NATIVE_BBOX_BUFFER_M = 1000


def _build_exposure_lookup(permits, trees, dust_radius_m=DUST_SAMPLE_RADIUS_M,
                           pollen_radius_m=POLLEN_SAMPLE_RADIUS_M):
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
    import random
    nodes = list(G.nodes)
    if len(nodes) < 2:
        return 1.0, 1.0
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
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month
    G = get_graph(profile)
    speed_mps = SPEEDS_MPS[profile]
    orig = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)
    if orig == dest:
        raise RuntimeError("Start and end snap to the same graph node — points are too close.")

    od_bbox = bbox_around_points(
        [(start_lat, start_lon), (end_lat, end_lon)],
        padding_m=NATIVE_BBOX_BUFFER_M,
    )
    permits = query_permits_in_bbox(db_conn, od_bbox, query_date)
    trees = query_allergenic_trees_in_bbox(db_conn, od_bbox, current_month)
    exposure_at = _build_exposure_lookup(permits, trees)
    dust_scale, pollen_scale = _normalise_exposure_for_edges(G, exposure_at)

    def edge_cost(u, v, edge_data):
        d_attrs = min(edge_data.values(), key=lambda d: d.get('length', float('inf')))
        length = d_attrs.get('length', 0.0)
        if length <= 0:
            return 0.0
        midlat = (G.nodes[u]['y'] + G.nodes[v]['y']) / 2
        midlon = (G.nodes[u]['x'] + G.nodes[v]['x']) / 2
        dust, pollen = exposure_at(midlat, midlon)
        penalty = alpha * (dust / dust_scale) + beta * (pollen / pollen_scale)
        return length * (1 + penalty)

    try:
        safe_path = nx.shortest_path(G, orig, dest, weight=edge_cost)
    except nx.NetworkXNoPath:
        raise RuntimeError(
            f"No path between ({start_lat},{start_lon}) and ({end_lat},{end_lon})"
        )
    baseline_path = nx.shortest_path(G, orig, dest, weight='length')

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
# POLLEN LEVEL AT A POINT
# ============================================================
def get_pollen_level(lat, lon, db_conn, radius_m=300, query_date=None):
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    current_month = datetime.strptime(query_date, '%Y-%m-%d').month
    active_genera = POLLEN_SEASONS.get(current_month, [])

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

    nearby_trees = []
    total_score = 0.0
    genus_counts = {}
    for t in candidate_trees:
        d = haversine_m(lat, lon, float(t['lat']), float(t['lon']))
        if d <= radius_m:
            distance_weight = max(10, d) ** -1 * 100
            contribution = (float(t['allergen_weight'])
                           * float(t['pollen_factor'])
                           * distance_weight)
            total_score += contribution
            nearby_trees.append({**t, 'distance_m': d})
            genus_counts[t['genus']] = genus_counts.get(t['genus'], 0) + 1

    if total_score < 50:
        level = 'Low'
        advice = 'Pollen exposure here is low. Routine precautions are sufficient.'
    elif total_score < 200:
        level = 'Moderate'
        advice = 'Some allergenic trees are nearby. Consider taking medication before extended outdoor activity, especially in the morning.'
    else:
        level = 'High'
        advice = 'High pollen exposure expected. Avoid lingering in the area, keep windows closed, and consider antihistamines before going out.'

    top_genera = sorted(genus_counts.items(), key=lambda x: -x[1])[:3]
    dominant_species = [{'genus': g, 'count': c} for g, c in top_genera]

    if not nearby_trees:
        explanation = (
            f"While {len(active_genera)} tree species are in pollen season this month, "
            f"none were found within {radius_m}m of this location."
        )
    else:
        lead_genus, lead_count = top_genera[0]
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
# ROUTE COMPARISON
# ============================================================
def compare_routes(start_lat, start_lon, end_lat, end_lon, db_conn,
                   profile='walking', query_date=None):
    result = find_safe_route(start_lat, start_lon, end_lat, end_lon,
                             db_conn=db_conn, profile=profile,
                             query_date=query_date)

    # Pick the shortest route. On tied distance_m, prefer faster, then less
    # combined exposure. Every tiebreak here is something the user could
    # understand if asked "why this one?" — never opaque hashing.
    # Includes co_recommended routes since they're genuinely candidates too.
    all_routes = ([result['recommended']]
                  + result.get('co_recommended', [])
                  + result['alternatives'])
    shortest = min(all_routes, key=lambda r: (
        r['distance_m'],
        r['duration_s'],
        r['scores']['raw_dust'] + r['scores']['raw_pollen'],
    ))
    recommended = result['recommended']
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
        rec_pollen = recommended['scores']['raw_pollen']
        short_pollen = shortest['scores']['raw_pollen']
        if short_pollen > 0:
            pollen_pct_reduction = round(100 * (short_pollen - rec_pollen) / short_pollen, 1)
        else:
            pollen_pct_reduction = 0
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
    parts = []
    if pollen_pct > 5:
        parts.append(f"{pollen_pct}% less pollen")
    if dust_pct > 5:
        parts.append(f"{dust_pct}% less dust")
    if not parts:
        return f"Recommended adds {extra_min} min ({extra_m}m) without significant exposure reduction."
    benefits = " and ".join(parts)
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