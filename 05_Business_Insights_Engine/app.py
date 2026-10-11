import csv
import io
import os
from datetime import date
from decimal import Decimal
from time import perf_counter

import psycopg
from flask import Flask, Response, jsonify, render_template, request
from psycopg.rows import dict_row


app = Flask(__name__)

QUERIES = {
    "total_sales": {"title": "Total Completed Sales Revenue", "concepts": ["JOIN", "SUM"], "currency": ["total_revenue_gbp"], "sql": """SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue_gbp
FROM order_items oi
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0;"""},
    "monthly_revenue": {"title": "Monthly Sales Revenue", "concepts": ["JOIN", "GROUP BY", "SUM"], "currency": ["revenue_gbp"], "sql": """SELECT TO_CHAR(DATE_TRUNC('month', i.invoice_date), 'YYYY-MM') AS month,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY DATE_TRUNC('month', i.invoice_date)
ORDER BY DATE_TRUNC('month', i.invoice_date);"""},
    "top_products": {"title": "Top 10 Products by Revenue", "concepts": ["JOIN", "GROUP BY", "SUM"], "currency": ["revenue_gbp"], "sql": """SELECT p.stock_code,
       COALESCE(p.description, 'Description unavailable') AS product,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM products p
JOIN order_items oi ON oi.stock_code = p.stock_code
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY p.stock_code, p.description
ORDER BY revenue_gbp DESC
LIMIT 10;"""},
    "country_revenue": {"title": "Revenue by Country", "concepts": ["JOIN", "GROUP BY", "COUNT"], "currency": ["revenue_gbp"], "sql": """SELECT i.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY i.country
ORDER BY revenue_gbp DESC;"""},
    "orders_per_customer": {"title": "Orders per Customer", "concepts": ["JOIN", "GROUP BY", "COUNT"], "currency": [], "sql": """SELECT c.customer_id,
       c.country,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM customers c
JOIN invoices i ON i.customer_id = c.customer_id
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY c.customer_id, c.country
ORDER BY order_count DESC, c.customer_id
LIMIT 20;"""},
    "average_order": {"title": "Average Order Value", "concepts": ["JOIN", "GROUP BY", "AVG"], "currency": ["average_order_value_gbp"], "sql": """WITH order_totals AS (
    SELECT i.invoice_no,
           SUM(oi.quantity * oi.unit_price) AS order_value
    FROM invoices i
    JOIN order_items oi ON oi.invoice_no = i.invoice_no
    WHERE NOT i.is_cancelled
      AND oi.quantity > 0
      AND oi.unit_price > 0
    GROUP BY i.invoice_no
)
SELECT ROUND(AVG(order_value), 2) AS average_order_value_gbp
FROM order_totals;"""},
    "products_sold": {"title": "Products Sold Using JOIN", "concepts": ["JOIN", "GROUP BY", "SUM"], "currency": [], "sql": """SELECT p.stock_code,
       COALESCE(p.description, 'Description unavailable') AS product,
       SUM(oi.quantity) AS units_sold
FROM products p
JOIN order_items oi ON oi.stock_code = p.stock_code
JOIN invoices i ON i.invoice_no = oi.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY p.stock_code, p.description
ORDER BY units_sold DESC
LIMIT 20;"""},
    "countries_having": {"title": "Countries Above £100,000 Revenue", "concepts": ["JOIN", "GROUP BY", "HAVING"], "currency": ["revenue_gbp"], "sql": """SELECT i.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue_gbp
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY i.country
HAVING SUM(oi.quantity * oi.unit_price) > 100000
ORDER BY revenue_gbp DESC;"""},
    "customers_having": {"title": "Customers Above £10,000 Spending", "concepts": ["JOIN", "GROUP BY", "HAVING"], "currency": ["spending_gbp"], "sql": """SELECT c.customer_id,
       c.country,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS spending_gbp
FROM customers c
JOIN invoices i ON i.customer_id = c.customer_id
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY c.customer_id, c.country
HAVING SUM(oi.quantity * oi.unit_price) > 10000
ORDER BY spending_gbp DESC;"""},
    "monthly_orders": {"title": "Monthly Order Counts", "concepts": ["JOIN", "GROUP BY", "COUNT"], "currency": [], "sql": """SELECT TO_CHAR(DATE_TRUNC('month', i.invoice_date), 'YYYY-MM') AS month,
       COUNT(DISTINCT i.invoice_no) AS order_count
FROM invoices i
JOIN order_items oi ON oi.invoice_no = i.invoice_no
WHERE NOT i.is_cancelled
  AND oi.quantity > 0
  AND oi.unit_price > 0
GROUP BY DATE_TRUNC('month', i.invoice_date)
ORDER BY DATE_TRUNC('month', i.invoice_date);"""},
}


def database_settings():
    user = os.getenv("PGUSER")
    if not user:
        raise RuntimeError("PGUSER is not configured.")
    return {"host": os.getenv("PGHOST", "127.0.0.1"), "port": int(os.getenv("PGPORT", "5432")), "dbname": os.getenv("PGDATABASE", "retail_db"), "user": user, "password": os.getenv("PGPASSWORD", "")}


def serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def fetch_all(cursor, statement, params=()):
    cursor.execute(statement, params)
    return [{key: serialize(value) for key, value in row.items()} for row in cursor.fetchall()]


def read_filters():
    values = {key: request.args.get(key, "").strip() for key in ("start", "end", "country", "product", "customer", "transaction_type")}
    if values["transaction_type"] not in ("", "completed", "cancelled"):
        raise ValueError("Invalid transaction type.")
    for key in ("start", "end"):
        if values[key]:
            date.fromisoformat(values[key])
    return values


def where_clause(values, completed_only=False, search=""):
    clauses, params = [], []
    if values["start"]:
        clauses.append("i.invoice_date >= %s")
        params.append(values["start"])
    if values["end"]:
        clauses.append("i.invoice_date < (%s::date + INTERVAL '1 day')")
        params.append(values["end"])
    if values["country"]:
        clauses.append("i.country = %s")
        params.append(values["country"])
    if values["product"]:
        clauses.append("(p.stock_code ILIKE %s OR COALESCE(p.description, '') ILIKE %s)")
        params.extend([f"%{values['product']}%"] * 2)
    if values["customer"]:
        clauses.append("COALESCE(i.customer_id::text, '') ILIKE %s")
        params.append(f"%{values['customer']}%")
    if search:
        clauses.append("(i.invoice_no ILIKE %s OR oi.stock_code ILIKE %s OR COALESCE(p.description, '') ILIKE %s OR COALESCE(i.customer_id::text, '') ILIKE %s)")
        params.extend([f"%{search}%"] * 4)
    if completed_only and values["transaction_type"] == "cancelled":
        clauses.append("FALSE")
    elif completed_only or values["transaction_type"] == "completed":
        clauses.extend(["NOT i.is_cancelled", "oi.quantity > 0", "oi.unit_price > 0"])
    elif values["transaction_type"] == "cancelled":
        clauses.append("i.is_cancelled")
    return ("WHERE " + " AND ".join(clauses)) if clauses else "", params


def readonly_connection():
    connection = psycopg.connect(**database_settings(), row_factory=dict_row)
    connection.execute("SET TRANSACTION READ ONLY")
    return connection


@app.get("/")
def index():
    choices = [{"id": key, **{field: value[field] for field in ("title", "sql", "concepts")}} for key, value in QUERIES.items()]
    return render_template("index.html", choices=choices)


@app.get("/api/status")
def status():
    try:
        with readonly_connection() as connection:
            row = connection.execute("SELECT current_setting('server_version') AS version, MIN(invoice_date) AS start_date, MAX(invoice_date) AS end_date FROM invoices").fetchone()
        return jsonify({"connected": True, **{key: serialize(value) for key, value in row.items()}})
    except Exception as error:
        return jsonify({"connected": False, "error": str(error)}), 503


@app.get("/api/filter-options")
def filter_options():
    with readonly_connection() as connection:
        countries = [row["country"] for row in fetch_all(connection.cursor(), "SELECT DISTINCT country FROM invoices ORDER BY country")]
    return jsonify({"countries": countries})


@app.get("/api/dashboard")
def dashboard():
    try:
        values = read_filters()
        completed_where, completed_params = where_clause(values, completed_only=True)
        all_where, all_params = where_clause(values)
        with readonly_connection() as connection:
            cursor = connection.cursor()
            summary = fetch_all(cursor, f"""SELECT COUNT(DISTINCT i.invoice_no) AS total_orders, ROUND(COALESCE(SUM(oi.quantity*oi.unit_price),0),2) AS total_revenue_gbp,
                COUNT(DISTINCT i.customer_id) AS unique_customers, ROUND(COALESCE(AVG(oi.quantity*oi.unit_price),0),2) AS average_line_value_gbp
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {completed_where}""", completed_params)[0]
            cancelled = fetch_all(cursor, f"""SELECT COUNT(DISTINCT i.invoice_no) AS cancelled_invoices FROM invoices i
                JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code
                {all_where + (' AND ' if all_where else 'WHERE ') + 'i.is_cancelled'}""", all_params)[0]
            monthly = fetch_all(cursor, f"""SELECT TO_CHAR(DATE_TRUNC('month',i.invoice_date),'YYYY-MM') AS month,
                ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue_gbp, COUNT(DISTINCT i.invoice_no) AS order_count
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {completed_where}
                GROUP BY DATE_TRUNC('month',i.invoice_date) ORDER BY DATE_TRUNC('month',i.invoice_date)""", completed_params)
            products = fetch_all(cursor, f"""SELECT p.stock_code, COALESCE(p.description,'Description unavailable') AS product,
                SUM(oi.quantity) AS units_sold, ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue_gbp
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {completed_where}
                GROUP BY p.stock_code,p.description ORDER BY units_sold DESC LIMIT 6""", completed_params)
            recent = fetch_all(cursor, f"""SELECT i.invoice_no,i.invoice_date,i.customer_id,i.country,COALESCE(p.description,'Description unavailable') AS product,
                oi.quantity,ROUND(oi.quantity*oi.unit_price,2) AS line_amount_gbp,CASE WHEN i.is_cancelled THEN 'Cancelled' ELSE 'Completed' END AS transaction_type
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {all_where}
                ORDER BY i.invoice_date DESC,oi.item_id DESC LIMIT 8""", all_params)
        return jsonify({"summary": {**summary, **cancelled}, "monthly": monthly, "products": products, "recent": recent})
    except (ValueError, psycopg.Error) as error:
        return jsonify({"error": str(error)}), 400


@app.get("/api/sales")
def sales():
    try:
        values = read_filters()
        where, params = where_clause(values, completed_only=True)
        with readonly_connection() as connection:
            cursor = connection.cursor()
            countries = fetch_all(cursor, f"""SELECT i.country,ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue_gbp,COUNT(DISTINCT i.invoice_no) AS order_count
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where}
                GROUP BY i.country ORDER BY revenue_gbp DESC""", params)
            products = fetch_all(cursor, f"""SELECT p.stock_code,COALESCE(p.description,'Description unavailable') AS product,
                ROUND(SUM(oi.quantity*oi.unit_price),2) AS revenue_gbp,SUM(oi.quantity) AS units_sold
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where}
                GROUP BY p.stock_code,p.description ORDER BY revenue_gbp DESC LIMIT 12""", params)
        return jsonify({"countries": countries, "products": products})
    except (ValueError, psycopg.Error) as error:
        return jsonify({"error": str(error)}), 400


@app.get("/api/customers")
def customers():
    try:
        values = read_filters()
        where, params = where_clause(values, completed_only=True)
        extra = "AND" if where else "WHERE"
        with readonly_connection() as connection:
            cursor = connection.cursor()
            rankings = fetch_all(cursor, f"""SELECT i.customer_id,MIN(i.country) AS country,COUNT(DISTINCT i.invoice_no) AS order_count,
                ROUND(SUM(oi.quantity*oi.unit_price),2) AS spending_gbp FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no
                JOIN products p ON p.stock_code=oi.stock_code {where} {extra} i.customer_id IS NOT NULL
                GROUP BY i.customer_id ORDER BY spending_gbp DESC LIMIT 20""", params)
            distribution = fetch_all(cursor, f"""WITH totals AS (SELECT i.customer_id,SUM(oi.quantity*oi.unit_price) AS spending
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code
                {where} {extra} i.customer_id IS NOT NULL GROUP BY i.customer_id)
                SELECT CASE WHEN spending<500 THEN 'Under £500' WHEN spending<2000 THEN '£500–£1,999' WHEN spending<10000 THEN '£2,000–£9,999' ELSE '£10,000+' END AS spending_band,
                COUNT(*) AS customer_count FROM totals GROUP BY spending_band ORDER BY MIN(spending)""", params)
            countries = fetch_all(cursor, f"""SELECT i.country,COUNT(DISTINCT i.customer_id) AS customer_count FROM invoices i
                JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where} {extra} i.customer_id IS NOT NULL
                GROUP BY i.country ORDER BY customer_count DESC LIMIT 12""", params)
        return jsonify({"rankings": rankings, "distribution": distribution, "countries": countries})
    except (ValueError, psycopg.Error) as error:
        return jsonify({"error": str(error)}), 400


@app.get("/api/orders")
def orders():
    try:
        values = read_filters()
        page = max(1, request.args.get("page", 1, type=int))
        per_page = min(100, max(10, request.args.get("per_page", 25, type=int)))
        search = request.args.get("search", "").strip()
        where, params = where_clause(values, search=search)
        with readonly_connection() as connection:
            cursor = connection.cursor()
            total = fetch_all(cursor, f"SELECT COUNT(*) AS total FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where}", params)[0]["total"]
            rows = fetch_all(cursor, f"""SELECT i.invoice_no,i.invoice_date,i.customer_id,p.stock_code,COALESCE(p.description,'Description unavailable') AS product,
                oi.quantity,oi.unit_price,ROUND(oi.quantity*oi.unit_price,2) AS line_amount_gbp,
                CASE WHEN i.is_cancelled THEN 'Cancelled' ELSE 'Completed' END AS transaction_type
                FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where}
                ORDER BY i.invoice_date DESC,oi.item_id DESC LIMIT %s OFFSET %s""", [*params, per_page, (page-1)*per_page])
        return jsonify({"rows": rows, "total": total, "page": page, "per_page": per_page, "pages": (total+per_page-1)//per_page})
    except (ValueError, psycopg.Error) as error:
        return jsonify({"error": str(error)}), 400


@app.post("/api/query/<query_id>")
def run_query(query_id):
    query = QUERIES.get(query_id)
    if not query:
        return jsonify({"error": "Only predefined read-only queries are allowed."}), 400
    started = perf_counter()
    try:
        with readonly_connection() as connection:
            rows = fetch_all(connection.cursor(), query["sql"])
        return jsonify({"title": query["title"], "sql": query["sql"], "concepts": query["concepts"], "columns": list(rows[0]) if rows else [], "rows": rows, "count": len(rows), "currency": query["currency"], "duration_ms": round((perf_counter()-started)*1000,2)})
    except psycopg.Error as error:
        return jsonify({"error": str(error)}), 500


@app.get("/api/export")
def export_csv():
    query_id = request.args.get("query_id", "")
    if query_id:
        query = QUERIES.get(query_id)
        if not query:
            return jsonify({"error": "Unknown report."}), 400
        with readonly_connection() as connection:
            rows = fetch_all(connection.cursor(), query["sql"])
        columns = list(rows[0]) if rows else []
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={query_id}.csv"})
    try:
        values = read_filters()
        where, params = where_clause(values, search=request.args.get("search", "").strip())
        connection = readonly_connection()
        cursor = connection.cursor()
        cursor.execute(f"""SELECT i.invoice_no,i.invoice_date,i.customer_id,p.stock_code,COALESCE(p.description,'Description unavailable') AS product,
            oi.quantity,oi.unit_price,ROUND(oi.quantity*oi.unit_price,2) AS line_amount_gbp,
            CASE WHEN i.is_cancelled THEN 'Cancelled' ELSE 'Completed' END AS transaction_type
            FROM invoices i JOIN order_items oi ON oi.invoice_no=i.invoice_no JOIN products p ON p.stock_code=oi.stock_code {where}
            ORDER BY i.invoice_date DESC,oi.item_id DESC""", params)

        def generate():
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            writer.writerow([column.name for column in cursor.description])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
            while rows := cursor.fetchmany(2000):
                writer.writerows(rows)
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)
            cursor.close()
            connection.close()

        return Response(generate(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=retail_transactions.csv"})
    except (ValueError, psycopg.Error) as error:
        return jsonify({"error": str(error)}), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005)
