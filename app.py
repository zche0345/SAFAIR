# app.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
import requests
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

TRIGGERS_PATH = Path(__file__).parent / "triggers.json"

DB_CONFIG = {
    "host": "database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "tptp1515",
    "database": "iteration_1",
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

OBF_API = "https://world.openbeautyfacts.org/api/v2/product/{}.json"
OPF_API = "https://world.openproductsfacts.org/api/v2/product/{}.json"

with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
    ASTHMA_TRIGGERS = json.load(f)

logging.basicConfig(
    filename="missing_barcodes.log",
    level=logging.INFO,
    format="%(asctime)s\t%(message)s",
)


# ---------------------------------------------------------------------------
# Risk scoring configuration
# ---------------------------------------------------------------------------

LEVEL_SCORES = {"high": 3, "medium": 1, "low": 0.3}

# Multipliers based on how a product is typically used. Aerosols and cleaners
# create higher inhalation exposure; rinse-off products are mostly washed away.
FORM_MULTIPLIERS = {
    "aerosol":   1.5,
    "cleaner":   1.3,
    "leave_on":  0.7,
    "rinse_off": 0.4,
    "unknown":   1.0,
}

ADVICE_TEMPLATES = {
    "high": {
        "aerosol":   "High inhalation risk. Avoid using this aerosol around the asthmatic family member. Apply outdoors or with strong ventilation, and wait before they re-enter the room.",
        "cleaner":   "High respiratory risk during use. Open windows, use gloves, and keep the asthmatic family member out of the room until the air clears.",
        "leave_on":  "Contains multiple known asthma triggers. Patch-test on a small area first; if any respiratory symptoms occur, switch to a fragrance-free alternative.",
        "rinse_off": "Contains known triggers but most ingredients are washed off. Ventilate the bathroom during use; consider fragrance-free options if symptoms occur.",
        "unknown":   "Multiple asthma triggers detected. Use with caution and consider fragrance-free alternatives if symptoms occur.",
    },
    "medium": {
        "aerosol":   "Moderate inhalation risk. Ventilate the room and avoid prolonged spraying near the asthmatic family member.",
        "cleaner":   "Moderate respiratory risk. Ventilate during use and avoid mixing with other cleaning products.",
        "leave_on":  "Contains some fragrance allergens. Generally safe for most users but monitor for skin or breathing reactions.",
        "rinse_off": "Mild risk during use; ingredients are largely rinsed away. Acceptable for most users.",
        "unknown":   "Some asthma-related ingredients present. Use with normal ventilation.",
    },
    "low": {
        "aerosol":   "Low risk overall, but ventilate when spraying.",
        "cleaner":   "Low risk; standard ventilation is sufficient.",
        "leave_on":  "Low risk for most users.",
        "rinse_off": "Low risk; most ingredients are rinsed off.",
        "unknown":   "Low risk based on ingredient profile.",
    },
    "none": {
        "aerosol":   "No specific asthma triggers detected, but ventilate when using any aerosol.",
        "cleaner":   "No specific asthma triggers detected in our database.",
        "leave_on":  "No known asthma triggers detected.",
        "rinse_off": "No known asthma triggers detected.",
        "unknown":   "No known asthma triggers detected in available ingredient data.",
    },
}


# ---------------------------------------------------------------------------
# Ingredient text parsing
# ---------------------------------------------------------------------------

def clean_ingredient(s):
    s = re.sub(r"[^\w\s-]", "", s)
    s = s.strip().lower()
    s = re.sub(r"\s+\d{2,}\s+\d+(\s+\d+)*$", "", s)
    return s.strip()


def is_garbage_ingredient(ing):
    # OBF data often contains marketing copy, addresses, URLs etc. mixed into
    # the ingredient field. Real INCI names are short single tokens or short
    # phrases. Anything outside that shape is not a real ingredient.
    if not ing:
        return True
    if len(ing) > 60:
        return True
    if len(ing.split()) > 5:
        return True
    bad_substrings = [
        "www", "http", "tel ", "gmbh", "ingredients", "ingredient",
        "beiersdorf", "hamburg", "wien", "basel", "lagern", "conserver",
        "geniessen", "decouvrez", "découvrez", "sensation", "fr ",
    ]
    if any(bad in ing for bad in bad_substrings):
        return True
    # Drop strings that are mostly digits (batch numbers, phone numbers).
    digits = sum(1 for c in ing if c.isdigit())
    if len(ing) > 0 and digits / len(ing) > 0.4:
        return True
    return False


def parse_ingredients_text(raw):
    # Strip marketing prefixes like "Ingredients:" / "Ingrédients:" so we keep
    # only the actual ingredient list, then split on commas/semicolons.
    if not raw:
        return []
    text = raw.replace("\n", ",").replace(";", ",")

    lower = text.lower()
    for marker in ["ingredients:", "ingredients ", "ingrédients:", "ingrédients ",
                   "zutaten:", "ingredienti:", "ingredientes:"]:
        idx = lower.rfind(marker)
        if idx >= 0:
            text = text[idx + len(marker):]
            break

    items = []
    for piece in text.split(","):
        ing = clean_ingredient(piece)
        if is_garbage_ingredient(ing):
            continue
        items.append(ing)
    return items


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    return pymysql.connect(**DB_CONFIG)


def fetch_product_from_rds(barcode):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT barcode, name, brand, categories, ingredients, source "
                "FROM products WHERE barcode = %s",
                (barcode,),
            )
            row = cur.fetchone()
    if not row:
        return None
    ings = row["ingredients"]
    if isinstance(ings, str):
        ings = json.loads(ings)
    # Filter out junk in case the DB was populated before parse_ingredients_text.
    ings = [i for i in ings if not is_garbage_ingredient(i)]
    return {
        "name": row["name"] or "",
        "brand": row["brand"] or "",
        "categories": row["categories"] or "",
        "ingredients": ings,
        "source": row["source"],
    }


def fetch_from_api(barcode):
    # Cold-start fallback: only triggered when a barcode is missing from RDS.
    # The result is persisted to RDS so subsequent lookups go to the database.
    for url, src in [(OBF_API, "OBF-API"), (OPF_API, "OPF-API")]:
        try:
            r = requests.get(
                url.format(barcode),
                timeout=5,
                headers={"User-Agent": "AsthmaSafe-Melbourne/1.0 (educational; Monash FIT5120)"},
            )
            if r.status_code != 200:
                continue
            j = r.json()
            if j.get("status") != 1:
                continue
            p = j["product"]
            ings_raw = (
                p.get("ingredients_text_en")
                or p.get("ingredients_text_fr")
                or p.get("ingredients_text_de")
                or p.get("ingredients_text")
                or ""
            )
            ings = parse_ingredients_text(ings_raw)
            if not ings:
                continue
            return {
                "name": (p.get("product_name") or "")[:500],
                "brand": (p.get("brands") or "")[:200],
                "categories": (p.get("categories") or "")[:5000],
                "ingredients": ings,
                "source": src,
            }
        except requests.RequestException:
            continue
    return None


def write_to_rds(barcode, product):
    sql = """
        INSERT INTO products (barcode, name, brand, categories, ingredients, source)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            brand = VALUES(brand),
            categories = VALUES(categories),
            ingredients = VALUES(ingredients),
            source = VALUES(source)
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (
                barcode,
                product["name"],
                product["brand"],
                product.get("categories", ""),
                json.dumps(product["ingredients"], ensure_ascii=False),
                product["source"],
            ))
        conn.commit()


def get_or_fetch_product(barcode):
    product = fetch_product_from_rds(barcode)
    if product and product["ingredients"]:
        return product, "rds"

    product = fetch_from_api(barcode)
    if product:
        try:
            write_to_rds(barcode, product)
        except Exception as e:
            logging.warning(f"WRITEBACK_FAIL\t{barcode}\t{e}")
        return product, "api"

    return None, "miss"


# ---------------------------------------------------------------------------
# Image decoding
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Risk analysis
# ---------------------------------------------------------------------------

def detect_form(product):
    # Decide product form from name + categories + brand. Drives the inhalation
    # exposure weighting in the risk score. Multilingual keywords included
    # because OBF is mostly French/German content.
    if not product:
        return "unknown"
    name = (product.get("name") or "").lower()
    cats = (product.get("categories") or "").lower()
    brand = (product.get("brand") or "").lower()
    text = name + " " + cats + " " + brand

    aerosol_kw = [
        "spray", "aerosol", "mist", "deodorant", "déodorant", "deodorante",
        "air freshener", "perfume", "eau de toilette", "eau de parfum",
        "anti-perspirant", "antiperspirant", "fragrances",
    ]
    if any(k in text for k in aerosol_kw):
        return "aerosol"

    cleaner_kw = [
        "bleach", "cleaner", "detergent", "disinfectant", "degreaser",
        "lessive", "nettoyant", "javel", "wash-up", "dishwash", "laundry",
    ]
    if any(k in text for k in cleaner_kw):
        return "cleaner"

    rinse_kw = [
        "shampoo", "shower gel", "body wash", "face wash", "cleanser",
        "soap", "shampooing", "douche", "savon", "gel douche", "shower",
    ]
    if any(k in text for k in rinse_kw):
        return "rinse_off"

    leave_on_kw = [
        "cream", "lotion", "moisturiz", "moisturis", "balm", "serum",
        "butter", "crème", "creme", "lait", "soin",
        "cosmétique", "cosmetique", "cosmetic", "skin care", "skincare",
        "face care", "body care", "hand cream", "moisturizer", "moisturiser",
    ]
    if any(k in text for k in leave_on_kw):
        return "leave_on"

    return "unknown"


def analyse(ingredients, product=None):
    hits = []
    for ing in ingredients:
        for key, info in ASTHMA_TRIGGERS.items():
            if key in ing:
                hits.append({"ingredient": ing, **info})
                break

    # Fragrance allergens often co-occur (many products list 5+ of them) but
    # represent the same underlying mechanism. Use diminishing returns within
    # the fragrance category, but stack independent risk categories normally.
    fragrance_score = 0.0
    other_score = 0.0
    fragrance_count = 0
    for h in hits:
        s = LEVEL_SCORES.get(h["level"], 0)
        if h.get("category") == "fragrance":
            if fragrance_count == 0:
                fragrance_score = s
            else:
                fragrance_score += s * 0.3
            fragrance_count += 1
        else:
            other_score += s

    raw_score = fragrance_score + other_score

    form = detect_form(product)
    multiplier = FORM_MULTIPLIERS[form]
    final_score = raw_score * multiplier

    if final_score >= 4.0:
        risk = "high"
    elif final_score >= 2.0:
        risk = "medium"
    elif final_score >= 0.5:
        risk = "low"
    else:
        risk = "none"

    advice = ADVICE_TEMPLATES[risk][form]

    return {
        "risk_level": risk,
        "risk_score": round(final_score, 2),
        "product_form": form,
        "triggers": hits,
        "advice": advice,
    }


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid barcode"}), 400

    product, origin = get_or_fetch_product(barcode)
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
        "data_origin": origin,
        "product": product,
        "analysis": analyse(product["ingredients"], product),
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

    product, origin = get_or_fetch_product(barcode)
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
        "data_origin": origin,
        "product": product,
        "analysis": analyse(product["ingredients"], product),
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