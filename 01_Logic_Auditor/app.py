import sqlite3
from flask import Flask, jsonify, render_template
import pandas as pd
from src.benchmark import CSV_PATH, DB_PATH, SCENARIOS, equivalent, measure, pandas_operation, sqlite_operation, summary

app = Flask(__name__)


def benchmark_scenario(scenario):
    args = SCENARIOS[scenario]
    loaded = pd.read_csv(CSV_PATH, dtype={"student_id": str})
    rows = []
    with sqlite3.connect(DB_PATH) as warm_connection:
        pandas_result = pandas_operation(loaded, scenario, args)
        sqlite_result = sqlite_operation(warm_connection, scenario, args)
        equivalent(pandas_result, sqlite_result)

        def pandas_end_to_end():
            frame = pd.read_csv(CSV_PATH, dtype={"student_id": str})
            return pandas_operation(frame, scenario, args)

        def sqlite_end_to_end():
            with sqlite3.connect(DB_PATH) as connection:
                return sqlite_operation(connection, scenario, args)

        operations = [
            ("End-to-end", "CSV/Pandas", pandas_end_to_end),
            ("End-to-end", "SQLite", sqlite_end_to_end),
            ("Warm query", "Pandas", lambda: pandas_operation(loaded, scenario, args)),
            ("Warm query", "SQLite", lambda: sqlite_operation(warm_connection, scenario, args)),
        ]
        for category, system, operation in operations:
            rows.append(summary(scenario, category, system, measure(operation)))
    return rows


@app.get("/")
def index():
    return render_template("index.html", scenarios=list(SCENARIOS))


@app.post("/api/benchmark/<path:scenario>")
def run_scenario(scenario):
    if scenario not in SCENARIOS:
        return jsonify({"error": "Unknown benchmark scenario."}), 400
    try:
        return jsonify({"scenario": scenario, "matched": True, "results": benchmark_scenario(scenario)})
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)

