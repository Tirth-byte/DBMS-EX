# Experiment 04 — Data Integrity Guard

## Aim

To implement primary keys, foreign keys, and unique constraints in a Library Management System and observe how MySQL protects data integrity.

## Software used

- MySQL 8
- MySQL Workbench
- Python 3 and Flask for the faculty demonstration interface

## Database constraints

A primary key uniquely identifies every row. A unique constraint prevents duplicate values in a selected column. A foreign key allows a value only when the related parent record exists. It also prevents a parent record from being deleted while child records still refer to it.

## Tables

| Table | Purpose | Important constraints |
|---|---|---|
| MEMBER | Library members | `Member_ID` primary key; `Email` unique |
| CATEGORY | Book categories | `Category_ID` primary key; `Category_Name` unique |
| BOOK | Library books | `Book_ID` primary key; `ISBN` unique; category foreign key |
| BORROW | Borrowing records | `Borrow_ID` primary key; member and book foreign keys |

All four tables use the InnoDB storage engine.

## Sample data

The scripts insert 5 members, 4 categories, 8 books, and 6 borrowing records. The values are deterministic and satisfy every constraint.

## Constraint tests

`03_constraint_tests.sql` contains five demonstrations. Run each statement or statement group separately because MySQL Workbench may stop after an intentional error.

| Test | Expected observation |
|---|---|
| Duplicate `Member_ID` | Error 1062: duplicate primary key |
| Duplicate member email | Error 1062: duplicate unique value |
| Nonexistent `Book_ID` in BORROW | Error 1452: child foreign key failure |
| Valid member insertion | Accepted; the surrounding transaction is rolled back |
| Delete Member 1 | Error 1451: parent row is referenced by BORROW |

The invalid statements do not change data. The valid statement uses Member 199 inside `START TRANSACTION` and `ROLLBACK`, making it safe to repeat. Foreign-key checks are never disabled.

## Execute in MySQL Workbench

1. Start MySQL 8 and create a Workbench connection.
2. For the verified local setup, use host `127.0.0.1` and port `3308`.
3. Open and execute `01_database.sql`.
4. Open and execute `02_sample_data.sql`.
5. Refresh **Schemas** and inspect `library_db`.
6. Open `03_constraint_tests.sql` and execute each test separately. Read the expected error table above when an invalid operation is rejected.

## Launch the Flask interface

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DB_HOST=127.0.0.1
export DB_PORT=3308
export DB_NAME=library_db
export DB_USER=integrity_lab
export DB_PASSWORD='your-local-password'
python app.py
```

On Windows PowerShell, set variables using `$env:DB_USER="integrity_lab"` and the same form for the remaining values. Open `http://127.0.0.1:5004`, choose a constraint, and select **Test Constraint**. Only predefined parameterized operations are available. Every test runs in a transaction and is rolled back.

## Expected observations

MySQL accepts rows that satisfy all rules. It rejects duplicate primary keys, duplicate unique values, invalid foreign-key references, and deletion of referenced parent records. The interface displays the real MySQL error and verifies the expected error number.

## Conclusion

Primary keys, unique constraints, and foreign keys prevent inconsistent library records. These rules are enforced by MySQL itself, even when an application attempts an invalid operation.
