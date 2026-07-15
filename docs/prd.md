# School Library Management System — Product Requirements Document (PRD)

## 1. Product Name

**School Library Management System**

---

## 2. Document Version

| Item | Details |
|---|---|
| Document Name | Product Requirements Document |
| File Name | `prd.md` |
| Project Type | Offline Desktop Application |
| Target User | School Librarian / Admin |
| Recommended Stack | Python, PySide6, SQLite, openpyxl |
| Version | 1.0 |

---

## 3. Product Overview

The **School Library Management System** is an offline desktop application designed for school libraries.

The application helps the librarian manage:

- Books
- Book quantities
- Students
- Book issue records
- Book return records
- Pending returns
- Overdue books
- Reports
- Excel import/export
- Local backup

The software should work on a local computer without requiring internet access.

The system should use **SQLite** as the main local database for safe and reliable data storage. Excel should be used for importing data, exporting reports, backups, and sharing records with school administration.

---

## 4. Product Goal

The main goal is to provide a simple and reliable desktop software solution for school library operations.

The system should allow the librarian to:

- Add books and manage stock quantity.
- Register students.
- Issue books to students.
- Record book returns.
- Automatically update available book quantity.
- Track pending and overdue returns.
- Generate useful reports.
- Export data to Excel.
- Work fully offline on a local computer.

---

## 5. Problem Statement

Many small school libraries manage books manually using notebooks or Excel sheets. This creates problems such as:

- Difficulty tracking available quantity.
- Manual mistakes in issue and return records.
- Duplicate or missing records.
- Difficulty finding which student has which book.
- Difficulty tracking overdue books.
- Risk of Excel file corruption or accidental editing.
- Time-consuming report generation.
- No clear dashboard for library status.

This application solves these problems by providing a structured desktop system with a local database and Excel support.

---

## 6. Target Users

## 6.1 Primary User

### Admin / Librarian

The librarian is responsible for daily library operations.

The librarian can:

- Add books.
- Add students.
- Issue books.
- Return books.
- Search records.
- View reports.
- Export reports.
- Create backups.

## 6.2 Secondary User

### School Management

School management may use exported reports to review:

- Total books
- Student issue activity
- Pending returns
- Overdue books
- Library stock status

School management does not need direct access in version 1.

---

## 7. User Personas

## 7.1 Librarian

| Field | Description |
|---|---|
| Role | Daily software user |
| Technical Skill | Basic computer knowledge |
| Main Need | Manage books and students easily |
| Pain Point | Manual records are slow and confusing |
| Goal | Quickly issue and return books without mistakes |

## 7.2 School Admin

| Field | Description |
|---|---|
| Role | Reviews reports |
| Technical Skill | Basic to moderate |
| Main Need | Accurate reports |
| Pain Point | Manual reports take time |
| Goal | Get clear Excel reports when needed |

---

## 8. Scope

## 8.1 In Scope

The first version of the application will include:

- Offline desktop application
- Dashboard
- Books management
- Student management
- Issue book workflow
- Return book workflow
- Pending returns tracking
- Overdue tracking
- Search and filters
- Reports
- Excel import/export
- SQLite database
- Backup and restore
- Settings page

## 8.2 Out of Scope for Version 1

The following features are not required in version 1:

- Cloud login
- Online database
- Mobile app
- Web dashboard
- Multi-branch library system
- Multi-computer real-time sync
- Barcode scanner support
- Fine payment collection
- SMS/WhatsApp notification
- Advanced role-based permissions

These can be added in future versions.

---

## 9. Recommended Technology Stack

| Layer | Recommended Technology | Reason |
|---|---|---|
| Desktop UI | Python PySide6 | Professional desktop interface |
| Application Logic | Python | Simple, maintainable, fast development |
| Main Database | SQLite | Reliable local storage |
| Excel Import/Export | openpyxl | Excel support for reports and backups |
| Packaging | PyInstaller | Convert Python app to Windows `.exe` |
| Backup | SQLite file copy + Excel export | Easy local backup |

---

## 10. Storage Requirement

## 10.1 Main Database

The application must use **SQLite** as the main local database.

Database file:

```text
database/library.db
```

SQLite should store:

- Books
- Students
- Issue records
- Return records
- Settings

## 10.2 Excel Usage

Excel should be used only for:

- Importing book lists
- Importing student lists
- Exporting reports
- Exporting backups
- Sharing records

Excel should not be used as the main database because it is less reliable for structured data operations.

---

## 11. Why SQLite Instead of Excel as Main Storage

| Requirement | SQLite | Excel |
|---|---|---|
| Safe local storage | Yes | Limited |
| Prevents duplicate records | Yes | Difficult |
| Handles linked data | Yes | Not ideal |
| Fast search | Yes | Slower with large files |
| Reduces manual mistakes | Yes | No |
| Supports validation | Yes | Limited |
| Handles issue/return records safely | Yes | Risky |
| Better for software | Yes | No |

### Final Storage Decision

Use:

```text
SQLite = Main database
Excel = Import/export/report/backup
```

---

## 12. Functional Requirements

## 12.1 Dashboard

### Description

The dashboard gives the librarian a quick overview of the library.

### Requirements

The dashboard must show:

- Total books
- Available books
- Issued books
- Total students
- Pending returns
- Overdue books
- Low-stock books
- Recent issue records
- Recent return records

### Priority

High

---

## 12.2 Books Management

### Description

The librarian can add, edit, deactivate, search, and manage books.

### Requirements

The system must allow the librarian to:

- Add new book.
- Edit existing book.
- Deactivate book.
- Search books.
- Filter books.
- View total quantity.
- View available quantity.
- View book availability status.
- Import books from Excel.
- Export books to Excel.

### Book Fields

| Field | Required |
|---|---|
| Book Title | Yes |
| Author | No |
| Category | No |
| ISBN | No |
| Publisher | No |
| Rack Number | No |
| Total Quantity | Yes |
| Available Quantity | Auto-managed |
| Status | Auto/default |

### Priority

High

---

## 12.3 Student Management

### Description

The librarian can add, edit, deactivate, search, and manage student records.

### Requirements

The system must allow the librarian to:

- Add student.
- Edit student.
- Deactivate student.
- Search students.
- Filter students by class/division/status.
- View student issue history.
- Import students from Excel.
- Export students to Excel.

### Student Fields

| Field | Required |
|---|---|
| Student ID / Admission Number | Yes |
| Student Name | Yes |
| Class | No |
| Division | No |
| Phone | No |
| Email | No |
| Address | No |
| Status | Auto/default |

### Priority

High

---

## 12.4 Issue Book

### Description

The librarian can issue an available book to a student.

### Requirements

The system must:

- Allow selecting/searching a student.
- Allow selecting/searching a book.
- Show available quantity before issuing.
- Allow entering issue date.
- Auto-suggest due date based on default settings.
- Save issue record.
- Decrease available quantity by 1.
- Prevent issue if quantity is 0.
- Prevent same student from taking the same book twice without return.
- Prevent issue to inactive student.
- Prevent issue of inactive book.

### Priority

High

---

## 12.5 Return Book

### Description

The librarian can return books that were issued to students.

### Requirements

The system must:

- Show/search pending issue records.
- Allow selecting an issued record.
- Allow entering return date.
- Mark the issue record as returned.
- Increase available quantity by 1.
- Prevent returning the same record twice.
- Show overdue days if applicable.

### Priority

High

---

## 12.6 Pending Returns

### Description

The system must show books that are issued but not returned.

### Requirements

Pending returns report must show:

- Student ID
- Student name
- Book title
- Issue date
- Due date
- Overdue status
- Overdue days

### Priority

High

---

## 12.7 Overdue Tracking

### Description

The system must identify overdue books automatically.

### Requirement

A book is overdue when:

```text
Current Date > Due Date
AND Issue Status = ISSUED
```

The system should display:

- Overdue badge
- Overdue days
- Student details
- Book details

### Priority

Medium

---

## 12.8 Reports

### Description

The system must generate important library reports.

### Required Reports

- All books report
- Available books report
- Issued books report
- Returned books report
- Pending returns report
- Overdue books report
- Students report
- Student-wise issue history
- Date-wise issue report
- Date-wise return report
- Low-stock report

### Report Features

Each report should support:

- Search
- Filters
- Date range where useful
- Export to Excel

### Priority

High

---

## 12.9 Excel Import

### Description

The system must allow importing books and students from Excel files.

### Requirements

The system must support:

- Import books from Excel.
- Import students from Excel.
- Validate required columns.
- Skip invalid rows.
- Show import summary.
- Prevent duplicate student IDs.
- Prevent duplicate ISBN values if ISBN is provided.

### Priority

Medium

---

## 12.10 Excel Export

### Description

The system must allow exporting data and reports to Excel.

### Requirements

The system must export:

- Books list
- Students list
- Reports
- Pending returns
- Overdue records
- Student issue history
- Full backup

### Priority

High

---

## 12.11 Backup and Restore

### Description

The system must provide local backup and restore options.

### Requirements

The system must support:

- Backup SQLite database.
- Restore SQLite database backup.
- Export full Excel backup.
- Show backup success/failure message.
- Store backups in a `backups` folder.

### Priority

Medium

---

## 12.12 Settings

### Description

The Settings screen must allow basic configuration.

### Settings

- School name
- Library name
- Default due days
- Low-stock limit
- Backup folder path
- Export folder path

### Priority

Medium

---

## 13. Non-Functional Requirements

## 13.1 Offline Support

The application must work fully offline.

```text
No internet connection should be required for core features.
```

## 13.2 Performance

The application should work smoothly for:

- 10,000+ book records
- 5,000+ student records
- 50,000+ issue/return records

## 13.3 Reliability

The system must protect data from common mistakes.

Requirements:

- Use SQLite transactions for issue/return actions.
- Do not manually edit database from UI.
- Prevent invalid quantity updates.
- Keep history records.
- Prefer deactivation over deletion.

## 13.4 Usability

The application should be easy for school staff.

Requirements:

- Simple labels
- Clear buttons
- Search boxes
- Helpful messages
- Easy report export
- No technical error messages shown to user

## 13.5 Security

Version 1 may be single-user without login.

Optional login can be added later.

Basic security expectations:

- Local data stored on school computer.
- Backup option available.
- No external data sharing.
- Optional password protection in future.

## 13.6 Maintainability

Code should be modular.

Required structure:

- UI files separate from business logic.
- Database logic separate from UI.
- Services for books, students, issues, reports, Excel, and backup.
- Clear file and function names.

---

## 14. User Stories

## 14.1 Book Management

### Add Book

As a librarian, I want to add a new book with quantity so that the library stock is recorded.

### Edit Book

As a librarian, I want to edit book details so that wrong or old information can be corrected.

### Search Book

As a librarian, I want to search books by title, author, or ISBN so that I can find books quickly.

### Manage Quantity

As a librarian, I want the system to automatically update available quantity so that I do not need to calculate manually.

---

## 14.2 Student Management

### Add Student

As a librarian, I want to add student details so that books can be issued to students.

### Search Student

As a librarian, I want to search students by ID or name so that I can issue or return books quickly.

### View Student History

As a librarian, I want to see a student's issue history so that I can track previous borrowing.

---

## 14.3 Issue and Return

### Issue Book

As a librarian, I want to issue a book to a student so that the borrowing is recorded.

### Return Book

As a librarian, I want to mark a book as returned so that the available quantity updates automatically.

### Prevent Duplicate Issue

As a librarian, I want the system to block the same student from taking the same book twice without return so that records stay correct.

---

## 14.4 Reports

### Export Report

As a librarian, I want to export reports to Excel so that I can share records with school management.

### Pending Returns

As a librarian, I want to see pending returns so that I can remind students to return books.

### Overdue Books

As a librarian, I want to see overdue books so that I can follow up with students.

---

## 15. Acceptance Criteria

## 15.1 Dashboard Acceptance Criteria

The dashboard is accepted when:

- It loads after app startup.
- It shows correct total books.
- It shows correct available books.
- It shows correct issued books.
- It shows correct student count.
- It shows pending returns.
- It shows overdue books.

---

## 15.2 Book Management Acceptance Criteria

Book management is accepted when:

- Librarian can add a book.
- Librarian can edit a book.
- Librarian can deactivate a book.
- Book title is required.
- Quantity is required.
- Quantity cannot be negative.
- Available quantity is set correctly.
- Books can be searched.
- Books can be exported to Excel.

---

## 15.3 Student Management Acceptance Criteria

Student management is accepted when:

- Librarian can add a student.
- Librarian can edit a student.
- Librarian can deactivate a student.
- Student ID is required.
- Student name is required.
- Student ID is unique.
- Students can be searched.
- Students can be exported to Excel.

---

## 15.4 Issue Book Acceptance Criteria

Issue book flow is accepted when:

- Librarian can select a student.
- Librarian can select a book.
- System blocks issue if available quantity is 0.
- System blocks duplicate pending issue.
- System saves issue record.
- Book available quantity decreases by 1.
- Issue status is saved as `ISSUED`.

---

## 15.5 Return Book Acceptance Criteria

Return book flow is accepted when:

- Librarian can search pending issue records.
- Librarian can select an issue record.
- System saves return date.
- Issue status changes to `RETURNED`.
- Book available quantity increases by 1.
- Already returned books cannot be returned again.

---

## 15.6 Reports Acceptance Criteria

Reports are accepted when:

- Required reports can be generated.
- Reports show correct data.
- Filters work correctly.
- Reports can be exported to Excel.
- Exported Excel files open correctly.

---

## 15.7 Backup Acceptance Criteria

Backup is accepted when:

- SQLite database backup can be created.
- Full Excel backup can be exported.
- Restore backup works correctly.
- User sees clear success or error messages.

---

## 16. Validation Rules

## 16.1 Book Rules

- Book title is required.
- Total quantity is required.
- Quantity must be a valid number.
- Quantity cannot be negative.
- Available quantity cannot be negative.
- Available quantity cannot be greater than total quantity.
- ISBN must be unique if provided.
- Book with active issue records should not be permanently deleted.

## 16.2 Student Rules

- Student ID is required.
- Student name is required.
- Student ID must be unique.
- Email must be valid if entered.
- Phone number must be valid if entered.
- Student with active issue records should not be permanently deleted.

## 16.3 Issue Rules

- Student must be selected.
- Book must be selected.
- Book must be active.
- Student must be active.
- Available quantity must be greater than 0.
- Same student cannot borrow same book twice without return.
- Due date cannot be earlier than issue date.

## 16.4 Return Rules

- Issue record must be selected.
- Only `ISSUED` records can be returned.
- Return date is required.
- Return date cannot be earlier than issue date.
- Quantity must increase only once.
- Available quantity cannot exceed total quantity.

---

## 17. Database Requirements

## 17.1 Database File

```text
database/library.db
```

## 17.2 Required Tables

- `books`
- `students`
- `book_issues`
- `settings`

---

## 17.3 Books Table

| Field | Type | Requirement |
|---|---|---|
| id | INTEGER | Primary key |
| title | TEXT | Required |
| author | TEXT | Optional |
| category | TEXT | Optional |
| isbn | TEXT | Unique if entered |
| publisher | TEXT | Optional |
| rack_number | TEXT | Optional |
| total_quantity | INTEGER | Required |
| available_quantity | INTEGER | Required |
| status | TEXT | Default ACTIVE |
| created_at | TEXT | Required |
| updated_at | TEXT | Required |

---

## 17.4 Students Table

| Field | Type | Requirement |
|---|---|---|
| id | INTEGER | Primary key |
| student_code | TEXT | Required, unique |
| name | TEXT | Required |
| class_name | TEXT | Optional |
| division | TEXT | Optional |
| phone | TEXT | Optional |
| email | TEXT | Optional |
| address | TEXT | Optional |
| status | TEXT | Default ACTIVE |
| created_at | TEXT | Required |
| updated_at | TEXT | Required |

---

## 17.5 Book Issues Table

| Field | Type | Requirement |
|---|---|---|
| id | INTEGER | Primary key |
| book_id | INTEGER | Required |
| student_id | INTEGER | Required |
| issue_date | TEXT | Required |
| due_date | TEXT | Optional |
| return_date | TEXT | Optional |
| status | TEXT | Default ISSUED |
| remarks | TEXT | Optional |
| created_at | TEXT | Required |
| updated_at | TEXT | Required |

---

## 17.6 Settings Table

| Field | Type | Requirement |
|---|---|---|
| id | INTEGER | Primary key |
| setting_key | TEXT | Required, unique |
| setting_value | TEXT | Optional |

---

## 18. UI Requirements

## 18.1 Main Layout

The app should use:

```text
Top Bar
Left Sidebar
Main Content Area
```

## 18.2 Sidebar Pages

- Dashboard
- Books Management
- Student Management
- Issue Book
- Return Book
- Reports
- Settings

## 18.3 UI Style

The UI should be:

- Clean
- Light themed
- Professional
- Table-based
- Simple to use
- Suitable for school staff

## 18.4 UI Components

Required UI components:

- Dashboard cards
- Tables
- Forms
- Search bars
- Filter dropdowns
- Buttons
- Status badges
- Confirmation dialogs
- Success/error messages

---

## 19. Report Requirements

## 19.1 Report List

| Report | Priority |
|---|---|
| All Books | High |
| Available Books | High |
| Issued Books | High |
| Returned Books | High |
| Pending Returns | High |
| Overdue Books | Medium |
| Students | High |
| Student-wise Issue History | Medium |
| Date-wise Issue Report | Medium |
| Date-wise Return Report | Medium |
| Low-stock Books | Medium |

## 19.2 Report Export

All reports must have an:

```text
Export to Excel
```

button.

---

## 20. Excel Requirements

## 20.1 Book Import Columns

| Column | Required |
|---|---|
| Book Title | Yes |
| Total Quantity | Yes |
| Author | No |
| Category | No |
| ISBN | No |
| Publisher | No |
| Rack Number | No |

## 20.2 Student Import Columns

| Column | Required |
|---|---|
| Student ID | Yes |
| Student Name | Yes |
| Class | No |
| Division | No |
| Phone | No |
| Email | No |
| Address | No |

## 20.3 Export Format

Excel exports should include:

- Clear sheet name
- Column headers
- Auto-sized columns if possible
- Export date
- School/library name if available

---

## 21. Development Phases

## Phase 1: Setup

- Create project structure.
- Create virtual environment.
- Install dependencies.
- Create `requirements.txt`.

## Phase 2: Database

- Create SQLite database.
- Create schema.
- Create database connection helper.
- Add default settings.

## Phase 3: Services

- Build book service.
- Build student service.
- Build issue service.
- Build report service.
- Build Excel service.
- Build backup service.

## Phase 4: UI

- Create main window.
- Create sidebar.
- Create dashboard.
- Create books page.
- Create students page.
- Create issue page.
- Create return page.
- Create reports page.
- Create settings page.

## Phase 5: Integration

- Connect UI to services.
- Implement validation.
- Implement quantity update logic.
- Implement reports.
- Implement Excel import/export.
- Implement backup/restore.

## Phase 6: Testing

- Test book features.
- Test student features.
- Test issue/return.
- Test reports.
- Test Excel import/export.
- Test backup/restore.
- Fix bugs.

## Phase 7: Packaging

- Package app using PyInstaller.
- Test `.exe` on Windows.
- Prepare final delivery folder.
- Add user guide.

---

## 22. Success Metrics

The project is successful when:

- The librarian can manage books easily.
- The librarian can manage students easily.
- Book issue and return works without quantity mistakes.
- Pending returns are easy to track.
- Reports can be exported to Excel.
- The app works fully offline.
- The app can be installed and used on the school computer.
- The client can use the system without technical help.

---

## 23. Risks and Mitigation

| Risk | Mitigation |
|---|---|
| Client wants Excel as main storage | Use SQLite internally and provide Excel import/export |
| Data loss | Add backup and restore feature |
| Wrong quantity update | Use transactions and validation |
| Duplicate records | Add unique constraints |
| User accidentally deletes data | Use deactivate instead of delete |
| Non-technical user confusion | Keep UI simple and clear |
| App crash during issue/return | Use SQLite transactions |

---

## 24. Future Enhancements

Future versions can include:

- Login system
- Barcode scanner support
- Fine calculation
- SMS/WhatsApp reminders
- Cloud backup
- Multi-computer support
- Role-based permissions
- Student ID card integration
- Print issue/return receipts
- Book reservation system
- Advanced analytics

---

## 25. Final Product Recommendation

The final product should be a simple but professional offline desktop application.

Recommended final stack:

```text
Desktop UI: Python PySide6
Backend Logic: Python
Database: SQLite
Excel Support: openpyxl
Packaging: PyInstaller
```

Final storage rule:

```text
SQLite should be the main database.
Excel should be used only for import, export, reports, and backup.
```

The final application should be suitable for real school library use and should help the librarian manage books, students, issue records, return records, and reports with minimum manual work.
