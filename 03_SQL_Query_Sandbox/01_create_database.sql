-- Experiment 03: create the university database and its five main tables.
-- Existing tables in university_db are recreated so the lab can start fresh.

CREATE DATABASE IF NOT EXISTS university_db;
USE university_db;

-- Drop only this experiment's tables, in child-to-parent order.
DROP TABLE IF EXISTS ENROLLMENT;
DROP TABLE IF EXISTS COURSE;
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS FACULTY;
DROP TABLE IF EXISTS DEPARTMENT;

CREATE TABLE DEPARTMENT (
    Department_ID INT PRIMARY KEY,
    Department_Name VARCHAR(100) NOT NULL
);

CREATE TABLE STUDENT (
    Student_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    Phone VARCHAR(15),
    Semester INT,
    Department_ID INT,
    CONSTRAINT fk_student_department
        FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID)
);

CREATE TABLE FACULTY (
    Faculty_ID INT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100),
    Designation VARCHAR(50),
    Department_ID INT,
    CONSTRAINT fk_faculty_department
        FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID)
);

CREATE TABLE COURSE (
    Course_ID INT PRIMARY KEY,
    Course_Name VARCHAR(100) NOT NULL,
    Credits INT,
    Department_ID INT,
    Faculty_ID INT,
    CONSTRAINT fk_course_department
        FOREIGN KEY (Department_ID) REFERENCES DEPARTMENT(Department_ID),
    CONSTRAINT fk_course_faculty
        FOREIGN KEY (Faculty_ID) REFERENCES FACULTY(Faculty_ID)
);

CREATE TABLE ENROLLMENT (
    Enrollment_ID INT PRIMARY KEY,
    Enrollment_Date DATE,
    Grade VARCHAR(5),
    Student_ID INT,
    Course_ID INT,
    CONSTRAINT fk_enrollment_student
        FOREIGN KEY (Student_ID) REFERENCES STUDENT(Student_ID),
    CONSTRAINT fk_enrollment_course
        FOREIGN KEY (Course_ID) REFERENCES COURSE(Course_ID)
);

