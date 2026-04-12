import pandas as pd

df = pd.read_csv("building-permits.csv")
print(df.head())
print(df.columns)


df.columns = df.columns.str.strip().str.lower()
print(df.columns)

df = df[[
    "council_ref",
    "permit_number",
    "issue_date",
    "address",
    "desc_of_works",
    "estimated_cost_of_works",
    "commence_by_date",
    "completed_by_date",
    "permit_certificate_type"
]]
print(df.head())

df = df[df["address"].notna()]
df = df[df["address"] != ""]
print(len(df))

df["address"] = df["address"].str.strip()
print(df["address"].head())
