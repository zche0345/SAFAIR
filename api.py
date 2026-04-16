"""
AsthmaSafe Melbourne — Dust Risk Prediction API
=================================================
Loads the trained XGBoost model and serves predictions via REST API.

Usage:
  1. pip install flask xgboost pandas numpy flask-cors mysql-connector-python requests gunicorn
  2. Make sure xgboost_dust_risk_model.json is in model_outputs/
  3. Run locally:        python api.py
  4. Run on Render:      gunicorn api:app
  5. API will be available at http://localhost:5000 (or the Render URL)

Endpoints:
  GET  /api/dust-risk?active_permits=50&active_permits_cost=5000000&wind_speed=3.5&temperature=25
  POST /api/dust-risk  (JSON body)
  GET  /api/health     (health check)
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import xgboost as xgb
import numpy as np
import pandas as pd
from datetime import datetime
import requests
import mysql.connector

app = Flask(__name__)
CORS(app)  # Allow frontend to call this API

# ============================================================
# DATABASE CONFIG
# ============================================================
DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',
    'database': 'iteration_1',
}

def get_db():
    """Get a MySQL connection"""
    return mysql.connector.connect(**DB_CONFIG)

# Verify DB connection on startup
try:
    conn = get_db()
    conn.close()
    print("MySQL connected successfully!")
except Exception as e:
    print(f"WARNING: MySQL connection failed: {e}")
    print("Make sure MySQL is running and run setup_database.py first.")

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
    """Get active building permits from MySQL database"""
    if query_date is None:
        query_date = datetime.now().strftime('%Y-%m-%d')
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT COUNT(*) as cnt, COALESCE(SUM(estimated_cost), 0) as total_cost
            FROM building_permits
            WHERE suburb = %s
              AND issue_date <= %s
              AND completed_by_date >= %s
        """, (suburb, query_date, query_date))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        count = int(result['cnt'])
        total_cost = float(result['total_cost'])
        
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

def find_closest_suburb(lat, lon):
    """Find the suburb whose center is closest to the given coordinates"""
    min_dist = float('inf')
    closest = 'Melbourne'
    for name, coords in SUBURB_COORDS.items():
        d = haversine_distance(lat, lon, coords['lat'], coords['lon'])
        if d < min_dist:
            min_dist = d
            closest = name
    return closest

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_weather(lat, lon):
    """Get latest weather data from MySQL database"""
    try:
        closest = find_closest_suburb(lat, lon)
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT temperature, wind_speed_ms
            FROM weather_data
            WHERE suburb = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (closest,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'wind_speed': float(result['wind_speed_ms']),
                'temperature': float(result['temperature']),
            }
        else:
            # Fallback to API if DB is empty
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,wind_speed_10m"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            wind_kmh = data['current']['wind_speed_10m']
            return {
                'wind_speed': round(wind_kmh / 3.6, 2),
                'temperature': data['current']['temperature_2m'],
            }
    except Exception as e:
        print(f"  Weather error: {e}")
        return {'wind_speed': 3.0, 'temperature': 15.0}

def get_hourly_forecast(lat, lon, hours=6):
    """
    Get hourly forecast from MySQL database.
    Joins weather_forecast + aqi_forecast on (suburb, forecast_time)
    so each hour has its own temperature/wind/AQI — not copied from current.
    """
    try:
        closest = find_closest_suburb(lat, lon)
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        
        # LEFT JOIN: keep AQI rows even if weather forecast is missing,
        # and vice versa. Each hour gets its own forecast values.
        cursor.execute("""
            SELECT 
                a.forecast_time,
                a.us_aqi,
                a.pm25,
                a.pm10,
                w.temperature,
                w.wind_speed_kmh,
                w.wind_speed_ms
            FROM aqi_forecast a
            LEFT JOIN weather_forecast w
                ON w.suburb = a.suburb
                AND w.forecast_time = a.forecast_time
            WHERE a.suburb = %s
              AND a.forecast_time >= CONVERT_TZ(NOW(), 'UTC', 'Australia/Melbourne')
            ORDER BY a.forecast_time ASC
            LIMIT %s
        """, (closest, hours))
        rows = cursor.fetchall()
        
        # Also fetch current weather as fallback for any hour missing forecast data
        cursor.execute("""
            SELECT temperature, wind_speed_ms, wind_speed_kmh
            FROM weather_data
            WHERE suburb = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (closest,))
        current_weather = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if rows:
            hourly = []
            for r in rows:
                # Prefer hourly forecast values; fall back to current weather if NULL
                temp = r['temperature']
                if temp is None and current_weather:
                    temp = current_weather['temperature']
                
                wind_ms = r['wind_speed_ms']
                if wind_ms is None and current_weather:
                    wind_ms = current_weather['wind_speed_ms']
                
                wind_kmh = r['wind_speed_kmh']
                if wind_kmh is None and current_weather:
                    wind_kmh = current_weather['wind_speed_kmh']
                
                hourly.append({
                    'time': r['forecast_time'].strftime('%Y-%m-%dT%H:%M') if r['forecast_time'] else None,
                    'temperature': float(temp) if temp is not None else 15.0,
                    'wind_speed_kmh': float(wind_kmh) if wind_kmh is not None else 10.0,
                    'wind_speed_ms': float(wind_ms) if wind_ms is not None else 3.0,
                    'aqi': r['us_aqi'],
                    'pm10': r['pm10'],
                    'pm25': r['pm25'],
                })
            return hourly
        
        # Fallback to live API if both forecast tables are empty
        print(f"  DB forecast empty for {closest}, falling back to live API")
        aqi_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=us_aqi,pm10,pm2_5"
            f"&forecast_hours={hours}"
            f"&timezone=Australia%2FMelbourne"
        )
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m,wind_speed_10m"
            f"&forecast_hours={hours}"
            f"&timezone=Australia%2FMelbourne"
        )
        aqi_data = requests.get(aqi_url, timeout=5).json()
        weather_data = requests.get(weather_url, timeout=5).json()
        
        aqi_hourly = aqi_data.get('hourly', {})
        weather_hourly = weather_data.get('hourly', {})
        times = aqi_hourly.get('time', [])
        aqis = aqi_hourly.get('us_aqi', [])
        pm10s = aqi_hourly.get('pm10', [])
        pm25s = aqi_hourly.get('pm2_5', [])
        temps = weather_hourly.get('temperature_2m', [])
        winds_kmh = weather_hourly.get('wind_speed_10m', [])
        
        hourly = []
        for i in range(min(len(times), hours)):
            w_kmh = winds_kmh[i] if i < len(winds_kmh) else 10.0
            hourly.append({
                'time': times[i] if i < len(times) else None,
                'temperature': temps[i] if i < len(temps) else 15.0,
                'wind_speed_kmh': w_kmh,
                'wind_speed_ms': round(w_kmh / 3.6, 2) if w_kmh else 3.0,
                'aqi': aqis[i] if i < len(aqis) else None,
                'pm10': pm10s[i] if i < len(pm10s) else None,
                'pm25': pm25s[i] if i < len(pm25s) else None,
            })
        return hourly
    except Exception as e:
        print(f"  Forecast error: {e}")
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

def dust_contribution_to_score(contribution):
    """Convert dust contribution (extra PM10 from construction) to a 0-100 risk score.
    
    Dust contribution = PM10 with construction - PM10 without construction.
    This measures ONLY the additional PM10 caused by nearby construction activity.
    
    Scale based on WHO and research on construction dust impact:
      0-5 ug/m3 extra  → 0-25   Low (barely noticeable)
      5-15 ug/m3 extra → 25-50  Moderate (detectable increase)
      15-30 ug/m3 extra→ 50-75  High (significant construction dust)
      30+ ug/m3 extra  → 75-100 Very High (heavy construction dust)
    """
    if contribution <= 0: return 0
    elif contribution <= 5: return int(contribution / 5 * 25)
    elif contribution <= 15: return int(25 + (contribution - 5) / 10 * 25)
    elif contribution <= 30: return int(50 + (contribution - 15) / 15 * 25)
    else: return min(100, int(75 + (contribution - 30) / 30 * 25))

def predict_dust_score(active_permits, active_permits_cost, is_construction_time,
                       wind_speed, temperature, hour, is_workday, season):
    """
    Calculate Dust Score = PM10 with construction - PM10 without construction.
    Uses the same XGBoost model twice with different inputs.
    Returns: (dust_score, dust_level, predicted_pm10, baseline_pm10, dust_contribution)
    """
    # Prediction WITH real construction data
    features_real = pd.DataFrame([[
        active_permits, active_permits_cost, is_construction_time,
        wind_speed, temperature, hour, is_workday, season,
    ]], columns=FEATURE_NAMES)
    predicted_pm10 = max(0, float(model.predict(features_real)[0]))
    
    # Prediction WITHOUT construction (baseline)
    features_baseline = pd.DataFrame([[
        0, 0, 0,  # no permits, no cost, not construction time
        wind_speed, temperature, hour, is_workday, season,
    ]], columns=FEATURE_NAMES)
    baseline_pm10 = max(0, float(model.predict(features_baseline)[0]))
    
    # Dust contribution = extra PM10 caused by construction
    dust_contribution = max(0, predicted_pm10 - baseline_pm10)
    
    # Convert to 0-100 score
    dust_score = dust_contribution_to_score(dust_contribution)
    dust_level = get_risk_level(dust_score)
    
    return {
        'dust_score': dust_score,
        'dust_level': dust_level,
        'predicted_pm10': round(predicted_pm10, 2),
        'baseline_pm10': round(baseline_pm10, 2),
        'dust_contribution': round(dust_contribution, 2),
    }

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
        
        # Predict Dust Score (construction contribution to PM10)
        dust = predict_dust_score(
            active_permits, active_permits_cost, is_construction_time,
            wind_speed, temperature, hour, is_workday, season
        )
        recommendation = get_recommendation(dust['dust_level'])
        
        return jsonify({
            "success": True,
            "suburb": suburb if suburb else "custom",
            "predicted_pm10": dust['predicted_pm10'],
            "baseline_pm10": dust['baseline_pm10'],
            "dust_contribution": dust['dust_contribution'],
            "risk_score": dust['dust_score'],
            "risk_level": dust['dust_level'],
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
        
        dust = predict_dust_score(
            float(nearby['active_permits']), float(nearby['total_estimated_cost']),
            is_construction_time, weather['wind_speed'], weather['temperature'],
            hour, is_workday, season
        )
        
        # Boost score based on proximity (closer sites = higher risk)
        proximity_boost = min(25, int(nearby['dust_proximity_weight']))
        adjusted_score = min(100, dust['dust_score'] + proximity_boost)
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
                "predicted_pm10": dust['predicted_pm10'],
                "baseline_pm10": dust['baseline_pm10'],
                "dust_contribution": dust['dust_contribution'],
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

        dust = predict_dust_score(
            float(permits['active_permits']), float(permits['total_estimated_cost']),
            is_construction_time, weather['wind_speed'], weather['temperature'],
            hour, is_workday, season
        )

        # 2. Get current AQI from database
        try:
            conn2 = get_db()
            cursor2 = conn2.cursor(dictionary=True)
            cursor2.execute("""
                SELECT us_aqi, pm25, pm10
                FROM aqi_data
                WHERE suburb = %s
                ORDER BY recorded_at DESC
                LIMIT 1
            """, (suburb,))
            aqi_row = cursor2.fetchone()
            cursor2.close()
            conn2.close()
            
            if aqi_row:
                current_aqi = aqi_row['us_aqi']
                current_pm10_aqi = aqi_row['pm10']
                current_pm25_aqi = aqi_row['pm25']
            else:
                current_aqi = None
                current_pm10_aqi = None
                current_pm25_aqi = None
        except:
            current_aqi = None
            current_pm10_aqi = None
            current_pm25_aqi = None

        # 3. Combine into overall risk
        overall_score = get_combined_risk(dust['dust_score'], current_aqi)
        overall_level = get_risk_level(overall_score)
        recommendation = get_recommendation(overall_level)
        precautions = get_precautions(
            overall_level, dust['dust_level'], get_aqi_risk_level(current_aqi),
            dust['dust_score'], current_aqi, int(permits['active_permits'])
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
                "score": dust['dust_score'],
                "level": dust['dust_level'],
                "predicted_pm10": dust['predicted_pm10'],
                "baseline_pm10": dust['baseline_pm10'],
                "dust_contribution": dust['dust_contribution'],
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
    Predict risk for the next N hours and recommend the best time to go outside.
    Combines hourly AQI forecast + hourly weather forecast + Dust Score per hour.
    
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

        # 1. Get active permits from DB (same for all hours today)
        permits = get_active_permits_from_com(suburb)
        active_permits = float(permits['active_permits'])
        active_permits_cost = float(permits['total_estimated_cost'])

        # 2. Get hourly AQI + weather forecast (joined from DB)
        hourly_forecast = get_hourly_forecast(coords['lat'], coords['lon'], forecast_hours)

        # 3. For each hour, calculate Dust Score + combine with AQI
        hourly_results = []
        for hour_data in hourly_forecast:
            # Parse actual hour from forecast_time (more reliable than now.hour + i)
            time_str = hour_data.get('time', '')
            try:
                forecast_dt = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
                future_hour = forecast_dt.hour
                future_weekday = forecast_dt.weekday()
                future_month = forecast_dt.month
            except (ValueError, TypeError):
                # Fallback if time string is malformed
                forecast_dt = now
                future_hour = now.hour
                future_weekday = now.weekday()
                future_month = now.month

            is_workday = 1 if future_weekday < 5 else 0
            is_work_hour = 1 if 7 <= future_hour <= 17 else 0
            is_construction_time = is_workday * is_work_hour
            season = get_season(future_month)

            wind_speed = hour_data.get('wind_speed_ms') or 3.0
            temperature = hour_data.get('temperature') or 15.0

            dust = predict_dust_score(
                active_permits, active_permits_cost, is_construction_time,
                wind_speed, temperature, future_hour, is_workday, season
            )
            aqi = hour_data.get('aqi')
            overall_score = get_combined_risk(dust['dust_score'], aqi)

            hourly_results.append({
                "time": time_str,
                "hour": future_hour,
                "overall_score": overall_score,
                "overall_level": get_risk_level(overall_score),
                "dust_score": dust['dust_score'],
                "dust_level": dust['dust_level'],
                "dust_contribution": dust['dust_contribution'],
                "aqi": aqi,
                "aqi_level": get_aqi_risk_level(aqi),
                "predicted_pm10": dust['predicted_pm10'],
                "baseline_pm10": dust['baseline_pm10'],
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
            
            dust = predict_dust_score(
                active_permits, active_permits_cost, is_construction_time,
                wind_speed, temperature, hour, is_workday, season
            )
            
            results.append({
                "name": loc.get('name', ''),
                "predicted_pm10": dust['predicted_pm10'],
                "baseline_pm10": dust['baseline_pm10'],
                "dust_contribution": dust['dust_contribution'],
                "risk_score": dust['dust_score'],
                "risk_level": dust['dust_level'],
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
    print(f"  GET  /api/street-risk?lat=-37.81&lon=144.96")
    print(f"  GET  /api/dust-risk?suburb=Melbourne")
    print(f"  POST /api/dust-risk/batch")
    print(f"=" * 50 + "\n")
    
    # Use PORT env var if set (for Render/Heroku), otherwise default to 5000 (local)
    port = int(os.environ.get('PORT', 5000))
    # host='0.0.0.0' so external requests can reach it (required for Render)
    app.run(host='0.0.0.0', port=port, debug=False)