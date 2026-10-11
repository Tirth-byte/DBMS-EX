from pathlib import Path
import os
import re
from flask import Flask, jsonify, render_template
import pymysql
from pymysql.cursors import DictCursor

app = Flask(__name__)
ROOT = Path(__file__).resolve().parent
TABLES = ("DEPARTMENT", "STUDENT", "FACULTY", "COURSE", "ENROLLMENT")


def read_queries():
    text = (ROOT / "05_select_queries.sql").read_text(encoding="utf-8")
    matches = re.findall(r"--\s*(\d+)\.\s*([^\n]+)\n(SELECT.*?;)", text, re.IGNORECASE | re.DOTALL)
    return {number: {"title": title.rstrip("."), "sql": sql.strip()} for number, title, sql in matches}


QUERIES = read_queries()
OPERATIONS = {
    **{f"table:{table}": {"group": "Browse Tables", "title": table, "sql": f"SELECT * FROM {table};"} for table in TABLES},
    **{f"query:{query_id}": {"group": "SQL Query Examples", "title": f"{query_id}. {query['title']}", "sql": query["sql"]} for query_id, query in QUERIES.items()},
}


def connection():
    missing = [name for name in ("DB_USER", "DB_PASSWORD") if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3307")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "university_db"),
        cursorclass=DictCursor,
        connect_timeout=4,
        read_timeout=8,
        autocommit=True,
    )


def execute_read(sql):
    with connection() as database:
        with database.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchmany(101)
            columns = [item[0] for item in cursor.description]
    return columns, rows[:100], len(rows) > 100


@app.get("/")
def index():
    return render_template("index.html", operations=OPERATIONS)


@app.get("/api/status")
def status():
    try:
        columns, rows, truncated = execute_read("SELECT VERSION() AS MariaDB_Version")
        return jsonify({"connected": True, "version": rows[0]["MariaDB_Version"]})
    except Exception as error:
        return jsonify({"connected": False, "error": str(error)}), 503


@app.post("/api/operation/<path:operation_id>")
def operation_data(operation_id):
    selected = OPERATIONS.get(operation_id)
    if selected is None:
        return jsonify({"error": "Only predefined read-only operations are allowed."}), 400
    if not selected["sql"].lstrip().upper().startswith("SELECT"):
        return jsonify({"error": "Only read-only SELECT operations are allowed."}), 400
    try:
        columns, rows, truncated = execute_read(selected["sql"])
        return jsonify({"title": selected["title"], "sql": selected["sql"], "columns": columns, "rows": rows, "count": len(rows), "truncated": truncated})
    except Exception as error:
        return jsonify({"error": str(error)}), 503


@app.get("/api/table/<table_name>")
def table_data(table_name):
    table = table_name.upper()
    if table not in TABLES:
        return jsonify({"error": "Unknown table."}), 404
    try:
        columns, rows, truncated = execute_read(f"SELECT * FROM `{table}` LIMIT 100")
        return jsonify({"title": table, "columns": columns, "rows": rows, "count": len(rows), "truncated": truncated})
    except Exception as error:
        return jsonify({"error": str(error)}), 503


@app.post("/api/query/<query_id>")
def query_data(query_id):
    selected = QUERIES.get(query_id)
    if selected is None:
        return jsonify({"error": "Only predefined SELECT queries are allowed."}), 400
    if not selected["sql"].lstrip().upper().startswith("SELECT"):
        return jsonify({"error": "Only read-only SELECT queries are allowed."}), 400
    try:
        columns, rows, truncated = execute_read(selected["sql"])
        return jsonify({"title": selected["title"], "sql": selected["sql"], "columns": columns, "rows": rows, "count": len(rows), "truncated": truncated})
    except Exception as error:
        return jsonify({"error": str(error)}), 503


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False)

