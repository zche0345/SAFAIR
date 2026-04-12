import pandas as pd

# ============================================================
# LOAD
# ============================================================
df = pd.read_csv("table3_construction_air_quality.csv")

print("Original rows:", len(df))

# ============================================================
# REMOVE MISSING
# ============================================================
df = df.dropna(subset=["pm10", "pm2_5", "aqi"])

# ============================================================
# DATA TYPE FIX
# ============================================================
df["pm10"] = pd.to_numeric(df["pm10"], errors="coerce")
df["pm2_5"] = pd.to_numeric(df["pm2_5"], errors="coerce")
df["aqi"] = pd.to_numeric(df["aqi"], errors="coerce")

# ============================================================
# ADD RISK LEVEL 
# ============================================================
def get_risk(pm10):
    if pm10 <= 15:
        return "Low"
    elif pm10 <= 30:
        return "Moderate"
    elif pm10 <= 45:
        return "High"
    else:
        return "Very High"

df["risk_level"] = df["pm10"].apply(get_risk)

# ============================================================
# OPTIONAL: simplify status
# ============================================================
if "status" in df.columns:
    df["status_clean"] = df["status"].str.lower()

# ============================================================
# FINAL SAVE
# ============================================================
OUTPUT = "final_dataset.csv"
df.to_csv(OUTPUT, index=False)

print("Final dataset saved:", OUTPUT)
print(df.head())