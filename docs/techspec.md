# School Library Management System — Technical Specification

## 1. Document Purpose

This document defines the technical architecture, module responsibilities, data flow, dependency graph, and detailed specifications for the School Library Management System desktop application.

It is intended for developers, maintainers, and technical reviewers.

---

## 2. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Desktop UI | PySide6 | >= 6.5.0 | Qt6 bindings for Python — windowing, widgets, event loop |
| Application Logic | Python | >= 3.10 | Business rules, validation, orchestration |
| Local Database | SQLite (via sqlite3) | Bundled with Python | Persistent structured data storage |
| Excel Support | openpyxl | >= 3.1.0 | Read/write Excel files for import, export, backup |
| Packaging | PyInstaller | >= 6.0 | Bundle Python app into standalone Windows `.exe` |
| Styling | Qt Stylesheets (QSS) | — | Visual theming without external CSS |

---

## 3. Architecture Overview

### 3.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     UI Layer (ui/)                        │
│  PySide6 widgets — no SQL, no business logic             │
│  Calls service-layer methods, displays results           │
├─────────────────────────────────────────────────────────┤
│                   Service Layer (services/)               │
│  Business logic, transactions, Excel I/O, backup/restore │
│  Throws ServiceError for user-facing problems            │
├─────────────────────────────────────────────────────────┤
│                     App Layer (app/)                      │
│  Config, database connection, validators, date utils     │
│  Lowest-level reusable utilities                         │
├─────────────────────────────────────────────────────────┤
│                 Data Layer (database/)                    │
│  SQLite .db file, schema.sql, migrations/                │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Rules

- **UI never imports `sqlite3` directly.** All database access goes through services.
- **Services never import `PySide6`.** UI remains swappable.
- **Services raise `ServiceError`** for expected failures (validation, missing records, conflicts).
- **Unexpected errors bubble to the UI** where a generic "Something went wrong" message is shown.
- **App layer has no dependency on services or UI.**

---

## 4. Module Map

### 4.1 `app/` — Core Application Package

| File | Responsibility |
|---|---|
| `__init__.py` | Package marker |
| `config.py` | `Config` dataclass: paths, defaults, settings loaded from DB at startup. Provides `load_config()` and `save_config()`. |
| `database.py` | `get_connection()`, `initialize_database()`, `execute()`, `fetch_all()`, `fetch_one()`. Encapsulates `sqlite3`, manages schema creation and index setup from `_EMBEDDED_SCHEMA` (16 indexes). |
| `validators.py` | Pure functions: `validate_book()`, `validate_student()`, `validate_issue()`, `validate_return()`. Return `list[str]` of error messages (empty = valid). |
| `utils.py` | `format_display_date()`, `parse_date()`, `get_today_iso()`, `datetime_now_iso()` helpers. |

### 4.2 `services/` — Business Logic Layer

| File | Responsibility | Key Functions |
|---|---|---|
| `__init__.py` | Package marker + `ServiceError` exception class | — |
| `book_service.py` | Book CRUD, search, filter, quantity validity checks | `add_book()`, `update_book()`, `deactivate_book()`, `get_books()`, `get_book_by_id()`, `search_books()` |
| `student_service.py` | Student CRUD, search, filter, issue history | `add_student()`, `update_student()`, `deactivate_student()`, `get_students()`, `search_students()`, `get_student_history()` |
| `issue_service.py` | Issue/return workflow with transactions | `issue_book()`, `return_book()`, `get_pending_returns()`, `get_overdue_books()` |
| `report_service.py` | 10 report types with filters and date ranges | `get_report_data(report_type, filters)` |
| `excel_service.py` | Import books/students from Excel; export reports and data to Excel | `import_books_excel()`, `import_students_excel()`, `export_books_excel()`, `export_students_excel()`, `export_report_excel()`, `export_full_backup_excel()` |
| `backup_service.py` | SQLite file copy backup and restore | `create_db_backup()`, `restore_db_backup()` |

### 4.3 `ui/` — Presentation Layer

| File | Responsibility |
|---|---|
| `__init__.py` | Package marker |
| `theme.py` | `global_stylesheet()` (QSS string), `make_button()`, `badge_in_cell()`, `show_success()`, `show_error()`, `show_confirmation()`, dialog helpers |
| `main_window.py` | `MainWindow(QMainWindow)`: sidebar + `QStackedWidget` with all 7 pages. `NAV_ITEMS` list defines nav structure. `navigate(index)` switches pages. `refresh_all()` refreshes every page. |
| `dashboard.py` | `DashboardPage`: 7 stat cards, recent issues/returns tables |
| `books_page.py` | `BooksPage`: search, filter, table, add/edit dialog, import/export buttons |
| `students_page.py` | `StudentsPage`: search, filter, table, add/edit dialog, view history, import/export |
| `issue_book_page.py` | `IssueBookPage`: student picker, book picker, date inputs, issue button |
| `return_book_page.py` | `ReturnBookPage`: pending returns table, detail panel, return form |
| `reports_page.py` | `ReportsPage`: report type selector, filters, table, export button |
| `settings_page.py` | `SettingsPage`: config form fields, save, backup/restore buttons |

### 4.4 Root Files

| File | Responsibility |
|---|---|
| `main.py` | Entry point: create `QApplication`, set stylesheet, instantiate `MainWindow`, show, exec event loop |
| `requirements.txt` | Python package dependencies |
| `README.md` | User-facing setup and usage instructions |

---

## 5. Database Schema

### 5.1 Tables (5 total)

| Table | Purpose | Key Constraints |
|---|---|---|
| `books` | Book metadata + quantity | `CHECK(total >= 0)`, `CHECK(avail >= 0)`, `CHECK(avail <= total)`, `isbn UNIQUE` |
| `students` | Student records | `student_code UNIQUE` |
| `book_issues` | Issue + return records | `FOREIGN KEY(book_id, student_id)`, `CHECK(return_date >= issue_date)` |
| `settings` | Key-value app config | `setting_key UNIQUE` |
| `activity_logs` | Optional audit trail | — |

### 5.2 Indexes (16 total)

- `books`: title, author, category, isbn, status
- `students`: student_code, name, class_name, status
- `book_issues`: book_id, student_id, status, issue_date, due_date, return_date
- `idx_unique_active_issue`: partial unique index on `(student_id, book_id) WHERE status = 'ISSUED'` (enforces no duplicate pending issues)

### 5.3 Default Settings

| Key | Default Value |
|---|---|
| `school_name` | ABC Public School |
| `library_name` | School Library |
| `default_due_days` | 7 |
| `low_stock_limit` | 2 |
| `backup_path` | backups |
| `export_path` | exports |

---

## 6. Data Flow Diagrams

### 6.1 Issue Book

```
IssueBookPage                issue_service                 database
    │                            │                            │
    ├─ validate_input() ────────>│                            │
    │<── valid / error ──────────│                            │
    │                            ├─ BEGIN TRANSACTION ───────>│
    │                            ├─ Check student active ────>│
    │                            ├─ Check book active ───────>│
    │                            ├─ Check avail > 0 ─────────>│
    │                            ├─ Check no duplicate ──────>│
    │                            ├─ INSERT book_issues ──────>│
    │                            ├─ UPDATE books SET avail-1 >│
    │                            ├─ COMMIT ──────────────────>│
    │<── success / error ────────│                            │
```

### 6.2 Return Book

```
ReturnBookPage                issue_service                 database
    │                            │                            │
    ├─ validate_return() ───────>│                            │
    │<── valid / error ──────────│                            │
    │                            ├─ BEGIN TRANSACTION ───────>│
    │                            ├─ Check status = ISSUED ───>│
    │                            ├─ UPDATE status=RETURNED ──>│
    │                            ├─ SET return_date ─────────>│
    │                            ├─ UPDATE books SET avail+1 >│
    │                            ├─ COMMIT ──────────────────>│
    │<── success / error ────────│                            │
```

### 6.3 Excel Import

```
User                     excel_service                 database
  │                            │                            │
  ├─ Select .xlsx file ────────>│                            │
  │                            ├─ openpyxl load_workbook ───>│
  │                            ├─ Validate columns ─────────>│
  │                            ├─ For each row: ────────────>│
  │                            │   ├─ Validate fields ──────>│
  │                            │   ├─ INSERT or UPDATE ─────>│
  │                            ├─ Return summary ───────────>│
  │<── "120 imported, 5 skipped"│                            │
```

---

## 7. Validation Matrix

Every function in `app/validators.py` returns a list of error messages.

| Function | Checks |
|---|---|
| `validate_book(data)` | title required, total_quantity required & >= 0, ISBN unique if given |
| `validate_student(data)` | student_code required & unique, name required, email format if given |
| `validate_issue(student, book, issue_date, due_date)` | student/book selected, both active, avail > 0, no duplicate pending, due >= issue |
| `validate_return(issue_record, return_date)` | record exists, status=ISSUED, return_date >= issue_date |

---

## 8. Python Dependencies

| Package | Min Version | Used For |
|---|---|---|
| PySide6 | 6.5.0 | Desktop UI framework |
| openpyxl | 3.1.0 | Excel file read/write |
| (sqlite3) | Bundled | Database engine |
| (os, shutil, datetime) | Bundled | File ops, date handling |

Python 3.10+ is required (for structural pattern matching, `|` union types in type hints).

---

## 9. Directory Structure After Build

```
school-library-management/
├── main.py                  # Entry point
├── requirements.txt         # pip dependencies
├── README.md                # Setup guide
├── plan.md                  # Original project plan
├── prd.md                   # Product requirements
├── appflow.md               # Application flow
├── design.md                # Visual design spec
├── database.md              # Database design spec
├── techspec.md              # THIS FILE
├── implementationplan.md    # Implementation plan
├── security.md              # Security considerations
├── testing.md               # Testing plan
├── deployment.md            # Deployment guide
├── app/                     # Core logic (5 files)
├── services/                # Business logic (7 files)
├── ui/                      # PySide6 UI (10 files)
├── database/
│   ├── library.db           # SQLite database (auto-created)
│   └── schema.sql           # Full schema reference
├── exports/                 # Excel report output folder
├── backups/                 # Database backup folder
└── assets/
    ├── icons/               # Application icons
    └── images/              # Application images
```

---

## 10. Error Handling Strategy

| Error Source | Handling |
|---|---|
| Validation errors | Returned as list of strings → displayed in UI dialog |
| `ServiceError` | Caught in UI, shown as user-friendly error popup |
| Database constraint violation | Caught in service, wrapped in `ServiceError` with clear message |
| Unexpected exception | Caught in UI event handler, logged if possible, generic "Something went wrong" shown |
| Excel file not found/readable | `ServiceError` with "Cannot read file" message |
| Excel incorrect columns | `ServiceError` listing required columns |
| Backup folder missing | Auto-created; if creation fails, shown as error |
| Restore cancelled mid-way | Current DB auto-backed up before restore; original can be recovered |

---

## 11. Performance Targets

| Operation | Target | Notes |
|---|---|---|
| App startup | < 3 seconds | Cold start, DB init |
| Search 10,000 books | < 500 ms | With indexes |
| Issue a book | < 200 ms | Transaction includes 2 writes |
| Return a book | < 200 ms | Transaction includes 2 updates |
| Export 5,000-row report | < 5 seconds | openpyxl write |
| Database backup | < 1 second | File copy of .db |

---

## 12. Future Technical Considerations

- **Migrations**: Add `database/migrations/` folder with numbered SQL files and a `migrations` tracking table.
- **Login**: Add `users` table, `app/auth.py` for password hashing, login dialog in UI.
- **Barcode**: Add `book_barcodes` table, integrate USB barcode scanner as keyboard input.
- **Multi-language**: Externalize all UI strings into `app/strings.py` or JSON resource files.
- **Logging**: Replace `print()` with `logging` module, direct output to `logs/` folder.

---

## 13. Technical Constraints

- Must run fully offline with no internet dependency.
- Must run on Windows 10/11 (64-bit).
- Must not require admin privileges to install or run.
- Database file must be portable — can be copied for backup.
- Excel files must be openable in Microsoft Excel 2016+ and LibreOffice.
