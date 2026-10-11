# Normalization Report - Hospital Appointment Database

## 1. Aim

The aim is to identify redundancy and data anomalies in a hospital patient
spreadsheet and normalize it from UNF to 1NF, 2NF, 3NF, and BCNF.

The example contains 20 appointment records, 12 patients, 5 doctors, 5
departments, and 8 treatment types. A single appointment may contain multiple
treatments.

## 2. Software used

- LibreOffice Calc for opening and inspecting the CSV files.
- LibreOffice Base for creating tables, keys, relationships, and queries.
- DBDesigner or diagrams.net/draw.io for the editable schema diagram.

The SQL is deliberately standard and does not depend on PostgreSQL or MySQL.

## 3. Original unnormalized data

`00_unnormalized_data.csv` stores one appointment per row. The `Treatments`
column contains values such as `T01 Consultation; T02 ECG`. This is a repeating
group rather than one atomic value. Patient, doctor, and department facts are
also repeated on every appointment row.

Examples of repeated facts:

- `Aisha Khan` and her phone number appear in A1001, A1013, and other visits.
- `Dr Kavita Rao` and `Cardiology` appear on every appointment assigned to D01.
- The treatment list contains multiple treatment values in one cell.

## 4. Functional dependencies and candidate keys

The business rules are:

1. Each appointment number identifies one patient visit.
2. Each patient ID identifies one patient and phone number.
3. Each doctor ID identifies one doctor and one department.
4. Each department ID identifies one department name.
5. Each treatment code identifies one treatment and its standard fee.
6. A treatment can occur at most once per appointment in this teaching dataset.

Functional dependencies:

```text
AppointmentID -> PatientID, DoctorID, AppointmentDate, Reason, Status
PatientID -> PatientName, PatientPhone
DoctorID -> DoctorName, DepartmentID
DepartmentID -> DepartmentName
TreatmentCode -> TreatmentName, StandardFee
(AppointmentID, TreatmentCode) -> Quantity, ChargedFee
```

The 1NF relation has candidate key `(AppointmentID, TreatmentCode)`. The
appointment identifier alone cannot identify a treatment line because one
appointment may have several treatments. The treatment code alone cannot
identify a visit quantity or charged fee.

## 5. UNF to 1NF

The UNF spreadsheet violates 1NF because:

- `Treatments` contains a list of values in one cell.
- A treatment name and quantity are not represented as separate atomic rows.
- The same patient, doctor, and department values are repeated.

In `01_1NF.csv`, every row contains exactly one treatment code and one
treatment name. The repeating group is expanded into atomic rows. The
composite candidate key is `(AppointmentID, TreatmentCode)`.

Example:

```text
A1003, T01, Consultation
A1003, T04, X-Ray
A1003, T05, Physiotherapy
```

The rows are atomic, but the table still contains partial and transitive
dependencies.

## 6. 1NF to 2NF

2NF removes partial dependency on only part of a composite key.

In the 1NF relation:

```text
AppointmentID -> PatientID, PatientName, DoctorID, DoctorName, DepartmentID,
                 DepartmentName, AppointmentDate, Reason, Status
TreatmentCode -> TreatmentName, StandardFee
```

These attributes depend on only one part of `(AppointmentID, TreatmentCode)`.
They do not depend on the complete composite key. This is a genuine partial
dependency.

The decomposition in `02_2NF.sql` creates:

- `NF2_APPOINTMENT(AppointmentID, patient and appointment facts)`
- `NF2_TREATMENT(TreatmentCode, TreatmentName, StandardFee)`
- `NF2_APPOINTMENT_TREATMENT(AppointmentID, TreatmentCode, Quantity, ChargedFee)`

The line relation keeps only attributes that require the complete composite
key.

## 7. 2NF to 3NF

2NF removes partial dependencies, but the appointment relation still contains
transitive dependencies:

```text
PatientID -> PatientName, PatientPhone
DoctorID -> DoctorName, DepartmentID
DepartmentID -> DepartmentName
```

For example, `AppointmentID -> DoctorID -> DoctorName`, and
`AppointmentID -> DoctorID -> DepartmentID -> DepartmentName`.

The decomposition in `03_3NF.sql` creates separate `Patient`, `Doctor`, and
`Department` relations. `Appointment` stores only the corresponding foreign
keys. Treatment facts remain in `Treatment`, and appointment-specific facts
remain in `AppointmentTreatment`.

## 8. 3NF to BCNF

BCNF requires that for every non-trivial functional dependency `X -> Y`, X is
a superkey of its relation.

| Relation | Non-trivial determinant | Is determinant a candidate key? |
| --- | --- | --- |
| Department | DepartmentID | Yes |
| Patient | PatientID | Yes |
| Doctor | DoctorID | Yes |
| Treatment | TreatmentCode | Yes |
| Appointment | AppointmentID | Yes |
| AppointmentTreatment | AppointmentID, TreatmentCode | Yes |

Therefore the 3NF schema already satisfies BCNF under the stated business
rules. No additional decomposition is necessary. This is the academically
correct result; BCNF should not be forced when no violating dependency exists.

The final schema is provided in `04_BCNF.sql`.

## 9. Data anomalies

### Insertion anomaly

Suppose the hospital hires a new doctor, Dr Mira Sen, for a new department,
Neurology, before the doctor has an appointment. In the unnormalized
spreadsheet, there is no natural row in which to store the new department and
doctor without inventing an appointment.

In the normalized design, the department and doctor can be inserted
independently into `Department` and `Doctor`.

### Update anomaly

If the phone number of Aisha Khan changes, every spreadsheet row containing
P001 must be updated. Missing one row leaves conflicting phone numbers.

In the normalized design, the phone number is updated once in `Patient`.

### Deletion anomaly

If the only appointment for a doctor or treatment is deleted from the
spreadsheet, the doctor, department, or treatment description may disappear
with it. The spreadsheet cannot distinguish an appointment fact from a master
data fact.

In the normalized design, deleting an appointment-treatment row does not
delete the independent patient, doctor, department, or treatment record.

## 10. Final schema

```text
Department(DepartmentID PK, DepartmentName UNIQUE)
Patient(PatientID PK, PatientName, PatientPhone UNIQUE)
Doctor(DoctorID PK, DoctorName, DepartmentID FK)
Treatment(TreatmentCode PK, TreatmentName UNIQUE, StandardFee)
Appointment(AppointmentID PK, PatientID FK, DoctorID FK,
            AppointmentDate, Reason, Status)
AppointmentTreatment(AppointmentID PK/FK, TreatmentCode PK/FK,
                     Quantity, ChargedFee)
```

Relationships:

- One department has many doctors.
- One patient has many appointments.
- One doctor has many appointments.
- One appointment has many treatment lines.
- One treatment type may appear in many treatment lines.

## 11. Lossless decomposition and dependency preservation

The decompositions are lossless because the common attributes used for joins
are keys in the referenced relations:

- `AppointmentTreatment` joins to `Appointment` using `AppointmentID`.
- `AppointmentTreatment` joins to `Treatment` using `TreatmentCode`.
- `Appointment` joins to `Patient` and `Doctor` using their primary keys.
- `Doctor` joins to `Department` using `DepartmentID`.

The original appointment and treatment information can therefore be
reconstructed by joining the final relations, without spurious tuples.

The main dependencies are preserved directly in their owning tables:
patient, doctor, department, treatment, and appointment identifiers determine
their attributes without requiring a join.

## 12. Verification

The final SQL includes:

- Row-count checks for all six relations.
- A reconstruction join for the original appointment-treatment information.
- A duplicate composite-key check.
- Primary and foreign-key declarations.
- Unique constraints for department names, patient phone numbers, and
  treatment names where justified by the stated rules.

Expected imported counts:

```text
Patient = 12
Doctor = 5
Department = 5
Treatment = 8
Appointment = 20
AppointmentTreatment = 46
```

## 13. Screenshots

The `screenshots/` directory contains genuine rendered views of:

1. Original redundant data.
2. 1NF atomic rows.
3. 2NF decomposition.
4. 3NF decomposition.
5. BCNF verification.
6. Final editable database diagram.

## 14. Result

The hospital spreadsheet was converted from a repeating, redundant structure
to a relational design in BCNF. The final schema reduces update, insertion, and
deletion anomalies while preserving the intended information.

## 15. Conclusion

Normalization is a practical method for storing each fact in the relation
where it belongs. The example demonstrates that 2NF removes partial
dependencies, 3NF removes transitive dependencies, and BCNF verifies that
every determinant is a candidate key. Because the 3NF relations already meet
BCNF, no artificial further split is required.

## 16. Tool limitation

LibreOffice is installed and the CSV/SQL files are prepared for LibreOffice
Base. A DBDesigner executable was not detected in the environment. The
editable Draw.io file provides the same final ER structure and can be opened
in diagrams.net or recreated in DBDesigner during the practical session.
