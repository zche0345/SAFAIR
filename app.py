from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
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

TRIGGERS_PATH = Path("triggers.json")

DB_CONFIG = {
    "host": "database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "tptp1515",
    "database": "iteration_1",
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
    ASTHMA_TRIGGERS = json.load(f)

logging.basicConfig(
    filename="missing_barcodes.log",
    level=logging.INFO,
    format="%(asctime)s\t%(message)s",
)


def get_db():
    return pymysql.connect(**DB_CONFIG)


def fetch_product_from_rds(barcode):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT barcode, name, brand, ingredients, source "
                "FROM products WHERE barcode = %s",
                (barcode,),
            )
            row = cur.fetchone()
    if not row:
        return None
    # MySQL JSON column comes back as a string in pymysql; decode if needed.
    ings = row["ingredients"]
    if isinstance(ings, str):
        ings = json.loads(ings)
    return {
        "name": row["name"],
        "brand": row["brand"],
        "ingredients": ings,
        "source": row["source"],
    }


def clean_ingredient(s):
    s = re.sub(r"[^\w\s-]", "", s)
    return s.strip().lower()


def decode_barcode_from_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

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


@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid barcode"}), 400

    product = fetch_product_from_rds(barcode)
    if not product:
        logging.info(f"MISS\t{barcode}")
        return jsonify({
            "barcode": barcode,
            "found": False,
            "message": "Product not in our database.",
        }), 404

    return jsonify({
        "barcode": barcode,
        "found": True,
        "product": product,
        "analysis": analyse(product["ingredients"]),
    })


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

    product = fetch_product_from_rds(barcode)
    if not product:
        logging.info(f"MISS\t{barcode}")
        return jsonify({
            "barcode": barcode,
            "found": False,
            "message": "Product not in our database.",
        }), 404

    return jsonify({
        "barcode": barcode,
        "found": True,
        "product": product,
        "analysis": analyse(product["ingredients"]),
    })


@app.route("/health")
def health():
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) AS n FROM products")
                count = cur.fetchone()["n"]
        return {
            "status": "ok",
            "products_in_db": count,
            "triggers_loaded": len(ASTHMA_TRIGGERS),
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)