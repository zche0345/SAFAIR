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

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    _S3_OK = True
except ImportError:
    _S3_OK = False
    logging.warning("boto3 not installed; /upload_product_image endpoint will return 503")

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB; matches MAX_UPLOAD_BYTES

TRIGGERS_PATH = Path(__file__).parent / "triggers.json"
TYPICAL_PATH = Path(__file__).parent / "typical_ingredients.json"

DB_CONFIG = {
    "host": "database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "tptp1515",
    "database": "iteration_1",
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

# S3 bucket for user-uploaded product photos. One image per barcode; new
# uploads overwrite the previous one. Bucket is private — admins access via
# AWS console / CLI; the URL stored in RDS is the s3:// path, not a public URL.
S3_BUCKET = "asthmasafe-product-images"
S3_REGION = "ap-southeast-2"
S3_KEY_PREFIX = "user_uploads/"   # objects land at user_uploads/{barcode}.jpg
MAX_UPLOAD_BYTES = 5 * 1024 * 1024   # 5 MB cap per image

# Open Food Facts family — same JSON schema across all four. Order matters:
# we try them in the order most likely to have ingredient data, falling back
# to broader sources. OFF is by far the largest (~3M food items).
OFF_APIS = [
    ("https://world.openfoodfacts.org/api/v2/product/{}.json",      "OFF-API"),
    ("https://world.openbeautyfacts.org/api/v2/product/{}.json",    "OBF-API"),
    ("https://world.openproductsfacts.org/api/v2/product/{}.json",  "OPF-API"),
    ("https://world.openpetfoodfacts.org/api/v2/product/{}.json",   "OPFF-API"),
]

# UPCitemdb free tier: no API key, ~100 lookups/day per IP. Returns product
# name/brand/category but NOT ingredients — used purely to enable the
# typical-ingredients fallback when OFF family has nothing.
UPCITEMDB_API = "https://api.upcitemdb.com/prod/trial/lookup?upc={}"

with open(TRIGGERS_PATH, "r", encoding="utf-8") as f:
    ASTHMA_TRIGGERS = json.load(f)

with open(TYPICAL_PATH, "r", encoding="utf-8") as f:
    TYPICAL_INGREDIENTS = json.load(f)

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
    "food":      0.3,   # ingestion-only, no inhalation exposure
    "unknown":   1.0,
}

ADVICE_TEMPLATES = {
    "high": {
        "aerosol":   "High inhalation risk. Avoid using this aerosol around the asthmatic family member. Apply outdoors or with strong ventilation, and wait before they re-enter the room.",
        "cleaner":   "High respiratory risk during use. Open windows, use gloves, and keep the asthmatic family member out of the room until the air clears.",
        "leave_on":  "Contains multiple known asthma triggers. Patch-test on a small area first; if any respiratory symptoms occur, switch to a fragrance-free alternative.",
        "rinse_off": "Contains known triggers but most ingredients are washed off. Ventilate the bathroom during use; consider fragrance-free options if symptoms occur.",
        "food":      "Contains multiple food additives that may trigger asthma in sensitive individuals (especially sulfites). Check the label carefully; if the asthmatic family member is sulfite-sensitive, consider avoiding this product.",
        "unknown":   "Multiple asthma triggers detected. Use with caution and consider fragrance-free alternatives if symptoms occur.",
    },
    "medium": {
        "aerosol":   "Moderate inhalation risk. Ventilate the room and avoid prolonged spraying near the asthmatic family member.",
        "cleaner":   "Moderate respiratory risk. Ventilate during use and avoid mixing with other cleaning products.",
        "leave_on":  "Contains some fragrance allergens. Generally safe for most users but monitor for skin or breathing reactions.",
        "rinse_off": "Mild risk during use; ingredients are largely rinsed away. Acceptable for most users.",
        "food":      "Contains some food additives (colourants, preservatives, MSG, sulfites) that may trigger asthma in sensitive users. Check label if the family member is known to react to specific additives.",
        "unknown":   "Some asthma-related ingredients present. Use with normal ventilation.",
    },
    "low": {
        "aerosol":   "Low risk overall, but ventilate when spraying.",
        "cleaner":   "Low risk; standard ventilation is sufficient.",
        "leave_on":  "Low risk for most users.",
        "rinse_off": "Low risk; most ingredients are rinsed off.",
        "food":      "Low risk for most users; contains common food additives.",
        "unknown":   "Low risk based on ingredient profile.",
    },
    "none": {
        "aerosol":   "No specific asthma triggers detected, but ventilate when using any aerosol.",
        "cleaner":   "No specific asthma triggers detected in our database.",
        "leave_on":  "No known asthma triggers detected.",
        "rinse_off": "No known asthma triggers detected.",
        "food":      "No known asthma-related food additives detected.",
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


def _fetch_off_family(barcode):
    # Try all four Open Food Facts family databases. Returns the first hit
    # that has either ingredients OR at least a product name (so the typical
    # fallback has something to classify on).
    headers = {"User-Agent": "AsthmaSafe-Melbourne/1.0 (educational; Monash FIT5120)"}

    best_metadata_only = None  # remember a name-only hit in case nothing has ingredients

    for url, src in OFF_APIS:
        try:
            r = requests.get(url.format(barcode), timeout=5, headers=headers)
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
            name = (p.get("product_name") or "")[:500]
            brand = (p.get("brands") or "")[:200]
            cats = (p.get("categories") or "")[:5000]

            if ings:
                # Best case: full data, return immediately.
                return {
                    "name": name, "brand": brand, "categories": cats,
                    "ingredients": ings, "source": src,
                }
            if (name or brand or cats) and best_metadata_only is None:
                # Hit but no ingredients — keep as fallback in case nothing
                # else has ingredients either.
                best_metadata_only = {
                    "name": name, "brand": brand, "categories": cats,
                    "ingredients": [], "source": src,
                }
        except requests.RequestException:
            continue

    return best_metadata_only


def _fetch_upcitemdb(barcode):
    # UPCitemdb has no ingredients but covers many North American / Asian
    # products that OFF family misses. Used purely to give the typical
    # fallback a product name/category to classify on.
    try:
        r = requests.get(
            UPCITEMDB_API.format(barcode),
            timeout=5,
            headers={"User-Agent": "AsthmaSafe-Melbourne/1.0"},
        )
        if r.status_code != 200:
            return None
        j = r.json()
        items = j.get("items") or []
        if not items:
            return None
        item = items[0]
        name = (item.get("title") or "")[:500]
        brand = (item.get("brand") or "")[:200]
        cats = (item.get("category") or "")[:5000]
        if not (name or brand or cats):
            return None
        return {
            "name": name, "brand": brand, "categories": cats,
            "ingredients": [], "source": "UPCitemdb",
        }
    except requests.RequestException:
        return None


def fetch_from_api(barcode):
    # Cold-start fallback: only triggered when a barcode is missing from RDS.
    # Tries OFF family (food, beauty, products, pet food) first, then
    # UPCitemdb for general product metadata. The result — even if it lacks
    # ingredients — is persisted to RDS so the typical fallback can run on
    # subsequent lookups without another API roundtrip.
    product = _fetch_off_family(barcode)
    if product:
        return product

    product = _fetch_upcitemdb(barcode)
    if product:
        return product

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
    rds_product = fetch_product_from_rds(barcode)
    if rds_product and rds_product["ingredients"]:
        return rds_product, "rds"

    api_product = fetch_from_api(barcode)
    if api_product:
        try:
            write_to_rds(barcode, api_product)
        except Exception as e:
            logging.warning(f"WRITEBACK_FAIL\t{barcode}\t{e}")
        origin = "api" if api_product.get("ingredients") else "api_no_ingredients"
        return api_product, origin

    # No real ingredients available anywhere. If RDS at least has product
    # metadata (name/brand/categories), return that so the caller can still
    # classify the product and surface typical ingredients for its category.
    if rds_product:
        return rds_product, "rds_no_ingredients"

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
    # because OBF/OFF are mostly French/German content.
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
        "shampoo", "shower gel", "body wash", "face wash",
        "shampooing", "gel douche", "shower",
    ]
    if any(k in text for k in rinse_kw):
        return "rinse_off"

    # Food / beverage — checked before leave_on because some food terms
    # (butter, cream, lait) overlap with cosmetic terms.
    food_kw = [
        "chocolate", "chocolat", "biscuit", "cookie", "cereal", "céréales",
        "yogurt", "yoghurt", "yaourt", "snack", "candy", "sweets", "bonbon",
        "juice", "jus de fruit", "soda", "cola", "lemonade", "wine", "vin",
        "beer", "bière", "coffee", "café", "tea", "thé", "milk", "lait",
        "cheese", "fromage", "bread", "pain", "pasta", "pâtes", "noodle",
        "sausage", "ham", "bacon", "salami", "ketchup", "mayonnaise",
        "sauce", "spread", "tartiner", "nutella", "ferrero", "kinder",
        "haribo", "raisins", "snacks", "groceries", "food", "aliment",
    ]
    if any(k in text for k in food_kw):
        return "food"

    leave_on_kw = [
        "moisturiz", "moisturis", "balm", "serum",
        "body butter", "body cream", "face cream", "hand cream",
        "crème visage", "creme visage", "crème corps", "creme corps",
        "cosmétique", "cosmetique", "cosmetic", "skin care", "skincare",
        "face care", "body care", "moisturizer", "moisturiser",
        "lotion", "soin",
    ]
    if any(k in text for k in leave_on_kw):
        return "leave_on"

    return "unknown"


def detect_subcategory(product):
    # Finer-grained category for the typical-ingredients fallback. Returns a key
    # into TYPICAL_INGREDIENTS, or None if no specific match was found (caller
    # should then fall back to form-level lookup).
    if not product:
        return None
    text = " ".join([
        (product.get("name") or "").lower(),
        (product.get("categories") or "").lower(),
        (product.get("brand") or "").lower(),
    ])

    # Order matters: more specific keywords come first. Generic terms like
    # "spray" or "cleaner" come last so they don't capture more specific items.
    rules = [
        # --- Hair ---
        ("hair_bleach",          ["hair bleach", "bleach powder", "decolorant"]),
        ("hair_dye",             ["hair dye", "hair colour", "hair color", "coloration"]),
        ("hair_spray",           ["hair spray", "hairspray", "laque"]),
        ("conditioner",          ["conditioner", "après-shampooing", "apres-shampooing",
                                  "hair mask", "hair conditioner"]),
        ("shampoo",              ["shampoo", "shampooing"]),

        # --- Personal care: skin / body ---
        ("nail_polish_remover",  ["nail polish remover", "nail varnish remover",
                                  "dissolvant"]),
        ("nail_polish",          ["nail polish", "nail varnish", "vernis"]),
        ("hand_sanitizer",       ["hand sanitiz", "hand sanitis", "antibacterial gel",
                                  "gel hydroalcoolique"]),
        ("baby_wipes",           ["baby wipe", "baby wet"]),
        ("wet_wipes",            ["wet wipe", "moist wipe", "cleansing wipe", "lingette"]),
        ("baby_lotion",          ["baby lotion", "baby cream", "baby moisturiz"]),
        ("sunscreen",            ["sunscreen", "sun cream", "sunblock", "spf",
                                  "crème solaire", "creme solaire"]),
        ("shaving_cream",        ["shaving cream", "shaving foam", "shaving gel",
                                  "mousse à raser", "after shave"]),
        ("perfume",              ["perfume", "eau de toilette", "eau de parfum",
                                  "eau de cologne", "fragrance mist", "cologne"]),
        ("deodorant",            ["deodorant", "déodorant", "deodorante",
                                  "anti-perspirant", "antiperspirant"]),
        ("hand_soap",            ["hand soap", "hand wash", "savon main",
                                  "savon liquide"]),
        ("face_cleanser",        ["face wash", "face cleanser", "facial cleanser",
                                  "face foam", "nettoyant visage", "micellar"]),
        ("body_wash",            ["shower gel", "body wash", "gel douche",
                                  "shower cream", "douche"]),
        ("soap_bar",             ["soap bar", "bar soap", "savon"]),
        ("face_cream",           ["face cream", "day cream", "night cream",
                                  "moisturiz", "moisturis", "face moisturiser",
                                  "crème visage", "creme visage", "anti-aging cream",
                                  "anti-wrinkle"]),
        ("body_lotion",          ["body lotion", "hand cream", "body cream",
                                  "body butter", "body milk", "lait corps",
                                  "crème corps", "creme corps"]),

        # --- Makeup ---
        ("makeup_foundation",    ["foundation", "fond de teint", "bb cream", "cc cream"]),
        ("lipstick",             ["lipstick", "lip balm", "lip gloss", "rouge à lèvres"]),
        ("mascara",              ["mascara", "eyeliner", "eye liner"]),

        # --- Oral ---
        ("denture_cleaner",      ["denture cleaner", "denture tablet"]),
        ("mouthwash",            ["mouthwash", "mouth rinse", "bain de bouche"]),
        ("toothpaste",           ["toothpaste", "dentifrice"]),

        # --- Household cleaning ---
        ("oven_cleaner",         ["oven cleaner", "grill cleaner",
                                  "nettoyant four"]),
        ("drain_cleaner",        ["drain cleaner", "drain unblock", "déboucheur"]),
        ("toilet_cleaner",       ["toilet cleaner", "toilet bowl", "wc cleaner",
                                  "nettoyant wc", "nettoyant toilette"]),
        ("bathroom_cleaner",     ["bathroom cleaner", "shower cleaner",
                                  "salle de bain"]),
        ("glass_cleaner",        ["glass cleaner", "window cleaner", "vitres"]),
        ("bleach",               ["bleach", "javel", "eau de javel", "chlorine bleach"]),
        ("rinse_aid",            ["rinse aid", "rinse agent", "liquide de rinçage"]),
        ("dishwasher_tablet",    ["dishwasher tablet", "dishwasher capsule",
                                  "lave-vaisselle"]),
        ("dishwash",             ["dishwash", "dish soap", "washing-up",
                                  "wash-up", "liquide vaisselle"]),
        ("fabric_softener",      ["fabric softener", "fabric conditioner",
                                  "assouplissant"]),
        ("stain_remover",        ["stain remover", "détachant"]),
        ("carpet_cleaner",       ["carpet cleaner", "carpet shampoo",
                                  "nettoyant tapis"]),
        ("laundry_powder",       ["laundry powder", "washing powder", "lessive poudre"]),
        ("laundry_detergent",    ["laundry", "lessive", "fabric detergent",
                                  "washing liquid"]),
        ("multipurpose_spray",   ["multi-purpose", "multipurpose", "all-purpose",
                                  "all purpose"]),
        ("surface_cleaner",      ["surface cleaner", "multi-surface",
                                  "nettoyant", "kitchen cleaner"]),

        # --- Air / pesticides ---
        ("plug_in_air_freshener", ["plug-in", "plug in air", "diffuser refill"]),
        ("car_air_freshener",    ["car air freshener", "car perfume", "désodorisant voiture"]),
        ("air_freshener",        ["air freshener", "désodorisant", "room spray",
                                  "room freshener"]),
        ("scented_candle",       ["scented candle", "bougie parfumée"]),
        ("incense",              ["incense", "encens"]),
        ("mosquito_repellent",   ["mosquito repellent", "insect repellent",
                                  "anti-moustique", "bug spray"]),
        ("insect_spray",         ["insecticide", "insect killer", "bug killer",
                                  "raid", "anti-insecte", "fly spray"]),

        # --- DIY ---
        ("polyurethane_foam",    ["polyurethane foam", "expanding foam",
                                  "mousse polyuréthane"]),
        ("contact_cement",       ["contact cement", "contact adhesive", "néoprène"]),
        ("adhesive_glue",        ["glue", "adhesive", "colle"]),
        ("wood_varnish",         ["varnish", "wood stain", "vernis bois", "lacquer"]),
        ("spray_paint",          ["spray paint", "aerosol paint", "peinture aérosol"]),
        ("paint",                ["paint", "primer", "peinture", "emulsion"]),

        # --- Automotive ---
        ("tire_shine",           ["tire shine", "tyre shine", "brillant pneu"]),
        ("car_wash",             ["car wash", "car shampoo", "shampoing voiture",
                                  "car cleaner"]),

        # --- Food packaging / plastics ---
        ("canned_food_lining",   ["canned food", "tin can", "conserve"]),
        ("food_packaging_film",  ["packaging film", "cling film", "food wrap",
                                  "film alimentaire"]),
        ("food_container",       ["food container", "tupperware", "lunch box",
                                  "boîte alimentaire"]),
        ("plastic_bottle",       ["plastic bottle", "pet bottle", "bouteille plastique"]),

        # --- Processed food (specific items first to avoid keyword collisions) ---
        ("chocolate_spread",     ["chocolate spread", "hazelnut spread", "nutella",
                                  "pâte à tartiner"]),
        ("chocolate_confectionery", ["chocolate", "chocolat", "praline", "truffle",
                                  "ferrero", "kinder", "bonbon chocolat"]),
        ("biscuit_cookie",       ["biscuit", "cookie", "cracker", "wafer",
                                  "shortbread", "digestive"]),
        ("breakfast_cereal",     ["cereal", "cornflakes", "muesli", "granola",
                                  "céréales"]),
        ("dried_fruit",          ["dried fruit", "dried apricot", "dried mango",
                                  "raisins", "fruits secs"]),
        ("wine",                 [" wine", "red wine", "white wine", "rosé wine",
                                  "vin rouge", "vin blanc", "vin rosé"]),
        ("processed_meat",       ["sausage", "ham", "bacon", "salami", "charcuterie",
                                  "hot dog", "deli meat", "cured meat"]),
        ("juice_drink",          ["juice", "jus de fruit", "fruit drink",
                                  "nectar"]),
        ("soft_drink",           ["soft drink", "soda", "coca-cola", "pepsi",
                                  "lemonade", "boisson gazeuse", "energy drink",
                                  "carbonated drink"]),
        ("coffee_tea",           ["coffee", "café", " tea", "thé", "espresso"]),
        ("packaged_bread",       ["sliced bread", "white bread", "wholemeal bread",
                                  "pain de mie", "toast bread"]),
        ("instant_noodles",      ["instant noodle", "ramen", "cup noodle",
                                  "nouilles instantanées"]),
        ("yogurt",               ["yogurt", "yoghurt", "yaourt"]),
        ("cheese_processed",     ["cheese spread", "processed cheese", "cheese slice",
                                  "fromage fondu"]),
        ("dairy_product",        ["milk", "cream", "butter", "lait",
                                  "crème laitière"]),
        ("sauce_condiment",      ["ketchup", "mayonnaise", "mustard", "sauce",
                                  "dressing", "soy sauce"]),
        ("candy_sweet",          ["candy", "sweets", "lollipop", "gummy",
                                  "marshmallow", "bonbon", "haribo"]),
        ("snack_food",           ["chips", "crisps", "snack", "pretzel",
                                  "popcorn"]),
    ]
    for key, kws in rules:
        if any(k in text for k in kws):
            return key
    return None


def get_typical_ingredients(product):
    # Returns (ingredients_list, category_label). Used when we can't get real
    # ingredients for this barcode but still want to show the user what is
    # *commonly* found in this product type.
    sub = detect_subcategory(product)
    if sub and sub in TYPICAL_INGREDIENTS:
        return TYPICAL_INGREDIENTS[sub], sub

    form = detect_form(product)
    fallback = TYPICAL_INGREDIENTS.get("_form_fallback", {})
    return fallback.get(form, fallback.get("unknown", [])), form


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

def _typical_response(barcode, product):
    # Build the fallback response when we don't have real ingredients for this
    # specific barcode. We classify the product using its name/brand/categories
    # and return typical ingredients for that category, with triggers flagged.
    #
    # IMPORTANT: this is only called when we have *some* product metadata to
    # classify on. Callers must check classifiability first; we double-check
    # here as a safety net and 404 if classification would be meaningless.
    sub = detect_subcategory(product)
    form = detect_form(product)
    if sub is None and form == "unknown":
        # We have no basis to classify this product. Returning a generic
        # ingredient list would be misleading; tell the user we don't know.
        return jsonify({
            "barcode": barcode,
            "found": product is not None,
            "ingredients_source": "none",
            "message": (
                "Product found but we cannot determine what category it belongs to, "
                "so we have no ingredient information to show."
                if product else
                "Product not in our database."
            ),
        }), 404

    typical, category = get_typical_ingredients(product)

    # Mark which of the typical ingredients are asthma triggers by reusing
    # the same matching logic as analyse(), so the frontend can highlight them.
    annotated = []
    for ing in typical:
        match = None
        for key, info in ASTHMA_TRIGGERS.items():
            if key.startswith("_"):
                continue
            if key in ing:
                match = info
                break
        item = {"ingredient": ing, "is_trigger": match is not None}
        if match:
            item.update(match)
        annotated.append(item)

    analysis = analyse(typical, product)
    # Override advice so the user knows this is a category-level estimate, not
    # an analysis of the actual product they scanned.
    analysis["advice"] = (
        "We don't have ingredient data for this specific product. "
        "The list below shows ingredients commonly found in this product type "
        f"({category}); flagged items are known asthma triggers. "
        "Treat this as general guidance, not a product-specific analysis."
    )
    analysis["is_estimate"] = True

    payload = {
        "barcode": barcode,
        "found": product is not None,
        "ingredients_source": "typical",
        "category": category,
        "typical_ingredients": annotated,
        "analysis": analysis,
    }
    if product:
        payload["product"] = {
            "name": product.get("name", ""),
            "brand": product.get("brand", ""),
            "categories": product.get("categories", ""),
        }
    return jsonify(payload), 200


@app.route("/lookup", methods=["GET"])
def lookup():
    barcode = request.args.get("barcode", "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid barcode"}), 400

    product, origin = get_or_fetch_product(barcode)
    if not product:
        # Barcode is not in RDS and the upstream APIs (OBF/OPF) don't have it
        # either. We have no product name, no brand, no categories — there is
        # nothing meaningful to return.
        logging.info(f"MISS\t{barcode}")
        return jsonify({
            "barcode": barcode,
            "found": False,
            "ingredients_source": "none",
            "message": "Product not in our database.",
        }), 404

    if not product.get("ingredients"):
        # We have product metadata but no ingredients. Try to classify and
        # show typical ingredients for the category. _typical_response will
        # itself 404 if classification fails.
        logging.info(f"NO_INGREDIENTS\t{barcode}")
        return _typical_response(barcode, product=product)

    return jsonify({
        "barcode": barcode,
        "found": True,
        "data_origin": origin,
        "ingredients_source": "actual",
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
            "ingredients_source": "none",
            "message": "Product not in our database.",
        }), 404

    if not product.get("ingredients"):
        logging.info(f"NO_INGREDIENTS\t{barcode}")
        return _typical_response(barcode, product=product)

    return jsonify({
        "barcode": barcode,
        "found": True,
        "data_origin": origin,
        "ingredients_source": "actual",
        "product": product,
        "analysis": analyse(product["ingredients"], product),
    })


@app.route("/upload_product_image", methods=["POST"])
def upload_product_image():
    # User-uploaded product photo for barcodes where we don't have ingredient
    # data. The image is stored in S3 (one per barcode, overwriting any
    # previous upload), and the S3 URI is recorded against the product row in
    # RDS so an admin can review uploads later and fill in ingredients
    # manually.
    #
    # Frontend should call this whenever ingredients_source != "actual"
    # from /lookup or /scan.
    if not _S3_OK:
        return jsonify({"error": "Image upload not available on this server"}), 503

    barcode = (request.form.get("barcode") or "").strip()
    if not barcode.isdigit() or not (8 <= len(barcode) <= 14):
        return jsonify({"error": "invalid or missing barcode"}), 400

    if "image" not in request.files:
        return jsonify({"error": "no image uploaded, expected field name 'image'"}), 400
    file_storage = request.files["image"]
    image_bytes = file_storage.read()
    if not image_bytes:
        return jsonify({"error": "empty image"}), 400
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        return jsonify({"error": f"image too large (max {MAX_UPLOAD_BYTES // (1024*1024)} MB)"}), 413

    # Validate it's an actual image (not someone POSTing a .exe with an
    # image filename). Sniff with PIL.
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        fmt = (img.format or "").lower()
    except Exception:
        return jsonify({"error": "uploaded file is not a valid image"}), 422

    # Map PIL format to a sensible extension and content type
    ext_map = {"jpeg": ("jpg", "image/jpeg"),
               "png":  ("png", "image/png"),
               "webp": ("webp", "image/webp")}
    if fmt not in ext_map:
        return jsonify({"error": f"unsupported image format '{fmt}'; use JPG/PNG/WebP"}), 422
    ext, content_type = ext_map[fmt]

    s3_key = f"{S3_KEY_PREFIX}{barcode}.{ext}"
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"

    # Upload — uses default credential chain (IAM role on EC2/Lambda, or
    # ~/.aws/credentials locally). Overwrites any previous upload for this
    # barcode, which is the intended behaviour.
    try:
        s3 = boto3.client("s3", region_name=S3_REGION)
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=image_bytes,
            ContentType=content_type,
            Metadata={"barcode": barcode},
        )
    except (BotoCoreError, ClientError) as e:
        logging.warning(f"S3_UPLOAD_FAIL\t{barcode}\t{e}")
        return jsonify({"error": f"failed to store image: {e}"}), 502

    # Update RDS: preserve any existing metadata, just add image_url. If the
    # product row doesn't exist yet (cold-start barcode), create a stub row
    # so admins can find it later.
    try:
        existing = fetch_product_from_rds(barcode)
        if existing:
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE products SET image_url=%s WHERE barcode=%s",
                        (s3_uri, barcode),
                    )
                conn.commit()
        else:
            stub = {
                "name": "",
                "brand": "",
                "categories": "",
                "ingredients": [],
                "source": "user_upload",
            }
            write_to_rds(barcode, stub)
            with get_db() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE products SET image_url=%s WHERE barcode=%s",
                        (s3_uri, barcode),
                    )
                conn.commit()
    except Exception as e:
        # The image is already in S3 — log the DB failure but tell the user
        # success, since the photo isn't lost.
        logging.warning(f"IMAGE_URL_WRITEBACK_FAIL\t{barcode}\t{e}")

    logging.info(f"IMAGE_UPLOAD_OK\t{barcode}\t{len(image_bytes)} bytes")

    return jsonify({
        "barcode": barcode,
        "uploaded": True,
        "image_stored": True,
        "message": (
            "Thanks — your photo has been saved. We'll review it and add the "
            "ingredient information for this product as soon as we can."
        ),
    }), 200



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
            "typical_categories": len(TYPICAL_INGREDIENTS) - 1,  # minus _form_fallback
            "image_upload_available": _S3_OK,
        }
    except Exception as e:
        return {"status": "degraded", "error": str(e)}, 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)