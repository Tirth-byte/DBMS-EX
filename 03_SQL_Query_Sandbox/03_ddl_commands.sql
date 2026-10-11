-- Basic DDL commands. Only a temporary demonstration table is changed.
USE university_db;

-- Remove leftovers if this demonstration was stopped during an earlier run.
DROP TABLE IF EXISTS LAB_DEMO_RENAMED;
DROP TABLE IF EXISTS LAB_DEMO;

-- 1. CREATE TABLE creates a new table.
CREATE TABLE LAB_DEMO (
    Demo_ID INT PRIMARY KEY,
    Demo_Text VARCHAR(30)
);

-- 2. ALTER TABLE adds a new column.
ALTER TABLE LAB_DEMO
ADD COLUMN Created_On DATE;

-- 3. ALTER TABLE modifies the data type or size of a column.
ALTER TABLE LAB_DEMO
MODIFY COLUMN Demo_Text VARCHAR(50);

-- Add a row so the effect of TRUNCATE can be observed.
INSERT INTO LAB_DEMO (Demo_ID, Demo_Text, Created_On)
VALUES (1, 'Temporary record', '2026-10-11');

-- 4. RENAME TABLE changes the table name.
RENAME TABLE LAB_DEMO TO LAB_DEMO_RENAMED;

-- 5. TRUNCATE TABLE removes all rows but keeps the table structure.
TRUNCATE TABLE LAB_DEMO_RENAMED;

-- 6. DROP TABLE removes the temporary table.
DROP TABLE LAB_DEMO_RENAMED;

