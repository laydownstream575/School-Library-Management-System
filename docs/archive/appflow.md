# School Library Management System — App Flow

## 1. Document Purpose

This `appflow.md` file explains the complete application flow for the **School Library Management System** desktop application.

It defines how the librarian/admin moves through the software, how each screen works, and how data flows during important actions such as:

- Adding books
- Adding students
- Issuing books
- Returning books
- Updating book quantity
- Searching records
- Generating reports
- Importing and exporting Excel files
- Creating backups

The application is designed as an **offline desktop application** using:

```text
Desktop UI: Python PySide6 or Tkinter
Application Logic: Python
Main Database: SQLite
Excel Support: openpyxl
```

---

## 2. Main User Role

## Admin / Librarian

The first version of the application will have one main user role: **Admin / Librarian**.

The librarian can:

- Open the desktop application.
- View dashboard statistics.
- Add, edit, delete, and search books.
- Manage book quantity.
- Add, edit, delete, and search students.
- Issue books to students.
- Return issued books.
- View pending returns.
- Generate reports.
- Export reports to Excel.
- Import book/student data from Excel.
- Manage application settings.
- Create backups.

---

## 3. High-Level Application Flow

```text
Start Application
↓
Load SQLite Database
↓
Show Dashboard
↓
Librarian selects a module
↓
Perform action
↓
Validate input
↓
Save/update data in SQLite
↓
Refresh screen data
↓
Optional Excel export/report/backup
```

---

## 4. Application Launch Flow

When the librarian opens the software:

```text
User opens desktop application
↓
Application checks if SQLite database exists
↓
If database exists:
    Load existing data
↓
If database does not exist:
    Create database
    Create required tables
    Load default settings
↓
Open Dashboard screen
```

### Startup Checks

| Check | Action |
|---|---|
| Database file exists | Load database |
| Database file missing | Create new database |
| Tables missing | Create required tables |
| Settings missing | Load default settings |
| Backup folder missing | Create backup folder |
| Export folder missing | Create export folder |

---

## 5. Main Navigation Flow

The application should use a simple navigation structure.

Recommended layout:

- Sidebar navigation on the left
- Main content area on the right
- Top bar with app title and quick actions

### Main Navigation Items

```text
Dashboard
Books Management
Student Management
Issue Book
Return Book
Reports
Settings
```

### Navigation Flow

```text
Dashboard
├── Books Management
├── Student Management
├── Issue Book
├── Return Book
├── Reports
└── Settings
```

---

## 6. Dashboard Flow

The Dashboard is the first screen after opening the application.

### Dashboard Shows

- Total books
- Available books
- Issued books
- Total students
- Pending returns
- Overdue books
- Low-stock books
- Recent issue records
- Recent return records

### Dashboard Flow

```text
Open Dashboard
↓
Fetch summary data from SQLite
↓
Calculate statistics
↓
Display dashboard cards
↓
Display recent activity
```

### Dashboard Actions

| Action | Result |
|---|---|
| Click Total Books | Opens Books Management |
| Click Issued Books | Opens Reports with issued books filter |
| Click Pending Returns | Opens Return Book or Pending Returns report |
| Click Students | Opens Student Management |
| Click Low Stock | Opens Low Stock report |

---

## 7. Books Management Flow

The Books Management screen is used to manage all library books.

### Main Actions

- Add book
- Edit book
- Delete/deactivate book
- Search book
- Filter books
- Import books from Excel
- Export books to Excel

---

## 8. Add Book Flow

```text
Librarian opens Books Management
↓
Clicks Add Book
↓
System opens Add Book form
↓
Librarian enters book details
↓
Clicks Save
↓
System validates input
↓
If validation passes:
    Save book to SQLite
    Set available_quantity = total_quantity
    Show success message
    Refresh books list
↓
If validation fails:
    Show error message
```

### Required Fields

| Field | Required |
|---|---|
| Book Title | Yes |
| Total Quantity | Yes |
| Author | No |
| Category | No |
| ISBN | No |
| Publisher | No |
| Rack Number | No |

### Add Book Validation

```text
Book title cannot be empty
Total quantity must be a number
Total quantity must be greater than or equal to 0
ISBN must be unique if entered
```

---

## 9. Edit Book Flow

```text
Librarian opens Books Management
↓
Searches/selects a book
↓
Clicks Edit
↓
System opens Edit Book form with existing data
↓
Librarian updates details
↓
Clicks Save
↓
System validates updated data
↓
System updates book record in SQLite
↓
System refreshes books list
```

### Quantity Editing Rule

When editing total quantity:

```text
New total quantity cannot be less than currently issued quantity
```

Example:

```text
Total Quantity: 10
Currently Issued: 4
Minimum allowed new total quantity: 4
```

This prevents invalid stock records.

---

## 10. Delete / Deactivate Book Flow

Recommended action: **Deactivate book instead of permanently deleting it.**

```text
Librarian selects a book
↓
Clicks Delete or Deactivate
↓
System checks active issue records
↓
If book is currently issued:
    Do not delete
    Show message: Book has pending issue records
↓
If book has no active issue records:
    Mark book as INACTIVE
    Hide from normal issue list
    Keep history for reports
```

### Why Deactivate Instead of Delete

- Keeps old issue/return history safe.
- Prevents report errors.
- Avoids broken database relationships.
- Allows restoring the book later if needed.

---

## 11. Book Search Flow

```text
Librarian opens Books Management
↓
Types search keyword
↓
System searches matching records
↓
Display filtered results
```

### Search By

- Book title
- Author
- Category
- ISBN
- Publisher
- Rack number

### Filter By

- All books
- Available books
- Issued books
- Low-stock books
- Active books
- Inactive books

---

## 12. Student Management Flow

The Student Management screen is used to manage student records.

### Main Actions

- Add student
- Edit student
- Delete/deactivate student
- Search student
- Import students from Excel
- Export students to Excel
- View student issue history

---

## 13. Add Student Flow

```text
Librarian opens Student Management
↓
Clicks Add Student
↓
System opens Add Student form
↓
Librarian enters student details
↓
Clicks Save
↓
System validates input
↓
If validation passes:
    Save student to SQLite
    Show success message
    Refresh student list
↓
If validation fails:
    Show error message
```

### Required Fields

| Field | Required |
|---|---|
| Student ID / Admission Number | Yes |
| Student Name | Yes |
| Class | Optional |
| Division | Optional |
| Phone | Optional |
| Email | Optional |
| Address | Optional |

### Add Student Validation

```text
Student ID cannot be empty
Student name cannot be empty
Student ID must be unique
Phone number should be valid if entered
Email should be valid if entered
```

---

## 14. Edit Student Flow

```text
Librarian opens Student Management
↓
Searches/selects student
↓
Clicks Edit
↓
System opens Edit Student form
↓
Librarian updates details
↓
Clicks Save
↓
System validates updated data
↓
System updates student record in SQLite
↓
System refreshes student list
```

---

## 15. Delete / Deactivate Student Flow

Recommended action: **Deactivate student instead of permanently deleting.**

```text
Librarian selects student
↓
Clicks Delete or Deactivate
↓
System checks pending book issues
↓
If student has pending books:
    Do not delete
    Show pending return warning
↓
If student has no pending books:
    Mark student as INACTIVE
    Keep old issue/return history
```

---

## 16. Student Search Flow

```text
Librarian opens Student Management
↓
Types student name, ID, class, or phone number
↓
System searches matching student records
↓
Display filtered results
```

### Search By

- Student ID
- Student name
- Class
- Division
- Phone number

---

## 17. Issue Book Flow

The Issue Book screen is used when a student takes a book from the library.

### Issue Book Flow Diagram

```text
Open Issue Book Screen
↓
Select/Search Student
↓
Select/Search Book
↓
Enter Issue Date
↓
Enter Due Date
↓
Click Issue Book
↓
Validate Student
↓
Validate Book
↓
Check Available Quantity
↓
Check Duplicate Pending Issue
↓
Save Issue Record
↓
Decrease Available Quantity by 1
↓
Show Success Message
↓
Refresh Dashboard and Book List
```

---

## 18. Issue Book Detailed Flow

```text
Librarian opens Issue Book screen
↓
Searches student by ID/name
↓
Selects student
↓
Searches book by title/ISBN/category
↓
Selects book
↓
System shows available quantity
↓
Librarian selects issue date
↓
System suggests due date based on default due days
↓
Librarian clicks Issue Book
↓
System performs validation
↓
If valid:
    Insert record into book_issues table
    status = ISSUED
    Decrease available_quantity in books table
    Show issue success message
↓
If invalid:
    Show proper error message
```

### Issue Book Validation Rules

| Rule | Message |
|---|---|
| Student is required | Please select a student |
| Book is required | Please select a book |
| Book quantity is 0 | This book is currently not available |
| Student already has same book pending | This student already has this book issued |
| Student is inactive | Cannot issue book to inactive student |
| Book is inactive | Cannot issue inactive book |
| Due date before issue date | Due date cannot be earlier than issue date |

---

## 19. Duplicate Issue Prevention Flow

The system must prevent the same student from taking the same book again before returning it.

```text
Student selected
↓
Book selected
↓
Before issuing:
    Check book_issues table
    WHERE student_id = selected student
    AND book_id = selected book
    AND status = 'ISSUED'
↓
If record exists:
    Block issue
↓
If no record exists:
    Allow issue
```

---

## 20. Quantity Update During Issue

When book is issued:

```text
Before Issue:
available_quantity = 5

After Issue:
available_quantity = 4
```

System rule:

```text
Issue allowed only if available_quantity > 0
```

SQL logic example:

```text
UPDATE books
SET available_quantity = available_quantity - 1
WHERE id = selected_book_id
AND available_quantity > 0;
```

---

## 21. Return Book Flow

The Return Book screen is used when a student returns a book.

### Return Book Flow Diagram

```text
Open Return Book Screen
↓
Search Pending Issue Record
↓
Select Issued Book
↓
Confirm Return
↓
Enter Return Date
↓
Validate Issue Record
↓
Update Issue Status
↓
Increase Available Quantity by 1
↓
Show Success Message
↓
Refresh Dashboard and Reports
```

---

## 22. Return Book Detailed Flow

```text
Librarian opens Return Book screen
↓
Searches by student ID/name/book title
↓
System displays only ISSUED records
↓
Librarian selects the correct issue record
↓
System displays issue details
↓
Librarian enters return date
↓
Clicks Return Book
↓
System validates return
↓
If valid:
    Update book_issues record
    Set status = RETURNED
    Set return_date
    Increase available_quantity by 1
    Show success message
↓
If invalid:
    Show error message
```

### Return Book Validation Rules

| Rule | Message |
|---|---|
| Issue record is required | Please select an issued book record |
| Already returned | This book is already returned |
| Return date is missing | Please select return date |
| Return date before issue date | Return date cannot be before issue date |
| Quantity limit exceeded | Available quantity cannot exceed total quantity |

---

## 23. Quantity Update During Return

When book is returned:

```text
Before Return:
available_quantity = 4

After Return:
available_quantity = 5
```

System rule:

```text
available_quantity cannot be greater than total_quantity
```

SQL logic example:

```text
UPDATE books
SET available_quantity = available_quantity + 1
WHERE id = selected_book_id
AND available_quantity < total_quantity;
```

---

## 24. Book Issue Status Flow

### Status Values

```text
ISSUED
RETURNED
LOST
DAMAGED
```

### Status Transition

```text
ISSUED
├── RETURNED
├── LOST
└── DAMAGED
```

### Normal Return Flow

```text
ISSUED → RETURNED
```

### Lost Book Flow

```text
ISSUED → LOST
```

### Damaged Book Flow

```text
ISSUED → DAMAGED
```

For version 1, the main required statuses are:

```text
ISSUED
RETURNED
```

---

## 25. Pending Returns Flow

Pending returns are books with issue status `ISSUED`.

```text
Open Pending Returns Report
↓
Fetch book_issues where status = ISSUED
↓
Join with books and students tables
↓
Show pending list
↓
Highlight overdue records
```

### Pending Returns Display Fields

| Field | Description |
|---|---|
| Issue ID | Unique issue record |
| Student ID | Student admission number |
| Student Name | Name of student |
| Book Title | Issued book |
| Issue Date | Date issued |
| Due Date | Expected return date |
| Overdue Days | Number of days overdue |
| Status | ISSUED |

---

## 26. Overdue Book Flow

A book is overdue if:

```text
Current Date > Due Date
AND status = ISSUED
```

### Overdue Flow

```text
Open Dashboard or Reports
↓
System checks pending issue records
↓
Compare current date with due date
↓
If current date is greater than due date:
    Mark as overdue
    Calculate overdue days
```

### Overdue Days Formula

```text
Overdue Days = Current Date - Due Date
```

Fine calculation can be added in a future version.

---

## 27. Reports Flow

The Reports screen allows the librarian to view and export important records.

### Reports Available

- All books report
- Available books report
- Issued books report
- Returned books report
- Pending returns report
- Overdue books report
- Student list report
- Student-wise issue history
- Date-wise issue report
- Date-wise return report
- Low-stock report

### General Report Flow

```text
Open Reports screen
↓
Select report type
↓
Apply filters if needed
↓
System fetches data from SQLite
↓
Display report table
↓
Librarian can export to Excel
```

### Report Filters

| Filter | Used For |
|---|---|
| Date range | Issue/return reports |
| Student | Student-wise history |
| Class/division | Student reports |
| Book category | Book reports |
| Status | Issue/return reports |
| Low-stock limit | Low-stock report |

---

## 28. Export Report to Excel Flow

```text
Librarian opens Reports
↓
Selects report type
↓
Applies filters
↓
Clicks Export to Excel
↓
System fetches report data
↓
System creates Excel file using openpyxl
↓
File is saved in exports folder
↓
Show success message with file location
```

### Example Export Files

```text
exports/books_report.xlsx
exports/pending_returns_report.xlsx
exports/issued_books_report.xlsx
exports/student_issue_history.xlsx
exports/low_stock_report.xlsx
```

---

## 29. Import Books from Excel Flow

```text
Librarian opens Books Management
↓
Clicks Import from Excel
↓
Selects Excel file
↓
System reads Excel using openpyxl
↓
System validates each row
↓
Valid rows are inserted/updated in SQLite
↓
Invalid rows are skipped and shown in error report
↓
Books list is refreshed
```

### Required Excel Columns for Book Import

| Column | Required |
|---|---|
| Book Title | Yes |
| Total Quantity | Yes |
| Author | No |
| Category | No |
| ISBN | No |
| Publisher | No |
| Rack Number | No |

### Import Rule

If ISBN exists and matches an existing book:

```text
Update existing book
```

If ISBN is empty or new:

```text
Add as new book
```

---

## 30. Import Students from Excel Flow

```text
Librarian opens Student Management
↓
Clicks Import from Excel
↓
Selects Excel file
↓
System reads student records
↓
System validates required fields
↓
Valid students are saved to SQLite
↓
Duplicate student IDs are skipped or updated
↓
Student list is refreshed
```

### Required Excel Columns for Student Import

| Column | Required |
|---|---|
| Student ID | Yes |
| Student Name | Yes |
| Class | No |
| Division | No |
| Phone | No |
| Email | No |
| Address | No |

---

## 31. Backup Flow

The application should support backup to protect library data.

### SQLite Backup Flow

```text
Librarian opens Settings
↓
Clicks Backup Database
↓
System copies library.db
↓
Backup file is saved with date/time
↓
Show backup success message
```

### Backup File Example

```text
backups/library_backup_2026-07-06_10-30.db
```

### Excel Backup Flow

```text
Librarian opens Settings
↓
Clicks Export Full Backup to Excel
↓
System exports books, students, and book_issues
↓
Each table is saved as a separate Excel sheet
↓
Backup Excel file is saved
```

### Excel Backup File Example

```text
backups/library_full_backup_2026-07-06.xlsx
```

---

## 32. Restore Backup Flow

```text
Librarian opens Settings
↓
Clicks Restore Backup
↓
Selects backup database file
↓
System confirms restore action
↓
System replaces current database with selected backup
↓
Application restarts or reloads data
```

### Restore Warning

Before restoring backup, show:

```text
Restoring backup will replace current data. Please create a backup before continuing.
```

---

## 33. Settings Flow

The Settings screen allows the librarian to manage app configuration.

### Settings Options

| Setting | Description |
|---|---|
| School Name | Name of school |
| Library Name | Name of library |
| Default Due Days | Default number of days allowed for book return |
| Low Stock Limit | Quantity limit for low-stock warning |
| Backup Folder | Backup storage location |
| Export Folder | Excel export location |
| Theme | Optional UI theme |
| Database Backup | Create database backup |
| Restore Backup | Restore old backup |

### Settings Save Flow

```text
Open Settings
↓
Edit settings
↓
Click Save
↓
Validate values
↓
Save settings to SQLite
↓
Refresh application configuration
```

---

## 34. Error Handling Flow

The application should show clear error messages.

### Common Errors

| Error | Message |
|---|---|
| Empty required field | Please fill all required fields |
| Quantity is 0 | This book is not available |
| Duplicate issue | This student already has this book issued |
| Invalid date | Please select a valid date |
| Database error | Something went wrong while saving data |
| Excel import error | Invalid Excel file format |
| Backup error | Backup failed. Please check folder permission |

### Error Flow

```text
User performs action
↓
System validates data
↓
If error found:
    Stop action
    Show clear message
↓
If no error:
    Continue operation
```

---

## 35. Success Message Flow

After completing important actions, the system should show success messages.

### Examples

| Action | Message |
|---|---|
| Add book | Book added successfully |
| Update book | Book updated successfully |
| Add student | Student added successfully |
| Issue book | Book issued successfully |
| Return book | Book returned successfully |
| Export report | Report exported successfully |
| Backup | Backup created successfully |

---

## 36. Offline Data Flow

The application should work fully offline.

```text
User enters data
↓
Data is saved in local SQLite database
↓
Excel files are generated only when importing/exporting
↓
No internet is required
```

### Offline Storage

| Data | Storage |
|---|---|
| Books | SQLite |
| Students | SQLite |
| Issue records | SQLite |
| Return records | SQLite |
| Settings | SQLite |
| Reports | Excel export |
| Backup | SQLite backup / Excel backup |

---

## 37. Recommended Screen Flow Summary

```text
Start App
↓
Dashboard
├── Books Management
│   ├── Add Book
│   ├── Edit Book
│   ├── Deactivate Book
│   ├── Search Book
│   ├── Import Books from Excel
│   └── Export Books to Excel
│
├── Student Management
│   ├── Add Student
│   ├── Edit Student
│   ├── Deactivate Student
│   ├── Search Student
│   ├── Import Students from Excel
│   └── Export Students to Excel
│
├── Issue Book
│   ├── Select Student
│   ├── Select Book
│   ├── Validate Availability
│   ├── Save Issue Record
│   └── Decrease Quantity
│
├── Return Book
│   ├── Search Pending Issue
│   ├── Select Issue Record
│   ├── Save Return
│   └── Increase Quantity
│
├── Reports
│   ├── Books Report
│   ├── Issued Books Report
│   ├── Returned Books Report
│   ├── Pending Returns Report
│   ├── Overdue Report
│   └── Export to Excel
│
└── Settings
    ├── School Settings
    ├── Due Date Settings
    ├── Backup Settings
    ├── Database Backup
    └── Restore Backup
```

---

## 38. Important Business Rules

### Book Quantity Rules

```text
available_quantity cannot be less than 0
available_quantity cannot be greater than total_quantity
```

### Issue Rules

```text
A book can be issued only if available_quantity > 0
A student cannot take the same book twice without returning it
Inactive books cannot be issued
Inactive students cannot receive books
```

### Return Rules

```text
Only ISSUED records can be returned
Returned books should not be returned again
Quantity should increase only once after return
```

### Delete Rules

```text
Books with active issue records should not be deleted
Students with active issue records should not be deleted
Deactivate is preferred over permanent delete
```

---

## 39. Suggested User Experience Flow

The app should be simple for school staff.

### UX Principles

- Keep forms short and clear.
- Use large buttons for main actions.
- Use search boxes in Books and Students screens.
- Show available quantity clearly before issuing a book.
- Show warning messages before deleting/deactivating records.
- Show success messages after saving actions.
- Use table views for lists and reports.
- Keep Excel import/export buttons easy to find.
- Avoid complicated technical terms in the UI.

### Recommended Button Labels

| Action | Button Label |
|---|---|
| Add book | Add Book |
| Save book | Save Book |
| Edit book | Edit |
| Deactivate book | Deactivate |
| Issue book | Issue Book |
| Return book | Return Book |
| Export report | Export to Excel |
| Import data | Import from Excel |
| Backup | Backup Database |
| Restore | Restore Backup |

---

## 40. Final App Flow Recommendation

The recommended application flow is:

```text
Dashboard-first desktop application
↓
Simple sidebar navigation
↓
SQLite handles all main data
↓
Excel is used for import/export/report/backup
↓
Book quantity updates automatically during issue and return
↓
Reports help librarian track library activity
```

This flow is practical for a real school library client because it is:

- Easy to understand
- Fully offline
- Reliable
- Safe for local data
- Simple for librarians
- Expandable in the future
