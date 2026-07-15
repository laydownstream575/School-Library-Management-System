# School Library Management System — Testing Plan

## 1. Document Purpose

This document defines the testing strategy, test cases, and acceptance criteria for the School Library Management System desktop application.

Tests are organized by module and cover unit, integration, and end-to-end scenarios.

---

## 2. Testing Levels

| Level | Scope | Responsibility |
|---|---|---|
| Unit | Individual functions (validators, utils, helpers) | Developer |
| Integration | Service layer + database | Developer |
| UI | Page rendering, navigation, user interaction | Developer / QA |
| End-to-End | Complete workflows (add → issue → return → report) | QA |
| Acceptance | Feature-level verification against PRD | QA / Client |
| Packaging | Installed `.exe` behavior | QA |

---

## 3. Unit Tests — `app/validators.py`

### Test: `validate_book`

| # | Input | Expected Errors |
|---|---|---|
| 1 | Empty title | `["Book title is required."]` |
| 2 | Missing total_quantity | `["Total quantity is required."]` |
| 3 | Non-numeric quantity | `["Quantity must be a valid number."]` |
| 4 | Negative quantity | `["Quantity cannot be negative."]` |
| 5 | Valid book | `[]` (no errors) |
| 6 | ISBN already in use | `["ISBN already exists in the database."]` |

### Test: `validate_student`

| # | Input | Expected Errors |
|---|---|---|
| 1 | Empty student_code | `["Student ID is required."]` |
| 2 | Empty name | `["Student name is required."]` |
| 3 | Duplicate student_code | `["Student ID already exists."]` |
| 4 | Invalid email | `["Invalid email format."]` |
| 5 | Valid student | `[]` |

### Test: `validate_issue`

| # | Input | Expected Errors |
|---|---|---|
| 1 | No student selected | `["Please select a student."]` |
| 2 | No book selected | `["Please select a book."]` |
| 3 | Inactive student | `["Cannot issue book to inactive student."]` |
| 4 | Inactive book | `["Cannot issue inactive book."]` |
| 5 | Available qty = 0 | `["This book is currently not available."]` |
| 6 | Duplicate pending issue | `["This student already has this book issued."]` |
| 7 | Due date < issue date | `["Due date cannot be earlier than issue date."]` |
| 8 | All valid | `[]` |

### Test: `validate_return`

| # | Input | Expected Errors |
|---|---|---|
| 1 | No issue record | `["Please select an issued book record."]` |
| 2 | Status = RETURNED | `["This book has already been returned."]` |
| 3 | Return date < issue date | `["Return date cannot be before issue date."]` |
| 4 | All valid | `[]` |

---

## 4. Unit Tests — `app/utils.py`

| # | Test | Expected |
|---|---|---|
| 1 | `format_display_date("2026-07-01")` | `"01 Jul 2026"` |
| 2 | `format_display_date(None)` | `"-"` |
| 3 | `get_today_iso()` | Current date in `YYYY-MM-DD` format |
| 4 | `parse_date("2026-07-01")` | `date(2026, 7, 1)` |
| 5 | `datetime_now_iso()` | Current datetime in `YYYY-MM-DD HH:MM:SS` format |

---

## 5. Integration Tests — Book Service

### Test: Book CRUD

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Add valid book | `add_book({"title": "Math 10", "total_quantity": 5})` | Returns book dict with id, avail=5 |
| 2 | Add book without title | `add_book({"total_quantity": 5})` | Raises ServiceError |
| 3 | Search by title | Search "Math" | Returns matching books |
| 4 | Search by partial title | Search "Ma" | Returns matching books |
| 5 | Update book quantity | `update_book(id, {"total_quantity": 10})` | total=10, avail unchanged |
| 6 | Deactivate book | `deactivate_book(id)` | status = 'INACTIVE' |
| 7 | Deactivate book with active issues | Attempt deactivation while issued | Raises ServiceError |
| 8 | Search returns only active by default | After deactivation | Book not in search results |

### Test: Book Quantity Rules

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Available = total on creation | Add book with total=10 | avail=10 |
| 2 | Cannot reduce total below issued | total=5, issued=3, set total=2 | Raises ServiceError |

---

## 6. Integration Tests — Student Service

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Add valid student | `add_student({"student_code": "STU001", "name": "Rahul"})` | Returns student dict with id |
| 2 | Add duplicate student_code | Same code again | Raises ServiceError |
| 3 | Search by name | Search "Rahul" | Returns matching students |
| 4 | Search by student_code | Search "STU001" | Returns exact match |
| 5 | Deactivate student | `deactivate_student(id)` | status = 'INACTIVE' |
| 6 | Deactivate with active issues | Attempt while student has pending books | Raises ServiceError |
| 7 | View issue history | After issue/return | Returns ordered list of records |

---

## 7. Integration Tests — Issue Service

### Test: Issue Book

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Issue available book | Issue book to student | avail decreases by 1, status=ISSUED |
| 2 | Issue when qty=0 | Try issuing at 0 avail | Raises ServiceError |
| 3 | Duplicate issue | Issue same book to same student again | Raises ServiceError |
| 4 | Issue inactive book | Deactivate book, try to issue | Raises ServiceError |
| 5 | Issue to inactive student | Deactivate student, try to issue | Raises ServiceError |
| 6 | Issue multiple students | Issue same book to different students | Works, avail decreases each time |
| 7 | Verify transaction rollback | Force error between INSERT and UPDATE | No orphan records |

### Test: Return Book

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Return issued book | Return with valid return date | avail increases by 1, status=RETURNED |
| 2 | Return already returned | Try returning the same record | Raises ServiceError |
| 3 | Return with date < issue date | Return date before issue | Raises ServiceError |
| 4 | Verify quantity ceiling | After return, avail <= total | Constraint enforced |

### Test: Pending Returns

| # | Scenario | Steps | Expected |
|---|---|---|---|
| 1 | Get pending returns | Issue book, call `get_pending_returns()` | Returns 1 record |
| 2 | After return, empty | Return the book, call again | Returns 0 records |
| 3 | Overdue calculation | Issue with old due date | Overdue days > 0 |

---

## 8. Integration Tests — Report Service

| # | Report Type | Verification |
|---|---|---|
| 1 | All books | Returns all active books with full columns |
| 2 | Available books | Returns only books with avail > 0 |
| 3 | Issued books | Returns books with active issues |
| 4 | Returned books | Returns books with status = RETURNED |
| 5 | Pending returns | Returns issued books with student/book details |
| 6 | Overdue books | Returns only books past due date |
| 7 | Students | Returns all active students |
| 8 | Student-wise history | Returns issue history for a given student |
| 9 | Date-wise issues | Filters by issue date range |
| 10 | Date-wise returns | Filters by return date range |
| 11 | Low stock | Returns books with avail <= low_stock_limit |

---

## 9. Integration Tests — Excel Service

### Test: Import Books

| # | Scenario | Expected |
|---|---|---|
| 1 | Valid .xlsx with all columns | All rows imported, correct count returned |
| 2 | Missing required column | Error with list of required columns |
| 3 | Mixed valid and invalid rows | Valid imported, invalid skipped, summary shown |
| 4 | ISBN matches existing book | Book updated, not duplicated |
| 5 | Empty quantity field | Row skipped, reported in summary |

### Test: Import Students

| # | Scenario | Expected |
|---|---|---|
| 1 | Valid .xlsx with all columns | All rows imported |
| 2 | Duplicate student_code | Row skipped, reported in summary |
| 3 | Missing name field | Row skipped |

### Test: Export

| # | Scenario | Expected |
|---|---|---|
| 1 | Export books | Valid .xlsx with correct headers |
| 2 | Export students | Valid .xlsx with correct headers |
| 3 | Export all 11 report types | Each file opens correctly in Excel |
| 4 | Full backup export | 4 sheets: Books, Students, Book Issues, Settings |

---

## 10. Integration Tests — Backup Service

| # | Scenario | Expected |
|---|---|---|
| 1 | Create SQLite backup | File created at `backups/library_backup_YYYY-MM-DD_HH-MM.db` |
| 2 | Restore SQLite backup | Database replaced, data matches backup |
| 3 | Restore with missing backup file | Clear error message |
| 4 | Pre-restore auto-backup | Current DB backed up before restore |

---

## 11. UI Tests

### Test: Main Window

| # | Scenario | Expected |
|---|---|---|
| 1 | App launches without error | Window appears with title |
| 2 | Default window size | >= 1100x700 |
| 3 | Sidebar visible | 7 navigation items |
| 4 | Dashboard shown by default | Dashboard page loaded |
| 5 | Each nav item switches page | All 7 pages navigate correctly |

### Test: Dashboard

| # | Scenario | Expected |
|---|---|---|
| 1 | All stat cards visible | 7 cards with correct labels |
| 2 | Numbers match database | Each card shows correct live count |
| 3 | Recent activity tables | Recent issues and returns shown |
| 4 | Empty state | Shows "No data" when database is empty |

### Test: Books Page

| # | Scenario | Expected |
|---|---|---|
| 1 | Table columns match spec | All 10 columns present |
| 2 | Add Book dialog opens | Form with required field indicators |
| 3 | Save with missing title | Error shown, not saved |
| 4 | Save valid book | Book added, table refreshed, success message |
| 5 | Edit prepopulates form | Existing values shown |
| 6 | Search filters table | Results update on each keystroke |
| 7 | Category filter works | Books filtered by selected category |
| 8 | Status badge colors | Green/orange/red/gray as per spec |

### Test: Students Page

| # | Scenario | Expected |
|---|---|---|
| 1 | Table columns match spec | All columns present |
| 2 | Add/Edit dialog validates | Required fields enforced |
| 3 | View History shows modal | Issue/return records displayed |
| 4 | Class/division filter works | Students filtered |

### Test: Issue Book Page

| # | Scenario | Expected |
|---|---|---|
| 1 | Student search works | Results update on input |
| 2 | Book search works | Results update on input |
| 3 | Available quantity shown | Clear label before issuing |
| 4 | Issue button disabled when | No selection, qty=0, inactive entities |
| 5 | Successful issue | Success message, quantity updates everywhere |

### Test: Return Book Page

| # | Scenario | Expected |
|---|---|---|
| 1 | Only ISSUED records shown | No RETURNED records in list |
| 2 | Select shows detail | Student/book/dates displayed |
| 3 | Overdue rows highlighted | Red background for overdue |
| 4 | Successful return | Success message, quantity updates |

### Test: Reports Page

| # | Scenario | Expected |
|---|---|---|
| 1 | All report types selectable | Dropdown shows 10+ report types |
| 2 | Generate shows correct data | Table matches database state |
| 3 | Export creates file | Valid .xlsx in exports/ |
| 4 | Date filters work | Records filtered correctly |

### Test: Settings Page

| # | Scenario | Expected |
|---|---|---|
| 1 | Settings load on page open | Fields populated from DB |
| 2 | Save persists settings | After restart, values unchanged |
| 3 | Backup button works | File created in backups/ |
| 4 | Restore with confirmation | Warning dialog shown |

---

## 12. End-to-End Workflow Tests

### E2E 1: Full Lifecycle

```
1. Launch app
2. Verify dashboard shows 0 for all counts
3. Add book "Mathematics" (qty=3)
4. Add student "Rahul" (ID=STU001)
5. Verify dashboard: books=3, students=1
6. Issue "Mathematics" to Rahul with 7-day due period
7. Verify dashboard: issued=1, avail=2
8. Issue same book to Rahul again → blocked with error
9. Add another student "Priya" (ID=STU002)
10. Issue "Mathematics" to Priya → works
11. Verify dashboard: issued=2, avail=1
12. Return Rahul's book
13. Verify dashboard: issued=1, avail=2
14. Generate pending returns report → shows Priya's book
15. Export pending returns to Excel → file opens correctly
16. Verify quantity: total=3, avail=2, issued=1 → 2 + 1 = 3 ✓
```

### E2E 2: Edge Cases

```
1. Try issuing when avail=0 → blocked
2. Try returning already returned book → blocked
3. Deactivate book with active issue → blocked
4. Deactivate student with active issue → blocked
5. Search with empty query → shows all
6. Search with no match → empty state message
7. Import Excel with 50 valid + 5 invalid rows → 50 imported, 5 reported
8. Backup database → verify file exists
9. Restore backup → verify data matches pre-restore state
```

---

## 13. Packaging Tests

| # | Test | Expected |
|---|---|---|
| 1 | PyInstaller build completes | `.exe` generated without errors |
| 2 | `.exe` runs on Windows 10 | App launches, all features work |
| 3 | `.exe` runs on Windows 11 | App launches, all features work |
| 4 | Database created on first run | `database/library.db` exists |
| 5 | Backup/restore work in packaged app | File operations succeed |
| 6 | Excel import/export work in packaged app | File operations succeed |
| 7 | Error messages shown gracefully | No console windows or tracebacks |

---

## 14. Test Environment

| Component | Specification |
|---|---|
| OS | Windows 10 (22H2), Windows 11 (23H2) |
| Python | 3.10, 3.11, 3.12 |
| RAM | 4 GB minimum |
| Disk | 100 MB free space |
| Display | 1366x768 minimum |

---

## 15. Bug Severity Classification

| Severity | Definition | Response |
|---|---|---|
| Critical | App crashes, data loss, quantity calculation wrong | Fix immediately, block release |
| High | Feature broken, wrong data shown, import/export fails | Fix in current sprint |
| Medium | Minor UI issue, non-critical validation message | Fix before next release |
| Low | Cosmetic, typo, label improvement | Defer to future release |
