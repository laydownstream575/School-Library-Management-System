"""Student business logic: add, edit, deactivate, search, issue history."""

import logging
import time

from app import config, database, utils, validators
from services import ServiceError

logger = logging.getLogger(__name__)


def get_students(search: str = "", status: str = None, class_name: str = None,
                 division: str = None):
    """Return students matching the search text and filters."""
    clauses = []
    params = []

    if search and search.strip():
        like = f"%{search.strip()}%"
        clauses.append(
            "(student_code LIKE ? OR name LIKE ? OR class_name LIKE ? "
            "OR division LIKE ?)"
        )
        params.extend([like, like, like, like])

    if status in (config.STATUS_ACTIVE, config.STATUS_INACTIVE):
        clauses.append("status = ?")
        params.append(status)

    if class_name:
        clauses.append("class_name = ?")
        params.append(class_name)

    if division:
        clauses.append("division = ?")
        params.append(division)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"SELECT * FROM students {where} ORDER BY name ASC"
    try:
        rows = database.fetch_all(query, tuple(params))
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load student records.") from exc
    return [_upper_division(dict(r)) for r in rows]


def get_student(student_id: int):
    try:
        row = database.fetch_one("SELECT * FROM students WHERE id = ?", (student_id,))
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load student record.") from exc
    return _upper_division(utils.row_to_dict(row))


def get_active_students(search: str = ""):
    """Active students matching the search text (for the Issue screen)."""
    like = f"%{search.strip()}%" if search else "%"
    query = (
        "SELECT * FROM students WHERE status = 'ACTIVE' AND "
        "(student_code LIKE ? OR name LIKE ? OR class_name LIKE ? "
        "OR division LIKE ?) ORDER BY name ASC"
    )
    try:
        rows = database.fetch_all(query, (like, like, like, like))
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load active students.") from exc
    return [_upper_division(dict(r)) for r in rows]


def add_student(data: dict) -> int:
    """Validate and insert a new student. Returns new student id."""
    code = (data.get("student_code") or "").strip()
    name = (data.get("name") or "").strip()

    result = validators.validate_student_form(code, name)
    if not result:
        raise ServiceError(result.message)

    if _code_exists(code):
        raise ServiceError("A student with this Student ID already exists.")

    division = (data.get("division") or "").strip().upper() or None

    now = utils.now_timestamp()
    try:
        student_id = database.execute(
            "INSERT INTO students (student_code, name, class_name, division, "
            "status, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                code,
                name,
                (data.get("class_name") or "").strip() or None,
                division,
                data.get("status") or config.STATUS_ACTIVE,
                now,
                now,
            ),
        )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity("STUDENT_ADDED", f"Student added: {name} ({code})")
    return student_id


def update_student(student_id: int, data: dict) -> None:
    """Validate and update an existing student."""
    student = get_student(student_id)
    if student is None:
        raise ServiceError("Student not found.")

    code = (data.get("student_code") or "").strip()
    name = (data.get("name") or "").strip()
    result = validators.validate_student_form(code, name)
    if not result:
        raise ServiceError(result.message)

    if _code_exists(code, exclude_id=student_id):
        raise ServiceError("Another student with this Student ID already exists.")

    division = (data.get("division") or "").strip().upper() or None

    try:
        database.execute(
            "UPDATE students SET student_code = ?, name = ?, class_name = ?, "
            "division = ?, status = ?, "
            "updated_at = ? WHERE id = ?",
            (
                code,
                name,
                (data.get("class_name") or "").strip() or None,
                division,
                data.get("status") or student["status"],
                utils.now_timestamp(),
                student_id,
            ),
        )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity("STUDENT_UPDATED", f"Student updated: {name} ({code})")


def delete_student(student_id: int) -> None:
    """Permanently delete a student and all their history.

    Refused if the student has any currently ISSUED books.
    All operations run inside a single transaction.
    """
    student = get_student(student_id)
    if student is None:
        raise ServiceError("Student not found.")
    if get_pending_count(student_id) > 0:
        raise ServiceError(
            "This student cannot be deleted because they still have one or "
            "more books issued. Return all books before deleting the student."
        )
    try:
        with database.transaction() as conn:
            conn.execute(
                "DELETE FROM book_issues WHERE student_id = ?", (student_id,)
            )
            conn.execute(
                "DELETE FROM students WHERE id = ?", (student_id,)
            )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity(
        "STUDENT_DELETED",
        f"Student deleted: {student['name']} ({student['student_code']})",
    )


def get_pending_count(student_id: int) -> int:
    """Number of books this student currently has out."""
    try:
        val = database.fetch_value(
            "SELECT COUNT(*) FROM book_issues WHERE student_id = ? AND status = 'ISSUED'",
            (student_id,),
            default=0,
        )
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load pending count.") from exc
    return int(val)


def get_student_history(student_id: int):
    """Full issue/return history for one student, newest first."""
    query = (
        "SELECT bi.id AS issue_id, b.title AS book_title, bi.issue_date, "
        "bi.due_date, bi.return_date, bi.status "
        "FROM book_issues bi JOIN books b ON bi.book_id = b.id "
        "WHERE bi.student_id = ? ORDER BY bi.issue_date DESC, bi.id DESC"
    )
    try:
        rows = database.fetch_all(query, (student_id,))
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load student history.") from exc
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Duplicate-aware import (used by Excel import)
# ---------------------------------------------------------------------------

def import_student(data: dict) -> str:
    """Import a single student from Excel (idempotent upsert).

    Returns ``"imported"``, ``"updated"``, or ``"skipped"``.
    Uses student_code as the unique key. Division is uppercased.
    Does not overwrite status (keeps existing status).
    """
    code = (data.get("student_code") or "").strip()
    name = (data.get("name") or "").strip()

    result = validators.validate_student_form(code, name)
    if not result:
        raise ServiceError(result.message)

    existing = _find_student_by_code(code)
    division = (data.get("division") or "").strip().upper() or None

    if existing:
        existing_name = (existing.get("name") or "").strip()
        existing_class = (existing.get("class_name") or "").strip() or None
        existing_div = (existing.get("division") or "").strip().upper() or None
        new_class = (data.get("class_name") or "").strip() or None

        if (existing_name == name
                and existing_class == new_class
                and existing_div == division):
            return "skipped"

        now = utils.now_timestamp()
        try:
            database.execute(
                "UPDATE students SET name=?, class_name=?, division=?, "
                "updated_at=? WHERE id=?",
                (name, new_class, division, now, existing["id"]),
            )
        except database.DatabaseError as exc:
            raise ServiceError(_friendly_db_error(exc)) from exc

        utils.log_activity("STUDENT_UPDATED",
                           f"Student updated via import: {name} ({code})")
        return "updated"

    add_student(data)
    return "imported"


def import_students_batch(students: list[dict]) -> dict:
    """Import many students in a single transaction.

    Each student dict must have: student_code, name, class_name, division.
    Uses student_code as the unique key. Division is uppercased.

    Returns dict with keys: imported, updated, skipped, errors, error_details
    (list of (student_code, reason) tuples).
    """
    imported = 0
    updated = 0
    skipped = 0
    errors = 0
    error_details = []

    existing = {}
    try:
        for r in database.fetch_all("SELECT * FROM students"):
            d = dict(r)
            existing[d["student_code"]] = d
    except database.DatabaseError as exc:
        raise ServiceError("Unable to load existing students.") from exc

    now = utils.now_timestamp()
    t0 = time.perf_counter()
    try:
        with database.transaction() as conn:
            for data in students:
                code = (data.get("student_code") or "").strip()
                name = (data.get("name") or "").strip()
                result = validators.validate_student_form(code, name)
                if not result:
                    errors += 1
                    error_details.append((code, result.message))
                    continue

                division = (data.get("division") or "").strip().upper() or None
                class_name = (data.get("class_name") or "").strip() or None

                if code in existing:
                    ex = existing[code]
                    ex_name = (ex.get("name") or "").strip()
                    ex_class = (ex.get("class_name") or "").strip() or None
                    ex_div = (ex.get("division") or "").strip().upper() or None

                    if ex_name == name and ex_class == class_name and ex_div == division:
                        skipped += 1
                        continue

                    conn.execute(
                        "UPDATE students SET name=?, class_name=?, division=?, "
                        "updated_at=? WHERE id=?",
                        (name, class_name, division, now, ex["id"]),
                    )
                    updated += 1
                else:
                    conn.execute(
                        "INSERT INTO students (student_code, name, class_name, "
                        "division, status, created_at, updated_at) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (code, name, class_name, division,
                         config.STATUS_ACTIVE, now, now),
                    )
                    imported += 1
    except database.DatabaseError as exc:
        raise ServiceError("Error during batch import.") from exc

    db_elapsed = time.perf_counter() - t0
    logger.debug(
        "import_students_batch: %d rows, %d ins, %d upd, %d skip in %.4fs",
        len(students), imported, updated, skipped, db_elapsed,
    )

    if imported or updated:
        utils.log_activity(
            "STUDENTS_IMPORTED",
            f"Imported {imported}, updated {updated}, "
            f"skipped {skipped} students from Excel",
        )
    return {
        "imported": imported,
        "updated": updated,
        "skipped": skipped,
        "errors": errors,
        "error_details": error_details,
    }


def _find_student_by_code(code: str) -> dict | None:
    """Return a student dict by normalized student_code, or None."""
    try:
        row = database.fetch_one(
            "SELECT * FROM students WHERE student_code = ?", (code.strip(),)
        )
    except database.DatabaseError as exc:
        raise ServiceError("Unable to look up existing student.") from exc
    return _upper_division(dict(row)) if row else None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _code_exists(code: str, exclude_id: int = None) -> bool:
    if exclude_id:
        row = database.fetch_one(
            "SELECT id FROM students WHERE student_code = ? AND id != ?",
            (code, exclude_id),
        )
    else:
        row = database.fetch_one(
            "SELECT id FROM students WHERE student_code = ?", (code,)
        )
    return row is not None


def _friendly_db_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "unique" in text and "student_code" in text:
        return "A student with this Student ID already exists."
    return "Unable to save the student. Please try again."


def _upper_division(student):
    """Uppercase division in a student dict (or None)."""
    if student is not None and student.get("division"):
        student["division"] = student["division"].strip().upper()
    return student
