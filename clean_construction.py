import pandas as pd
import requests
import time

# ============================================================
# CONFIG
# ============================================================
INPUT_FILE = "building-permits.csv"
OUTPUT_CLEAN_FILE = "clean_permits_city_of_melbourne.csv"
OUTPUT_GEO_FILE = "geocoded_permits_sample_200.csv"

USER_AGENT = "MonashStudentProject/1.0 (hzha0359@student.monash.edu)"

# ============================================================
# ADDRESS CLEANING
# ============================================================
def clean_address(addr):
    if pd.isna(addr):
        return None

    addr = str(addr).upper()

    # remove useless parts (level/floor etc.)
    keywords = ["LEVEL", "LVL", "FLOOR", "PART", "BASEMENT"]
    for k in keywords:
        if k in addr:
            addr = addr.split(",")[-1]

    return addr.strip() + ", Melbourne, Australia"


# ============================================================
# GEOCODING FUNCTION (Nominatim)
# ============================================================
def get_lat_lon(address):
    url = "https://nominatim.openstreetmap.org/search"

    params = {
        "q": address,
        "format": "json",
        "limit": 1
    }

    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Status error {response.status_code} for {address}")
            return None, None

        data = response.json()

        if len(data) > 0:
            return data[0]["lat"], data[0]["lon"]

    except Exception as e:
        print(f"Error for {address}: {e}")

    return None, None


# ============================================================
# LOAD DATA
# ============================================================
df = pd.read_csv(INPUT_FILE)

# clean column names
df.columns = df.columns.str.strip().str.lower()

# keep useful columns
df = df[
    [
        "council_ref",
        "permit_number",
        "issue_date",
        "address",
        "desc_of_works",
        "estimated_cost_of_works",
        "commence_by_date",
        "completed_by_date",
        "permit_certificate_type",
    ]
].copy()

# remove empty address
df = df[df["address"].notna()]
df["address"] = df["address"].astype(str).str.strip()
df = df[df["address"] != ""]

# date format
df["issue_date"] = pd.to_datetime(df["issue_date"], errors="coerce")
df["commence_by_date"] = pd.to_datetime(df["commence_by_date"], errors="coerce")
df["completed_by_date"] = pd.to_datetime(df["completed_by_date"], errors="coerce")

# only Building Permit
df = df[
    df["permit_certificate_type"].str.upper().str.strip() == "BUILDING PERMIT"
]

# remove duplicates
df = df.drop_duplicates()

# save cleaned data
df.to_csv(OUTPUT_CLEAN_FILE, index=False)

print("Clean dataset saved:", OUTPUT_CLEAN_FILE)
print("Clean rows:", len(df))
print("Unique addresses:", df["address"].nunique())


# ============================================================
# SELECT SAMPLE FOR API
# ============================================================
unique_addresses = df["address"].drop_duplicates().head(200)

df_geo_input = pd.DataFrame({
    "raw_address": unique_addresses
})

df_geo_input["clean_address"] = df_geo_input["raw_address"].apply(clean_address)

# remove duplicates after cleaning
df_geo_input = df_geo_input.drop_duplicates(subset=["clean_address"])

print("Addresses selected for geocoding:", len(df_geo_input))


# ============================================================
# CALL API (WITH CACHE)
# ============================================================
cache = {}
results = []

for i, row in enumerate(df_geo_input.itertuples(index=False), start=1):
    raw_addr = row.raw_address
    clean_addr = row.clean_address

    if clean_addr in cache:
        lat, lon = cache[clean_addr]
    else:
        lat, lon = get_lat_lon(clean_addr)
        cache[clean_addr] = (lat, lon)
        time.sleep(1)  # VERY IMPORTANT (API limit)

    results.append({
        "raw_address": raw_addr,
        "clean_address": clean_addr,
        "lat": lat,
        "lon": lon
    })

    print(f"[{i}/{len(df_geo_input)}] {clean_addr} -> lat={lat}, lon={lon}")

df_geo = pd.DataFrame(results)


# ============================================================
# MERGE BACK
# ============================================================
df_final = df.merge(
    df_geo[["raw_address", "lat", "lon"]],
    left_on="address",
    right_on="raw_address",
    how="left"
)

df_final = df_final.drop(columns=["raw_address"])

# ============================================================
# ADD STATUS (active / inactive)
# ============================================================

today = pd.Timestamp.today()

df_final["status"] = df_final["completed_by_date"].apply(
    lambda x: "active" if pd.isna(x) or x >= today else "inactive"
)

# save final result
df_final.to_csv(OUTPUT_GEO_FILE, index=False)

print("Geocoded dataset saved:", OUTPUT_GEO_FILE)
print("Rows with coordinates:", df_final["lat"].notna().sum())
print("Rows without coordinates:", df_final["lat"].isna().sum())

# ============================================================
# ADD STATUS (active / inactive)
# ============================================================

today = pd.Timestamp.today()

df_final["status"] = df_final["completed_by_date"].apply(
    lambda x: "active" if pd.isna(x) or x >= today else "inactive"
)