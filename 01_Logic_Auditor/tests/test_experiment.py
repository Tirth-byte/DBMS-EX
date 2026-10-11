import sqlite3
import sys
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.benchmark import SCENARIOS, pandas_operation, sqlite_operation
from src.generate_data import DEPARTMENTS, ROWS, generate_students


class ExperimentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame = pd.read_csv(ROOT / "data" / "students.csv", dtype={"student_id": str})
        cls.connection = sqlite3.connect(ROOT / "data" / "students.db")

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()

    def test_generated_data_is_deterministic(self):
        pd.testing.assert_frame_equal(generate_students(), generate_students())

    def test_data_integrity(self):
        self.assertEqual(len(self.frame), ROWS)
        self.assertTrue(self.frame.student_id.is_unique)
        self.assertFalse(self.frame.isna().any().any())
        self.assertTrue(self.frame.semester.between(1, 8).all())
        self.assertTrue(self.frame.cgpa.between(0, 10).all())
        self.assertTrue(set(self.frame.department).issubset(DEPARTMENTS))

    def test_csv_and_database_are_identical(self):
        database = pd.read_sql_query("SELECT * FROM students ORDER BY student_id", self.connection)
        csv = self.frame.sort_values("student_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(csv, database, check_dtype=False)

    def test_all_queries_are_equivalent(self):
        for scenario, args in SCENARIOS.items():
            with self.subTest(scenario=scenario):
                pd.testing.assert_frame_equal(
                    pandas_operation(self.frame, scenario, args),
                    sqlite_operation(self.connection, scenario, args),
                    check_dtype=False, check_exact=False, rtol=1e-10, atol=1e-10,
                )

    def test_student_id_index_exists(self):
        indexes = self.connection.execute("PRAGMA index_list(students)").fetchall()
        self.assertTrue(any(row[1] == "idx_students_student_id" and row[2] == 1 for row in indexes))


if __name__ == "__main__":
    unittest.main()
