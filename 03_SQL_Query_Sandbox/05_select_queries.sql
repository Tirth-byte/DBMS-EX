-- Beginner-friendly retrieval queries for university_db.
USE university_db;

-- 1. Display all students.
SELECT *
FROM STUDENT;

-- 2. Display selected columns.
SELECT Student_ID, Name, Semester
FROM STUDENT;

-- 3. Filter rows using WHERE.
SELECT Student_ID, Name, Semester
FROM STUDENT
WHERE Semester = 5;

-- 4. Combine conditions using AND and OR.
SELECT Student_ID, Name, Semester, Department_ID
FROM STUDENT
WHERE (Semester = 3 AND Department_ID = 1)
   OR Department_ID = 2;

-- 5. Sort students by name.
SELECT Student_ID, Name, Semester
FROM STUDENT
ORDER BY Name ASC;

-- 6. Display the first five students in ID order.
SELECT Student_ID, Name
FROM STUDENT
ORDER BY Student_ID
LIMIT 5;

-- 7. Count all students.
SELECT COUNT(*) AS Total_Students
FROM STUDENT;

-- 8. Count students in each department.
SELECT Department_ID, COUNT(*) AS Student_Count
FROM STUDENT
GROUP BY Department_ID
ORDER BY Department_ID;

-- 9. Join students with their department names.
SELECT s.Student_ID, s.Name, d.Department_Name
FROM STUDENT AS s
INNER JOIN DEPARTMENT AS d
    ON s.Department_ID = d.Department_ID
ORDER BY s.Student_ID;

-- 10. Join students, enrollments, and courses.
SELECT s.Name AS Student_Name,
       c.Course_Name,
       e.Enrollment_Date,
       e.Grade
FROM STUDENT AS s
INNER JOIN ENROLLMENT AS e
    ON s.Student_ID = e.Student_ID
INNER JOIN COURSE AS c
    ON e.Course_ID = c.Course_ID
ORDER BY s.Student_ID, c.Course_ID;

