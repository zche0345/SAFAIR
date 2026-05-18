# check_db.py
import mysql.connector

DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',  # 你的真实密码
    'database': 'iteration_1',
}

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor(dictionary=True)

print("=== DB clock ===")
cur.execute("SELECT NOW() AS db_utc_now, CONVERT_TZ(NOW(),'UTC','Australia/Melbourne') AS db_melb_now")
print(cur.fetchone())

print("\n=== aqi_forecast freshness ===")
cur.execute("""
    SELECT suburb,
           MIN(forecast_time) AS earliest,
           MAX(forecast_time) AS latest,
           COUNT(*) AS n
    FROM aqi_forecast GROUP BY suburb
""")
for r in cur.fetchall():
    print(r)

print("\n=== weather_forecast freshness ===")
cur.execute("""
    SELECT suburb,
           MIN(forecast_time) AS earliest,
           MAX(forecast_time) AS latest,
           COUNT(*) AS n
    FROM weather_forecast GROUP BY suburb
""")
for r in cur.fetchall():
    print(r)

# 关键：模拟 api.py 那条 SQL 看到底有没有行
print("\n=== what get_hourly_forecast actually sees for Melbourne ===")
cur.execute("""
    SELECT a.forecast_time, a.us_aqi, w.temperature, w.wind_speed_ms
    FROM aqi_forecast a
    LEFT JOIN weather_forecast w
      ON w.suburb = a.suburb AND w.forecast_time = a.forecast_time
    WHERE a.suburb = 'Melbourne'
      AND a.forecast_time >= CONVERT_TZ(NOW(),'UTC','Australia/Melbourne')
    ORDER BY a.forecast_time ASC
    LIMIT 6
""")
rows = cur.fetchall()
print(f"返回 {len(rows)} 行")
for r in rows:
    print(r)

cur.close(); conn.close()