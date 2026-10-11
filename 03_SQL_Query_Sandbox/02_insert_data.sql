-- Insert deterministic sample data into the university tables.
USE university_db;

INSERT INTO DEPARTMENT (Department_ID, Department_Name) VALUES
    (1, 'Computer Science and Engineering'),
    (2, 'Electronics and Communication Engineering'),
    (3, 'Mechanical Engineering'),
    (4, 'Civil Engineering');

INSERT INTO STUDENT (Student_ID, Name, Email, Phone, Semester, Department_ID) VALUES
    (1001, 'Aarav Sharma', 'aarav.sharma@university.edu', '9876501001', 3, 1),
    (1002, 'Ananya Iyer', 'ananya.iyer@university.edu', '9876501002', 3, 1),
    (1003, 'Rohan Mehta', 'rohan.mehta@university.edu', '9876501003', 5, 1),
    (1004, 'Diya Nair', 'diya.nair@university.edu', '9876501004', 5, 2),
    (1005, 'Arjun Reddy', 'arjun.reddy@university.edu', '9876501005', 3, 2),
    (1006, 'Kavya Patel', 'kavya.patel@university.edu', '9876501006', 5, 2),
    (1007, 'Ishaan Gupta', 'ishaan.gupta@university.edu', '9876501007', 3, 3),
    (1008, 'Meera Joshi', 'meera.joshi@university.edu', '9876501008', 5, 3),
    (1009, 'Nikhil Rao', 'nikhil.rao@university.edu', '9876501009', 3, 3),
    (1010, 'Saanvi Singh', 'saanvi.singh@university.edu', '9876501010', 3, 4),
    (1011, 'Rahul Das', 'rahul.das@university.edu', '9876501011', 5, 4),
    (1012, 'Tanvi Kulkarni', 'tanvi.kulkarni@university.edu', '9876501012', 5, 4);

INSERT INTO FACULTY (Faculty_ID, Name, Email, Designation, Department_ID) VALUES
    (201, 'Dr. Priya Menon', 'priya.menon@university.edu', 'Professor', 1),
    (202, 'Dr. Vikram Bose', 'vikram.bose@university.edu', 'Associate Professor', 1),
    (203, 'Dr. Neha Kapoor', 'neha.kapoor@university.edu', 'Professor', 2),
    (204, 'Prof. Amit Desai', 'amit.desai@university.edu', 'Assistant Professor', 2),
    (205, 'Dr. Sunil Mishra', 'sunil.mishra@university.edu', 'Associate Professor', 3),
    (206, 'Prof. Pooja Shah', 'pooja.shah@university.edu', 'Assistant Professor', 4);

INSERT INTO COURSE (Course_ID, Course_Name, Credits, Department_ID, Faculty_ID) VALUES
    (301, 'Database Management Systems', 4, 1, 201),
    (302, 'Data Structures', 4, 1, 202),
    (303, 'Computer Networks', 3, 1, 201),
    (304, 'Digital Electronics', 4, 2, 203),
    (305, 'Signals and Systems', 3, 2, 204),
    (306, 'Thermodynamics', 4, 3, 205),
    (307, 'Engineering Mechanics', 3, 3, 205),
    (308, 'Structural Analysis', 4, 4, 206);

INSERT INTO ENROLLMENT
    (Enrollment_ID, Enrollment_Date, Grade, Student_ID, Course_ID) VALUES
    (401, '2026-07-10', 'A', 1001, 301),
    (402, '2026-07-10', 'A+', 1001, 302),
    (403, '2026-07-11', 'B+', 1002, 301),
    (404, '2026-07-11', 'A', 1002, 303),
    (405, '2026-07-12', 'A+', 1003, 301),
    (406, '2026-07-12', 'B', 1003, 302),
    (407, '2026-07-13', 'A', 1004, 304),
    (408, '2026-07-13', 'B+', 1004, 305),
    (409, '2026-07-14', 'A+', 1005, 304),
    (410, '2026-07-14', 'A', 1005, 305),
    (411, '2026-07-15', 'B+', 1006, 304),
    (412, '2026-07-15', 'A', 1006, 305),
    (413, '2026-07-16', 'A', 1007, 306),
    (414, '2026-07-16', 'B+', 1007, 307),
    (415, '2026-07-17', 'A+', 1008, 306),
    (416, '2026-07-17', 'A', 1009, 307),
    (417, '2026-07-18', 'B+', 1010, 308),
    (418, '2026-07-18', 'A', 1011, 308),
    (419, '2026-07-19', 'A+', 1012, 308),
    (420, '2026-07-19', 'B+', 1012, 301);

