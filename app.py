# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import sqlite3
import json
import logging
import re
import io
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

app = Flask(__name__)
CORS(app)

DB_PATH = Path("cache.db")
TRIGGERS_PATH = Path("triggers.json")
OBF_API = "https://world.openbeautyfacts.org/api/v2/product/{}.json"
OPF_API = "https://world.openproductsfacts.org/api/v2/product/{}.json"

with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
    ASTHMA_TRIGGERS = json.load(f)

logging.basicConfig(
    filename="missing_barcodes.log",
    level=logging.INFO,
    format="%(asctime)s\t%(message)s",
)


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
        row = c.execute(
            "SELECT name, brand, ingredients, source FROM products WHERE barcode=?",
            (barcode,),
        ).fetchone()
    if not row:
        return None
    return {
        "name": row[0],
        "brand": row[1],
        "ingredients": json.loads(row[2]) if row[2] else [],
        "source": row[3],
    }


def cache_put(barcode, data):
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            "INSERT OR REPLACE INTO products VALUES (?,?,?,?,?)",
            (
                barcode,
                data["name"],
                data["brand"],
                json.dumps(data["ingredients"]),
                data["source"],
            ),
        )


def clean_ingredient(s):
    s = re.sub(r"[^\w\s-]", "", s)
    return s.strip().lower()


def fetch_openfacts(barcode):
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
            ings = [clean_ingredient(i) for i in ings_raw.replace("\n", ",").split(",")]
            ings = [i for i in ings if i]
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


def decode_barcode_from_image(image_bytes):
    # Decode image bytes into an OpenCV BGR array.
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    # Try at original resolution and a downscaled copy; large phone photos
    # sometimes fail at full size but succeed when scaled down.
    candidates = [bgr]
    h, w = bgr.shape[:2]
    if max(h, w) > 1600:
        scale = 1600 / max(h, w)
        candidates.append(cv2.resize(bgr, (int(w * scale), int(h * scale))))

    detector = cv2.barcode.BarcodeDetector()
    for img_arr in candidates:
        ok, decoded_info, _, _ = detector.detectAndDecodeWithType(img_arr)
        if ok and decoded_info:
            for code in decoded_info:
                if code:
                    return code

        # Try grayscale + adaptive threshold to rescue low-contrast shots.
        gray = cv2.cvtColor(img_arr, cv2.COLOR_BGR2GRAY)
        thr = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10
        )
        thr_bgr = cv2.cvtColor(thr, cv2.COLOR_GRAY2BGR)
        ok, decoded_info, _, _ = detector.detectAndDecodeWithType(thr_bgr)
        if ok and decoded_info:
            for code in decoded_info:
                if code:
                    return code

    return None


def lookup_barcode(barcode):
    # Shared logic used by /lookup and /scan.
    product = cache_get(barcode)
    cached = product is not None

    if not product:
        product = fetch_openfacts(barcode)
        if not product:
            logging.info(f"MISS\t{barcode}")
            return None, cached
        cache_put(barcode, product)

    return product, cached


@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid barcode"}), 400

    product, cached = lookup_barcode(barcode)
    if not product:
        return (
            jsonify(
                {
                    "barcode": barcode,
                    "found": False,
                    "message": "Product not in database.",
                }
            ),
            404,
        )

    result = analyse(product["ingredients"])
    return jsonify(
        {
            "barcode": barcode,
            "found": True,
            "cached": cached,
            "product": product,
            "analysis": result,
        }
    )


@app.route("/scan", methods=["POST"])
def scan():
    if "image" not in request.files:
        return jsonify({"error": "no image uploaded, expected field name 'image'"}), 400

    image_bytes = request.files["image"].read()
    if not image_bytes:
        return jsonify({"error": "empty image"}), 400

    barcode = decode_barcode_from_image(image_bytes)
    if not barcode:
        return jsonify({"error": "no barcode detected in image"}), 422

    product, cached = lookup_barcode(barcode)
    if not product:
        return (
            jsonify(
                {
                    "barcode": barcode,
                    "found": False,
                    "message": "Product not in database.",
                }
            ),
            404,
        )

    result = analyse(product["ingredients"])
    return jsonify(
        {
            "barcode": barcode,
            "found": True,
            "cached": cached,
            "product": product,
            "analysis": result,
        }
    )


@app.route("/health")
def health():
    return {"status": "ok", "triggers_loaded": len(ASTHMA_TRIGGERS)}


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5001, debug=True)