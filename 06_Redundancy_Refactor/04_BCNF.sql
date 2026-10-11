-- DBMS Experiment 06: final BCNF schema
-- Standard SQL intended for LibreOffice Base.
-- All relations satisfy BCNF under the business rules in normalization_report.md.

CREATE TABLE Department (
    DepartmentID VARCHAR(10) PRIMARY KEY,
    DepartmentName VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE Patient (
    PatientID VARCHAR(10) PRIMARY KEY,
    PatientName VARCHAR(80) NOT NULL,
    PatientPhone VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE Doctor (
    DoctorID VARCHAR(10) PRIMARY KEY,
    DoctorName VARCHAR(80) NOT NULL,
    DepartmentID VARCHAR(10) NOT NULL,
    FOREIGN KEY (DepartmentID) REFERENCES Department (DepartmentID)
);

CREATE TABLE Treatment (
    TreatmentCode VARCHAR(10) PRIMARY KEY,
    TreatmentName VARCHAR(80) NOT NULL UNIQUE,
    StandardFee DECIMAL(10,2) NOT NULL
);

CREATE TABLE Appointment (
    AppointmentID VARCHAR(10) PRIMARY KEY,
    PatientID VARCHAR(10) NOT NULL,
    DoctorID VARCHAR(10) NOT NULL,
    AppointmentDate DATE NOT NULL,
    Reason VARCHAR(120) NOT NULL,
    Status VARCHAR(20) NOT NULL,
    FOREIGN KEY (PatientID) REFERENCES Patient (PatientID),
    FOREIGN KEY (DoctorID) REFERENCES Doctor (DoctorID)
);

CREATE TABLE AppointmentTreatment (
    AppointmentID VARCHAR(10) NOT NULL,
    TreatmentCode VARCHAR(10) NOT NULL,
    Quantity INTEGER NOT NULL,
    ChargedFee DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (AppointmentID, TreatmentCode),
    FOREIGN KEY (AppointmentID) REFERENCES Appointment (AppointmentID),
    FOREIGN KEY (TreatmentCode) REFERENCES Treatment (TreatmentCode)
);

INSERT INTO Department VALUES ('DEP01', 'Cardiology');
INSERT INTO Department VALUES ('DEP02', 'Pediatrics');
INSERT INTO Department VALUES ('DEP03', 'Orthopedics');
INSERT INTO Department VALUES ('DEP04', 'Dermatology');
INSERT INTO Department VALUES ('DEP05', 'General Medicine');

INSERT INTO Patient VALUES ('P001', 'Aisha Khan', '9876500011');
INSERT INTO Patient VALUES ('P002', 'Rohan Mehta', '9876500012');
INSERT INTO Patient VALUES ('P003', 'Neha Singh', '9876500013');
INSERT INTO Patient VALUES ('P004', 'Arjun Rao', '9876500014');
INSERT INTO Patient VALUES ('P005', 'Isha Patel', '9876500015');
INSERT INTO Patient VALUES ('P006', 'Kabir Shah', '9876500016');
INSERT INTO Patient VALUES ('P007', 'Meera Nair', '9876500017');
INSERT INTO Patient VALUES ('P008', 'Vivaan Gupta', '9876500018');
INSERT INTO Patient VALUES ('P009', 'Sana Ali', '9876500019');
INSERT INTO Patient VALUES ('P010', 'Aditya Bose', '9876500020');
INSERT INTO Patient VALUES ('P011', 'Priya Das', '9876500021');
INSERT INTO Patient VALUES ('P012', 'Rahul Verma', '9876500022');

INSERT INTO Doctor VALUES ('D01', 'Dr Kavita Rao', 'DEP01');
INSERT INTO Doctor VALUES ('D02', 'Dr Neel Shah', 'DEP02');
INSERT INTO Doctor VALUES ('D03', 'Dr Arjun Menon', 'DEP03');
INSERT INTO Doctor VALUES ('D04', 'Dr Sara Joseph', 'DEP04');
INSERT INTO Doctor VALUES ('D05', 'Dr Rahul Bose', 'DEP05');

INSERT INTO Treatment VALUES ('T01', 'Consultation', 500.00);
INSERT INTO Treatment VALUES ('T02', 'ECG', 800.00);
INSERT INTO Treatment VALUES ('T03', 'Blood Test', 350.00);
INSERT INTO Treatment VALUES ('T04', 'X-Ray', 700.00);
INSERT INTO Treatment VALUES ('T05', 'Physiotherapy', 600.00);
INSERT INTO Treatment VALUES ('T06', 'Skin Examination', 450.00);
INSERT INTO Treatment VALUES ('T07', 'Dressing', 250.00);
INSERT INTO Treatment VALUES ('T08', 'Ultrasound', 1200.00);

-- Import the appointment and appointment-treatment rows from 01_1NF.csv.
INSERT INTO Appointment VALUES ('A1001', 'P001', 'D01', '2025-01-06', 'Chest discomfort', 'Completed');
INSERT INTO Appointment VALUES ('A1002', 'P002', 'D02', '2025-01-07', 'Seasonal fever', 'Completed');
INSERT INTO Appointment VALUES ('A1003', 'P003', 'D03', '2025-01-08', 'Knee pain', 'Completed');
INSERT INTO Appointment VALUES ('A1004', 'P004', 'D04', '2025-01-09', 'Skin rash', 'Completed');
INSERT INTO Appointment VALUES ('A1005', 'P005', 'D01', '2025-01-10', 'Palpitations', 'Completed');
INSERT INTO Appointment VALUES ('A1006', 'P006', 'D03', '2025-01-11', 'Back pain', 'Completed');
INSERT INTO Appointment VALUES ('A1007', 'P007', 'D02', '2025-01-13', 'Cough', 'Completed');
INSERT INTO Appointment VALUES ('A1008', 'P008', 'D04', '2025-01-14', 'Acne', 'Completed');
INSERT INTO Appointment VALUES ('A1009', 'P009', 'D05', '2025-01-15', 'Headache', 'Completed');
INSERT INTO Appointment VALUES ('A1010', 'P010', 'D05', '2025-01-16', 'Diabetes review', 'Completed');
INSERT INTO Appointment VALUES ('A1011', 'P011', 'D01', '2025-01-17', 'High blood pressure', 'Completed');
INSERT INTO Appointment VALUES ('A1012', 'P012', 'D03', '2025-01-18', 'Shoulder pain', 'Completed');
INSERT INTO Appointment VALUES ('A1013', 'P001', 'D01', '2025-01-20', 'Follow-up', 'Completed');
INSERT INTO Appointment VALUES ('A1014', 'P002', 'D02', '2025-01-21', 'Growth review', 'Completed');
INSERT INTO Appointment VALUES ('A1015', 'P003', 'D03', '2025-01-22', 'Knee follow-up', 'Completed');
INSERT INTO Appointment VALUES ('A1016', 'P004', 'D04', '2025-01-23', 'Eczema review', 'Completed');
INSERT INTO Appointment VALUES ('A1017', 'P005', 'D01', '2025-01-24', 'Chest follow-up', 'Completed');
INSERT INTO Appointment VALUES ('A1018', 'P006', 'D03', '2025-01-25', 'Back follow-up', 'Completed');
INSERT INTO Appointment VALUES ('A1019', 'P009', 'D05', '2025-01-27', 'Migraine', 'Completed');
INSERT INTO Appointment VALUES ('A1020', 'P010', 'D05', '2025-01-28', 'Thyroid review', 'Completed');
INSERT INTO AppointmentTreatment VALUES ('A1001', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1001', 'T02', 1, 800.00);
INSERT INTO AppointmentTreatment VALUES ('A1002', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1002', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1003', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1003', 'T04', 1, 700.00);
INSERT INTO AppointmentTreatment VALUES ('A1003', 'T05', 1, 600.00);
INSERT INTO AppointmentTreatment VALUES ('A1004', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1004', 'T06', 1, 450.00);
INSERT INTO AppointmentTreatment VALUES ('A1005', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1005', 'T02', 1, 800.00);
INSERT INTO AppointmentTreatment VALUES ('A1005', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1006', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1006', 'T05', 2, 1200.00);
INSERT INTO AppointmentTreatment VALUES ('A1007', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1007', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1008', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1008', 'T06', 1, 450.00);
INSERT INTO AppointmentTreatment VALUES ('A1009', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1009', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1010', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1010', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1010', 'T08', 1, 1200.00);
INSERT INTO AppointmentTreatment VALUES ('A1011', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1011', 'T02', 1, 800.00);
INSERT INTO AppointmentTreatment VALUES ('A1012', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1012', 'T04', 1, 700.00);
INSERT INTO AppointmentTreatment VALUES ('A1013', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1013', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1014', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1014', 'T08', 1, 1200.00);
INSERT INTO AppointmentTreatment VALUES ('A1015', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1015', 'T04', 1, 700.00);
INSERT INTO AppointmentTreatment VALUES ('A1015', 'T05', 1, 600.00);
INSERT INTO AppointmentTreatment VALUES ('A1016', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1016', 'T06', 1, 450.00);
INSERT INTO AppointmentTreatment VALUES ('A1016', 'T07', 1, 250.00);
INSERT INTO AppointmentTreatment VALUES ('A1017', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1017', 'T02', 1, 800.00);
INSERT INTO AppointmentTreatment VALUES ('A1018', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1018', 'T05', 3, 1800.00);
INSERT INTO AppointmentTreatment VALUES ('A1019', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1019', 'T03', 1, 350.00);
INSERT INTO AppointmentTreatment VALUES ('A1020', 'T01', 1, 500.00);
INSERT INTO AppointmentTreatment VALUES ('A1020', 'T08', 1, 1200.00);
INSERT INTO AppointmentTreatment VALUES ('A1020', 'T03', 1, 350.00);

-- The following queries are used after the import to verify the design.

-- Row counts expected after import:
-- Patient = 12, Doctor = 5, Department = 5, Treatment = 8,
-- Appointment = 20, AppointmentTreatment = 46.
SELECT COUNT(*) AS PatientCount FROM Patient;
SELECT COUNT(*) AS DoctorCount FROM Doctor;
SELECT COUNT(*) AS DepartmentCount FROM Department;
SELECT COUNT(*) AS TreatmentCount FROM Treatment;
SELECT COUNT(*) AS AppointmentCount FROM Appointment;
SELECT COUNT(*) AS AppointmentTreatmentCount FROM AppointmentTreatment;

-- Foreign-key reconstruction query for the original information.
SELECT a.AppointmentID, p.PatientName, d.DoctorName, dep.DepartmentName,
       a.AppointmentDate, t.TreatmentName, at.Quantity, at.ChargedFee
FROM (((Appointment AS a
INNER JOIN Patient AS p ON a.PatientID = p.PatientID)
INNER JOIN Doctor AS d ON a.DoctorID = d.DoctorID)
INNER JOIN Department AS dep ON d.DepartmentID = dep.DepartmentID)
INNER JOIN AppointmentTreatment AS at ON a.AppointmentID = at.AppointmentID
INNER JOIN Treatment AS t ON at.TreatmentCode = t.TreatmentCode;

-- Duplicate-key checks should return zero rows.
SELECT AppointmentID, TreatmentCode, COUNT(*) AS DuplicateCount
FROM AppointmentTreatment
GROUP BY AppointmentID, TreatmentCode
HAVING COUNT(*) > 1;
