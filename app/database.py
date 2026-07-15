"""SQLite database access layer.

This module owns everything about the raw database: creating required
folders, initializing the schema on first run, handing out connections with
foreign keys enabled, and providing small query helpers plus a transaction
context manager. Services build on top of this; UI never touches it directly.
"""

import os
import shutil
import sqlite3
import sys
from contextlib import contextmanager

from app import config


class DatabaseError(Exception):
    """Raised for database problems that services can surface to the UI."""


def ensure_directories() -> None:
    """Create all required application folders if they are missing."""
    for path in config.REQUIRED_DIRS:
        os.makedirs(path, exist_ok=True)


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
    """
    ensure_directories()
    _maybe_copy_bundled_db()
    schema_sql = _load_schema_sql()
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
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
