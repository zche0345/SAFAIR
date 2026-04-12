import pandas as pd

# ============================================================
# CONFIG
# ============================================================
TABLE1_FILE = "table1_construction_sites.csv"
TABLE2_FILE = "table2_air_quality.csv"
OUTPUT_FILE = "table3_construction_air_quality.csv"

# ============================================================
# LOAD DATA
# ============================================================
table1 = pd.read_csv(TABLE1_FILE)
table2 = pd.read_csv(TABLE2_FILE)

print("Table 1 rows:", len(table1))
print("Table 2 rows:", len(table2))

# ============================================================
# CLEAN DATA TYPES
# ============================================================
table1["latitude"] = pd.to_numeric(table1["latitude"], errors="coerce")
table1["longitude"] = pd.to_numeric(table1["longitude"], errors="coerce")

table2["latitude"] = pd.to_numeric(table2["latitude"], errors="coerce")
table2["longitude"] = pd.to_numeric(table2["longitude"], errors="coerce")

# remove rows with missing coordinates
table1 = table1[table1["latitude"].notna() & table1["longitude"].notna()].copy()
table2 = table2[table2["latitude"].notna() & table2["longitude"].notna()].copy()

# ============================================================
# ROUND COORDINATES FOR MERGE
# ============================================================
table1["lat_round"] = table1["latitude"].round(5)
table1["lon_round"] = table1["longitude"].round(5)

table2["lat_round"] = table2["latitude"].round(5)
table2["lon_round"] = table2["longitude"].round(5)

# ============================================================
# MERGE TABLE 1 + TABLE 2
# ============================================================
table3 = table1.merge(
    table2[["timestamp", "pm10", "pm2_5", "aqi", "lat_round", "lon_round"]],
    on=["lat_round", "lon_round"],
    how="left"
)

# ============================================================
# SELECT FINAL COLUMNS
# ============================================================
table3_final = table3[
    [
        "site_id",
        "latitude",
        "longitude",
        "start_date",
        "end_date",
        "status",
        "timestamp",
        "pm10",
        "pm2_5",
        "aqi"
    ]
].copy()

# ============================================================
# SAVE
# ============================================================
table3_final.to_csv(OUTPUT_FILE, index=False)

print("\nTable 3 saved:", OUTPUT_FILE)
print("Rows in Table 3:", len(table3_final))
print("Matched rows with air quality:", table3_final["pm10"].notna().sum())
print("Unmatched rows:", table3_final["pm10"].isna().sum())

print("\nPreview:")
print(table3_final.head())