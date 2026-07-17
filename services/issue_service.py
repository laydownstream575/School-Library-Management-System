"""Issue / return business logic.

Both issue and return run inside a single SQLite transaction so the issue
record and the book's ``available_quantity`` always stay consistent — if any
step fails, the whole operation rolls back.
"""

from app import database, utils, validators
from services import ServiceError


def has_active_issue(student_id: int, book_id: int) -> bool:
    """True if this student already holds this specific book (unreturned)."""
    try:
        row = database.fetch_one(
            "SELECT id FROM book_issues WHERE student_id = ? AND book_id = ? "
            "AND status = 'ISSUED'",
            (student_id, book_id),
        )
    except database.DatabaseError:
        raise ServiceError("Could not check existing issues.")
    return row is not None


def issue_book(student_id: int, book_id: int, issue_date: str,
               due_date: str = None, remarks: str = "") -> int:
    """Issue a book to a student atomically. Returns the new issue id.

    Validates active student/book, availability, duplicate pending issue, and
    date rules before writing. Decrements available_quantity by exactly 1.
    """
    if not student_id:
        raise ServiceError("Please select a student.")
    if not book_id:
        raise ServiceError("Please select a book.")

    date_check = validators.validate_issue_dates(issue_date, due_date)
    if not date_check:
        raise ServiceError(date_check.message)

    now = utils.now_timestamp()
    try:
        with database.transaction() as conn:
            student = conn.execute(
                "SELECT * FROM students WHERE id = ?", (student_id,)
            ).fetchone()
            if student is None:
                raise ServiceError("Student not found.")
            if student["status"] != "ACTIVE":
                raise ServiceError("Cannot issue book to an inactive student.")

            book = conn.execute(
                "SELECT * FROM books WHERE id = ?", (book_id,)
            ).fetchone()
            if book is None:
                raise ServiceError("Book not found.")
            if book["status"] != "ACTIVE":
                raise ServiceError("Cannot issue an inactive book.")
            if book["available_quantity"] <= 0:
                raise ServiceError("This book is currently not available.")

            # Duplicate pending issue guard (also enforced by a unique index).
            existing = conn.execute(
                "SELECT id FROM book_issues WHERE student_id = ? AND book_id = ? "
                "AND status = 'ISSUED'",
                (student_id, book_id),
            ).fetchone()
            if existing is not None:
                raise ServiceError("This student already has this book issued.")

            cursor = conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "due_date, return_date, status, remarks, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, NULL, 'ISSUED', ?, ?, ?)",
                (
                    book_id,
                    student_id,
                    issue_date,
                    due_date or None,
                    (remarks or "").strip() or None,
                    now,
                    now,
                ),
            )
            issue_id = cursor.lastrowid

            # Decrement availability only if a copy is genuinely free.
            updated = conn.execute(
                "UPDATE books SET available_quantity = available_quantity - 1, "
                "updated_at = ? WHERE id = ? AND available_quantity > 0",
                (now, book_id),
            )
            if updated.rowcount != 1:
                raise ServiceError("This book is currently not available.")
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_issue_error(exc)) from exc

    utils.log_activity(
        "BOOK_ISSUED",
        f"Book id={book_id} issued to student id={student_id}",
    )
    return issue_id


def return_book(issue_id: int, return_date: str, remarks: str = None) -> None:
    """Return an issued book atomically.

    Only ISSUED records can be returned. Sets status/return_date and increments
    available_quantity by exactly 1 (never above total_quantity).
    """
    if not issue_id:
        raise ServiceError("Please select an issued book record.")

    now = utils.now_timestamp()
    try:
        with database.transaction() as conn:
            issue = conn.execute(
                "SELECT * FROM book_issues WHERE id = ?", (issue_id,)
            ).fetchone()
            if issue is None:
                raise ServiceError("Issue record not found.")
            if issue["status"] != "ISSUED":
                raise ServiceError("This book has already been returned.")

            date_check = validators.validate_return_date(
                issue["issue_date"], return_date
            )
            if not date_check:
                raise ServiceError(date_check.message)

            new_remarks = remarks if remarks is not None else issue["remarks"]
            conn.execute(
                "UPDATE book_issues SET status = 'RETURNED', return_date = ?, "
                "remarks = ?, updated_at = ? WHERE id = ? AND status = 'ISSUED'",
                (return_date, new_remarks, now, issue_id),
            )

            # Increment availability, capped at total_quantity.
            conn.execute(
                "UPDATE books SET available_quantity = available_quantity + 1, "
                "updated_at = ? WHERE id = ? AND available_quantity < total_quantity",
                (now, issue["book_id"]),
            )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_issue_error(exc)) from exc

    utils.log_activity("BOOK_RETURNED", f"Issue id={issue_id} returned")


def get_pending_returns(search: str = ""):
    """All ISSUED records with student/book details and overdue days."""
    like = f"%{search.strip()}%" if search else "%"
    query = (
        "SELECT bi.id AS issue_id, s.id AS student_id, s.student_code, "
        "s.name AS student_name, b.id AS book_id, b.title AS book_title, "
        "bi.issue_date, bi.due_date, bi.status "
        "FROM book_issues bi "
        "JOIN books b ON bi.book_id = b.id "
        "JOIN students s ON bi.student_id = s.id "
        "WHERE bi.status = 'ISSUED' AND "
        "(s.student_code LIKE ? OR s.name LIKE ? OR b.title LIKE ?) "
        "ORDER BY bi.due_date IS NULL, bi.due_date ASC"
    )
    try:
        rows = database.fetch_all(query, (like, like, like))
    except database.DatabaseError:
        raise ServiceError("Could not load pending returns.")
    result = []
    for row in rows:
        item = dict(row)
        item["overdue_days"] = utils.overdue_days(item.get("due_date"))
        result.append(item)
    return result


def get_overdue_books(search: str = ""):
    """ISSUED records whose due date is in the past, with overdue days.

    If ``search`` is provided, filters by student code, name, or book title.
    """
    like = f"%{search.strip()}%" if search else "%"
    query = (
        "SELECT bi.id AS issue_id, s.student_code, s.name AS student_name, "
        "b.title AS book_title, bi.issue_date, bi.due_date, "
        "CAST(julianday('now') - julianday(bi.due_date) AS INTEGER) AS overdue_days "
        "FROM book_issues bi "
        "JOIN books b ON bi.book_id = b.id "
        "JOIN students s ON bi.student_id = s.id "
        "WHERE bi.status = 'ISSUED' AND bi.due_date IS NOT NULL "
        "AND date(bi.due_date) < date('now') "
        "AND (s.student_code LIKE ? OR s.name LIKE ? OR b.title LIKE ?) "
        "ORDER BY bi.due_date ASC"
    )
    try:
        rows = database.fetch_all(query, (like, like, like))
    except database.DatabaseError:
        raise ServiceError("Could not load overdue books.")
    return [dict(r) for r in rows]


def get_issue(issue_id: int):
    """Full detail for one issue record joined with student and book."""
    query = (
        "SELECT bi.*, s.student_code, s.name AS student_name, "
        "b.title AS book_title, b.total_quantity, b.available_quantity "
        "FROM book_issues bi "
        "JOIN books b ON bi.book_id = b.id "
        "JOIN students s ON bi.student_id = s.id WHERE bi.id = ?"
    )
    try:
        row = database.fetch_one(query, (issue_id,))
    except database.DatabaseError:
        raise ServiceError("Could not load issue details.")
    return dict(row) if row is not None else None


def _friendly_issue_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "unique" in text:
        return "This student already has this book issued."
    if "check" in text:
        return "Quantity limits prevent this action."
    return "Something went wrong while saving. Please try again."
