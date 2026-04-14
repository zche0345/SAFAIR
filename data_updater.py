"""
AsthmaSafe Melbourne — Data Updater
=====================================
Fetches data from external APIs and stores in MySQL.
Run this as a scheduled task every 15 minutes.

Usage:
  pip install mysql-connector-python requests schedule
  
  # Option 1: Run once (for cron job)
  python data_updater.py --once

  # Option 2: Run continuously (self-scheduling every 15 min)
  python data_updater.py
"""

import mysql.connector
import requests
import re
import sys
import time
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================
DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',
    'database': 'iteration_1',
}

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
    return mysql.connector.connect(**DB_CONFIG)

# ============================================================
# 1. UPDATE BUILDING PERMITS (from CoM Open Data API)
# ============================================================
def update_building_permits():
    """Fetch active building permits from CoM API and store in MySQL"""
    print("\n[1/3] Updating Building Permits...")
    
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    today = now.strftime('%Y-%m-%d')
    total_inserted = 0
    
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
                params = {
                    'where': where_clause,
                    'limit': 100,
                    'offset': offset,
                }
                resp = requests.get(COM_API_BASE, params=params, timeout=15)
                data = resp.json()
                records = data.get('results', [])
                
                if not records:
                    break
                
                for r in records:
                    permit_id = r.get('permit_number', '')
                    issue_date = r.get('issue_date', '')
                    
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
                        permit_id,
                        r.get('council_ref', ''),
                        suburb,
                        r.get('address', ''),
                        issue_date if issue_date else None,
                        r.get('completed_by_date', '') or None,
                        r.get('estimated_cost_of_works') or 0,
                        r.get('desc_of_works', ''),
                        'Building Permit',
                    ))
                    total_inserted += 1
                
                if len(records) < 100:
                    break
                offset += 100
        
        except Exception as e:
            print(f"    Error for {suburb}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    ✓ {total_inserted} permit records upserted across {len(SUBURBS)} suburbs")

# ============================================================
# 2. UPDATE WEATHER DATA (from Open-Meteo Forecast API)
# ============================================================
def update_weather():
    """Fetch current weather for each suburb and store in MySQL"""
    print("\n[2/3] Updating Weather Data...")
    
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    inserted = 0
    
    for suburb, coords in SUBURBS.items():
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=temperature_2m,wind_speed_10m"
            )
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            temp = data['current']['temperature_2m']
            wind_kmh = data['current']['wind_speed_10m']
            wind_ms = round(wind_kmh / 3.6, 2)
            
            cursor.execute("""
                INSERT INTO weather_data 
                (suburb, latitude, longitude, temperature, wind_speed_kmh, wind_speed_ms, recorded_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (suburb, coords['lat'], coords['lon'], temp, wind_kmh, wind_ms, now))
            inserted += 1
        
        except Exception as e:
            print(f"    Error for {suburb}: {e}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    ✓ {inserted} weather records inserted")

# ============================================================
# 3. UPDATE AQI DATA (from Open-Meteo Air Quality API)
# ============================================================
def update_aqi():
    """Fetch current AQI + hourly forecast for each suburb and store in MySQL"""
    print("\n[3/3] Updating AQI Data...")
    
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()
    aqi_inserted = 0
    forecast_inserted = 0
    
    for suburb, coords in SUBURBS.items():
        try:
            # Current AQI
            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality"
                f"?latitude={coords['lat']}&longitude={coords['lon']}"
                f"&current=us_aqi,pm10,pm2_5"
                f"&hourly=us_aqi,pm10,pm2_5"
                f"&forecast_hours=12"
                f"&timezone=Australia%2FMelbourne"
            )
            resp = requests.get(url, timeout=10)
            data = resp.json()
            
            # Store current AQI
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
            aqi_inserted += 1
            
            # Store hourly forecast
            hourly = data.get('hourly', {})
            times = hourly.get('time', [])
            aqis = hourly.get('us_aqi', [])
            pm25s = hourly.get('pm2_5', [])
            pm10s = hourly.get('pm10', [])
            
            for i in range(len(times)):
                forecast_time = times[i]
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
                        us_aqi = VALUES(us_aqi),
                        pm25 = VALUES(pm25),
                        pm10 = VALUES(pm10),
                        aqi_level = VALUES(aqi_level),
                        fetched_at = NOW()
                """, (suburb, forecast_time, h_aqi, h_pm25, h_pm10, h_level))
                forecast_inserted += 1
        
        except Exception as e:
            print(f"    Error for {suburb}: {e}")
    
    # Clean old forecast data (older than 24 hours)
    cursor.execute("DELETE FROM aqi_forecast WHERE forecast_time < NOW() - INTERVAL 24 HOUR")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"    ✓ {aqi_inserted} current AQI records inserted")
    print(f"    ✓ {forecast_inserted} forecast records upserted")

# ============================================================
# RUN ALL UPDATES
# ============================================================
def run_all_updates():
    """Run all data updates"""
    print("=" * 60)
    print(f"AsthmaSafe Data Update — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    update_building_permits()
    update_weather()
    update_aqi()
    
    print("\n" + "=" * 60)
    print("✓ All updates complete!")
    print("=" * 60)

# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    if '--once' in sys.argv:
        # Run once and exit (for cron job)
        run_all_updates()
    else:
        # Run continuously, every 15 minutes
        import schedule
        
        print("Starting AsthmaSafe Data Updater (every 15 minutes)")
        print("Press Ctrl+C to stop\n")
        
        # Run immediately on start
        run_all_updates()
        
        # Schedule every 15 minutes
        schedule.every(15).minutes.do(run_all_updates)
        
        while True:
            schedule.run_pending()
            time.sleep(60)
