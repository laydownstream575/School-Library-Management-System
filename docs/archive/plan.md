# School Library Management System — Desktop Application Plan

## 1. Project Title

**School Library Management System**

A simple offline desktop application for managing school library books, book quantities, students, issue records, returns, and reports.

---

## 2. Project Goal

The goal of this project is to build a desktop software application for a school library that allows the librarian to:

- Add and manage books.
- Track total and available book quantities.
- Add and manage student records.
- Issue books to students.
- Record book returns.
- Track pending returns.
- Generate reports.
- Export data and reports to Excel.

The software should work **offline on a local computer** without requiring an internet connection.

---

## 3. Client Requirements

| Requirement | Description |
|---|---|
| Offline desktop software | The application should run on a local computer without internet. |
| Book entry | Librarian can enter book details and quantity. |
| Quantity management | System should track total quantity and available quantity. |
| Student management | Librarian can add and search student details. |
| Book issue tracking | When a student takes a book, the issue record should be saved. |
| Book return tracking | When a student returns a book, the system should update the return status. |
| Automatic quantity update | Available quantity should decrease on issue and increase on return. |
| Excel support | Client wants local Excel storage or Excel-based records. |
| Reports | Librarian can generate issue, return, pending, and stock reports. |
| Simple UI | The interface should be easy for school staff to use. |

---

## 4. Recommended Tech Stack

### Recommended Stack

| Layer | Technology | Purpose |
|---|---|---|
| Desktop UI | **Python PySide6** or **Tkinter** | Build the desktop application interface |
| Backend / Logic | **Python** | Handle business rules, validation, and data operations |
| Main Local Database | **SQLite** | Store books, students, issue records, and return data safely |
| Excel Support | **openpyxl** | Import/export Excel files for reports, backup, and data sharing |
| Packaging | **PyInstaller** | Convert Python app into `.exe` desktop software |
| Optional Styling | Qt Stylesheets / Custom Tkinter styling | Improve UI appearance |

### Best Recommendation

Use:

- **Python + PySide6**
- **SQLite as the main database**
- **openpyxl for Excel import/export**
- **PyInstaller for desktop app packaging**

PySide6 is recommended if the client wants a more professional and modern-looking desktop application. Tkinter can be used if the project needs to be simpler and lighter.

---

## 5. Why Python is Suitable for This Desktop Application

Python is a good choice for this project because:

- It is easy to develop and maintain.
- It supports desktop application development.
- It works well with SQLite databases.
- It has strong Excel support through libraries like `openpyxl`.
- It can be converted into a Windows `.exe` file using PyInstaller.
- It is suitable for small and medium school management systems.
- It allows fast development with fewer complications.
- It is reliable for offline local applications.

### Python Desktop UI Options

| Option | Best For | Notes |
|---|---|---|
| PySide6 | Professional desktop UI | Modern design, powerful widgets, better for client projects |
| Tkinter | Simple desktop UI | Built into Python, easy to learn, basic design |
| CustomTkinter | Better-looking Tkinter apps | Good for modern UI with simple setup |

### Final UI Recommendation

For a real school client project, **PySide6** is the better option because it gives a more professional desktop software experience.

---

## 6. Why SQLite is Better Than Using Excel as the Main Database

The client may ask for “local storage in Excel,” but Excel should not be used as the main database for regular software operations.

### Recommended Approach

Use:

- **SQLite** as the main local database.
- **Excel** for import, export, backup, and reports.

### Why SQLite is Better

| Reason | SQLite | Excel |
|---|---|---|
| Data safety | High | Lower |
| Prevents duplicate or broken records | Yes | Difficult |
| Handles relationships between books, students, and issues | Yes | Not reliable |
| Supports search and filters | Fast | Slow with large data |
| Reduces data corruption | Yes | Excel files can get corrupted or overwritten |
| Multiple tables | Properly supported | Not ideal |
| Quantity update accuracy | Reliable | Risk of formula/manual errors |
| Validation rules | Easy to enforce | Hard to enforce |
| Report generation | Easy | Possible, but less structured |

### Practical Explanation for Client

Even though the client wants Excel-based local storage, the safer solution is to use SQLite as the internal database. Excel can still be used for:

- Importing book lists.
- Exporting reports.
- Creating backups.
- Sharing records with school administration.
- Printing stock and issue reports.

This gives the client the benefit of Excel while keeping the actual software reliable.

---

## 7. Excel Import/Export Feature Plan

Excel will be used as a support feature, not the main database.

### Excel Import Features

The system should allow the librarian to import:

- Book list from Excel.
- Student list from Excel.

Example book import columns:

| Column | Example |
|---|---|
| Book Title | Mathematics Class 10 |
| Author | R. D. Sharma |
| Category | Mathematics |
| ISBN | 978xxxxxxx |
| Total Quantity | 10 |
| Rack Number | A1 |

Example student import columns:

| Column | Example |
|---|---|
| Student ID | STU001 |
| Student Name | Rahul S |
| Class | 10 |
| Division | A |
| Phone | 9876543210 |

### Excel Export Features

The system should export:

- All books report.
- Available books report.
- Issued books report.
- Pending returns report.
- Student-wise issue history.
- Date-wise issue report.
- Date-wise return report.
- Low-stock book report.

### Excel Backup

The system can provide a **Backup to Excel** option that exports important tables into separate sheets:

- Books
- Students
- Book Issues
- Returns / Status

---

## 8. Main Features

### 8.1 Add Books

The librarian can add new books with details such as:

- Book title
- Author
- Category
- ISBN
- Publisher
- Rack number
- Total quantity
- Available quantity
- Added date

### 8.2 Edit Books

The librarian can update existing book details:

- Title
- Author
- Category
- Quantity
- Rack number
- Publisher
- ISBN

### 8.3 Delete Books

The librarian can delete a book record if:

- The book is no longer available in the library.
- There are no active pending issue records for that book.

Recommended rule:

- Do not allow deleting a book if it is currently issued to any student.
- Instead, provide an option to mark the book as inactive.

### 8.4 Manage Book Quantity

The system should track:

- Total quantity
- Available quantity
- Issued quantity

Formula:

```text
Available Quantity = Total Quantity - Currently Issued Quantity
```

When a book is issued:

```text
Available Quantity decreases by 1
```

When a book is returned:

```text
Available Quantity increases by 1
```

### 8.5 Add Students

The librarian can add student details such as:

- Student ID / Admission number
- Student name
- Class
- Division
- Phone number
- Email address
- Address
- Status

### 8.6 Issue Book to Student

When a student takes a book, the librarian enters:

- Student ID
- Book ID
- Issue date
- Due date
- Remarks, if any

The system should:

- Check if the book is available.
- Check if the student already has the same book pending.
- Save the issue record.
- Reduce available quantity by 1.
- Mark issue status as `ISSUED`.

### 8.7 Return Book

When a student returns a book, the librarian selects the active issue record and marks it as returned.

The system should:

- Save return date.
- Change issue status to `RETURNED`.
- Increase available quantity by 1.
- Optionally calculate overdue days.

### 8.8 Track Pending Returns

The system should show books that are currently issued but not returned.

Pending return details:

- Student name
- Student ID
- Book title
- Issue date
- Due date
- Overdue status
- Number of overdue days

### 8.9 Search Books

The librarian can search books by:

- Book title
- Author
- Category
- ISBN
- Rack number
- Availability status

### 8.10 Search Students

The librarian can search students by:

- Student ID
- Student name
- Class
- Division
- Phone number

### 8.11 Generate Reports

The system should generate:

- Total books report
- Available books report
- Issued books report
- Pending returns report
- Returned books report
- Student-wise report
- Class-wise report
- Date-wise issue report
- Date-wise return report
- Low-stock report

### 8.12 Export Reports to Excel

Every report should have an **Export to Excel** button.

Export file examples:

```text
books_report.xlsx
pending_returns_report.xlsx
student_issue_history.xlsx
low_stock_report.xlsx
```

---

## 9. User Roles

### Admin / Librarian

The first version of the system can have one main role: **Admin / Librarian**.

The librarian can:

- Add books.
- Edit books.
- Delete or deactivate books.
- Add students.
- Edit students.
- Issue books.
- Return books.
- View reports.
- Export Excel reports.
- Manage settings.
- Take database backup.

### Optional Future Roles

| Role | Access |
|---|---|
| Admin | Full access |
| Assistant Librarian | Issue/return access only |
| Viewer | Read-only reports access |

---

## 10. Main Pages / Screens

### 10.1 Dashboard

The dashboard should show quick statistics:

- Total books
- Available books
- Issued books
- Total students
- Pending returns
- Overdue books
- Low-stock books

Suggested dashboard cards:

| Card | Description |
|---|---|
| Total Books | Total number of book copies |
| Available Books | Books currently available |
| Issued Books | Books currently with students |
| Pending Returns | Books not yet returned |
| Overdue Books | Books past due date |
| Students | Total registered students |

---

### 10.2 Books Management

Features:

- Add new book
- Edit book
- Delete/deactivate book
- Search book
- Filter by category
- Filter by availability
- Import books from Excel
- Export books to Excel

Fields:

- Book ID
- Title
- Author
- Category
- ISBN
- Publisher
- Rack number
- Total quantity
- Available quantity
- Status

---

### 10.3 Student Management

Features:

- Add student
- Edit student
- Delete/deactivate student
- Search student
- Filter by class/division
- Import students from Excel
- Export students to Excel

Fields:

- Student ID
- Name
- Class
- Division
- Phone
- Email
- Address
- Status

---

### 10.4 Issue Book

Features:

- Select student
- Search book
- Select issue date
- Select due date
- Save issue record
- Automatically update book quantity

Issue form fields:

- Student ID
- Student name
- Book ID
- Book title
- Issue date
- Due date
- Remarks

---

### 10.5 Return Book

Features:

- Search active issue records
- Select issued book
- Mark as returned
- Save return date
- Automatically update quantity
- Show overdue information

Return form fields:

- Issue ID
- Student details
- Book details
- Issue date
- Due date
- Return date
- Status

---

### 10.6 Reports

Reports screen should include:

- Books report
- Student report
- Issued books report
- Returned books report
- Pending returns report
- Overdue report
- Low-stock report
- Date-wise report
- Student-wise issue history

Each report should support:

- Search
- Filters
- Date range
- Export to Excel
- Print option, if needed

---

### 10.7 Settings

Settings may include:

- School name
- Library name
- Default due days
- Backup location
- Excel export location
- Low-stock alert quantity
- Database backup option
- Restore backup option

---

## 11. Database Design

Recommended database: **SQLite**

Database file example:

```text
library.db
```

---

### 11.1 `books` Table

Stores book details and quantity information.

| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique book ID |
| title | TEXT NOT NULL | Book title |
| author | TEXT | Book author |
| category | TEXT | Book category |
| isbn | TEXT UNIQUE | ISBN number, if available |
| publisher | TEXT | Publisher name |
| rack_number | TEXT | Rack or shelf location |
| total_quantity | INTEGER NOT NULL | Total copies of the book |
| available_quantity | INTEGER NOT NULL | Copies currently available |
| status | TEXT DEFAULT 'ACTIVE' | ACTIVE or INACTIVE |
| created_at | TEXT | Created date/time |
| updated_at | TEXT | Updated date/time |

---

### 11.2 `students` Table

Stores student details.

| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Internal student record ID |
| student_code | TEXT UNIQUE NOT NULL | School admission number or student ID |
| name | TEXT NOT NULL | Student name |
| class_name | TEXT | Class |
| division | TEXT | Division |
| phone | TEXT | Phone number |
| email | TEXT | Email address |
| address | TEXT | Student address |
| status | TEXT DEFAULT 'ACTIVE' | ACTIVE or INACTIVE |
| created_at | TEXT | Created date/time |
| updated_at | TEXT | Updated date/time |

---

### 11.3 `book_issues` Table

Stores issue and return records.

| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Unique issue ID |
| book_id | INTEGER NOT NULL | Linked book ID |
| student_id | INTEGER NOT NULL | Linked student ID |
| issue_date | TEXT NOT NULL | Date book was issued |
| due_date | TEXT | Expected return date |
| return_date | TEXT | Actual return date |
| status | TEXT DEFAULT 'ISSUED' | ISSUED or RETURNED |
| remarks | TEXT | Optional notes |
| created_at | TEXT | Created date/time |
| updated_at | TEXT | Updated date/time |

Relationships:

```text
book_issues.book_id → books.id
book_issues.student_id → students.id
```

---

### 11.4 Suggested Status Values

Book status:

```text
ACTIVE
INACTIVE
```

Issue status:

```text
ISSUED
RETURNED
LOST
DAMAGED
```

Student status:

```text
ACTIVE
INACTIVE
```

---

### 11.5 Optional `settings` Table

Stores application settings.

| Field | Type | Description |
|---|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT | Setting ID |
| setting_key | TEXT UNIQUE NOT NULL | Setting name |
| setting_value | TEXT | Setting value |

Example settings:

| setting_key | setting_value |
|---|---|
| school_name | ABC Public School |
| default_due_days | 7 |
| low_stock_limit | 2 |
| backup_path | D:/LibraryBackup |

---

## 12. Data Flow

### 12.1 Add Book Flow

```text
Librarian opens Books Management
↓
Clicks Add Book
↓
Enters book title, author, category, quantity, and other details
↓
System validates required fields
↓
System saves book to SQLite database
↓
Book appears in Books Management list
```

### 12.2 Issue Book Flow

```text
Librarian opens Issue Book screen
↓
Searches/selects student
↓
Searches/selects book
↓
System checks available quantity
↓
System checks whether same book is already issued to same student
↓
Librarian enters issue date and due date
↓
System creates issue record in book_issues table
↓
System decreases available_quantity by 1
↓
Issue status becomes ISSUED
```

### 12.3 Return Book Flow

```text
Librarian opens Return Book screen
↓
Searches active issue record
↓
Selects the issued book record
↓
Clicks Return Book
↓
System updates return_date
↓
System changes status from ISSUED to RETURNED
↓
System increases available_quantity by 1
↓
Record appears in returned books report
```

### 12.4 Quantity Update Flow

When issuing a book:

```text
available_quantity = available_quantity - 1
```

When returning a book:

```text
available_quantity = available_quantity + 1
```

The system should never allow:

```text
available_quantity < 0
available_quantity > total_quantity
```

---

## 13. Validation Rules

### Book Validation

- Book title is required.
- Total quantity is required.
- Quantity must be a number.
- Quantity cannot be less than 0.
- Available quantity cannot be greater than total quantity.
- ISBN should be unique if entered.
- A book cannot be deleted if it has active issue records.

### Student Validation

- Student name is required.
- Student ID / admission number is required.
- Student ID must be unique.
- Phone number should be valid if entered.
- Email should be valid if entered.

### Issue Book Validation

- Student must be selected.
- Book must be selected.
- Cannot issue book if available quantity is 0.
- Cannot issue inactive book.
- Cannot issue book to inactive student.
- Cannot issue the same book twice to the same student without return.
- Issue date is required.
- Due date should not be earlier than issue date.

### Return Book Validation

- Only issued books can be returned.
- Return date is required.
- Return date should not be earlier than issue date.
- Quantity should increase only once per return.
- Already returned records should not be returned again.

---

## 14. Folder Structure

Recommended project structure:

```text
school-library-management/
│
├── main.py
├── requirements.txt
├── README.md
├── plan.md
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── validators.py
│   └── utils.py
│
├── ui/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── books_page.py
│   ├── students_page.py
│   ├── issue_book_page.py
│   ├── return_book_page.py
│   ├── reports_page.py
│   └── settings_page.py
│
├── services/
│   ├── __init__.py
│   ├── book_service.py
│   ├── student_service.py
│   ├── issue_service.py
│   ├── report_service.py
│   └── excel_service.py
│
├── database/
│   ├── library.db
│   └── schema.sql
│
├── exports/
│   ├── books_report.xlsx
│   └── pending_returns_report.xlsx
│
├── backups/
│   └── library_backup.xlsx
│
└── assets/
    ├── icons/
    └── images/
```

---

## 15. Development Phases

### Phase 1: Requirement Finalization

Tasks:

- Confirm exact client requirements.
- Confirm school details.
- Confirm required fields for books and students.
- Confirm whether login is needed in version 1.
- Confirm report formats.
- Confirm Excel import/export needs.

Deliverables:

- Final requirement document.
- Approved feature list.
- Basic UI wireframe.

---

### Phase 2: Database Design

Tasks:

- Create SQLite database.
- Create books table.
- Create students table.
- Create book_issues table.
- Create settings table if needed.
- Add validation constraints.
- Test sample data.

Deliverables:

- `library.db`
- `schema.sql`
- Sample data

---

### Phase 3: Basic UI Development

Tasks:

- Create main desktop window.
- Add sidebar or top navigation.
- Create dashboard screen.
- Create books management screen.
- Create student management screen.
- Create issue book screen.
- Create return book screen.
- Create reports screen.
- Create settings screen.

Deliverables:

- Working desktop UI layout.
- Navigation between screens.

---

### Phase 4: Book Management Module

Tasks:

- Add book feature.
- Edit book feature.
- Delete/deactivate book feature.
- Search books.
- Quantity management.
- Book availability status.

Deliverables:

- Complete books management module.

---

### Phase 5: Student Management Module

Tasks:

- Add student feature.
- Edit student feature.
- Delete/deactivate student feature.
- Search students.
- Filter by class/division.

Deliverables:

- Complete student management module.

---

### Phase 6: Issue and Return Module

Tasks:

- Issue book to student.
- Validate quantity.
- Prevent duplicate pending issue.
- Update available quantity.
- Return book.
- Update return status.
- Increase available quantity.
- Track pending and overdue books.

Deliverables:

- Complete issue/return workflow.

---

### Phase 7: Reports and Excel Export

Tasks:

- Create books report.
- Create issued books report.
- Create returned books report.
- Create pending returns report.
- Create overdue report.
- Create student-wise report.
- Add Excel export using `openpyxl`.
- Add Excel import for books and students.

Deliverables:

- Report screens.
- Excel export files.
- Excel import feature.

---

### Phase 8: Testing

Tasks:

- Test book add/edit/delete.
- Test student add/edit/delete.
- Test issue book flow.
- Test return book flow.
- Test quantity update accuracy.
- Test Excel import/export.
- Test validation rules.
- Test database backup and restore.
- Test app on client computer.

Deliverables:

- Bug-free local desktop application.
- Test report.
- Final corrections.

---

### Phase 9: Packaging and Delivery

Tasks:

- Package the app using PyInstaller.
- Create Windows `.exe` file.
- Include database file.
- Include required assets.
- Create backup folder.
- Create user guide.
- Install and test on client computer.

Deliverables:

- Final `.exe` application.
- SQLite database file.
- User guide.
- Backup/export folder.
- Source code backup.

---

## 16. Future Improvements

The first version should focus on the basic working library system. The following features can be added later.

### 16.1 Barcode Scanner Support

- Add barcode field for each book.
- Use barcode scanner to search books quickly.
- Issue and return books by scanning barcode.

### 16.2 Login System

- Admin login.
- Librarian login.
- Password protection.
- Role-based access.

### 16.3 Fine Calculation

- Set default due days.
- Calculate overdue days.
- Add fine amount per day.
- Generate fine report.

Example:

```text
Fine = Overdue Days × Fine Per Day
```

### 16.4 Cloud Backup

- Backup database to Google Drive, OneDrive, or cloud server.
- Automatic daily backup.
- Restore backup when needed.

### 16.5 Multi-Computer Support

For future multi-computer usage:

- Use a central server database.
- Use PostgreSQL or MySQL instead of SQLite.
- Connect multiple librarian computers to the same database.
- Add user accounts and permissions.

### 16.6 Print Receipts

- Print book issue receipt.
- Print return receipt.
- Print student library history.

### 16.7 ID Card Integration

- Search students by ID card number.
- Scan student ID barcode or QR code.

---

## 17. Excel-Only Alternative Approach

If the client strictly wants Excel as the main storage, the project can be built using Excel files only.

### Excel-Only Storage Files

Example files:

```text
books.xlsx
students.xlsx
book_issues.xlsx
reports.xlsx
```

### Excel-Only Approach

The software will:

- Read data from Excel files.
- Write new book records to Excel.
- Write student records to Excel.
- Save issue and return records to Excel.
- Update quantity inside Excel files.
- Generate reports from Excel sheets.

### Problems with Excel-Only Storage

| Problem | Explanation |
|---|---|
| Higher corruption risk | Excel files can become corrupted if the app closes suddenly. |
| Slower performance | Searching and updating large Excel files can become slow. |
| Data conflict risk | If the file is opened in Excel while the app writes to it, errors can happen. |
| Weak validation | It is harder to enforce database-like rules. |
| Difficult relationships | Linking books, students, and issues is less reliable. |
| Backup risk | Users may manually edit or delete important rows. |

### When Excel-Only is Acceptable

Excel-only storage may be acceptable if:

- The library has very few books.
- Only one person uses the system.
- The client strongly requires Excel files.
- The system is used for simple record keeping only.
- The client understands the limitations.

### Excel-Only Final Note

Excel-only storage is possible, but it is not the best professional solution. For a real school library system, SQLite is strongly recommended.

---

## 18. Final Recommendation

The best solution for this School Library Management System is:

| Requirement | Recommended Solution |
|---|---|
| Desktop application | Python PySide6 |
| Backend logic | Python |
| Main local storage | SQLite |
| Excel support | openpyxl |
| App packaging | PyInstaller |
| Reports | Export to Excel |
| Backup | SQLite backup + Excel export |

### Final Suggested Stack

```text
Frontend/Desktop UI: Python PySide6
Backend/Logic: Python
Database: SQLite
Excel Import/Export: openpyxl
Packaging: PyInstaller
```

### Final Client-Friendly Explanation

The application will work fully offline on the school computer. The librarian can add books, manage quantities, add students, issue books, return books, and generate reports. The system will use SQLite internally to safely store all records. Excel will be used for importing data, exporting reports, and creating backups.

This gives the client the simplicity of Excel and the reliability of a real database.

---

## 19. Summary

This project is practical, affordable, and suitable for a school library. The recommended Python + SQLite desktop application will be easy to use, reliable, and maintainable. Excel support will be included for reports, backup, and data sharing, while SQLite will protect the main data from corruption and manual mistakes.
