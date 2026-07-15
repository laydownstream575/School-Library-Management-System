# School Library Management System — Implementation Plan

## 1. Document Purpose

This document provides a detailed, step-by-step implementation plan for building the School Library Management System desktop application.

Each phase lists specific tasks, estimated effort, prerequisites, and acceptance criteria. The plan is designed to be followed sequentially.

---

## 2. Phase Overview

| Phase | Name | Effort | Dependencies |
|---|---|---|---|
| 0 | Environment Setup | 1 hour | None |
| 1 | Database Layer | 2 hours | Phase 0 |
| 2 | Core App Layer | 2 hours | Phase 1 |
| 3 | Service Layer | 6 hours | Phase 1, 2 |
| 4 | UI Base (window, nav, theme) | 4 hours | Phase 2 |
| 5 | UI — Dashboard & Books | 6 hours | Phase 3, 4 |
| 6 | UI — Students, Issue, Return | 8 hours | Phase 3, 4 |
| 7 | UI — Reports & Settings | 6 hours | Phase 3, 4 |
| 8 | Excel Import/Export Integration | 4 hours | Phase 3 |
| 9 | Backup/Restore Integration | 2 hours | Phase 3 |
| 10 | Testing & QA | 6 hours | Phase 5-9 |
| 11 | Packaging & Delivery | 3 hours | Phase 10 |

**Total estimated effort: ~44 hours**

---

## 3. Phase 0 — Environment Setup (1 hour)

### Tasks

| # | Task | Details |
|---|---|---|
| 0.1 | Create project directory structure | `school-library-management/` with all subfolders |
| 0.2 | Create Python virtual environment | `python -m venv venv` |
| 0.3 | Install dependencies | `pip install PySide6 openpyxl` |
| 0.4 | Create `requirements.txt` | Lock versions |
| 0.5 | Copy design document and all spec files | `plan.md`, `prd.md`, `appflow.md`, `design.md`, `database.md` |
| 0.6 | Initialize git repo | `git init` with `.gitignore` for `.db`, `__pycache__/`, `venv/`, `exports/`, `backups/` |

### Acceptance

- `pip install -r requirements.txt` succeeds.
- Project folder structure exists with all directories.

---

## 4. Phase 1 — Database Layer (2 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 1.1 | Create `database/schema.sql` | Full schema: 5 tables, 16 indexes, default settings |
| 1.2 | Implement `app/database.py` | `get_connection()`, `initialize_database()`, `execute()`, `fetch_all()`, `fetch_one()` |
| 1.3 | Test DB creation | Run `initialize_database()`, verify 5 tables + 16 indexes exist |
| 1.4 | Test constraint enforcement | Insert violates: negative quantity, duplicate student, duplicate pending issue |

### Acceptance

- SQLite file created at `database/library.db`.
- All 5 tables present with correct columns and constraints.
- Duplicate issue prevention (partial unique index) works.
- Quantity constraints (`CHECK`) work.

---

## 5. Phase 2 — Core App Layer (2 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 2.1 | Create `app/config.py` | `Config` dataclass, `load_config()`, `save_config()` |
| 2.2 | Create `app/validators.py` | `validate_book()`, `validate_student()`, `validate_issue()`, `validate_return()` |
| 2.3 | Create `app/utils.py` | Date formatting, ISO date helpers |
| 2.4 | Create `app/__init__.py` | Package docstring |

### Acceptance

- Each validator function returns correct errors for known bad inputs.
- Empty list returned for valid inputs.
- Date helpers handle None and ISO strings correctly.

---

## 6. Phase 3 — Service Layer (6 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 3.1 | Implement `services/__init__.py` | `ServiceError` exception class |
| 3.2 | Implement `services/book_service.py` | `add_book()`, `update_book()`, `deactivate_book()`, `get_books()`, `search_books()`, `get_book_by_id()` |
| 3.3 | Implement `services/student_service.py` | `add_student()`, `update_student()`, `deactivate_student()`, `get_students()`, `search_students()`, `get_student_history()` |
| 3.4 | Implement `services/issue_service.py` | `issue_book()` (transaction), `return_book()` (transaction), `get_pending_returns()`, `get_overdue_books()` |
| 3.5 | Implement `services/report_service.py` | 10 report types with search/filter/date-range |
| 3.6 | Implement `services/excel_service.py` | `import_books_excel()`, `import_students_excel()`, `export_*()` for all reports, `export_full_backup_excel()` |
| 3.7 | Implement `services/backup_service.py` | `create_db_backup()`, `restore_db_backup()` with pre-restore auto-backup |

### Acceptance

- Full CRUD cycle for books: add, search, update, deactivate.
- Full CRUD cycle for students: add, search, update, deactivate.
- Issue book: quantity decreases, duplicate blocked, inactive book/student blocked.
- Return book: quantity increases, already-returned blocked.
- Reports return correct data for every report type.
- Excel import reads valid rows, skips invalid, reports summary.
- Excel export creates valid .xlsx files.
- Backup copies .db; restore replaces .db with auto-backup of current.

---

## 7. Phase 4 — UI Base (4 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 4.1 | Create `ui/theme.py` | `global_stylesheet()`, `make_button()`, `badge_in_cell()`, `show_success()`, `show_error()`, `show_confirmation()` |
| 4.2 | Create `ui/main_window.py` | `MainWindow` with sidebar (`QListWidget`) + `QStackedWidget`, `navigate()`, `refresh_all()` |
| 4.3 | Create placeholder pages | 7 placeholder pages to verify navigation |
| 4.4 | Create `main.py` | Entry point: create `QApplication`, apply stylesheet, show window |
| 4.5 | Test navigation | Click each sidebar item, verify correct page shown |

### Acceptance

- App launches, shows sidebar + content area.
- Clicking each nav item switches the content page.
- Theme applied (colors, fonts, button styles consistent with `design.md`).

---

## 8. Phase 5 — UI Dashboard & Books (6 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 5.1 | Implement `ui/dashboard.py` | 7 stat cards: total books, available, issued, students, pending, overdue, low stock; recent issues/returns tables |
| 5.2 | Implement `ui/books_page.py` | Search bar, category/status/availability filter dropdowns, books table with edit/deactivate actions, add/edit dialog (modal) |
| 5.3 | Wire up: Add Book button | Open dialog → validate → call `book_service.add_book()` → refresh |
| 5.4 | Wire up: Edit Book button | Open dialog with data → validate → call `book_service.update_book()` → refresh |
| 5.5 | Wire up: Deactivate button | Confirmation dialog → call `book_service.deactivate_book()` → refresh |
| 5.6 | Wire up: Search/filter | TextChanged + filter combo → call `book_service.search_books()` → update table |
| 5.7 | Wire up: Import/Export buttons | File dialog → call `excel_service` functions |

### Acceptance

- Dashboard shows correct live stats.
- Books table shows all/search/filtered books.
- Add/edit form validates and saves.
- Deactivate shows confirmation and works.
- Available quantity badges display correctly (Available/Low Stock/Not Available).
- Excel import/export works from Books page.

---

## 9. Phase 6 — UI Students, Issue, Return (8 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 6.1 | Implement `ui/students_page.py` | Search, class/division/status filters, student table with edit/view history/deactivate, add/edit dialog |
| 6.2 | Implement: Student Issue History | Modal table showing all issue/return records for selected student |
| 6.3 | Implement `ui/issue_book_page.py` | Student search+selection panel, book search+selection panel, issue/due date inputs, issue button, available quantity display |
| 6.4 | Wire up: Issue Book | Validate → call `issue_service.issue_book()` → show success → refresh |
| 6.5 | Implement `ui/return_book_page.py` | Pending returns searchable table, detail card on selection, return date + remarks, return button |
| 6.6 | Wire up: Return Book | Validate → call `issue_service.return_book()` → show success → refresh |
| 6.7 | Wire up: Overdue highlighting | Rows with overdue days > 0 shown with red background + OVERDUE badge |

### Acceptance

- Issue flow: select student → select book → see available qty → issue → qty decreases.
- Return flow: search pending → select → return → qty increases.
- Duplicate issue blocked with clear message.
- Inactive student/book blocked with clear message.
- Overdue rows visually distinguished.
- Student history shows all past issues.

---

## 10. Phase 7 — UI Reports & Settings (6 hours)

### Tasks

| # | Task | File |
|---|---|---|
| 7.1 | Implement `ui/reports_page.py` | Report type dropdown, date range pickers, filter combos, generate button, export button, results table |
| 7.2 | Wire up: Generate Report | Call `report_service.get_report_data()` → populate table |
| 7.3 | Wire up: Export to Excel | Call `excel_service.export_report_excel()` → show success with file path |
| 7.4 | Implement `ui/settings_page.py` | School name, library name, default due days, low stock limit, backup/export path fields, save button |
| 7.5 | Wire up: Save Settings | Validate → call `config.save_config()` → show success |
| 7.6 | Wire up: Backup Database | Call `backup_service.create_db_backup()` → show success |
| 7.7 | Wire up: Export Full Backup | Call `excel_service.export_full_backup_excel()` → show success |
| 7.8 | Wire up: Restore Backup | Confirmation → file dialog → auto-backup current DB → call `backup_service.restore_db_backup()` → restart/refresh |

### Acceptance

- All 10 report types generate correct data.
- Date range and filter combos work.
- Excel export produces valid .xlsx files.
- Settings are saved and persist across app restarts.
- Database backup/restore works (backup creates file, restore replaces DB).
- Full Excel backup exports all tables as separate sheets.

---

## 11. Phase 8 — Excel Import/Export Integration (4 hours)

### Tasks

| # | Task | Details |
|---|---|---|
| 8.1 | Wire Books Import | File dialog → `excel_service.import_books_excel()` → show import summary dialog |
| 8.2 | Wire Students Import | File dialog → `excel_service.import_students_excel()` → show import summary dialog |
| 8.3 | Wire Books Export | `excel_service.export_books_excel()` → save in exports/ → show success |
| 8.4 | Wire Students Export | `excel_service.export_students_excel()` → save in exports/ → show success |
| 8.5 | Test import with invalid data | Missing columns, non-numeric quantity, duplicate student IDs |
| 8.6 | Test export all formats | Ensure .xlsx opens correctly in Excel |

### Acceptance

- Import with 100% valid data imports all rows.
- Import with mixed valid/invalid data imports valid rows and reports skipped count.
- Export files are valid Excel files with proper headers.

---

## 12. Phase 9 — Backup/Restore Integration (2 hours)

### Tasks

| # | Task | Details |
|---|---|---|
| 9.1 | Ensure `backups/` folder auto-created | In `initialize_database()` or first backup call |
| 9.2 | Test SQLite backup | Verify file created with timestamp, can be restored |
| 9.3 | Test SQLite restore | Replace current DB with backup, verify data matches |
| 9.4 | Test Excel full backup | Verify all 4 sheets (Books, Students, Book Issues, Settings) |

### Acceptance

- Backup file named `library_backup_YYYY-MM-DD_HH-MM.db` created in `backups/`.
- Restore replaces current data and shows success.
- Pre-restore auto-backup creates safety copy.
- Excel backup contains all 4 sheets with correct data.

---

## 13. Phase 10 — Testing & QA (6 hours)

### Tasks

| # | Task | Details |
|---|---|---|
| 10.1 | Run all service-level tests | CRUD, validation, edge cases, quantity accuracy |
| 10.2 | Run all UI navigation tests | All 7 pages load and render |
| 10.3 | Run end-to-end workflow | Add book → add student → issue → return → verify quantity |
| 10.4 | Run import/export tests | Excel import with edge cases, export readability |
| 10.5 | Run backup/restore tests | Backup, restore, verify data integrity |
| 10.6 | Test edge cases | Issue when qty=0, return already returned, deactivate active book, search with no results |
| 10.7 | Test with realistic data | 500 books, 200 students, 1000+ issue records |
| 10.8 | Fix all discovered bugs | — |

### Acceptance

- All acceptance criteria from PRD sections 15.1–15.7 pass.
- No unhandled crashes during any workflow.
- Quantity updates are atomic and correct after every issue/return.

---

## 14. Phase 11 — Packaging & Delivery (3 hours)

### Tasks

| # | Task | Details |
|---|---|---|
| 11.1 | Install PyInstaller | `pip install pyinstaller` |
| 11.2 | Create `.spec` file | Configure for single-folder or single-file output |
| 11.3 | Build executable | `pyinstaller main.py --name "SchoolLibrary" --windowed --add-data "database/schema.sql;database"` |
| 11.4 | Test executable | Run `.exe` on clean Windows machine |
| 11.5 | Verify DB auto-creation | `.exe` should create `database/library.db` on first run |
| 11.6 | Create delivery folder | `SchoolLibrary_v1.0/` with `.exe`, `database/`, `README.txt`, `user guide` |
| 11.7 | Final QA on delivery build | — |

### Acceptance

- `.exe` runs on Windows 10/11 without Python installed.
- All features work identically to development version.
- Delivery folder is self-contained.

---

## 15. Risk Mitigation

| Risk | Mitigation | Phase |
|---|---|---|
| Python version mismatch | Pin `python_requires >= 3.10` and document clearly | Phase 0 |
| PySide6 Qt dependency | Test on target Windows version early | Phase 10 |
| Large Excel import time | Process in batches, show progress | Phase 8 |
| Database file corruption | Transaction wrapping on critical writes | Phase 1 |
| User accidentally deletes data | Deactivate instead of delete, confirmation dialogs | Phase 5, 6 |
| Backup restore data loss | Auto-backup current DB before restoring | Phase 9 |

---

## 16. Deliverables Checklist

- [ ] `main.py` — Application entry point
- [ ] `requirements.txt` — Dependencies
- [ ] `README.md` — User documentation
- [ ] `app/` — 5 core Python files
- [ ] `services/` — 7 business logic files
- [ ] `ui/` — 10 PySide6 UI files
- [ ] `database/schema.sql` — Full schema
- [ ] `database/library.db` — Auto-created on first run
- [ ] `exports/` — Export output folder
- [ ] `backups/` — Backup output folder
- [ ] `assets/icons/` — App icons
- [ ] `assets/images/` — App images
- [ ] `dist/SchoolLibrary.exe` — Packaged Windows executable
