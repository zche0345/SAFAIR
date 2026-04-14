"""
AsthmaSafe Melbourne — Database Setup
======================================
Creates all tables in MySQL for storing API data.

Usage:
  pip install mysql-connector-python
  python setup_database.py
"""

import mysql.connector

DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',
}

DATABASE_NAME = 'iteration_1'

print("Connecting to AWS RDS MySQL...")
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Create database if not exists
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
cursor.execute(f"USE {DATABASE_NAME}")
print(f"  Using database: {DATABASE_NAME}")

# ============================================================
# TABLE 1: Building Permits (from CoM Open Data API)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS building_permits (
        id INT AUTO_INCREMENT PRIMARY KEY,
        permit_id VARCHAR(100),
        council_ref VARCHAR(50),
        suburb VARCHAR(100) NOT NULL,
        address TEXT,
        issue_date DATE,
        completed_by_date DATE,
        estimated_cost DECIMAL(15,2),
        description TEXT,
        permit_type VARCHAR(100),
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_suburb (suburb),
        INDEX idx_dates (issue_date, completed_by_date),
        INDEX idx_suburb_dates (suburb, issue_date, completed_by_date),
        UNIQUE KEY uk_permit (permit_id, issue_date)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("  ✓ building_permits table created")

# ============================================================
# TABLE 2: Weather Data (from Open-Meteo Forecast API)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        suburb VARCHAR(100) NOT NULL,
        latitude DECIMAL(10,6),
        longitude DECIMAL(10,6),
        temperature FLOAT,
        wind_speed_kmh FLOAT,
        wind_speed_ms FLOAT,
        recorded_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_suburb_time (suburb, recorded_at),
        INDEX idx_recorded (recorded_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("  ✓ weather_data table created")

# ============================================================
# TABLE 3: AQI Data (from Open-Meteo Air Quality API)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS aqi_data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        suburb VARCHAR(100) NOT NULL,
        latitude DECIMAL(10,6),
        longitude DECIMAL(10,6),
        us_aqi INT,
        pm25 FLOAT,
        pm10 FLOAT,
        aqi_level VARCHAR(20),
        recorded_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_suburb_time (suburb, recorded_at),
        INDEX idx_recorded (recorded_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("  ✓ aqi_data table created")

# ============================================================
# TABLE 4: AQI Forecast (hourly forecast from Open-Meteo)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS aqi_forecast (
        id INT AUTO_INCREMENT PRIMARY KEY,
        suburb VARCHAR(100) NOT NULL,
        forecast_time DATETIME NOT NULL,
        us_aqi INT,
        pm25 FLOAT,
        pm10 FLOAT,
        aqi_level VARCHAR(20),
        fetched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_suburb_forecast (suburb, forecast_time),
        UNIQUE KEY uk_suburb_time (suburb, forecast_time)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("  ✓ aqi_forecast table created")

# ============================================================
# TABLE 5: Dust Risk Predictions (log of model predictions)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dust_risk_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        suburb VARCHAR(100),
        latitude DECIMAL(10,6),
        longitude DECIMAL(10,6),
        active_permits INT,
        active_permits_cost DECIMAL(15,2),
        wind_speed FLOAT,
        temperature FLOAT,
        hour INT,
        is_workday TINYINT,
        is_construction_time TINYINT,
        season INT,
        predicted_pm10 FLOAT,
        baseline_pm10 FLOAT,
        dust_score INT,
        dust_level VARCHAR(20),
        aqi INT,
        overall_score INT,
        overall_level VARCHAR(20),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_suburb (suburb),
        INDEX idx_created (created_at)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")
print("  ✓ dust_risk_log table created")

# ============================================================
# TABLE 6: Suburb coordinates (reference table)
# ============================================================
cursor.execute("""
    CREATE TABLE IF NOT EXISTS suburbs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        postcode VARCHAR(10),
        latitude DECIMAL(10,6),
        longitude DECIMAL(10,6)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

# Insert suburb data
suburbs = [
    ('Carlton', '3053', -37.8000, 144.9670),
    ('Docklands', '3008', -37.8145, 144.9460),
    ('East Melbourne', '3002', -37.8160, 144.9870),
    ('Kensington', '3031', -37.7940, 144.9260),
    ('Melbourne', '3000', -37.8136, 144.9631),
    ('North Melbourne', '3051', -37.7990, 144.9430),
    ('Parkville', '3052', -37.7860, 144.9550),
    ('South Yarra', '3141', -37.8380, 144.9930),
    ('Southbank', '3006', -37.8230, 144.9650),
    ('West Melbourne', '3003', -37.8080, 144.9380),
]

cursor.execute("DELETE FROM suburbs")
for name, postcode, lat, lon in suburbs:
    cursor.execute(
        "INSERT INTO suburbs (name, postcode, latitude, longitude) VALUES (%s, %s, %s, %s)",
        (name, postcode, lat, lon)
    )
print("  ✓ suburbs table created and populated")

conn.commit()

# ============================================================
# VERIFY
# ============================================================
print("\nVerifying tables...")
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"  {t[0]}: {count} rows")

cursor.close()
conn.close()

print("\n✓ Database setup complete!")
print("Next step: run data_updater.py to start fetching data from APIs.")
