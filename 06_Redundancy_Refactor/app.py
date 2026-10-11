from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from copy import deepcopy

from flask import Flask, jsonify, render_template, send_from_directory


ROOT = Path(__file__).resolve().parent
app = Flask(__name__)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_1nf() -> list[dict[str, str]]:
    return read_csv("01_1NF.csv")


UNF = read_csv("00_unnormalized_data.csv")
NF1 = read_1nf()


def unique_rows(rows: list[dict[str, str]], keys: tuple[str, ...]) -> list[dict[str, str]]:
    seen: set[tuple[str, ...]] = set()
    result: list[dict[str, str]] = []
    for row in rows:
        marker = tuple(row[key] for key in keys)
        if marker not in seen:
            seen.add(marker)
            result.append(row)
    return result


def tables_2nf() -> dict[str, list[dict[str, str]]]:
    appointments = [
        {key: row[key] for key in (
            "AppointmentID",
            "PatientID",
            "PatientName",
            "PatientPhone",
            "DoctorID",
            "DoctorName",
            "DepartmentID",
            "DepartmentName",
            "AppointmentDate",
            "Reason",
            "Status",
        )}
        for row in unique_rows(NF1, ("AppointmentID",))
    ]
    treatments = [
        {key: row[key] for key in ("TreatmentCode", "TreatmentName", "StandardFee")}
        for row in unique_rows(NF1, ("TreatmentCode",))
    ]
    lines = [
        {key: row[key] for key in ("AppointmentID", "TreatmentCode", "Quantity", "ChargedFee")}
        for row in NF1
    ]
    return {
        "NF2_APPOINTMENT": appointments,
        "NF2_TREATMENT": treatments,
        "NF2_APPOINTMENT_TREATMENT": lines,
    }


def tables_3nf() -> dict[str, list[dict[str, str]]]:
    return {
        "Department": [
            {"DepartmentID": row["DepartmentID"], "DepartmentName": row["DepartmentName"]}
            for row in unique_rows(NF1, ("DepartmentID",))
        ],
        "Patient": [
            {"PatientID": row["PatientID"], "PatientName": row["PatientName"], "PatientPhone": row["PatientPhone"]}
            for row in unique_rows(NF1, ("PatientID",))
        ],
        "Doctor": [
            {"DoctorID": row["DoctorID"], "DoctorName": row["DoctorName"], "DepartmentID": row["DepartmentID"]}
            for row in unique_rows(NF1, ("DoctorID",))
        ],
        "Treatment": [
            {"TreatmentCode": row["TreatmentCode"], "TreatmentName": row["TreatmentName"], "StandardFee": row["StandardFee"]}
            for row in unique_rows(NF1, ("TreatmentCode",))
        ],
        "Appointment": [
            {key: row[key] for key in ("AppointmentID", "PatientID", "DoctorID", "AppointmentDate", "Reason", "Status")}
            for row in unique_rows(NF1, ("AppointmentID",))
        ],
        "AppointmentTreatment": [
            {key: row[key] for key in ("AppointmentID", "TreatmentCode", "Quantity", "ChargedFee")}
            for row in NF1
        ],
    }


TABLES = tables_3nf()


STAGES = [
    {
        "id": "unf",
        "label": "UNF",
        "title": "Unnormalized form",
        "key": "AppointmentID",
        "problem": "Treatments is a repeating, non-atomic group. Patient, doctor, and department facts are copied into every appointment row.",
        "operation": "Keep one appointment row with the treatment list visible so the anomaly is observable.",
        "satisfies": "This stage intentionally does not satisfy 1NF.",
        "tables": [{"name": "HospitalVisit_UNF", "rows": UNF[:5], "columns": list(UNF[0])}],
        "dependencies": ["AppointmentID -> patient, doctor, date, reason, status"],
    },
    {
        "id": "1nf",
        "label": "1NF",
        "title": "Atomic treatment rows",
        "key": "(AppointmentID, TreatmentCode)",
        "problem": "The repeating group is gone, but appointment and treatment attributes depend on only part of the composite key.",
        "operation": "Split each treatment in the list into its own atomic row.",
        "satisfies": "Every field is atomic and every row has a value for the composite candidate key.",
        "tables": [{"name": "NF1_AppointmentTreatment", "rows": NF1[:8], "columns": list(NF1[0])}],
        "dependencies": [
            "AppointmentID -> patient and appointment facts",
            "TreatmentCode -> treatment name and standard fee",
            "(AppointmentID, TreatmentCode) -> quantity and charged fee",
        ],
    },
    {
        "id": "2nf",
        "label": "2NF",
        "title": "Partial dependencies removed",
        "key": "AppointmentID; TreatmentCode; (AppointmentID, TreatmentCode)",
        "problem": "In 1NF, appointment attributes depend on AppointmentID and treatment attributes depend on TreatmentCode, not the whole key.",
        "operation": "Decompose the 1NF relation into appointment, treatment, and appointment-treatment relations.",
        "satisfies": "Non-key attributes in the line table depend on the complete composite key.",
        "tables": [{"name": name, "rows": rows[:5], "columns": list(rows[0]) if rows else []} for name, rows in tables_2nf().items()],
        "dependencies": [
            "AppointmentID -> appointment facts",
            "TreatmentCode -> treatment facts",
            "(AppointmentID, TreatmentCode) -> line facts",
        ],
    },
    {
        "id": "3nf",
        "label": "3NF",
        "title": "Transitive dependencies removed",
        "key": "Each table uses its identifier as a candidate key",
        "problem": "2NF appointment data still carries PatientID -> patient facts and DoctorID -> doctor and department facts.",
        "operation": "Separate Patient, Doctor, and Department master tables and reference them with foreign keys.",
        "satisfies": "Non-key attributes depend on the key, the whole key, and nothing but the key.",
        "tables": [{"name": name, "rows": rows[:5], "columns": list(rows[0]) if rows else []} for name, rows in TABLES.items()],
        "dependencies": [
            "PatientID -> PatientName, PatientPhone",
            "DoctorID -> DoctorName, DepartmentID",
            "DepartmentID -> DepartmentName",
        ],
    },
    {
        "id": "bcnf",
        "label": "BCNF",
        "title": "BCNF verification",
        "key": "Primary key of each final relation",
        "problem": "BCNF must be checked against every actual non-trivial functional dependency.",
        "operation": "Evaluate each determinant. No further split is required.",
        "satisfies": "Every non-trivial determinant is a superkey in its relation, so the 3NF design already satisfies BCNF.",
        "tables": [{"name": name, "rows": rows[:5], "columns": list(rows[0]) if rows else []} for name, rows in TABLES.items()],
        "dependencies": [
            "DepartmentID -> DepartmentName: determinant is a key",
            "PatientID -> PatientName, PatientPhone: determinant is a key",
            "DoctorID -> DoctorName, DepartmentID: determinant is a key",
            "TreatmentCode -> TreatmentName, StandardFee: determinant is a key",
            "AppointmentID -> appointment facts: determinant is a key",
            "(AppointmentID, TreatmentCode) -> line facts: determinant is a key",
        ],
    },
]


DEPENDENCIES = [
    {
        "id": "appointment",
        "label": "AppointmentID -> appointment facts",
        "determinant": "AppointmentID",
        "dependent": "PatientID, DoctorID, AppointmentDate, Reason, Status",
        "classification": "partial in the 1NF composite relation",
        "stage": "1NF -> 2NF",
        "why": "AppointmentID identifies the visit, but it is only one part of the 1NF candidate key.",
    },
    {
        "id": "treatment",
        "label": "TreatmentCode -> treatment facts",
        "determinant": "TreatmentCode",
        "dependent": "TreatmentName, StandardFee",
        "classification": "partial in the 1NF composite relation",
        "stage": "1NF -> 2NF",
        "why": "TreatmentCode identifies a treatment type independently of a particular appointment.",
    },
    {
        "id": "patient",
        "label": "PatientID -> patient facts",
        "determinant": "PatientID",
        "dependent": "PatientName, PatientPhone",
        "classification": "transitive in the 2NF appointment relation",
        "stage": "2NF -> 3NF",
        "why": "AppointmentID determines PatientID, which determines patient details.",
    },
    {
        "id": "doctor",
        "label": "DoctorID -> doctor and department",
        "determinant": "DoctorID",
        "dependent": "DoctorName, DepartmentID",
        "classification": "transitive in the 2NF appointment relation",
        "stage": "2NF -> 3NF",
        "why": "AppointmentID determines DoctorID, which determines doctor details and department membership.",
    },
    {
        "id": "department",
        "label": "DepartmentID -> department name",
        "determinant": "DepartmentID",
        "dependent": "DepartmentName",
        "classification": "transitive through DoctorID in the 2NF appointment relation",
        "stage": "2NF -> 3NF",
        "why": "DepartmentName belongs to the department master, not to an appointment row.",
    },
    {
        "id": "bcnf",
        "label": "(AppointmentID, TreatmentCode) -> line facts",
        "determinant": "(AppointmentID, TreatmentCode)",
        "dependent": "Quantity, ChargedFee",
        "classification": "BCNF compliant",
        "stage": "3NF -> BCNF",
        "why": "The determinant is the candidate key of AppointmentTreatment; no BCNF violation exists.",
    },
]


SCHEMAS = {
    "Department": {"columns": ["DepartmentID", "DepartmentName"], "pk": ["DepartmentID"], "fks": [], "relationships": ["1:N Doctor"]},
    "Patient": {"columns": ["PatientID", "PatientName", "PatientPhone"], "pk": ["PatientID"], "fks": [], "relationships": ["1:N Appointment"]},
    "Doctor": {"columns": ["DoctorID", "DoctorName", "DepartmentID"], "pk": ["DoctorID"], "fks": ["DepartmentID -> Department.DepartmentID"], "relationships": ["N:1 Department", "1:N Appointment"]},
    "Treatment": {"columns": ["TreatmentCode", "TreatmentName", "StandardFee"], "pk": ["TreatmentCode"], "fks": [], "relationships": ["1:N AppointmentTreatment"]},
    "Appointment": {"columns": ["AppointmentID", "PatientID", "DoctorID", "AppointmentDate", "Reason", "Status"], "pk": ["AppointmentID"], "fks": ["PatientID -> Patient.PatientID", "DoctorID -> Doctor.DoctorID"], "relationships": ["N:1 Patient", "N:1 Doctor", "1:N AppointmentTreatment"]},
    "AppointmentTreatment": {"columns": ["AppointmentID", "TreatmentCode", "Quantity", "ChargedFee"], "pk": ["AppointmentID", "TreatmentCode"], "fks": ["AppointmentID -> Appointment.AppointmentID", "TreatmentCode -> Treatment.TreatmentCode"], "relationships": ["N:1 Appointment", "N:1 Treatment"]},
}


def anomaly_data() -> dict[str, object]:
    patient_rows = [row for row in UNF if row["PatientID"] == "P001"]
    doctor_rows = [row for row in UNF if row["DoctorID"] == "D01"]
    deletion_rows = [row for row in UNF if row["AppointmentID"] == "A1001"]
    return {
        "update": {
            "title": "Update anomaly",
            "target": "P001",
            "field": "PatientPhone",
            "before": "9876500011",
            "after": "9876500099",
            "rows": patient_rows,
            "explanation": "The phone number appears in every P001 appointment. Updating one row only creates conflicting patient facts.",
        },
        "doctor": {
            "title": "Department update",
            "target": "D01",
            "field": "DepartmentName",
            "before": "Cardiology",
            "after": "Neurology",
            "rows": doctor_rows,
            "explanation": "The department value is repeated in every D01 appointment and must be updated consistently.",
        },
        "deletion": {
            "title": "Deletion anomaly",
            "target": "A1001",
            "rows": deletion_rows,
            "explanation": "Deleting the only A1001 row removes the appointment history for Aisha Khan's chest-discomfort visit. In a normalized design, the patient and master facts remain independent.",
        },
    }


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/database_schema.drawio")
def diagram():
    return send_from_directory(ROOT, "database_schema.drawio", as_attachment=False)


@app.get("/api/overview")
def overview():
    return jsonify({
        "records": UNF,
        "count": len(UNF),
        "patient_count": len(unique_rows(UNF, ("PatientID",))),
        "doctor_count": len(unique_rows(UNF, ("DoctorID",))),
        "department_count": len(unique_rows(UNF, ("DepartmentID",))),
        "treatment_line_count": len(NF1),
    })


@app.get("/api/anomalies")
def anomalies():
    return jsonify(anomaly_data())


@app.get("/api/stages")
def stages():
    return jsonify(STAGES)


@app.get("/api/dependencies")
def dependencies():
    return jsonify(DEPENDENCIES)


@app.get("/api/schema")
def schema():
    previews = {
        "Department": TABLES["Department"][:5],
        "Patient": TABLES["Patient"][:5],
        "Doctor": TABLES["Doctor"][:5],
        "Treatment": TABLES["Treatment"][:5],
        "Appointment": TABLES["Appointment"][:5],
        "AppointmentTreatment": TABLES["AppointmentTreatment"][:5],
    }
    purposes = {
        "Department": "Stores each hospital department once.",
        "Patient": "Stores stable patient identity and contact facts.",
        "Doctor": "Stores doctors and their department membership.",
        "Treatment": "Stores the treatment catalogue and standard fee.",
        "Appointment": "Stores one patient visit and its assigned doctor.",
        "AppointmentTreatment": "Associates appointments with atomic treatment lines.",
    }
    types = {
        column: ("DECIMAL" if column in {"StandardFee", "ChargedFee"} else "INTEGER" if column == "Quantity" else "DATE" if column == "AppointmentDate" else "VARCHAR")
        for table in TABLES.values() for column in table[0]
    }
    return jsonify({
        name: {
            **table,
            "purpose": purposes[name],
            "types": {column: types[column] for column in table["columns"]},
            "preview": previews[name],
        }
        for name, table in SCHEMAS.items()
    })


@app.get("/api/source")
def source():
    return jsonify({"unf": UNF, "nf1": NF1, "nf2": tables_2nf(), "nf3": TABLES, "bcnf": TABLES})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5006, debug=False)
