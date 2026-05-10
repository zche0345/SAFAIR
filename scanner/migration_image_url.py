"""Migration: add image_url column to products table.

Run once:
    python migration_image_url.py

Safe to re-run — it checks whether the column / index already exists before
making changes.
"""

import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host": "database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "admin",
    "password": "tptp1515",
    "database": "iteration_1",
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}


def column_exists(cur, table, column):
    cur.execute(
        """
        SELECT COUNT(*) AS n FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (DB_CONFIG["database"], table, column),
    )
    return cur.fetchone()["n"] > 0


def index_exists(cur, table, index_name):
    cur.execute(
        """
        SELECT COUNT(*) AS n FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND INDEX_NAME = %s
        """,
        (DB_CONFIG["database"], table, index_name),
    )
    return cur.fetchone()["n"] > 0


def main():
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cur:
            # 1. Add image_url column if missing
            if column_exists(cur, "products", "image_url"):
                print("[skip] products.image_url already exists")
            else:
                cur.execute(
                    "ALTER TABLE products "
                    "ADD COLUMN image_url VARCHAR(500) NULL AFTER source"
                )
                print("[ok]   added column products.image_url")

            # 2. Add index for admin queries that filter by image presence
            if index_exists(cur, "products", "idx_products_image_url"):
                print("[skip] index idx_products_image_url already exists")
            else:
                cur.execute(
                    "CREATE INDEX idx_products_image_url "
                    "ON products(image_url)"
                )
                print("[ok]   created index idx_products_image_url")

        conn.commit()

        # 3. Verify the result
        with conn.cursor() as cur:
            cur.execute("DESCRIBE products")
            cols = cur.fetchall()
            print("\nCurrent products table schema:")
            for c in cols:
                print(f"  {c['Field']:20s} {c['Type']:20s} {'NULL' if c['Null']=='YES' else 'NOT NULL'}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()