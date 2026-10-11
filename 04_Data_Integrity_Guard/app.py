import os
from flask import Flask, jsonify, render_template
import mysql.connector
from mysql.connector import IntegrityError

app = Flask(__name__)

TESTS = {
    "primary_key": {
        "title": "Primary Key — Duplicate Member_ID",
        "sql": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (1, 'Test Member', 'primary.test@example.com', '9000000001');",
        "statement": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (%s, %s, %s, %s)",
        "params": (1, "Test Member", "primary.test@example.com", "9000000001"),
        "expected_error": 1062,
        "accepted": False,
        "reason": "A primary key must uniquely identify every member.",
    },
    "unique": {
        "title": "Unique Constraint — Duplicate Email",
        "sql": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (101, 'Email Test', 'aarav.sharma@example.com', '9000000002');",
        "statement": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (%s, %s, %s, %s)",
        "params": (101, "Email Test", "aarav.sharma@example.com", "9000000002"),
        "expected_error": 1062,
        "accepted": False,
        "reason": "The UNIQUE constraint prevents two members from using the same email.",
    },
    "foreign_key": {
        "title": "Foreign Key — Nonexistent Book_ID",
        "sql": "INSERT INTO BORROW (Borrow_ID, Member_ID, Book_ID, Borrow_Date, Return_Date) VALUES (301, 1, 999, '2026-10-11', NULL);",
        "statement": "INSERT INTO BORROW (Borrow_ID, Member_ID, Book_ID, Borrow_Date, Return_Date) VALUES (%s, %s, %s, %s, %s)",
        "params": (301, 1, 999, "2026-10-11", None),
        "expected_error": 1452,
        "accepted": False,
        "reason": "The borrowed book must already exist in the BOOK table.",
    },
    "valid": {
        "title": "Valid Record — New Member",
        "sql": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (199, 'Valid Test Member', 'valid.test@example.com', '9000000199');",
        "statement": "INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES (%s, %s, %s, %s)",
        "params": (199, "Valid Test Member", "valid.test@example.com", "9000000199"),
        "expected_error": None,
        "accepted": True,
        "reason": "The record satisfies the primary key, unique, and required-field constraints.",
    },
    "restricted_delete": {
        "title": "Restricted Deletion — Borrowing Member",
        "sql": "DELETE FROM MEMBER WHERE Member_ID = 1;",
        "statement": "DELETE FROM MEMBER WHERE Member_ID = %s",
        "params": (1,),
        "expected_error": 1451,
        "accepted": False,
        "reason": "The member cannot be deleted while BORROW records still reference that member.",
    },
}


def database_connection():
    missing = [name for name in ("DB_USER", "DB_PASSWORD") if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing environment variables: " + ", ".join(missing))
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3308")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.getenv("DB_NAME", "library_db"),
        connection_timeout=4,
    )


@app.get("/")
def index():
    return render_template("index.html", tests=TESTS)


@app.get("/api/status")
def status():
    try:
        connection = database_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return jsonify({"connected": True, "version": version})
    except Exception as error:
        return jsonify({"connected": False, "error": str(error)}), 503


@app.post("/api/test/<test_id>")
def run_test(test_id):
    selected = TESTS.get(test_id)
    if selected is None:
        return jsonify({"error": "Only predefined constraint tests are allowed."}), 400
    connection = None
    cursor = None
    try:
        connection = database_connection()
        connection.start_transaction()
        cursor = connection.cursor()
        cursor.execute(selected["statement"], selected["params"])
        connection.rollback()
        if selected["accepted"]:
            return jsonify({"title": selected["title"], "sql": selected["sql"], "result": "Accepted", "reason": selected["reason"], "error": None, "verified": True})
        return jsonify({"title": selected["title"], "sql": selected["sql"], "result": "Accepted unexpectedly", "reason": "MySQL did not enforce the expected constraint.", "error": None, "verified": False}), 500
    except IntegrityError as error:
        if connection:
            connection.rollback()
        verified = not selected["accepted"] and error.errno == selected["expected_error"]
        status_code = 200 if verified else 500
        return jsonify({"title": selected["title"], "sql": selected["sql"], "result": "Rejected" if verified else "Unexpected database error", "reason": selected["reason"] if verified else "The error did not match the expected constraint.", "error": str(error), "error_code": error.errno, "verified": verified}), status_code
    except Exception as error:
        if connection:
            connection.rollback()
        return jsonify({"error": str(error)}), 503
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=False)

