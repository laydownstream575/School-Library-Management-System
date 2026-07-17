"""SQLite database access layer.

This module owns everything about the raw database: creating required
folders, initializing the schema on first run, handing out connections with
foreign keys enabled, and providing small query helpers plus a transaction
context manager. Services build on top of this; UI never touches it directly.
"""

import logging
import os
import shutil
import sqlite3
import sys
from contextlib import contextmanager

from app import config, utils

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 3


class DatabaseError(Exception):
    """Raised for database problems that services can surface to the UI."""


def ensure_directories() -> None:
    """Create all required application folders if they are missing."""
    for path in config.REQUIRED_DIRS:
        os.makedirs(path, exist_ok=True)


def check_integrity() -> None:
    """Run PRAGMA integrity_check on startup. Raises DatabaseError on failure."""
    if not os.path.exists(config.DATABASE_PATH):
        return
    conn = get_connection()
    try:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        if not row or row[0] != "ok":
            raise DatabaseError("Database integrity check failed. The database may be corrupted.")
    except sqlite3.Error as exc:
        raise DatabaseError(f"Could not verify database integrity: {exc}") from exc
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection with sensible defaults.

    - ``row_factory`` returns dict-like rows (access columns by name).
    - Foreign keys are enforced (must be enabled per-connection in SQLite).
    """
    try:
        conn = sqlite3.connect(config.DATABASE_PATH)
    except sqlite3.Error as exc:  # pragma: no cover - defensive
        raise DatabaseError(f"Could not open database: {exc}") from exc
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database() -> None:
    """Create folders, copy bundled DB on first frozen launch, and run the
    schema so the app is ready to use.

    Safe to call on every startup: the schema uses ``CREATE TABLE IF NOT
    EXISTS`` and ``INSERT OR IGNORE`` so existing data is never overwritten.
    Also records/checks a schema version via PRAGMA user_version, and runs
    any pending schema migrations.
    """
    ensure_directories()
    _maybe_copy_bundled_db()
    schema_sql = _load_schema_sql()
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        is_fresh = not conn.execute("PRAGMA user_version").fetchone()[0]
        if is_fresh:
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
        _run_migrations(conn)
        # Fresh databases also need the book_key index.
        if is_fresh:
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key "
                "ON books(book_key) WHERE book_key IS NOT NULL"
            )
            conn.commit()
    except sqlite3.Error as exc:
        conn.rollback()
        raise DatabaseError(f"Could not initialize database: {exc}") from exc
    finally:
        conn.close()


def _maybe_copy_bundled_db() -> None:
    """On the first launch of a packaged (.exe) build, copy the bundled
    database from the PyInstaller temp folder to the writable app-data
    directory so the user starts with any seed data we shipped."""
    if not getattr(sys, "frozen", False):
        return
    if os.path.exists(config.DATABASE_PATH):
        return
    bundled = config.resource_path(os.path.join("database", "library.db"))
    if os.path.exists(bundled):
        shutil.copy2(bundled, config.DATABASE_PATH)


# ---------------------------------------------------------------------------
# Schema migrations
# ---------------------------------------------------------------------------


def _compute_book_key(title, author, category):
    parts = [
        utils.normalize_key(title or ""),
        utils.normalize_key(author or ""),
        utils.normalize_key(category or ""),
    ]
    return "|".join(parts)


def _ensure_migration_audit(conn):
    """Create migration_audit if missing, adding status column for existing."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS migration_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_from INTEGER NOT NULL,
            migration_to INTEGER NOT NULL,
            table_name TEXT NOT NULL,
            row_id INTEGER,
            column_name TEXT NOT NULL DEFAULT '',
            old_value TEXT,
            new_value TEXT,
            status TEXT NOT NULL DEFAULT 'corrected'
                CHECK (status IN ('corrected', 'manual_review_required')),
            reason TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    """)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(migration_audit)").fetchall()}
    if "status" not in cols:
        conn.execute(
            "ALTER TABLE migration_audit ADD COLUMN "
            "status TEXT NOT NULL DEFAULT 'corrected'"
        )


def _migrate_v1_to_v2(conn):
    """Add book_key column and unique partial index for duplicate detection.

    Handles existing duplicate books by merging issue records into a canonical
    book and deleting the duplicate rows. Duplicate detection is based on
    normalized title|author|category only — the schema has no ISBN, accession,
    publisher, edition, or publication-year columns, so those cannot be checked.
    Future schema versions should add those columns and update this logic.
    """
    columns = {r[1] for r in conn.execute("PRAGMA table_info(books)").fetchall()}
    if "book_key" not in columns:
        conn.execute("ALTER TABLE books ADD COLUMN book_key TEXT")

    _ensure_migration_audit(conn)

    rows = conn.execute(
        "SELECT id, title, author, category FROM books WHERE book_key IS NULL"
    ).fetchall()
    groups = {}
    for row in rows:
        key = _compute_book_key(row["title"], row["author"], row["category"])
        groups.setdefault(key, []).append(dict(row))

    merged_ok = 0
    merged_review = 0

    for key, group in groups.items():
        if len(group) == 1:
            conn.execute("UPDATE books SET book_key = ? WHERE id = ?",
                         (key, group[0]["id"]))
        else:
            canonical = min(group, key=lambda r: r["id"])
            conn.execute("UPDATE books SET book_key = ? WHERE id = ?",
                         (key, canonical["id"]))
            duplicates = [r for r in group if r["id"] != canonical["id"]]
            dup_ids = tuple(r["id"] for r in duplicates)
            conn.execute(
                "UPDATE book_issues SET book_id = ? WHERE book_id IN ({})".format(
                    ",".join("?" * len(dup_ids))
                ),
                (canonical["id"], *dup_ids),
            )

            all_ids = tuple(r["id"] for r in group)
            total = conn.execute(
                "SELECT COALESCE(MAX(total_quantity), 0) FROM books "
                "WHERE id IN ({})".format(",".join("?" * len(all_ids))),
                all_ids,
            ).fetchone()[0]
            active = conn.execute(
                "SELECT COUNT(*) FROM book_issues "
                "WHERE book_id = ? AND status = 'ISSUED'",
                (canonical["id"],),
            ).fetchone()[0]
            avail = total - active
            if avail < 0:
                avail = 0

            conn.execute(
                "UPDATE books SET total_quantity = ?, available_quantity = ? "
                "WHERE id = ?",
                (total, avail, canonical["id"]),
            )
            conn.execute(
                "DELETE FROM books WHERE id IN ({})".format(
                    ",".join("?" * len(dup_ids))
                ),
                dup_ids,
            )

            if active > total:
                conn.execute(
                    "INSERT INTO migration_audit "
                    "(migration_from, migration_to, table_name, row_id, "
                    "column_name, old_value, new_value, status, reason) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (1, 2, "books", canonical["id"],
                     "total_quantity", str(total), str(avail),
                     "manual_review_required",
                     f"Active issues ({active}) exceed max quantity ({total}) "
                     f"after merging {len(dup_ids)} duplicate(s). "
                     "Manual inventory review required."),
                )
                logger.warning(
                    "v1→v2: merged %d duplicate(s) into book %s "
                    "(active=%d, total=%d) — requires manual review",
                    len(dup_ids), canonical["id"], active, total,
                )
                merged_review += 1
            else:
                merged_ok += 1
                logger.warning(
                    "Merged %d duplicate book(s) into canonical id=%s (key=%s)",
                    len(dup_ids), canonical["id"], key,
                )

    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key "
        "ON books(book_key) WHERE book_key IS NOT NULL"
    )

    parts = []
    if merged_ok:
        parts.append(f"{merged_ok} group(s) merged")
    if merged_review:
        parts.append(f"{merged_review} group(s) flagged for manual review")
    if not merged_ok and not merged_review:
        parts.append("no duplicates found")
    logger.info("Migration v1→v2 complete (%s)", ", ".join(parts))


def _migrate_v2_to_v3(conn):
    """Correct available_quantity for books affected by the v1→v2 sum bug.

    v1→v2 originally used SUM(total_quantity) when merging duplicates, inflating
    quantities. This migration recalculates available_quantity = total - active
    issues for every book and logs corrections in a migration_audit table.

    Books where active_issues > total_quantity are flagged for manual review
    (available set to 0 defensively). No quantities are automatically inflated.
    """
    _ensure_migration_audit(conn)

    rows = conn.execute("""
        SELECT b.id, b.title, b.total_quantity, b.available_quantity,
               COALESCE((SELECT COUNT(*) FROM book_issues bi
                WHERE bi.book_id = b.id AND bi.status = 'ISSUED'), 0) AS active_issues
        FROM books b
    """).fetchall()

    corrections = 0
    reviews = 0
    for row in rows:
        row_id = row["id"]
        total_qty = row["total_quantity"]
        avail_qty = row["available_quantity"]
        active = row["active_issues"]
        correct = total_qty - active
        if correct < 0:
            correct = 0
        needs_review = active > total_qty
        eq_needs_update = avail_qty != correct

        if eq_needs_update or needs_review:
            if eq_needs_update:
                conn.execute(
                    "UPDATE books SET available_quantity = ? WHERE id = ?",
                    (correct, row_id),
                )

            if needs_review:
                status = "manual_review_required"
                reason = (
                    f"Active issue count ({active}) exceeds total quantity "
                    f"({total_qty}). Manual inventory review is required."
                )
                reviews += 1
            else:
                status = "corrected"
                reason = (
                    f"Corrected available_quantity from {avail_qty} to {correct} "
                    f"(total={total_qty}, active_issues={active})"
                )
                corrections += 1

            conn.execute(
                "INSERT INTO migration_audit "
                "(migration_from, migration_to, table_name, row_id, "
                "column_name, old_value, new_value, status, reason) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (2, 3, "books", row_id,
                 "available_quantity", str(avail_qty), str(correct),
                 status, reason),
            )

    parts = []
    if corrections:
        parts.append(f"{corrections} corrected")
    if reviews:
        parts.append(f"{reviews} flagged for manual review")
    if not corrections and not reviews:
        parts.append("no changes needed")

    if corrections or reviews:
        logger.warning(
            "v2→v3: %s", ", ".join(parts),
        )
    logger.info("Migration v2→v3 complete (%s)", ", ".join(parts))


_MIGRATIONS: dict = {
    2: _migrate_v1_to_v2,
    3: _migrate_v2_to_v3,
}


def _run_migrations(conn):
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    while current < SCHEMA_VERSION:
        next_ver = current + 1
        migrator = _MIGRATIONS.get(next_ver)
        if migrator is None:
            break
        logger.info("Schema migration v%s → v%s", current, next_ver)
        migrator(conn)
        conn.execute(f"PRAGMA user_version = {next_ver}")
        conn.commit()
        current = next_ver


def _load_schema_sql() -> str:
    """Load schema.sql from disk, falling back to an embedded copy.

    The embedded fallback means a packaged .exe still works even if the
    external schema file is missing.
    """
    if os.path.exists(config.SCHEMA_PATH):
        with open(config.SCHEMA_PATH, "r", encoding="utf-8") as handle:
            return handle.read()
    return _EMBEDDED_SCHEMA


# ---------------------------------------------------------------------------
# Query helpers
# ---------------------------------------------------------------------------
def fetch_all(query: str, params: tuple = ()) -> list:
    """Run a SELECT and return all rows as a list of sqlite3.Row."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        return cursor.fetchall()
    except sqlite3.Error as exc:
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()


def fetch_one(query: str, params: tuple = ()):
    """Run a SELECT and return the first row (or None)."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        return cursor.fetchone()
    except sqlite3.Error as exc:
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()


def fetch_value(query: str, params: tuple = (), default=None):
    """Run a SELECT that returns a single scalar value."""
    row = fetch_one(query, params)
    if row is None:
        return default
    value = row[0]
    return default if value is None else value


def execute(query: str, params: tuple = ()) -> int:
    """Run a single INSERT/UPDATE/DELETE, commit, and return lastrowid."""
    conn = get_connection()
    try:
        cursor = conn.execute(query, params)
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as exc:
        conn.rollback()
        raise DatabaseError(str(exc)) from exc
    finally:
        conn.close()


@contextmanager
def transaction():
    """Context manager for multi-step transactions (issue/return).

    Yields a connection. Commits on success, rolls back on any exception, and
    always closes the connection. Use for operations that must be atomic.
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Minimal embedded schema fallback (kept in sync with database/schema.sql).
_EMBEDDED_SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT,
    book_key TEXT,
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
    CHECK (return_date IS NULL OR return_date >= issue_date)
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
CREATE TABLE IF NOT EXISTS migration_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_from INTEGER NOT NULL,
    migration_to INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    row_id INTEGER,
    column_name TEXT NOT NULL DEFAULT '',
    old_value TEXT,
    new_value TEXT,
    status TEXT NOT NULL DEFAULT 'corrected'
        CHECK (status IN ('corrected', 'manual_review_required')),
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_issue
ON book_issues(student_id, book_id) WHERE status = 'ISSUED';
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);

CREATE INDEX IF NOT EXISTS idx_books_status ON books(status);
CREATE INDEX IF NOT EXISTS idx_students_code ON students(student_code);
CREATE INDEX IF NOT EXISTS idx_students_name ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_class ON students(class_name);
CREATE INDEX IF NOT EXISTS idx_students_status ON students(status);
CREATE INDEX IF NOT EXISTS idx_issues_book_id ON book_issues(book_id);
CREATE INDEX IF NOT EXISTS idx_issues_student_id ON book_issues(student_id);
CREATE INDEX IF NOT EXISTS idx_issues_status ON book_issues(status);
CREATE INDEX IF NOT EXISTS idx_issues_issue_date ON book_issues(issue_date);
CREATE INDEX IF NOT EXISTS idx_issues_due_date ON book_issues(due_date);
CREATE INDEX IF NOT EXISTS idx_issues_return_date ON book_issues(return_date);
INSERT OR IGNORE INTO settings (setting_key, setting_value) VALUES
('school_name', 'ABC Public School'),
('library_name', 'School Library'),
('default_due_days', '7'),
('low_stock_limit', '2'),
('backup_path', 'backups'),
('export_path', 'exports');
"""
