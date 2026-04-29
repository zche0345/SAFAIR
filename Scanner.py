# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import sqlite3
import json
from pathlib import Path
import re

app = Flask(__name__)
CORS(app)

DB_PATH = Path("cache.db")
OBF_API = "https://world.openbeautyfacts.org/api/v2/product/{}.json"
OPF_API = "https://world.openproductsfacts.org/api/v2/product/{}.json"

# 哮喘触发成分库（INCI 名 / 通用名 → 风险等级 + 说明）
ASTHMA_TRIGGERS = {
    "parfum": {"level": "high", "category": "fragrance",
               "note": "Synthetic fragrance mix; common asthma trigger."},
    "fragrance": {"level": "high", "category": "fragrance",
                  "note": "Fragrance blends often contain VOCs that trigger bronchospasm."},
    "limonene": {"level": "medium", "category": "fragrance",
                 "note": "Citrus terpene; oxidises into respiratory irritants."},
    "linalool": {"level": "medium", "category": "fragrance",
                 "note": "Common fragrance allergen, can trigger airway inflammation."},
    "formaldehyde": {"level": "high", "category": "voc",
                     "note": "Known respiratory irritant and asthma trigger."},
    "quaternium-15": {"level": "high", "category": "voc",
                      "note": "Releases formaldehyde over time."},
    "dmdm hydantoin": {"level": "high", "category": "voc",
                       "note": "Formaldehyde releaser."},
    "benzalkonium chloride": {"level": "high", "category": "quat",
                              "note": "Quaternary ammonium disinfectant; strong occupational asthma link."},
    "didecyldimonium chloride": {"level": "high", "category": "quat",
                                 "note": "Quat disinfectant; respiratory sensitiser."},
    "sodium hypochlorite": {"level": "high", "category": "irritant",
                            "note": "Bleach; releases chlorine gas, severe asthma trigger."},
    "ammonia": {"level": "high", "category": "irritant",
                "note": "Strong airway irritant."},
    "methylisothiazolinone": {"level": "medium", "category": "preservative",
                              "note": "Preservative linked to airway sensitisation."},
    "cocamidopropyl betaine": {"level": "low", "category": "surfactant",
                               "note": "Mild surfactant; rare trigger but possible in sensitive users."},
    "sodium lauryl sulfate": {"level": "low", "category": "surfactant",
                              "note": "Aerosolised SLS may irritate airways."},
}


def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            brand TEXT,
            ingredients TEXT,
            source TEXT
        )""")


def cache_get(barcode):
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT name, brand, ingredients, source FROM products WHERE barcode=?",
                        (barcode,)).fetchone()
    if not row:
        return None
    return {"name": row[0], "brand": row[1],
            "ingredients": json.loads(row[2]) if row[2] else [],
            "source": row[3]}


def cache_put(barcode, data):
    with sqlite3.connect(DB_PATH) as c:
        c.execute("INSERT OR REPLACE INTO products VALUES (?,?,?,?,?)",
                  (barcode, data["name"], data["brand"],
                   json.dumps(data["ingredients"]), data["source"]))


def fetch_openfacts(barcode):
    """先查 Open Beauty Facts，再查 Open Products Facts。"""
    for url, src in [(OBF_API, "OBF"), (OPF_API, "OPF")]:
        try:
            r = requests.get(url.format(barcode), timeout=5)
            if r.status_code != 200:
                continue
            j = r.json()
            if j.get("status") != 1:
                continue
            p = j["product"]
            ings_raw = p.get("ingredients_text_en") or p.get("ingredients_text") or ""
            ings = [re.sub(r'[^\w\s-]', '', i).strip().lower() for i in ings_raw.replace("\n", ",").split(",") if i.strip()]
            return {
                "name": p.get("product_name") or "Unknown",
                "brand": p.get("brands") or "",
                "ingredients": ings,
                "source": src,
            }
        except requests.RequestException:
            continue
    return None


def analyse(ingredients):
    """匹配成分到哮喘触发物表。"""
    hits = []
    for ing in ingredients:
        for key, info in ASTHMA_TRIGGERS.items():
            if key in ing:
                hits.append({"ingredient": ing, **info})
                break

    if any(h["level"] == "high" for h in hits):
        risk = "high"
    elif any(h["level"] == "medium" for h in hits):
        risk = "medium"
    elif hits:
        risk = "low"
    else:
        risk = "none"

    advice = {
        "high": "Avoid use around the asthmatic teen. Consider fragrance-free alternatives and ensure strong ventilation if exposure is unavoidable.",
        "medium": "Use with caution. Ventilate the room and keep the asthmatic family member out during application.",
        "low": "Generally low risk, but monitor for individual sensitivity.",
        "none": "No known asthma triggers detected in available ingredient data.",
    }[risk]

    return {"risk_level": risk, "triggers": hits, "advice": advice}


@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid barcode"}), 400

    product = cache_get(barcode)
    cached = product is not None

    if not product:
        product = fetch_openfacts(barcode)
        if not product:
            return jsonify({"barcode": barcode, "found": False,
                            "message": "Product not in database. Local supplement DB needed."}), 404
        cache_put(barcode, product)

    result = analyse(product["ingredients"])
    return jsonify({
        "barcode": barcode,
        "found": True,
        "cached": cached,
        "product": product,
        "analysis": result,
    })


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)