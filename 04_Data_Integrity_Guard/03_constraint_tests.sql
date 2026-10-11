USE library_db;

INSERT INTO MEMBER (Member_ID, Name, Email, Phone)
VALUES (1, 'Test Member', 'primary.test@example.com', '9000000001');

INSERT INTO MEMBER (Member_ID, Name, Email, Phone)
VALUES (101, 'Email Test', 'aarav.sharma@example.com', '9000000002');

INSERT INTO BORROW (Borrow_ID, Member_ID, Book_ID, Borrow_Date, Return_Date)
VALUES (301, 1, 999, '2026-10-11', NULL);

START TRANSACTION;
INSERT INTO MEMBER (Member_ID, Name, Email, Phone)
VALUES (199, 'Valid Test Member', 'valid.test@example.com', '9000000199');
ROLLBACK;

DELETE FROM MEMBER
WHERE Member_ID = 1;

