"""Create and validate the SQLite representation of the dataset."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "students.csv"
DB_PATH = ROOT / "data" / "students.db"
SCHEMA = """
CREATE TABLE students (
    student_id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    department TEXT NOT NULL,
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    cgpa REAL NOT NULL CHECK (cgpa BETWEEN 0 AND 10),
    city TEXT NOT NULL,
    admission_year INTEGER NOT NULL
)
"""


def initialise_database(csv_path: Path = CSV_PATH, db_path: Path = DB_PATH) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"Generate {csv_path} first")
    frame = pd.read_csv(csv_path, dtype={"student_id": str})
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute("DROP TABLE IF EXISTS students")
        connection.execute(SCHEMA)
        connection.executemany(
            "INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?)",
            frame.itertuples(index=False, name=None),
        )
        # The PRIMARY KEY already creates a unique SQLite index; this named index
        # makes the indexing choice explicit and easy to inspect in a lab.
        connection.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id)")
        connection.commit()
    print(f"Initialized SQLite with {len(frame):,} records at {db_path.relative_to(ROOT)}")


def main() -> None:
    initialise_database()


if __name__ == "__main__":
    main()

