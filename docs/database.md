# School Library Management System — Database Design

## 1. Document Purpose

This `database.md` file defines the database design for the **School Library Management System** desktop application.

The application will use **SQLite** as the main local database because it is reliable, fast, offline-friendly, and suitable for desktop software.

Excel will be used only for:

- Importing book and student data
- Exporting reports
- Creating backups
- Sharing records with school management

Excel should not be used as the main database.

---

## 2. Database Overview

## Recommended Database

```text
SQLite
```

## Database File Location

```text
database/library.db
```

## Schema File Location

```text
database/schema.sql
```

## Main Tables

The database will contain these core tables:

| Table | Purpose |
|---|---|
| `books` | Stores book details and quantity information |
| `students` | Stores student details |
| `book_issues` | Stores issue and return records |
| `settings` | Stores app configuration |
| `activity_logs` | Optional table for tracking important actions |

---

## 3. Why SQLite is Recommended

SQLite is the best main database for this desktop application because:

- It works fully offline.
- It stores all data in one local `.db` file.
- It is safer than Excel for software data.
- It supports relationships between books, students, and issue records.
- It supports validation through constraints.
- It supports fast searching and filtering.
- It reduces the risk of accidental manual editing.
- It is simple to backup and restore.
- It does not require a separate database server.

---

## 4. Database Entity Relationship Summary

## Main Relationship

```text
students ───< book_issues >─── books
```

Meaning:

- One student can have many book issue records.
- One book can have many issue records.
- Each issue record belongs to one student and one book.

---

## 5. Entity Relationship Diagram

```text
+------------------+          +---------------------+          +------------------+
|    students      |          |     book_issues     |          |      books       |
+------------------+          +---------------------+          +------------------+
| id PK            |<---------| student_id FK       |          | id PK            |
| student_code     |          | book_id FK          |--------->| title            |
| name             |          | issue_date          |          | author           |
| class_name       |          | due_date            |          | category         |
| division         |          | return_date         |          | isbn             |
| phone            |          | status              |          | total_quantity   |
| email            |          | remarks             |          | available_qty    |
| status           |          | created_at          |          | status           |
| created_at       |          | updated_at          |          | created_at       |
| updated_at       |          +---------------------+          | updated_at       |
+------------------+                                             +------------------+
```

---

## 6. Table Naming Rules

Use lowercase table names with underscores.

Examples:

```text
books
students
book_issues
settings
activity_logs
```

Use lowercase column names with underscores.

Examples:

```text
student_code
class_name
total_quantity
available_quantity
created_at
updated_at
```

---

## 7. Data Type Rules

SQLite data types used in this project:

| Type | Usage |
|---|---|
| `INTEGER` | IDs, quantity, numeric values |
| `TEXT` | Names, dates, status, descriptions |
| `REAL` | Optional fine amount or decimal values |
| `BOOLEAN` | Use INTEGER 0 or 1 if needed |

Dates should be stored as text in ISO format:

```text
YYYY-MM-DD
```

Date-time values should be stored as:

```text
YYYY-MM-DD HH:MM:SS
```

---

## 8. Table: `books`

## 8.1 Purpose

The `books` table stores all book details and quantity information.

It tracks:

- Book title
- Author
- Category
- ISBN
- Publisher
- Rack number
- Total quantity
- Available quantity
- Status

---

## 8.2 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | INTEGER | Yes | Primary key |
| `title` | TEXT | Yes | Book title |
| `author` | TEXT | No | Book author |
| `category` | TEXT | No | Book category or subject |
| `isbn` | TEXT | No | ISBN number, unique if entered |
| `publisher` | TEXT | No | Publisher name |
| `rack_number` | TEXT | No | Rack or shelf location |
| `total_quantity` | INTEGER | Yes | Total copies owned by library |
| `available_quantity` | INTEGER | Yes | Copies currently available |
| `status` | TEXT | Yes | ACTIVE or INACTIVE |
| `created_at` | TEXT | Yes | Record created date/time |
| `updated_at` | TEXT | Yes | Record updated date/time |

---

## 8.3 Status Values

```text
ACTIVE
INACTIVE
```

## 8.4 Quantity Rules

```text
available_quantity >= 0
available_quantity <= total_quantity
total_quantity >= 0
```

## 8.5 Create Table SQL

```sql
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT,
    isbn TEXT UNIQUE,
    publisher TEXT,
    rack_number TEXT,
    total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0),
    available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (available_quantity <= total_quantity)
);
```

---

## 9. Table: `students`

## 9.1 Purpose

The `students` table stores student information.

It tracks:

- Student admission number / student ID
- Student name
- Class
- Division
- Contact details
- Status

---

## 9.2 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | INTEGER | Yes | Primary key |
| `student_code` | TEXT | Yes | Student ID or admission number |
| `name` | TEXT | Yes | Student name |
| `class_name` | TEXT | No | Student class |
| `division` | TEXT | No | Class division |
| `phone` | TEXT | No | Phone number |
| `email` | TEXT | No | Email address |
| `address` | TEXT | No | Address |
| `status` | TEXT | Yes | ACTIVE or INACTIVE |
| `created_at` | TEXT | Yes | Record created date/time |
| `updated_at` | TEXT | Yes | Record updated date/time |

---

## 9.3 Status Values

```text
ACTIVE
INACTIVE
```

## 9.4 Create Table SQL

```sql
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    class_name TEXT,
    division TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 10. Table: `book_issues`

## 10.1 Purpose

The `book_issues` table stores both issue and return records.

A record is created when a book is issued.

When the book is returned, the same record is updated with:

- Return date
- Return status
- Remarks, if any

---

## 10.2 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | INTEGER | Yes | Primary key |
| `book_id` | INTEGER | Yes | Linked book ID |
| `student_id` | INTEGER | Yes | Linked student ID |
| `issue_date` | TEXT | Yes | Date book was issued |
| `due_date` | TEXT | No | Expected return date |
| `return_date` | TEXT | No | Actual return date |
| `status` | TEXT | Yes | ISSUED, RETURNED, LOST, or DAMAGED |
| `remarks` | TEXT | No | Optional notes |
| `created_at` | TEXT | Yes | Record created date/time |
| `updated_at` | TEXT | Yes | Record updated date/time |

---

## 10.3 Status Values

Required version 1 statuses:

```text
ISSUED
RETURNED
```

Optional future statuses:

```text
LOST
DAMAGED
```

## 10.4 Create Table SQL

```sql
CREATE TABLE IF NOT EXISTS book_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'ISSUED'
        CHECK (status IN ('ISSUED', 'RETURNED', 'LOST', 'DAMAGED')),
    remarks TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (student_id) REFERENCES students(id),

    CHECK (
        return_date IS NULL
        OR return_date >= issue_date
    )
);
```

---

## 11. Prevent Duplicate Pending Issue

The system must prevent the same student from taking the same book again before returning it.

## Rule

```text
A student cannot have two active ISSUED records for the same book.
```

## Recommended Unique Index

SQLite supports partial unique indexes.

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_issue
ON book_issues(student_id, book_id)
WHERE status = 'ISSUED';
```

This means:

- Same student can borrow the same book again after returning.
- Same student cannot borrow the same book twice at the same time.

---

## 12. Table: `settings`

## 12.1 Purpose

The `settings` table stores application configuration.

Examples:

- School name
- Library name
- Default due days
- Low-stock limit
- Backup path
- Export path

---

## 12.2 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | INTEGER | Yes | Primary key |
| `setting_key` | TEXT | Yes | Unique setting key |
| `setting_value` | TEXT | No | Setting value |

---

## 12.3 Create Table SQL

```sql
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT
);
```

---

## 12.4 Default Settings

```sql
INSERT OR IGNORE INTO settings (setting_key, setting_value)
VALUES
('school_name', 'ABC Public School'),
('library_name', 'School Library'),
('default_due_days', '7'),
('low_stock_limit', '2'),
('backup_path', 'backups'),
('export_path', 'exports');
```

---

## 13. Optional Table: `activity_logs`

## 13.1 Purpose

The `activity_logs` table can be used to track important actions.

Examples:

- Book added
- Book edited
- Student added
- Book issued
- Book returned
- Report exported
- Backup created

This is optional for version 1 but useful for future auditing.

---

## 13.2 Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | INTEGER | Yes | Primary key |
| `action_type` | TEXT | Yes | Type of action |
| `description` | TEXT | No | Action details |
| `created_at` | TEXT | Yes | Action date/time |

---

## 13.3 Create Table SQL

```sql
CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);
```

---

## 14. Indexes

Indexes improve search speed.

## Recommended Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_books_title
ON books(title);

CREATE INDEX IF NOT EXISTS idx_books_author
ON books(author);

CREATE INDEX IF NOT EXISTS idx_books_category
ON books(category);

CREATE INDEX IF NOT EXISTS idx_books_isbn
ON books(isbn);

CREATE INDEX IF NOT EXISTS idx_books_status
ON books(status);

CREATE INDEX IF NOT EXISTS idx_students_code
ON students(student_code);

CREATE INDEX IF NOT EXISTS idx_students_name
ON students(name);

CREATE INDEX IF NOT EXISTS idx_students_class
ON students(class_name);

CREATE INDEX IF NOT EXISTS idx_students_status
ON students(status);

CREATE INDEX IF NOT EXISTS idx_issues_book_id
ON book_issues(book_id);

CREATE INDEX IF NOT EXISTS idx_issues_student_id
ON book_issues(student_id);

CREATE INDEX IF NOT EXISTS idx_issues_status
ON book_issues(status);

CREATE INDEX IF NOT EXISTS idx_issues_issue_date
ON book_issues(issue_date);

CREATE INDEX IF NOT EXISTS idx_issues_due_date
ON book_issues(due_date);

CREATE INDEX IF NOT EXISTS idx_issues_return_date
ON book_issues(return_date);
```

---

## 15. Complete `schema.sql`

Use this full schema inside:

```text
database/schema.sql
```

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT,
    isbn TEXT UNIQUE,
    publisher TEXT,
    rack_number TEXT,
    total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0),
    available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK (available_quantity <= total_quantity)
);

CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    class_name TEXT,
    division TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    status TEXT NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS book_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    issue_date TEXT NOT NULL,
    due_date TEXT,
    return_date TEXT,
    status TEXT NOT NULL DEFAULT 'ISSUED'
        CHECK (status IN ('ISSUED', 'RETURNED', 'LOST', 'DAMAGED')),
    remarks TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (student_id) REFERENCES students(id),

    CHECK (
        return_date IS NULL
        OR return_date >= issue_date
    )
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_type TEXT NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_issue
ON book_issues(student_id, book_id)
WHERE status = 'ISSUED';

CREATE INDEX IF NOT EXISTS idx_books_title
ON books(title);

CREATE INDEX IF NOT EXISTS idx_books_author
ON books(author);

CREATE INDEX IF NOT EXISTS idx_books_category
ON books(category);

CREATE INDEX IF NOT EXISTS idx_books_isbn
ON books(isbn);

CREATE INDEX IF NOT EXISTS idx_books_status
ON books(status);

CREATE INDEX IF NOT EXISTS idx_students_code
ON students(student_code);

CREATE INDEX IF NOT EXISTS idx_students_name
ON students(name);

CREATE INDEX IF NOT EXISTS idx_students_class
ON students(class_name);

CREATE INDEX IF NOT EXISTS idx_students_status
ON students(status);

CREATE INDEX IF NOT EXISTS idx_issues_book_id
ON book_issues(book_id);

CREATE INDEX IF NOT EXISTS idx_issues_student_id
ON book_issues(student_id);

CREATE INDEX IF NOT EXISTS idx_issues_status
ON book_issues(status);

CREATE INDEX IF NOT EXISTS idx_issues_issue_date
ON book_issues(issue_date);

CREATE INDEX IF NOT EXISTS idx_issues_due_date
ON book_issues(due_date);

CREATE INDEX IF NOT EXISTS idx_issues_return_date
ON book_issues(return_date);

INSERT OR IGNORE INTO settings (setting_key, setting_value)
VALUES
('school_name', 'ABC Public School'),
('library_name', 'School Library'),
('default_due_days', '7'),
('low_stock_limit', '2'),
('backup_path', 'backups'),
('export_path', 'exports');
```

---

## 16. Important Business Rules

## 16.1 Book Rules

```text
Book title is required.
Total quantity is required.
Total quantity cannot be negative.
Available quantity cannot be negative.
Available quantity cannot be greater than total quantity.
ISBN must be unique if provided.
Books with active issue records should not be permanently deleted.
```

---

## 16.2 Student Rules

```text
Student ID is required.
Student name is required.
Student ID must be unique.
Inactive students cannot receive books.
Students with active issue records should not be permanently deleted.
```

---

## 16.3 Issue Rules

```text
Book must be active.
Student must be active.
Available quantity must be greater than 0.
Same student cannot borrow the same book twice without return.
Issue date is required.
Due date cannot be earlier than issue date.
```

---

## 16.4 Return Rules

```text
Only ISSUED records can be returned.
Return date cannot be earlier than issue date.
Already returned records cannot be returned again.
Available quantity must increase only once.
Available quantity cannot exceed total quantity.
```

---

## 17. Quantity Update Logic

## 17.1 Issue Book Quantity Logic

When a book is issued:

```text
available_quantity = available_quantity - 1
```

Only allow this if:

```text
available_quantity > 0
```

## SQL Example

```sql
UPDATE books
SET available_quantity = available_quantity - 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
AND status = 'ACTIVE'
AND available_quantity > 0;
```

---

## 17.2 Return Book Quantity Logic

When a book is returned:

```text
available_quantity = available_quantity + 1
```

Only allow this if:

```text
available_quantity < total_quantity
```

## SQL Example

```sql
UPDATE books
SET available_quantity = available_quantity + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
AND available_quantity < total_quantity;
```

---

## 18. Transaction Rules

Issue and return actions must use transactions to prevent data corruption.

## 18.1 Issue Book Transaction

```text
BEGIN TRANSACTION
↓
Check student is active
↓
Check book is active
↓
Check available quantity > 0
↓
Check duplicate pending issue
↓
Insert book_issues record
↓
Decrease available_quantity by 1
↓
COMMIT
```

If any step fails:

```text
ROLLBACK
```

## 18.2 Return Book Transaction

```text
BEGIN TRANSACTION
↓
Check issue record exists
↓
Check issue status is ISSUED
↓
Update book_issues status to RETURNED
↓
Set return_date
↓
Increase available_quantity by 1
↓
COMMIT
```

If any step fails:

```text
ROLLBACK
```

---

## 19. Common SQL Queries

## 19.1 Get All Active Books

```sql
SELECT *
FROM books
WHERE status = 'ACTIVE'
ORDER BY title ASC;
```

## 19.2 Search Books

```sql
SELECT *
FROM books
WHERE status = 'ACTIVE'
AND (
    title LIKE ?
    OR author LIKE ?
    OR category LIKE ?
    OR isbn LIKE ?
    OR rack_number LIKE ?
)
ORDER BY title ASC;
```

## 19.3 Get Available Books

```sql
SELECT *
FROM books
WHERE status = 'ACTIVE'
AND available_quantity > 0
ORDER BY title ASC;
```

## 19.4 Get Low-Stock Books

```sql
SELECT *
FROM books
WHERE status = 'ACTIVE'
AND available_quantity <= ?
ORDER BY available_quantity ASC;
```

## 19.5 Get All Active Students

```sql
SELECT *
FROM students
WHERE status = 'ACTIVE'
ORDER BY name ASC;
```

## 19.6 Search Students

```sql
SELECT *
FROM students
WHERE status = 'ACTIVE'
AND (
    student_code LIKE ?
    OR name LIKE ?
    OR class_name LIKE ?
    OR division LIKE ?
    OR phone LIKE ?
)
ORDER BY name ASC;
```

## 19.7 Get Pending Returns

```sql
SELECT
    bi.id AS issue_id,
    s.student_code,
    s.name AS student_name,
    b.title AS book_title,
    bi.issue_date,
    bi.due_date,
    bi.status
FROM book_issues bi
JOIN books b ON bi.book_id = b.id
JOIN students s ON bi.student_id = s.id
WHERE bi.status = 'ISSUED'
ORDER BY bi.due_date ASC;
```

## 19.8 Get Overdue Books

```sql
SELECT
    bi.id AS issue_id,
    s.student_code,
    s.name AS student_name,
    b.title AS book_title,
    bi.issue_date,
    bi.due_date,
    CAST(julianday('now') - julianday(bi.due_date) AS INTEGER) AS overdue_days
FROM book_issues bi
JOIN books b ON bi.book_id = b.id
JOIN students s ON bi.student_id = s.id
WHERE bi.status = 'ISSUED'
AND bi.due_date IS NOT NULL
AND date(bi.due_date) < date('now')
ORDER BY bi.due_date ASC;
```

## 19.9 Get Student Issue History

```sql
SELECT
    bi.id AS issue_id,
    b.title AS book_title,
    bi.issue_date,
    bi.due_date,
    bi.return_date,
    bi.status
FROM book_issues bi
JOIN books b ON bi.book_id = b.id
WHERE bi.student_id = ?
ORDER BY bi.issue_date DESC;
```

## 19.10 Dashboard Summary Query Examples

### Total Book Copies

```sql
SELECT COALESCE(SUM(total_quantity), 0) AS total_books
FROM books
WHERE status = 'ACTIVE';
```

### Available Book Copies

```sql
SELECT COALESCE(SUM(available_quantity), 0) AS available_books
FROM books
WHERE status = 'ACTIVE';
```

### Issued Book Copies

```sql
SELECT COUNT(*) AS issued_books
FROM book_issues
WHERE status = 'ISSUED';
```

### Total Active Students

```sql
SELECT COUNT(*) AS total_students
FROM students
WHERE status = 'ACTIVE';
```

### Pending Returns

```sql
SELECT COUNT(*) AS pending_returns
FROM book_issues
WHERE status = 'ISSUED';
```

### Overdue Books

```sql
SELECT COUNT(*) AS overdue_books
FROM book_issues
WHERE status = 'ISSUED'
AND due_date IS NOT NULL
AND date(due_date) < date('now');
```

---

## 20. Soft Delete / Deactivation Strategy

Do not permanently delete books or students by default.

Use status update instead.

## Deactivate Book

```sql
UPDATE books
SET status = 'INACTIVE',
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?;
```

## Deactivate Student

```sql
UPDATE students
SET status = 'INACTIVE',
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?;
```

## Why Deactivation is Better

- Keeps old reports correct.
- Prevents broken issue history.
- Avoids foreign key problems.
- Allows restoring records later.

---

## 21. Backup Strategy

## 21.1 SQLite Backup

The SQLite database file can be copied to the backup folder.

Example backup file:

```text
backups/library_backup_2026-07-06_10-30.db
```

## 21.2 Excel Backup

The system can export all important tables to Excel.

Example backup file:

```text
backups/library_full_backup_2026-07-06.xlsx
```

Recommended Excel sheets:

- Books
- Students
- Book Issues
- Settings

---

## 22. Restore Strategy

Restore should replace the current database with a selected backup file.

## Restore Flow

```text
User selects backup file
↓
System confirms restore action
↓
Current database is backed up first
↓
Selected backup replaces library.db
↓
Application reloads or restarts
```

## Restore Warning

Show this warning:

```text
Restoring backup will replace the current data.
Please create a backup before continuing.
```

---

## 23. Excel Import Mapping

## 23.1 Book Import Columns

| Excel Column | Database Field |
|---|---|
| Book Title | `title` |
| Author | `author` |
| Category | `category` |
| ISBN | `isbn` |
| Publisher | `publisher` |
| Rack Number | `rack_number` |
| Total Quantity | `total_quantity` |
| Available Quantity | `available_quantity` |

If `Available Quantity` is missing:

```text
available_quantity = total_quantity
```

---

## 23.2 Student Import Columns

| Excel Column | Database Field |
|---|---|
| Student ID | `student_code` |
| Student Name | `name` |
| Class | `class_name` |
| Division | `division` |
| Phone | `phone` |
| Email | `email` |
| Address | `address` |

---

## 24. Excel Export Mapping

## 24.1 Books Export

Export columns:

```text
Book ID
Title
Author
Category
ISBN
Publisher
Rack Number
Total Quantity
Available Quantity
Status
Created At
Updated At
```

## 24.2 Students Export

Export columns:

```text
Student ID
Student Name
Class
Division
Phone
Email
Address
Status
Created At
Updated At
```

## 24.3 Issue Records Export

Export columns:

```text
Issue ID
Student ID
Student Name
Book Title
Issue Date
Due Date
Return Date
Status
Remarks
```

---

## 25. Migration Strategy

For future database changes, use migration files.

Recommended folder:

```text
database/migrations/
```

Example:

```text
001_initial_schema.sql
002_add_fine_columns.sql
003_add_login_users.sql
```

The app can later track applied migrations using a table:

```sql
CREATE TABLE IF NOT EXISTS migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL
);
```

Migration support is optional for version 1 but useful for future upgrades.

---

## 26. Future Database Enhancements

Future versions may add these tables:

| Table | Purpose |
|---|---|
| `users` | Login system |
| `fines` | Fine calculation |
| `categories` | Book category management |
| `publishers` | Publisher management |
| `book_barcodes` | Barcode scanner support |
| `reservations` | Book reservation system |
| `notifications` | SMS/WhatsApp reminder records |
| `damaged_lost_books` | Track damaged or lost books |

---

## 27. Optional Future Table: `users`

For login system:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'LIBRARIAN'
        CHECK (role IN ('ADMIN', 'LIBRARIAN')),
    status TEXT NOT NULL DEFAULT 'ACTIVE'
        CHECK (status IN ('ACTIVE', 'INACTIVE')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

---

## 28. Optional Future Table: `fines`

For overdue fine calculation:

```sql
CREATE TABLE IF NOT EXISTS fines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    overdue_days INTEGER NOT NULL DEFAULT 0,
    fine_per_day REAL NOT NULL DEFAULT 0,
    total_fine REAL NOT NULL DEFAULT 0,
    paid_status TEXT NOT NULL DEFAULT 'UNPAID'
        CHECK (paid_status IN ('PAID', 'UNPAID')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,

    FOREIGN KEY (issue_id) REFERENCES book_issues(id)
);
```

---

## 29. Database File Safety Rules

The application should follow these safety rules:

- Do not allow users to directly edit `library.db`.
- Always use transactions for issue and return.
- Create backups regularly.
- Keep database file inside the project data folder.
- Do not store the database only inside a temporary folder.
- Before restore, create an automatic backup of the current database.
- Validate Excel data before importing.
- Avoid permanent delete for books and students.

---

## 30. Final Database Recommendation

Use this final database setup:

```text
Main Database: SQLite
Database File: database/library.db
Schema File: database/schema.sql
Excel Library: openpyxl
Backup: SQLite file backup + Excel full backup
```

Final core tables:

```text
books
students
book_issues
settings
activity_logs
```

Final important rules:

```text
SQLite stores all real application data.
Excel is only for import, export, reports, and backup.
Issue and return actions must use transactions.
Book quantity must update automatically.
Duplicate pending issue must be blocked.
Books and students should be deactivated, not permanently deleted.
```

This database design is safe, practical, and suitable for a real offline school library desktop application.
