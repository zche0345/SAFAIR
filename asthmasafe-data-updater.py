"""
AsthmaSafe Melbourne — Lambda Data Updater
============================================
AWS Lambda function that fetches data from external APIs 
and stores in RDS MySQL. Triggered by EventBridge every 1 hour.

Deployment:
  1. pip install mysql-connector-python requests -t package/
  2. Copy this file into package/
  3. cd package && zip -r ../lambda_data_updater.zip .
  4. Upload lambda_data_updater.zip to AWS Lambda
  5. Set handler to: lambda_function.lambda_handler
  6. Set timeout to 120 seconds (2 minutes)
  7. Set memory to 256 MB
  8. Create EventBridge rule: rate(1 hour)

Required tables:
  - building_permits
  - weather_data
  - weather_forecast
  - aqi_data
  - aqi_forecast

Credentials:
  RDS credentials (host, port, username, password) read from
  AWS Secrets Manager entry `safair-rds-credentials` on cold start.
  Cached for the Lambda container lifetime. No env-var fallback;
  no hardcoded credentials in source.
"""

import json
import os
import boto3
import mysql.connector
import requests
from botocore.exceptions import ClientError
from datetime import datetime

# ============================================================
# CONFIG — credentials sourced from Secrets Manager
# ============================================================
SECRET_ID = "safair-rds-credentials"
DB_NAME = "iteration_1"  # schema name; not a credential

_sm = boto3.client("secretsmanager", region_name="ap-southeast-2")
_db_creds_cache = None


def get_db_creds():
    """Read RDS connection params from Secrets Manager. Cached per cold start."""
    global _db_creds_cache
    if _db_creds_cache is not None:
        return _db_creds_cache
    try:
        resp = _sm.get_secret_value(SecretId=SECRET_ID)
        parsed = json.loads(resp["SecretString"])
        _db_creds_cache = {
            "host": parsed["host"],
            "port": int(parsed["port"]),
            "user": parsed["username"],
            "password": parsed["password"],
            "database": DB_NAME,
        }
        return _db_creds_cache
    except ClientError as e:
        print(f"[ERROR] Secrets Manager read failed: {e}")
        raise


COM_API_BASE = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/building-permits/records"

SUBURBS = {
    'Carlton':         {'lat': -37.8000, 'lon': 144.9670},
    'Docklands':       {'lat': -37.8145, 'lon': 144.9460},
    'East Melbourne':  {'lat': -37.8160, 'lon': 144.9870},
    'Kensington':      {'lat': -37.7940, 'lon': 144.9260},
    'Melbourne':       {'lat': -37.8136, 'lon': 144.9631},
    'North Melbourne': {'lat': -37.7990, 'lon': 144.9430},
    'Parkville':       {'lat': -37.7860, 'lon': 144.9550},
    'South Yarra':     {'lat': -37.8380, 'lon': 144.9930},
    'Southbank':       {'lat': -37.8230, 'lon': 144.9650},
    'West Melbourne':  {'lat': -37.8080, 'lon': 144.9380},
}


def get_db():
    return mysql.connector.connect(**get_db_creds())


# ============================================================
# 1. UPDATE BUILDING PERMITS
# ============================================================
def update_building_permits():
    conn = get_db()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    total = 0
    
    for suburb in SUBURBS:
        suburb_upper = suburb.upper()
        where_clause = (
            f'permit_certificate_type = "Building Permit"'
            f' AND issue_date <= "{today}"'
            f' AND completed_by_date >= "{today}"'
            f' AND address LIKE "%{suburb_upper}%"'
        )
        
        try:
            offset = 0
            while True:
                params = {'where': where_clause, 'limit': 100, 'offset': offset}
                resp = requests.get(COM_API_BASE, params=params, timeout=15)
                records = resp.json().get('results', [])
                
                if not records:
                    break
                
                for r in records:
                    cursor.execute("""
                        INSERT INTO building_permits 
                        (permit_id, council_ref, suburb, address, issue_date, 
                         completed_by_date, estimated_cost, description, permit_type)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            estimated_cost = VALUES(estimated_cost),
                            completed_by_date = VALUES(completed_by_date),
                            last_updated = NOW()
                    """, (
                        r.get('permit_number', ''),
                        r.get('council_ref', ''),
                        suburb,
                        r.get('address', ''),
                        r.get('issue_date') or None,
                        r.get('completed_by_date') or None,
                        r.get('estimated_cost_of_works') or 0,
                        r.get('desc_of_works', ''),
                        'Building Permit',
                    ))
                    total += 1
                
                if len(records) < 100:
                    break
                offset += 100
        except Exception as e:
            print(f"Error for {suburb}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    return total

# ============================================================
# 2. UPDATE WEATHER (current + hourly forecast)
# ============================================================
def update_weather():
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    count = 0
    forecast_count = 0
    
    for suburb, coords in SUBURBS.items():
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=temperature_2m,wind_speed_10m"
                f"&hourly=temperature_2m,wind_speed_10m"
                f"&forecast_hours=12"
                f"&timezone=Australia%2FMelbourne"
            )
            data = requests.get(url, timeout=10).json()
            
            # --- Current weather ---
            current = data.get('current', {})
            temp = current.get('temperature_2m')
            wind_kmh = current.get('wind_speed_10m')
            wind_ms = round(wind_kmh / 3.6, 2) if wind_kmh is not None else None
            
            cursor.execute("""
                INSERT INTO weather_data 
                (suburb, latitude, longitude, temperature, wind_speed_kmh, wind_speed_ms, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (suburb, coords['lat'], coords['lon'], temp, wind_kmh, wind_ms, now))
            count += 1
            
            # --- Hourly forecast ---
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            temps = hourly.get('temperature_2m', [])
            winds = hourly.get('wind_speed_10m', [])
            
            for i in range(len(times)):
                h_temp = temps[i] if i < len(temps) else None
                h_wind_kmh = winds[i] if i < len(winds) else None
                h_wind_ms = round(h_wind_kmh / 3.6, 2) if h_wind_kmh is not None else None
                
                cursor.execute("""
                    INSERT INTO weather_forecast 
                    (suburb, forecast_time, temperature, wind_speed_kmh, wind_speed_ms)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        temperature = VALUES(temperature),
                        wind_speed_kmh = VALUES(wind_speed_kmh),
                        wind_speed_ms = VALUES(wind_speed_ms),
                        fetched_at = NOW()
                """, (suburb, times[i], h_temp, h_wind_kmh, h_wind_ms))
                forecast_count += 1
        except Exception as e:
            print(f"Weather error {suburb}: {e}")
    
    # Clean old forecast data
    cursor.execute("DELETE FROM weather_forecast WHERE forecast_time < NOW() - INTERVAL 24 HOUR")
    
    conn.commit()
    cursor.close()
    conn.close()
    return count, forecast_count

# ============================================================
# 3. UPDATE AQI
# ============================================================
def update_aqi():
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    aqi_count = 0
    forecast_count = 0
    
    for suburb, coords in SUBURBS.items():
        try:
            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=us_aqi,pm10,pm2_5"
                f"&hourly=us_aqi,pm10,pm2_5"
                f"&forecast_hours=12"
                f"&timezone=Australia%2FMelbourne"
            )
            data = requests.get(url, timeout=10).json()
            
            # Current AQI
            current = data.get('current', {})
            aqi = current.get('us_aqi')
            pm25 = current.get('pm2_5')
            pm10 = current.get('pm10')
            
            aqi_level = 'Low'
            if aqi and aqi > 150: aqi_level = 'Very High'
            elif aqi and aqi > 100: aqi_level = 'High'
            elif aqi and aqi > 50: aqi_level = 'Moderate'
            
            cursor.execute("""
                INSERT INTO aqi_data 
                (suburb, latitude, longitude, us_aqi, pm25, pm10, aqi_level, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (suburb, coords['lat'], coords['lon'], aqi, pm25, pm10, aqi_level, now))
            aqi_count += 1
            
            # Hourly forecast
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            aqis = hourly.get('us_aqi', [])
            pm25s = hourly.get('pm2_5', [])
            pm10s = hourly.get('pm10', [])
            
            for i in range(len(times)):
                h_aqi = aqis[i] if i < len(aqis) else None
                h_pm25 = pm25s[i] if i < len(pm25s) else None
                h_pm10 = pm10s[i] if i < len(pm10s) else None
                
                h_level = 'Low'
                if h_aqi and h_aqi > 150: h_level = 'Very High'
                elif h_aqi and h_aqi > 100: h_level = 'High'
                elif h_aqi and h_aqi > 50: h_level = 'Moderate'
                
                cursor.execute("""
                    INSERT INTO aqi_forecast 
                    (suburb, forecast_time, us_aqi, pm25, pm10, aqi_level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        us_aqi = VALUES(us_aqi), pm25 = VALUES(pm25),
                        pm10 = VALUES(pm10), aqi_level = VALUES(aqi_level),
                        fetched_at = NOW()
                """, (suburb, times[i], h_aqi, h_pm25, h_pm10, h_level))
                forecast_count += 1
        except Exception as e:
            print(f"AQI error {suburb}: {e}")
    
    # Clean old data
    cursor.execute("DELETE FROM aqi_forecast WHERE forecast_time < NOW() - INTERVAL 24 HOUR")
    
    conn.commit()
    cursor.close()
    conn.close()
    return aqi_count, forecast_count

# ============================================================
# LAMBDA HANDLER
# ============================================================
def lambda_handler(event, context):
    """AWS Lambda entry point, triggered by EventBridge"""
    print(f"Starting data update at {datetime.now().isoformat()}")
    
    permits = update_building_permits()
    print(f"Building permits: {permits} records")
    
    weather_count, weather_forecast_count = update_weather()
    print(f"Weather: {weather_count} current + {weather_forecast_count} forecast records")
    
    aqi_count, aqi_forecast_count = update_aqi()
    print(f"AQI: {aqi_count} current + {aqi_forecast_count} forecast records")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Data update complete',
            'building_permits': permits,
            'weather_current': weather_count,
            'weather_forecast': weather_forecast_count,
            'aqi_current': aqi_count,
            'aqi_forecast': aqi_forecast_count,
            'timestamp': datetime.now().isoformat(),
        })
    }
