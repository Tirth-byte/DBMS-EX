-- DBMS Experiment 06: 3NF decomposition
-- Standard SQL intended for LibreOffice Base SQL view.
--
-- 2NF still stores these transitive dependencies:
--   PatientID -> PatientName, PatientPhone
--   DoctorID -> DoctorName, DepartmentID
--   DepartmentID -> DepartmentName
-- They are separated below.

CREATE TABLE NF3_DEPARTMENT (
    DepartmentID VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE NF3_PATIENT (
    PatientID VARCHAR(10) PRIMARY KEY,
    PatientName VARCHAR(80) NOT NULL,
    PatientPhone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE NF3_DOCTOR (
    DoctorID VARCHAR(10) PRIMARY KEY,
    DoctorName VARCHAR(80) NOT NULL,
    DepartmentID VARCHAR(10) NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES NF3_DEPARTMENT (DepartmentID)
);

CREATE TABLE NF3_TREATMENT (
    TreatmentCode VARCHAR(10) PRIMARY KEY,
    TreatmentName VARCHAR(80) NOT NULL UNIQUE,
    StandardFee DECIMAL(10,2) NOT NULL
);

CREATE TABLE NF3_APPOINTMENT (
    AppointmentID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10) NOT NULL,
    DoctorID VARCHAR(10) NOT NULL,
    AppointmentDate DATE NOT NULL,
    Reason VARCHAR(120) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES NF3_PATIENT (PatientID),
    FOREIGN KEY (DoctorID) REFERENCES NF3_DOCTOR (DoctorID)
);

CREATE TABLE NF3_APPOINTMENT_TREATMENT (
    AppointmentID VARCHAR(10) NOT NULL,
    TreatmentCode VARCHAR(10) NOT NULL,
    Quantity INTEGER NOT NULL,
    ChargedFee DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (AppointmentID, TreatmentCode),
    FOREIGN KEY (AppointmentID) REFERENCES NF3_APPOINTMENT (AppointmentID),
    FOREIGN KEY (TreatmentCode) REFERENCES NF3_TREATMENT (TreatmentCode)
);

-- Populate the master tables from the distinct values in 01_1NF.csv.
INSERT INTO NF3_DEPARTMENT VALUES ('DEP01', 'Cardiology');
INSERT INTO NF3_DEPARTMENT VALUES ('DEP02', 'Pediatrics');
INSERT INTO NF3_DEPARTMENT VALUES ('DEP03', 'Orthopedics');
INSERT INTO NF3_DEPARTMENT VALUES ('DEP04', 'Dermatology');
INSERT INTO NF3_DEPARTMENT VALUES ('DEP05', 'General Medicine');

INSERT INTO NF3_TREATMENT VALUES ('T01', 'Consultation', 500.00);
INSERT INTO NF3_TREATMENT VALUES ('T02', 'ECG', 800.00);
INSERT INTO NF3_TREATMENT VALUES ('T03', 'Blood Test', 350.00);
INSERT INTO NF3_TREATMENT VALUES ('T04', 'X-Ray', 700.00);
INSERT INTO NF3_TREATMENT VALUES ('T05', 'Physiotherapy', 600.00);
INSERT INTO NF3_TREATMENT VALUES ('T06', 'Skin Examination', 450.00);
INSERT INTO NF3_TREATMENT VALUES ('T07', 'Dressing', 250.00);
INSERT INTO NF3_TREATMENT VALUES ('T08', 'Ultrasound', 1200.00);

-- Patient, doctor, appointment, and line rows can be imported from the
-- corresponding distinct columns of 01_1NF.csv in LibreOffice Base.
