"""
AsthmaSafe Melbourne — Dust Risk Prediction API
=================================================
Loads the trained XGBoost model and serves predictions via REST API.

Usage:
  1. pip install flask xgboost pandas numpy flask-cors
  2. Make sure xgboost_dust_risk_model.json is in the same folder
  3. Run:  python api.py
  4. API will be available at http://localhost:5000

Endpoints:
  GET  /api/dust-risk?active_permits=50&active_permits_cost=5000000&wind_speed=3.5&temperature=25
  POST /api/dust-risk  (JSON body)
  GET  /api/health     (health check)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import xgboost as xgb
import numpy as np
import pandas as pd
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

# ============================================================
# LOAD MODEL
# ============================================================
MODEL_PATH = "model_outputs/xgboost_dust_risk_model.json"

print("Loading XGBoost model...")
model = xgb.XGBRegressor()
model.load_model(MODEL_PATH)
print("Model loaded successfully!")

# ============================================================
# CoM OPEN DATA API CONFIG
# ============================================================
COM_API_BASE = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/building-permits/records"

# City of Melbourne suburbs
valid_suburbs = [
    'Carlton', 'Docklands', 'East Melbourne', 'Kensington',
    'Melbourne', 'North Melbourne', 'Parkville',
    'South Yarra', 'Southbank', 'West Melbourne',
]

def get_active_permits_from_com(suburb, query_date=None):
    """Query CoM Open Data API for active building permits in a suburb"""
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # CoM API uses OData-style filtering
        # Active permit: issue_date <= today AND completed_by_date >= today
        # Address contains suburb name in uppercase
        suburb_upper = suburb.upper()
        where_clause = (
            f'permit_certificate_type = "Building Permit"'
            f' AND issue_date <= "{query_date}"'
            f' AND completed_by_date >= "{query_date}"'
            f' AND address LIKE "%{suburb_upper}%"'
        )
        
        # First request: get count
        params = {
            'where': where_clause,
            'limit': 0,
        }
        resp = requests.get(COM_API_BASE, params=params, timeout=10)
        data = resp.json()
        total_count = data.get('total_count', 0)
        
        # Second request: get sum of estimated costs (use aggregation)
        agg_url = COM_API_BASE.replace('/records', '/aggregates')
        agg_params = {
            'where': where_clause,
            'select': 'count(*) as cnt, sum(estimated_cost_of_works) as total_cost',
        }
        agg_resp = requests.get(agg_url, params=agg_params, timeout=10)
        agg_data = agg_resp.json()
        
        if 'aggregations' in agg_data:
            total_cost = float(agg_data['aggregations'].get('total_cost') or 0)
            count = int(agg_data['aggregations'].get('cnt') or 0)
        elif 'results' in agg_data and len(agg_data['results']) > 0:
            total_cost = float(agg_data['results'][0].get('total_cost') or 0)
            count = int(agg_data['results'][0].get('cnt') or 0)
        else:
            total_cost = 0
            count = total_count
        
        return {
            'active_permits': count,
            'total_estimated_cost': total_cost,
            'average_estimated_cost': total_cost / count if count > 0 else 0,
        }
    
    except Exception as e:
        print(f"  CoM API error: {e}")
        # Fallback: return 0
        return {
            'active_permits': 0,
            'total_estimated_cost': 0,
            'average_estimated_cost': 0,
        }

print(f"CoM API configured. {len(valid_suburbs)} suburbs available.")

# ============================================================
# GEOCODING & STREET-LEVEL FUNCTIONS
# ============================================================
import math

def geocode_address(address):
    """Convert address to lat/lon using Open-Meteo Geocoding API (free, no key)"""
    try:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {'name': address, 'count': 1, 'language': 'en', 'format': 'json'}
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if 'results' in data and len(data['results']) > 0:
            r = data['results'][0]
            return {'lat': r['latitude'], 'lon': r['longitude']}
    except:
        pass
    return None

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters"""
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def get_nearby_permits(lat, lon, radius_m=500, query_date=None):
    """
    Get active building permits near a specific location.
    Fetches all active permits in the suburb, geocodes their addresses,
    and filters by distance. Returns permits within radius_m meters.
    """
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Find which suburb this coordinate is in (closest match)
        min_dist = float('inf')
        closest_suburb = 'Melbourne'
        for name, coords in SUBURB_COORDS.items():
            d = haversine_distance(lat, lon, coords['lat'], coords['lon'])
            if d < min_dist:
                min_dist = d
                closest_suburb = name
        
        # Fetch active permits for that suburb from CoM API
        suburb_upper = closest_suburb.upper()
        where_clause = (
            f'permit_certificate_type = "Building Permit"'
            f' AND issue_date <= "{query_date}"'
            f' AND completed_by_date >= "{query_date}"'
            f' AND address LIKE "%{suburb_upper}%"'
        )
        params = {
            'where': where_clause,
            'select': 'address, estimated_cost_of_works, desc_of_works, issue_date, completed_by_date',
            'limit': 100,
        }
        resp = requests.get(COM_API_BASE, params=params, timeout=15)
        data = resp.json()
        records = data.get('results', [])
        
        # Geocode each permit address and calculate distance
        nearby = []
        total_cost = 0
        
        # Simple street-level matching: extract street name from addresses
        # and estimate coordinates based on known suburb center + offset
        for record in records:
            addr = record.get('address', '')
            cost = float(record.get('estimated_cost_of_works') or 0)
            
            # Try to geocode the address
            permit_coords = geocode_address(addr + ", Melbourne, Australia")
            
            if permit_coords:
                dist = haversine_distance(lat, lon, permit_coords['lat'], permit_coords['lon'])
            else:
                # If geocoding fails, assume it's at suburb center
                sub_coords = SUBURB_COORDS.get(closest_suburb, DEFAULT_COORDS)
                dist = haversine_distance(lat, lon, sub_coords['lat'], sub_coords['lon'])
            
            if dist <= radius_m:
                nearby.append({
                    'address': addr,
                    'distance_m': round(dist),
                    'estimated_cost': cost,
                    'description': record.get('desc_of_works', ''),
                    'completed_by': record.get('completed_by_date', ''),
                })
                total_cost += cost
        
        # Sort by distance (closest first)
        nearby.sort(key=lambda x: x['distance_m'])
        
        # Calculate distance-weighted dust factor
        # Closer sites contribute more to dust exposure
        dust_weight = 0
        for p in nearby:
            if p['distance_m'] > 0:
                # Inverse distance weighting: 1/distance, capped
                weight = min(1.0, radius_m / p['distance_m']) * (p['estimated_cost'] / 1e6)
                dust_weight += weight
            else:
                dust_weight += (p['estimated_cost'] / 1e6)
        
        return {
            'suburb': closest_suburb,
            'nearby_permits': nearby,
            'active_permits': len(nearby),
            'total_estimated_cost': total_cost,
            'dust_proximity_weight': round(dust_weight, 2),
            'radius_m': radius_m,
        }
    
    except Exception as e:
        print(f"  Nearby permits error: {e}")
        return {
            'suburb': 'Unknown',
            'nearby_permits': [],
            'active_permits': 0,
            'total_estimated_cost': 0,
            'dust_proximity_weight': 0,
            'radius_m': radius_m,
        }

# Feature names must match training order exactly
FEATURE_NAMES = [
    'active_permits',
    'active_permits_cost',
    'is_construction_time',
    'wind_speed',
    'temperature',
    'hour',
    'is_workday',
    'season',
]

# ============================================================
# SUBURB COORDINATES (City of Melbourne neighbourhoods)
# ============================================================
SUBURB_COORDS = {
    'Melbourne':       {'lat': -37.8136, 'lon': 144.9631},
    'Southbank':       {'lat': -37.8230, 'lon': 144.9650},
    'Docklands':       {'lat': -37.8145, 'lon': 144.9460},
    'Carlton':         {'lat': -37.8000, 'lon': 144.9670},
    'North Melbourne': {'lat': -37.7990, 'lon': 144.9430},
    'West Melbourne':  {'lat': -37.8080, 'lon': 144.9380},
    'East Melbourne':  {'lat': -37.8160, 'lon': 144.9870},
    'Parkville':       {'lat': -37.7860, 'lon': 144.9550},
    'Kensington':      {'lat': -37.7940, 'lon': 144.9260},
    'South Yarra':     {'lat': -37.8380, 'lon': 144.9930},
}
# Default to Melbourne CBD if suburb not found
DEFAULT_COORDS = {'lat': -37.8136, 'lon': 144.9631}

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_weather(lat, lon):
    """Fetch current wind_speed and temperature from Open-Meteo API"""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,wind_speed_10m"
        )
        resp = requests.get(url, timeout=5)
        data = resp.json()
        # Open-Meteo returns wind_speed in km/h, model trained on m/s
        wind_kmh = data['current']['wind_speed_10m']
        wind_ms = wind_kmh / 3.6  # convert km/h to m/s
        return {
            'wind_speed': round(wind_ms, 2),
            'temperature': data['current']['temperature_2m'],
        }
    except Exception as e:
        print(f"  Weather API error: {e}")
        return {'wind_speed': 3.0, 'temperature': 15.0}

def get_hourly_forecast(lat, lon, hours=6):
    """Fetch hourly AQI + weather forecast from Open-Meteo for next N hours"""
    try:
        # Weather forecast
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,wind_speed_10m"
            f"&forecast_hours={hours}"
            f"&timezone=Australia%2FMelbourne"
        )
        weather_resp = requests.get(weather_url, timeout=5)
        weather_data = weather_resp.json()

        # AQI forecast
        aqi_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=us_aqi,pm10,pm2_5"
            f"&forecast_hours={hours}"
            f"&timezone=Australia%2FMelbourne"
        )
        aqi_resp = requests.get(aqi_url, timeout=5)
        aqi_data = aqi_resp.json()

        hourly = []
        times = weather_data.get('hourly', {}).get('time', [])
        temps = weather_data.get('hourly', {}).get('temperature_2m', [])
        winds = weather_data.get('hourly', {}).get('wind_speed_10m', [])
        aqis = aqi_data.get('hourly', {}).get('us_aqi', [])
        pm10s = aqi_data.get('hourly', {}).get('pm10', [])
        pm25s = aqi_data.get('hourly', {}).get('pm2_5', [])

        for i in range(min(len(times), hours)):
            hourly.append({
                'time': times[i] if i < len(times) else None,
                'temperature': temps[i] if i < len(temps) else None,
                'wind_speed_kmh': winds[i] if i < len(winds) else None,
                'wind_speed_ms': round(winds[i] / 3.6, 2) if i < len(winds) and winds[i] else None,
                'aqi': aqis[i] if i < len(aqis) else None,
                'pm10': pm10s[i] if i < len(pm10s) else None,
                'pm25': pm25s[i] if i < len(pm25s) else None,
            })
        return hourly
    except Exception as e:
        print(f"  Forecast API error: {e}")
        return []

def get_aqi_risk_level(aqi):
    """Convert AQI value to risk level"""
    if aqi is None: return "Unknown"
    if aqi <= 50: return "Low"
    elif aqi <= 100: return "Moderate"
    elif aqi <= 150: return "High"
    else: return "Very High"

def get_combined_risk(dust_score, aqi):
    """Combine Dust Score and AQI into overall risk"""
    if aqi is None:
        return dust_score
    # Take the worse of the two
    aqi_normalized = min(100, int(aqi / 3))  # AQI 0-300 → 0-100 scale
    return max(dust_score, aqi_normalized)

def get_season(month):
    """Southern Hemisphere seasons"""
    if month in [12, 1, 2]: return 0   # Summer
    elif month in [3, 4, 5]: return 1   # Autumn
    elif month in [6, 7, 8]: return 2   # Winter
    else: return 3                       # Spring

def pm10_to_risk_score(pm10):
    """Convert predicted PM10 to a 0-100 risk score"""
    # Based on WHO and Australian NEPM guidelines
    # WHO 24h guideline: 15 ug/m3, NEPM standard: 45 ug/m3
    if pm10 <= 0: return 0
    elif pm10 <= 15: return int(pm10 / 15 * 25)          # 0-25: Low
    elif pm10 <= 30: return int(25 + (pm10 - 15) / 15 * 25)  # 25-50: Moderate
    elif pm10 <= 45: return int(50 + (pm10 - 30) / 15 * 25)  # 50-75: High
    else: return min(100, int(75 + (pm10 - 45) / 30 * 25))   # 75-100: Very High

def get_risk_level(score):
    """Convert score to risk level label"""
    if score <= 25: return "Low"
    elif score <= 50: return "Moderate"
    elif score <= 75: return "High"
    else: return "Very High"

def get_recommendation(risk_level):
    """Return parent-friendly recommendation based on risk level"""
    recommendations = {
        "Low": "Air quality is good. Your child can enjoy outdoor activities as normal.",
        "Moderate": "Some dust or pollution present. If your child has severe asthma, consider a mask for prolonged outdoor activity.",
        "High": "Elevated risk due to dust or poor air quality. Limit your child's outdoor exercise time. Keep reliever medication accessible.",
        "Very High": "Very high risk. Keep your child indoors if possible. Close windows. Ensure asthma action plan is ready.",
    }
    return recommendations.get(risk_level, "")

def get_precautions(overall_level, dust_level, aqi_level, dust_score, aqi, active_permits):
    """Return detailed precautions based on risk sources"""
    precautions = []

    # General precautions by overall risk level
    if overall_level in ["High", "Very High"]:
        precautions.append({
            "icon": "medication",
            "title": "Carry reliever medication",
            "detail": "Ensure your child has their blue/grey reliever puffer (e.g. Ventolin) with them at all times.",
        })
        precautions.append({
            "icon": "plan",
            "title": "Review asthma action plan",
            "detail": "Check your child's asthma action plan and make sure they know what to do if symptoms worsen.",
        })

    if overall_level == "Very High":
        precautions.append({
            "icon": "indoor",
            "title": "Stay indoors",
            "detail": "Keep your child indoors with windows and doors closed. Use air conditioning on recirculate mode if available.",
        })
        precautions.append({
            "icon": "emergency",
            "title": "Know emergency contacts",
            "detail": "Have emergency numbers ready. Call 000 if your child has severe breathing difficulty that does not improve with reliever medication.",
        })

    # Dust-specific precautions
    if dust_level in ["High", "Very High"]:
        precautions.append({
            "icon": "mask",
            "title": "Wear a P2/N95 mask outdoors",
            "detail": f"There are {active_permits} active construction sites nearby generating dust. A P2/N95 mask filters out coarse dust particles.",
        })
        precautions.append({
            "icon": "route",
            "title": "Avoid construction zones",
            "detail": "Plan routes that avoid active construction sites. Use side streets away from major building works.",
        })
        precautions.append({
            "icon": "windows",
            "title": "Close windows near construction",
            "detail": "If your home or school is near a construction site, keep windows closed during work hours (7am–5pm on weekdays).",
        })

    if dust_level == "Moderate":
        precautions.append({
            "icon": "mask",
            "title": "Consider a mask for sensitive children",
            "detail": "If your child's asthma is moderate to severe, a mask can help when walking past construction areas.",
        })

    # AQI-specific precautions
    if aqi_level in ["High", "Very High"]:
        precautions.append({
            "icon": "exercise",
            "title": "Reduce outdoor exercise intensity",
            "detail": "Avoid vigorous outdoor exercise like running or cycling. Light walking is usually okay.",
        })
        precautions.append({
            "icon": "timing",
            "title": "Exercise early morning or evening",
            "detail": "Air pollution is usually lower before 7am and after 7pm. Plan outdoor activities for these times.",
        })

    if aqi_level == "Moderate":
        precautions.append({
            "icon": "monitor",
            "title": "Monitor your child's symptoms",
            "detail": "Watch for coughing, wheezing, or shortness of breath. Come indoors if symptoms appear.",
        })

    # Low risk — still give positive guidance
    if overall_level == "Low":
        precautions.append({
            "icon": "outdoor",
            "title": "Great day for outdoor activities",
            "detail": "Air quality and dust levels are both low. Your child can enjoy outdoor exercise, sports, and play safely.",
        })
        precautions.append({
            "icon": "hydrate",
            "title": "Stay hydrated",
            "detail": "Even on good air quality days, make sure your child drinks plenty of water during outdoor activities.",
        })

    return precautions

# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "model": "XGBoost Dust Risk Prediction",
        "features": FEATURE_NAMES,
        "suburbs": valid_suburbs,
    })

@app.route('/api/suburbs', methods=['GET'])
def get_suburbs():
    """Return list of available suburbs"""
    return jsonify({
        "success": True,
        "suburbs": valid_suburbs,
    })

@app.route('/api/permits', methods=['GET'])
def get_active_permits_endpoint():
    """
    Get active construction permits for a suburb.
    
    Usage: GET /api/permits?suburb=Melbourne
    Optional: &date=2024-06-15 (defaults to today)
    """
    try:
        suburb = request.args.get('suburb', '').strip().title()
        date_str = request.args.get('date', None)
        
        if not suburb:
            return jsonify({
                "success": False,
                "error": "Missing 'suburb' parameter",
                "available_suburbs": valid_suburbs,
            }), 400
        
        query_date = date_str if date_str else datetime.now().strftime('%Y-%m-%d')
        result = get_active_permits_from_com(suburb, query_date)
        
        return jsonify({
            "success": True,
            "suburb": suburb,
            "date": query_date,
            "active_permits": result['active_permits'],
            "total_estimated_cost": round(result['total_estimated_cost'], 2),
            "average_estimated_cost": round(result['average_estimated_cost'], 2),
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/permits/all', methods=['GET'])
def get_all_suburbs_permits():
    """
    Get active construction permits for ALL suburbs at once.
    
    Usage: GET /api/permits/all
    Optional: &date=2024-06-15
    """
    try:
        date_str = request.args.get('date', None)
        query_date = date_str if date_str else datetime.now().strftime('%Y-%m-%d')
        
        results = []
        total = 0
        for suburb in valid_suburbs:
            result = get_active_permits_from_com(suburb, query_date)
            count = result['active_permits']
            total += count
            results.append({
                "suburb": suburb,
                "active_permits": count,
                "total_estimated_cost": round(result['total_estimated_cost'], 2),
            })
        
        results.sort(key=lambda x: x['active_permits'], reverse=True)
        
        return jsonify({
            "success": True,
            "date": query_date,
            "total_active": total,
            "suburbs": results,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/dust-risk', methods=['GET', 'POST'])
def predict_dust_risk():
    """
    Predict dust risk score.
    
    Simple usage (backend fetches everything automatically):
      GET /api/dust-risk?suburb=Melbourne
    
    Advanced usage (override specific values):
      GET /api/dust-risk?suburb=Melbourne&hour=8
      GET /api/dust-risk?active_permits=50&active_permits_cost=5000000&wind_speed=3.5&temperature=25
    """
    try:
        # Get parameters from GET query or POST JSON
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args
        
        suburb = data.get('suburb', '').strip().title()
        now = datetime.now()
        
        # --- PERMITS: from DB or manual override ---
        if 'active_permits' in data and 'active_permits_cost' in data:
            # Manual override
            active_permits = float(data['active_permits'])
            active_permits_cost = float(data['active_permits_cost'])
        elif suburb:
            # Auto-fetch from CoM API
            permits_data = get_active_permits_from_com(suburb)
            active_permits = float(permits_data['active_permits'])
            active_permits_cost = float(permits_data['total_estimated_cost'])
        else:
            active_permits = 0
            active_permits_cost = 0
        
        # --- WEATHER: from Open-Meteo or manual override ---
        if 'wind_speed' in data and 'temperature' in data:
            # Manual override
            wind_speed = float(data['wind_speed'])
            temperature = float(data['temperature'])
        else:
            # Auto-fetch from Open-Meteo
            coords = SUBURB_COORDS.get(suburb, DEFAULT_COORDS)
            weather = get_weather(coords['lat'], coords['lon'])
            wind_speed = weather['wind_speed']
            temperature = weather['temperature']
        
        # --- TIME: auto-detect or manual override ---
        hour = int(data.get('hour', now.hour))
        is_workday = int(data.get('is_workday', 1 if now.weekday() < 5 else 0))
        is_work_hour = 1 if 7 <= hour <= 17 else 0
        is_construction_time = int(data.get('is_construction_time', is_workday * is_work_hour))
        season = int(data.get('season', get_season(now.month)))
        
        # Build feature array in correct order
        features = pd.DataFrame([[
            active_permits,
            active_permits_cost,
            is_construction_time,
            wind_speed,
            temperature,
            hour,
            is_workday,
            season,
        ]], columns=FEATURE_NAMES)
        
        # Predict PM10
        predicted_pm10 = float(model.predict(features)[0])
        predicted_pm10 = max(0, predicted_pm10)  # PM10 can't be negative
        
        # Convert to risk score
        risk_score = pm10_to_risk_score(predicted_pm10)
        risk_level = get_risk_level(risk_score)
        recommendation = get_recommendation(risk_level)
        
        return jsonify({
            "success": True,
            "suburb": suburb if suburb else "custom",
            "predicted_pm10": round(predicted_pm10, 2),
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "input": {
                "active_permits": active_permits,
                "active_permits_cost": active_permits_cost,
                "wind_speed": wind_speed,
                "temperature": temperature,
                "hour": hour,
                "is_workday": is_workday,
                "is_construction_time": is_construction_time,
                "season": season,
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
        }), 400

@app.route('/api/street-risk', methods=['GET'])
def get_street_risk():
    """
    Street-level dust risk assessment.
    Finds active construction sites near a specific location and calculates
    distance-weighted dust risk.
    
    Usage:
      GET /api/street-risk?lat=-37.8136&lon=144.9631
      GET /api/street-risk?lat=-37.8136&lon=144.9631&radius=1000
    """
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = int(request.args.get('radius', 500))  # default 500m
        radius = min(radius, 2000)  # cap at 2km
        
        # 1. Get nearby permits from CoM API
        nearby = get_nearby_permits(lat, lon, radius_m=radius)
        
        # 2. Get weather
        weather = get_weather(lat, lon)
        
        # 3. Calculate dust score using model
        now = datetime.now()
        hour = now.hour
        is_workday = 1 if now.weekday() < 5 else 0
        is_work_hour = 1 if 7 <= hour <= 17 else 0
        is_construction_time = is_workday * is_work_hour
        season = get_season(now.month)
        
        features = pd.DataFrame([[
            float(nearby['active_permits']),
            float(nearby['total_estimated_cost']),
            is_construction_time,
            weather['wind_speed'],
            weather['temperature'],
            hour,
            is_workday,
            season,
        ]], columns=FEATURE_NAMES)
        
        predicted_pm10 = max(0, float(model.predict(features)[0]))
        dust_score = pm10_to_risk_score(predicted_pm10)
        
        # Boost score based on proximity (closer sites = higher risk)
        proximity_boost = min(25, int(nearby['dust_proximity_weight']))
        adjusted_score = min(100, dust_score + proximity_boost)
        risk_level = get_risk_level(adjusted_score)
        
        # 4. Get AQI
        try:
            aqi_url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={lat}&longitude={lon}"
                f"&current=us_aqi,pm10,pm2_5"
            )
            aqi_resp = requests.get(aqi_url, timeout=5)
            aqi_data = aqi_resp.json()
            current_aqi = aqi_data.get('current', {}).get('us_aqi')
        except:
            current_aqi = None
        
        # 5. Combined risk
        overall_score = get_combined_risk(adjusted_score, current_aqi)
        overall_level = get_risk_level(overall_score)
        recommendation = get_recommendation(overall_level)
        precautions = get_precautions(
            overall_level, risk_level, get_aqi_risk_level(current_aqi),
            adjusted_score, current_aqi, nearby['active_permits']
        )
        
        return jsonify({
            "success": True,
            "location": {"lat": lat, "lon": lon},
            "suburb": nearby['suburb'],
            "radius_m": radius,
            "timestamp": now.isoformat(),
            "overall_risk": {
                "score": overall_score,
                "level": overall_level,
                "recommendation": recommendation,
            },
            "precautions": precautions,
            "dust_risk": {
                "score": adjusted_score,
                "level": risk_level,
                "predicted_pm10": round(predicted_pm10, 2),
                "proximity_boost": proximity_boost,
                "nearby_sites": nearby['active_permits'],
            },
            "aqi": {
                "value": current_aqi,
                "level": get_aqi_risk_level(current_aqi),
            },
            "nearby_construction": nearby['nearby_permits'][:10],  # top 10 closest
            "weather": {
                "temperature": weather['temperature'],
                "wind_speed_ms": weather['wind_speed'],
            },
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/current-risk', methods=['GET'])
def get_current_risk():
    """
    Get current overall risk for going outside in a suburb.
    Combines Dust Score + AQI into Low/Moderate/High/Very High.
    
    Usage: GET /api/current-risk?suburb=Melbourne
    """
    try:
        suburb = request.args.get('suburb', '').strip().title()
        if not suburb:
            return jsonify({"success": False, "error": "Missing 'suburb' parameter"}), 400

        now = datetime.now()
        coords = SUBURB_COORDS.get(suburb, DEFAULT_COORDS)

        # 1. Get Dust Score from model
        permits = get_active_permits_from_com(suburb)

        weather = get_weather(coords['lat'], coords['lon'])

        hour = now.hour
        is_workday = 1 if now.weekday() < 5 else 0
        is_work_hour = 1 if 7 <= hour <= 17 else 0
        is_construction_time = is_workday * is_work_hour
        season = get_season(now.month)

        features = pd.DataFrame([[
            float(permits['active_permits']), float(permits['total_estimated_cost']), is_construction_time,
            weather['wind_speed'], weather['temperature'],
            hour, is_workday, season,
        ]], columns=FEATURE_NAMES)

        predicted_pm10 = max(0, float(model.predict(features)[0]))
        dust_score = pm10_to_risk_score(predicted_pm10)
        dust_level = get_risk_level(dust_score)

        # 2. Get current AQI from Open-Meteo
        try:
            aqi_url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=us_aqi,pm10,pm2_5"
            )
            aqi_resp = requests.get(aqi_url, timeout=5)
            aqi_data = aqi_resp.json()
            current_aqi = aqi_data.get('current', {}).get('us_aqi')
            current_pm10_aqi = aqi_data.get('current', {}).get('pm10')
            current_pm25_aqi = aqi_data.get('current', {}).get('pm2_5')
        except:
            current_aqi = None
            current_pm10_aqi = None
            current_pm25_aqi = None

        # 3. Combine into overall risk
        overall_score = get_combined_risk(dust_score, current_aqi)
        overall_level = get_risk_level(overall_score)
        recommendation = get_recommendation(overall_level)
        precautions = get_precautions(
            overall_level, dust_level, get_aqi_risk_level(current_aqi),
            dust_score, current_aqi, int(permits['active_permits'])
        )

        return jsonify({
            "success": True,
            "suburb": suburb,
            "timestamp": now.isoformat(),
            "overall_risk": {
                "score": overall_score,
                "level": overall_level,
                "recommendation": recommendation,
            },
            "precautions": precautions,
            "dust_risk": {
                "score": dust_score,
                "level": dust_level,
                "predicted_pm10": round(predicted_pm10, 2),
                "active_permits": int(permits['active_permits']),
            },
            "aqi": {
                "value": current_aqi,
                "level": get_aqi_risk_level(current_aqi),
                "pm10": current_pm10_aqi,
                "pm25": current_pm25_aqi,
            },
            "weather": {
                "temperature": weather['temperature'],
                "wind_speed_ms": weather['wind_speed'],
            },
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/best-time', methods=['GET'])
def get_best_time():
    """
    Predict risk for the next 6 hours and recommend the best time to go outside.
    Combines hourly AQI forecast + Dust Score for each hour.
    
    Usage: GET /api/best-time?suburb=Melbourne
    Optional: &hours=6 (default 6, max 12)
    """
    try:
        suburb = request.args.get('suburb', '').strip().title()
        forecast_hours = min(int(request.args.get('hours', 6)), 12)

        if not suburb:
            return jsonify({"success": False, "error": "Missing 'suburb' parameter"}), 400

        now = datetime.now()
        coords = SUBURB_COORDS.get(suburb, DEFAULT_COORDS)

        # 1. Get active permits from CoM API (same for all hours today)
        permits = get_active_permits_from_com(suburb)
        active_permits = float(permits['active_permits'])
        active_permits_cost = float(permits['total_estimated_cost'])

        # 2. Get hourly AQI + weather forecast from Open-Meteo
        hourly_forecast = get_hourly_forecast(coords['lat'], coords['lon'], forecast_hours)

        # 3. For each hour, calculate Dust Score + combine with AQI
        hourly_results = []
        for i, hour_data in enumerate(hourly_forecast):
            future_hour = (now.hour + i + 1) % 24
            is_workday = 1 if now.weekday() < 5 else 0
            is_work_hour = 1 if 7 <= future_hour <= 17 else 0
            is_construction_time = is_workday * is_work_hour
            season = get_season(now.month)

            wind_speed = hour_data.get('wind_speed_ms') or 3.0
            temperature = hour_data.get('temperature') or 15.0

            features = pd.DataFrame([[
                active_permits, active_permits_cost, is_construction_time,
                wind_speed, temperature,
                future_hour, is_workday, season,
            ]], columns=FEATURE_NAMES)

            predicted_pm10 = max(0, float(model.predict(features)[0]))
            dust_score = pm10_to_risk_score(predicted_pm10)
            aqi = hour_data.get('aqi')
            overall_score = get_combined_risk(dust_score, aqi)

            hourly_results.append({
                "time": hour_data.get('time', ''),
                "hour": future_hour,
                "overall_score": overall_score,
                "overall_level": get_risk_level(overall_score),
                "dust_score": dust_score,
                "dust_level": get_risk_level(dust_score),
                "aqi": aqi,
                "aqi_level": get_aqi_risk_level(aqi),
                "predicted_pm10": round(predicted_pm10, 2),
                "temperature": temperature,
                "wind_speed": wind_speed,
            })

        # 4. Find best time (lowest overall score)
        if hourly_results:
            best = min(hourly_results, key=lambda x: x['overall_score'])
            best_time = best['time']
            best_hour = best['hour']
            best_score = best['overall_score']
            best_level = best['overall_level']
        else:
            best_time = None
            best_hour = None
            best_score = None
            best_level = "Unknown"

        return jsonify({
            "success": True,
            "suburb": suburb,
            "timestamp": now.isoformat(),
            "best_time": {
                "time": best_time,
                "hour": best_hour,
                "score": best_score,
                "level": best_level,
                "message": f"Best time to go outside is around {best_hour}:00 — risk is {best_level} (score: {best_score}/100)" if best_hour is not None else "Unable to determine",
            },
            "hourly_forecast": hourly_results,
            "active_permits": int(active_permits),
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/dust-risk/batch', methods=['POST'])
def predict_batch():
    """
    Predict dust risk for multiple locations at once.
    Useful for the safest route feature (Iteration 3).
    
    POST body: { "locations": [ {...params...}, {...params...} ] }
    """
    try:
        data = request.get_json()
        locations = data.get('locations', [])
        
        results = []
        for loc in locations:
            active_permits = float(loc.get('active_permits', 0))
            active_permits_cost = float(loc.get('active_permits_cost', 0))
            wind_speed = float(loc.get('wind_speed', 0))
            temperature = float(loc.get('temperature', 20))
            
            now = datetime.now()
            hour = int(loc.get('hour', now.hour))
            is_workday = int(loc.get('is_workday', 1 if now.weekday() < 5 else 0))
            is_work_hour = 1 if 7 <= hour <= 17 else 0
            is_construction_time = int(loc.get('is_construction_time', is_workday * is_work_hour))
            season = int(loc.get('season', get_season(now.month)))
            
            features = pd.DataFrame([[
                active_permits, active_permits_cost, is_construction_time,
                wind_speed, temperature, hour, is_workday, season,
            ]], columns=FEATURE_NAMES)
            
            predicted_pm10 = max(0, float(model.predict(features)[0]))
            risk_score = pm10_to_risk_score(predicted_pm10)
            
            results.append({
                "name": loc.get('name', ''),
                "predicted_pm10": round(predicted_pm10, 2),
                "risk_score": risk_score,
                "risk_level": get_risk_level(risk_score),
            })
        
        return jsonify({
            "success": True,
            "results": results,
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    import os

    print("\n" + "=" * 50)
    print("AsthmaSafe Melbourne — API")
    print("=" * 50)
    print(f"Endpoints:")
    print(f"  GET  /api/health")
    print(f"  GET  /api/suburbs")
    print(f"  GET  /api/permits?suburb=Melbourne")
    print(f"  GET  /api/permits/all")
    print(f"  GET  /api/current-risk?suburb=Melbourne")
    print(f"  GET  /api/best-time?suburb=Melbourne")
    print(f"  GET  /api/dust-risk?suburb=Melbourne")
    print(f"  POST /api/dust-risk/batch")
    print(f"=" * 50 + "\n")

    app.run(
        host='0.0.0.0',
        port=int(os.getenv("PORT", "8080")),
        debug=False,
    )
