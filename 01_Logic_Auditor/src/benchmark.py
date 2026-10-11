"""Fair, equivalent Pandas/CSV and SQLite retrieval microbenchmarks."""
from __future__ import annotations
from pathlib import Path
from time import perf_counter_ns
import platform
import sqlite3
import statistics
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "students.csv"
DB_PATH = ROOT / "data" / "students.db"
RESULT_PATH = ROOT / "results" / "benchmark_results.csv"
REPETITIONS = 30
WARMUPS = 5
COLUMNS = ["student_id", "full_name", "department", "semester", "cgpa", "city", "admission_year"]

SCENARIOS = {
    "Primary-key lookup": ("STU05000",),
    "Filtering CGPA > 8.5": (8.5,),
    "Department + semester": ("Computer Science", 4),
    "Top 10 by CGPA": (),
    "Average CGPA by department": (),
    "Count by department": (),
}


def pandas_operation(df: pd.DataFrame, scenario: str, args: tuple) -> pd.DataFrame:
    if scenario == "Primary-key lookup":
        out = df.loc[df.student_id == args[0], COLUMNS].sort_values("student_id")
    elif scenario == "Filtering CGPA > 8.5":
        out = df.loc[df.cgpa > args[0], COLUMNS].sort_values("student_id")
    elif scenario == "Department + semester":
        out = df.loc[(df.department == args[0]) & (df.semester == args[1]), COLUMNS].sort_values("student_id")
    elif scenario == "Top 10 by CGPA":
        out = df[COLUMNS].sort_values(["cgpa", "student_id"], ascending=[False, True]).head(10)
    elif scenario == "Average CGPA by department":
        out = df.groupby("department", as_index=False).agg(value=("cgpa", "mean")).sort_values("department")
    elif scenario == "Count by department":
        out = df.groupby("department", as_index=False).agg(value=("student_id", "count")).sort_values("department")
    else:
        raise ValueError(scenario)
    return out.reset_index(drop=True)


def sqlite_operation(connection: sqlite3.Connection, scenario: str, args: tuple) -> pd.DataFrame:
    base = "SELECT student_id, full_name, department, semester, cgpa, city, admission_year FROM students"
    if scenario == "Primary-key lookup":
        sql, params = base + " WHERE student_id = ? ORDER BY student_id", args
    elif scenario == "Filtering CGPA > 8.5":
        sql, params = base + " WHERE cgpa > ? ORDER BY student_id", args
    elif scenario == "Department + semester":
        sql, params = base + " WHERE department = ? AND semester = ? ORDER BY student_id", args
    elif scenario == "Top 10 by CGPA":
        sql, params = base + " ORDER BY cgpa DESC, student_id ASC LIMIT 10", ()
    elif scenario == "Average CGPA by department":
        sql, params = "SELECT department, AVG(cgpa) AS value FROM students GROUP BY department ORDER BY department", ()
    elif scenario == "Count by department":
        sql, params = "SELECT department, COUNT(student_id) AS value FROM students GROUP BY department ORDER BY department", ()
    else:
        raise ValueError(scenario)
    return pd.read_sql_query(sql, connection, params=params)


def equivalent(left: pd.DataFrame, right: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(left, right, check_dtype=False, check_exact=False, rtol=1e-10, atol=1e-10)


def measure(callable_, warmups: int = WARMUPS, repetitions: int = REPETITIONS) -> list[int]:
    for _ in range(warmups):
        callable_()
    samples = []
    for _ in range(repetitions):
        start = perf_counter_ns()
        callable_()
        samples.append(perf_counter_ns() - start)
    return samples


def summary(scenario: str, category: str, system: str, samples: list[int]) -> dict:
    ms = [value / 1_000_000 for value in samples]
    return {
        "scenario": scenario, "category": category, "system": system,
        "repetitions": len(ms), "median_ms": statistics.median(ms),
        "mean_ms": statistics.mean(ms), "stddev_ms": statistics.stdev(ms),
    }


def run_benchmarks() -> pd.DataFrame:
    if not CSV_PATH.exists() or not DB_PATH.exists():
        raise FileNotFoundError("Run generate_data.py and database.py first")
    loaded = pd.read_csv(CSV_PATH, dtype={"student_id": str})
    rows = []
    with sqlite3.connect(DB_PATH) as warm_connection:
        for scenario, args in SCENARIOS.items():
            equivalent(pandas_operation(loaded, scenario, args), sqlite_operation(warm_connection, scenario, args))

            def pandas_cold(s=scenario, a=args):
                return pandas_operation(pd.read_csv(CSV_PATH, dtype={"student_id": str}), s, a)

            def sqlite_cold(s=scenario, a=args):
                with sqlite3.connect(DB_PATH) as connection:
                    return sqlite_operation(connection, s, a)

            tasks = [
                ("End-to-end", "CSV/Pandas", pandas_cold),
                ("End-to-end", "SQLite", sqlite_cold),
                ("Warm query", "Pandas", lambda s=scenario, a=args: pandas_operation(loaded, s, a)),
                ("Warm query", "SQLite", lambda s=scenario, a=args: sqlite_operation(warm_connection, s, a)),
            ]
            for category, system, operation in tasks:
                rows.append(summary(scenario, category, system, measure(operation)))
            print(f"Verified and benchmarked: {scenario}")
    result = pd.DataFrame(rows)
    result["python_version"] = platform.python_version()
    result["pandas_version"] = pd.__version__
    result["sqlite_version"] = sqlite3.sqlite_version
    result["operating_system"] = platform.platform()
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(RESULT_PATH, index=False, float_format="%.6f")
    print(f"Saved {len(result)} benchmark summaries to {RESULT_PATH.relative_to(ROOT)}")
    return result


if __name__ == "__main__":
    run_benchmarks()

