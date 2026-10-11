# DBMS Experiment 06 - The Redundancy Refactor

## Aim

To identify redundancy and insertion, update, and deletion anomalies in a
poorly designed hospital spreadsheet, then decompose it step by step into 1NF,
2NF, 3NF, and BCNF.

## Software

- LibreOffice Calc: inspect the CSV stages.
- LibreOffice Base: create and query the final relational tables.
- DBDesigner or diagrams.net/draw.io: recreate or edit the final ER diagram.
- Python 3.10+ and Flask: run the interactive normalization laboratory.

The deliverables use standard SQL, editable Draw.io XML, and a small
CSV-backed Flask application. No PostgreSQL or MySQL server is required for
the interactive demonstration.

LibreOffice (`soffice`) is available in the environment. A DBDesigner
executable was not detected, so `database_schema.drawio` is supplied as the
editable diagram source; it can be opened in diagrams.net or recreated in
DBDesigner for the laboratory demonstration.

## Files

| File | Purpose |
| --- | --- |
| `00_unnormalized_data.csv` | Repeating groups and duplicated hospital data |
| `01_1NF.csv` | Atomic treatment rows with the composite key `(AppointmentID, TreatmentCode)` |
| `02_2NF.sql` | Removes partial dependencies |
| `03_3NF.sql` | Separates transitive patient, doctor, and department dependencies |
| `04_BCNF.sql` | Final BCNF schema, sample data, and verification queries |
| `normalization_report.md` | Full academic explanation and anomaly examples |
| `database_schema.drawio` | Editable final schema diagram |
| `app.py` | Flask server for the interactive laboratory |
| `templates/` and `static/` | Interactive teaching interface |
| `screenshots/` | Genuine rendered evidence from the supplied files |

## Launch the interactive laboratory

From this directory, create or activate a Python environment and install the
declared dependency:

```bash
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5006/` in a browser. The five sections use the CSV
source data and the schema metadata represented by the SQL deliverables.
Anomaly simulations operate on temporary browser copies and do not modify the
source files.

## Suggested LibreOffice Base demonstration

1. Open `04_BCNF.sql` in LibreOffice Base or use the SQL view.
2. Create the tables in dependency order: departments, patients, doctors,
   treatments, appointments, and appointment treatments.
3. Run the verification queries at the end of the script.
4. Open `database_schema.drawio` in diagrams.net or import the same entities
   into DBDesigner.

## Result

The final design stores each fact once, preserves the intended appointment and
treatment information, and satisfies BCNF under the stated business rules.
