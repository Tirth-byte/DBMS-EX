"""Generate a deterministic, realistic student dataset."""
from pathlib import Path
import random
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "students.csv"
SEED = 202601
ROWS = 10_000

FIRST_NAMES = ["Aarav", "Aditi", "Akash", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Meera", "Neha", "Nikhil", "Priya", "Rahul", "Riya", "Rohan", "Saanvi", "Siddharth", "Tanvi", "Varun", "Vihaan"]
LAST_NAMES = ["Agarwal", "Bose", "Chauhan", "Das", "Desai", "Gupta", "Iyer", "Joshi", "Kapoor", "Kulkarni", "Mehta", "Menon", "Mishra", "Nair", "Patel", "Rao", "Reddy", "Shah", "Sharma", "Singh"]
DEPARTMENTS = ["Computer Science", "Electronics", "Mechanical", "Civil", "Information Technology", "Electrical"]
CITIES = ["Ahmedabad", "Bengaluru", "Bhopal", "Chandigarh", "Chennai", "Delhi", "Hyderabad", "Jaipur", "Kochi", "Kolkata", "Lucknow", "Mumbai", "Nagpur", "Pune", "Surat"]


def generate_students(rows: int = ROWS, seed: int = SEED) -> pd.DataFrame:
    rng = random.Random(seed)
    records = []
    for number in range(1, rows + 1):
        semester = rng.randint(1, 8)
        records.append({
            "student_id": f"STU{number:05d}",
            "full_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "department": rng.choice(DEPARTMENTS),
            "semester": semester,
            "cgpa": round(rng.triangular(4.0, 10.0, 7.6), 2),
            "city": rng.choice(CITIES),
            "admission_year": 2026 - ((semester - 1) // 2),
        })
    return pd.DataFrame.from_records(records)


def main() -> None:
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_students()
    frame.to_csv(CSV_PATH, index=False, lineterminator="\n")
    print(f"Generated {len(frame):,} records at {CSV_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

