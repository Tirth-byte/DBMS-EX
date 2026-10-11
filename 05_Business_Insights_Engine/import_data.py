import os
from decimal import Decimal
from pathlib import Path

import pandas as pd
import psycopg


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "Online Retail.xlsx"


def connection_settings():
    user = os.getenv("PGUSER")
    if not user:
        raise RuntimeError("Set PGUSER before importing the dataset.")
    return {
        "host": os.getenv("PGHOST", "127.0.0.1"),
        "port": int(os.getenv("PGPORT", "5432")),
        "dbname": os.getenv("PGDATABASE", "retail_db"),
        "user": user,
        "password": os.getenv("PGPASSWORD", ""),
    }


def optional_text(value):
    if pd.isna(value):
        return None
    return str(value)


def optional_customer(value):
    if pd.isna(value):
        return None
    return int(float(value))


def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    frame = pd.read_excel(
        DATA_FILE,
        dtype={"InvoiceNo": "string", "StockCode": "string", "Description": "string"},
    )
    expected_columns = [
        "InvoiceNo", "StockCode", "Description", "Quantity",
        "InvoiceDate", "UnitPrice", "CustomerID", "Country",
    ]
    if list(frame.columns) != expected_columns:
        raise RuntimeError("The Excel columns do not match the official Online Retail dataset.")

    with psycopg.connect(**connection_settings()) as connection:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE order_items, invoices, products, customers, raw_retail RESTART IDENTITY CASCADE")
            with cursor.copy(
                "COPY raw_retail (invoice_no, stock_code, description, quantity, invoice_date, unit_price, customer_id, country) FROM STDIN"
            ) as copy:
                for row in frame.itertuples(index=False, name=None):
                    copy.write_row(
                        (
                            str(row[0]),
                            str(row[1]),
                            optional_text(row[2]),
                            int(row[3]),
                            row[4].to_pydatetime(),
                            Decimal(str(row[5])),
                            optional_customer(row[6]),
                            str(row[7]),
                        )
                    )

            cursor.execute(
                """
                WITH ranked AS (
                    SELECT customer_id, BTRIM(country) AS country,
                           ROW_NUMBER() OVER (
                               PARTITION BY customer_id
                               ORDER BY COUNT(*) DESC, BTRIM(country)
                           ) AS position
                    FROM raw_retail
                    WHERE customer_id IS NOT NULL
                    GROUP BY customer_id, BTRIM(country)
                )
                INSERT INTO customers (customer_id, country)
                SELECT customer_id, country FROM ranked WHERE position = 1
                """
            )
            cursor.execute(
                """
                WITH codes AS (
                    SELECT DISTINCT stock_code FROM raw_retail
                ), ranked AS (
                    SELECT stock_code, NULLIF(BTRIM(description), '') AS description,
                           ROW_NUMBER() OVER (
                               PARTITION BY stock_code
                               ORDER BY COUNT(*) DESC, NULLIF(BTRIM(description), '')
                           ) AS position
                    FROM raw_retail
                    WHERE NULLIF(BTRIM(description), '') IS NOT NULL
                    GROUP BY stock_code, NULLIF(BTRIM(description), '')
                )
                INSERT INTO products (stock_code, description)
                SELECT codes.stock_code, ranked.description
                FROM codes
                LEFT JOIN ranked
                  ON ranked.stock_code = codes.stock_code AND ranked.position = 1
                """
            )
            cursor.execute(
                """
                INSERT INTO invoices (invoice_no, customer_id, invoice_date, country, is_cancelled)
                SELECT invoice_no,
                       MAX(customer_id),
                       MIN(invoice_date),
                       MIN(BTRIM(country)),
                       invoice_no LIKE 'C%'
                FROM raw_retail
                GROUP BY invoice_no
                """
            )
            cursor.execute(
                """
                INSERT INTO order_items (item_id, invoice_no, stock_code, quantity, unit_price)
                SELECT raw_id, invoice_no, stock_code, quantity, unit_price
                FROM raw_retail
                ORDER BY raw_id
                """
            )

            cursor.execute(
                """
                SELECT
                    (SELECT COUNT(*) FROM raw_retail),
                    (SELECT COUNT(*) FROM order_items),
                    (SELECT COUNT(*) FROM raw_retail WHERE customer_id IS NULL),
                    (SELECT COUNT(*) FROM raw_retail WHERE description IS NULL),
                    (SELECT COUNT(*) FROM raw_retail WHERE invoice_no LIKE 'C%'),
                    (SELECT COUNT(*) FROM raw_retail WHERE quantity <= 0),
                    (SELECT COUNT(*) FROM raw_retail WHERE unit_price <= 0)
                """
            )
            counts = cursor.fetchone()

    print(f"Raw rows: {counts[0]}")
    print(f"Imported order items: {counts[1]}")
    print(f"Excluded rows: {counts[0] - counts[1]}")
    print(f"Rows with missing customer: {counts[2]}")
    print(f"Rows with missing description: {counts[3]}")
    print(f"Cancellation rows: {counts[4]}")
    print(f"Rows with non-positive quantity: {counts[5]}")
    print(f"Rows with non-positive price: {counts[6]}")


if __name__ == "__main__":
    main()
