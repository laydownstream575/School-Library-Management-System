"""Book business logic: add, edit, delete, search, quantity helpers."""

from app import config, database, utils, validators
from services import ServiceError


def get_books(search: str = "", status: str = None, availability: str = None,
              low_stock_only: bool = False):
    """Return books matching the given search text and filters.

    - ``search`` matches title/author/category (case-insensitive).
    - ``status`` filters ACTIVE/INACTIVE (None = all).
    - ``availability`` may be 'available' or 'issued' (issued = some copies out).
    - ``low_stock_only`` limits to books at/under the low-stock limit.
    """
    clauses = []
    params = []

    if search and search.strip():
        like = f"%{search.strip()}%"
        clauses.append(
            "(title LIKE ? OR author LIKE ? OR category LIKE ?)"
        )
        params.extend([like, like, like])

    if status in (config.STATUS_ACTIVE, config.STATUS_INACTIVE):
        clauses.append("status = ?")
        params.append(status)

    if availability == "available":
        clauses.append("available_quantity > 0")
    elif availability == "issued":
        clauses.append("available_quantity < total_quantity")

    if low_stock_only:
        limit = utils.get_setting_int("low_stock_limit", 2)
        clauses.append("available_quantity <= ?")
        params.append(limit)

    where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
    query = f"SELECT * FROM books {where} ORDER BY title ASC"
    return [dict(r) for r in database.fetch_all(query, tuple(params))]


def get_book(book_id: int):
    """Return a single book as a dict, or None."""
    return utils.row_to_dict(
        database.fetch_one("SELECT * FROM books WHERE id = ?", (book_id,))
    )


def get_active_available_books(search: str = ""):
    """Active books that currently have at least one available copy."""
    like = f"%{search.strip()}%" if search else "%"
    query = (
        "SELECT * FROM books WHERE status = 'ACTIVE' AND available_quantity > 0 "
        "AND (title LIKE ? OR author LIKE ? OR category LIKE ?) ORDER BY title ASC"
    )
    return [dict(r) for r in database.fetch_all(query, (like, like, like))]


def add_book(data: dict) -> int:
    """Validate and insert a new book. Returns the new book id.

    ``available_quantity`` defaults to ``total_quantity`` when not supplied.
    """
    title = (data.get("title") or "").strip()
    total_raw = data.get("total_quantity")
    available_raw = data.get("available_quantity")

    result = validators.validate_book_form(title, total_raw, available_raw)
    if not result:
        raise ServiceError(result.message)

    total = int(str(total_raw).strip())
    if available_raw is None or str(available_raw).strip() == "":
        available = total
    else:
        available = int(str(available_raw).strip())

    now = utils.now_timestamp()
    try:
        book_id = database.execute(
            "INSERT INTO books (title, author, category, "
            "total_quantity, available_quantity, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                title,
                (data.get("author") or "").strip() or None,
                (data.get("category") or "").strip() or None,
                total,
                available,
                data.get("status") or config.STATUS_ACTIVE,
                now,
                now,
            ),
        )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity("BOOK_ADDED", f"Book added: {title}")
    return book_id


def update_book(book_id: int, data: dict) -> None:
    """Validate and update an existing book.

    Total quantity cannot drop below the number of copies currently issued.
    Available quantity is adjusted so ``total - available == issued`` stays true.
    """
    book = get_book(book_id)
    if book is None:
        raise ServiceError("Book not found.")

    title = (data.get("title") or "").strip()
    total_raw = data.get("total_quantity")
    result = validators.validate_book_form(title, total_raw)
    if not result:
        raise ServiceError(result.message)
    new_total = int(str(total_raw).strip())

    issued = get_issued_count(book_id)
    if new_total < issued:
        raise ServiceError(
            f"Total quantity cannot be less than currently issued copies ({issued})."
        )

    # Keep issued count constant: available = total - issued.
    new_available = new_total - issued

    try:
        database.execute(
            "UPDATE books SET title = ?, author = ?, category = ?, "
            "total_quantity = ?, "
            "available_quantity = ?, status = ?, updated_at = ? WHERE id = ?",
            (
                title,
                (data.get("author") or "").strip() or None,
                (data.get("category") or "").strip() or None,
                new_total,
                new_available,
                data.get("status") or book["status"],
                utils.now_timestamp(),
                book_id,
            ),
        )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity("BOOK_UPDATED", f"Book updated: {title}")


def delete_book(book_id: int) -> None:
    """Permanently delete a book and all its issue/return history.

    Refused if any copies of the book are currently issued.
    All operations run inside a single transaction.
    """
    book = get_book(book_id)
    if book is None:
        raise ServiceError("Book not found.")
    if get_issued_count(book_id) > 0:
        raise ServiceError(
            "This book cannot be deleted because one or more copies are "
            "currently issued. Return all copies before deleting the book."
        )
    try:
        with database.transaction() as conn:
            conn.execute(
                "DELETE FROM book_issues WHERE book_id = ?", (book_id,)
            )
            conn.execute(
                "DELETE FROM books WHERE id = ?", (book_id,)
            )
    except database.DatabaseError as exc:
        raise ServiceError(_friendly_db_error(exc)) from exc

    utils.log_activity(
        "BOOK_DELETED",
        f"Book deleted: {book['title']} (id={book_id})",
    )


def get_issued_count(book_id: int) -> int:
    """How many copies of this book are currently issued out."""
    return int(
        database.fetch_value(
            "SELECT COUNT(*) FROM book_issues WHERE book_id = ? AND status = 'ISSUED'",
            (book_id,),
            default=0,
        )
    )


def availability_label(book: dict) -> str:
    """Human badge text for a book's availability."""
    if book.get("status") == config.STATUS_INACTIVE:
        return "Inactive"
    available = book.get("available_quantity", 0)
    if available <= 0:
        return "Not Available"
    low_limit = utils.get_setting_int("low_stock_limit", 2)
    if available <= low_limit:
        return "Low Stock"
    return "Available"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _friendly_db_error(exc: Exception) -> str:
    text = str(exc).lower()
    if "check" in text:
        return "Invalid quantity values. Please check the numbers entered."
    return "Unable to save the book. Please try again."
