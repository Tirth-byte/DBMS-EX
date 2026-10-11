USE library_db;

INSERT INTO MEMBER (Member_ID, Name, Email, Phone) VALUES
    (1, 'Aarav Sharma', 'aarav.sharma@example.com', '9876502001'),
    (2, 'Ananya Iyer', 'ananya.iyer@example.com', '9876502002'),
    (3, 'Rohan Mehta', 'rohan.mehta@example.com', '9876502003'),
    (4, 'Diya Nair', 'diya.nair@example.com', '9876502004'),
    (5, 'Kavya Patel', 'kavya.patel@example.com', '9876502005');

INSERT INTO CATEGORY (Category_ID, Category_Name) VALUES
    (1, 'Computer Science'),
    (2, 'Literature'),
    (3, 'Science'),
    (4, 'History');

INSERT INTO BOOK (Book_ID, Title, ISBN, Category_ID) VALUES
    (101, 'Database System Concepts', '9780073523323', 1),
    (102, 'Introduction to Algorithms', '9780262046305', 1),
    (103, 'Computer Networks', '9780132126953', 1),
    (104, 'The Guide', '9788185986173', 2),
    (105, 'The Discovery of India', '9780143031031', 4),
    (106, 'A Brief History of Time', '9780553380163', 3),
    (107, 'The God of Small Things', '9780679457312', 2),
    (108, 'India After Gandhi', '9780060958589', 4);

INSERT INTO BORROW
    (Borrow_ID, Member_ID, Book_ID, Borrow_Date, Return_Date) VALUES
    (201, 1, 101, '2026-08-01', '2026-08-15'),
    (202, 2, 104, '2026-08-03', '2026-08-17'),
    (203, 3, 106, '2026-08-05', NULL),
    (204, 1, 103, '2026-08-08', NULL),
    (205, 4, 105, '2026-08-10', '2026-08-24'),
    (206, 5, 108, '2026-08-12', NULL);

