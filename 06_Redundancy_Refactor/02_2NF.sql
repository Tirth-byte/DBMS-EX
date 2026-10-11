-- DBMS Experiment 06: 2NF decomposition
-- Standard SQL intended for LibreOffice Base SQL view.
--
-- 1NF key: (AppointmentID, TreatmentCode)
-- Partial dependencies:
--   AppointmentID -> PatientID, PatientName, PatientPhone, DoctorID,
--                    DoctorName, DepartmentID, DepartmentName,
--                    AppointmentDate, Reason, Status
--   TreatmentCode -> TreatmentName, StandardFee
-- Full dependency:
--   (AppointmentID, TreatmentCode) -> Quantity, ChargedFee

CREATE TABLE NF2_APPOINTMENT (
    AppointmentID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10) NOT NULL,
    PatientName VARCHAR(80) NOT NULL,
    PatientPhone VARCHAR(20) NOT NULL,
    DoctorID VARCHAR(10) NOT NULL,
    DoctorName VARCHAR(80) NOT NULL,
    DepartmentID VARCHAR(10) NOT NULL,
    DepartmentName VARCHAR(80) NOT NULL,
    AppointmentDate DATE NOT NULL,
    Reason VARCHAR(120) NOT NULL,
    Status VARCHAR(20) NOT NULL
);

CREATE TABLE NF2_TREATMENT (
    TreatmentCode VARCHAR(10) PRIMARY KEY,
    TreatmentName VARCHAR(80) NOT NULL,
    StandardFee DECIMAL(10,2) NOT NULL
);

CREATE TABLE NF2_APPOINTMENT_TREATMENT (
    AppointmentID VARCHAR(10) NOT NULL,
    TreatmentCode VARCHAR(10) NOT NULL,
    Quantity INTEGER NOT NULL,
    ChargedFee DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (AppointmentID, TreatmentCode),
    FOREIGN KEY (AppointmentID) REFERENCES NF2_APPOINTMENT (AppointmentID),
    FOREIGN KEY (TreatmentCode) REFERENCES NF2_TREATMENT (TreatmentCode)
);

-- Import the appointment and treatment rows from 01_1NF.csv into the three
-- tables, keeping one row per fact in each relation.
-- Example LibreOffice Base import workflow:
--   1. Import the CSV into a temporary table named NF1_SOURCE.
--   2. Insert distinct appointment, treatment, and appointment-treatment rows.

INSERT INTO NF2_TREATMENT VALUES ('T01', 'Consultation', 500.00);
INSERT INTO NF2_TREATMENT VALUES ('T02', 'ECG', 800.00);
INSERT INTO NF2_TREATMENT VALUES ('T03', 'Blood Test', 350.00);
INSERT INTO NF2_TREATMENT VALUES ('T04', 'X-Ray', 700.00);
INSERT INTO NF2_TREATMENT VALUES ('T05', 'Physiotherapy', 600.00);
INSERT INTO NF2_TREATMENT VALUES ('T06', 'Skin Examination', 450.00);
INSERT INTO NF2_TREATMENT VALUES ('T07', 'Dressing', 250.00);
INSERT INTO NF2_TREATMENT VALUES ('T08', 'Ultrasound', 1200.00);

-- The appointment and line tables are intentionally left ready for CSV
-- import so that a student can demonstrate the decomposition in Base.
