-- Basic DML commands using one temporary student record.
USE university_db;

-- 1. INSERT adds a demonstration student in an existing department.
INSERT INTO STUDENT
    (Student_ID, Name, Email, Phone, Semester, Department_ID)
VALUES
    (1099, 'Vivek Malhotra', 'vivek.malhotra@university.edu', '9876501099', 1, 1);

-- 2. UPDATE changes the semester of the same student.
UPDATE STUDENT
SET Semester = 2
WHERE Student_ID = 1099;

-- 3. SELECT displays the updated demonstration record.
SELECT *
FROM STUDENT
WHERE Student_ID = 1099;

-- 4. DELETE removes only the demonstration student.
DELETE FROM STUDENT
WHERE Student_ID = 1099;

-- Display the original student records after the demonstration.
SELECT *
FROM STUDENT
ORDER BY Student_ID;

