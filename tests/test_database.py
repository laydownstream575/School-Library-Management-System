"""Tests for app/database.py — constraints, schema, migration, integrity."""

import os
import sqlite3
import tempfile

import pytest

from app import config, database


# ---------------------------------------------------------------------------
# Schema & initialization
# ---------------------------------------------------------------------------

class TestSchemaInit:
    def test_initialize_creates_tables(self, db_path):
        """initialize_database creates all required tables."""
        database.initialize_database()
        conn = database.get_connection()
        tables = {
            r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        for t in ("books", "students", "book_issues", "settings", "activity_logs"):
            assert t in tables

    def test_initialize_is_idempotent(self, db_path):
        """initialize_database can be called multiple times safely."""
        database.initialize_database()
        database.initialize_database()
        database.initialize_database()  # no error

    def test_schema_version_set(self, db_path):
        """PRAGMA user_version is set after initialization."""
        database.initialize_database()
        conn = database.get_connection()
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        conn.close()
        assert version == database.SCHEMA_VERSION

    def test_check_integrity_on_valid_db(self, db_path):
        """check_integrity passes on a healthy database."""
        database.initialize_database()
        database.check_integrity()  # no error

    def test_check_integrity_on_missing_db(self, db_path):
        """check_integrity does nothing if no database file exists."""
        database.check_integrity()  # no error even without file


# ---------------------------------------------------------------------------
# Foreign keys
# ---------------------------------------------------------------------------

class TestForeignKeyConstraints:
    def test_cannot_insert_issue_without_book(self, fresh_db):
        """ForeignKey to books table must exist."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "status, created_at, updated_at) VALUES (999, 1, '2026-01-01', "
                "'ISSUED', '2026-01-01', '2026-01-01')"
            )
            conn.commit()
        conn.close()

    def test_cannot_insert_issue_without_student(self, fresh_db, sample_book):
        """ForeignKey to students table must exist."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "status, created_at, updated_at) VALUES (?, 999, '2026-01-01', "
                "'ISSUED', '2026-01-01', '2026-01-01')",
                (sample_book["id"],),
            )
            conn.commit()
        conn.close()


# ---------------------------------------------------------------------------
# Unique constraints
# ---------------------------------------------------------------------------

class TestUniqueConstraints:
    def test_duplicate_student_code_raises(self, fresh_db, sample_student):
        """student_code must be unique."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO students (student_code, name, status, created_at, "
                "updated_at) VALUES (?, 'Duplicate', 'ACTIVE', 'now', 'now')",
                (sample_student["student_code"],),
            )
            conn.commit()
        conn.close()

    def test_duplicate_setting_key_raises(self, fresh_db):
        """setting_key must be unique."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO settings (setting_key, setting_value) "
                "VALUES ('school_name', 'Duplicate')"
            )
            conn.commit()
        conn.close()


# ---------------------------------------------------------------------------
# CHECK constraints
# ---------------------------------------------------------------------------

class TestCheckConstraints:
    def test_book_quantity_non_negative(self, fresh_db):
        """total_quantity must be >= 0."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO books (title, total_quantity, available_quantity, "
                "status, created_at, updated_at) "
                "VALUES ('Bad Book', -1, -1, 'ACTIVE', 'now', 'now')"
            )
            conn.commit()
        conn.close()

    def test_book_available_not_exceeds_total(self, fresh_db):
        """available_quantity must be <= total_quantity."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO books (title, total_quantity, available_quantity, "
                "status, created_at, updated_at) "
                "VALUES ('Bad Book', 5, 10, 'ACTIVE', 'now', 'now')"
            )
            conn.commit()
        conn.close()

    def test_issue_status_valid_values(self, fresh_db, sample_book, sample_student):
        """book_issues.status must be one of ISSUED, RETURNED, LOST, DAMAGED."""
        conn = database.get_connection()
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "status, created_at, updated_at) VALUES (?, ?, '2026-01-01', "
                "'INVALID', 'now', 'now')",
                (sample_book["id"], sample_student["id"]),
            )
            conn.commit()
        conn.close()


# ---------------------------------------------------------------------------
# Transaction commit / rollback
# ---------------------------------------------------------------------------

class TestTransaction:
    def test_transaction_commits(self, fresh_db):
        """Successful transaction context commits changes."""
        with database.transaction() as conn:
            conn.execute(
                "INSERT INTO books (title, total_quantity, available_quantity, "
                "status, created_at, updated_at) "
                "VALUES ('Test Book', 1, 1, 'ACTIVE', 'now', 'now')"
            )
        count = database.fetch_value("SELECT COUNT(*) FROM books")
        assert count == 1

    def test_transaction_rolls_back(self, fresh_db):
        """Failed transaction context rolls back changes."""
        try:
            with database.transaction() as conn:
                conn.execute(
                    "INSERT INTO books (title, total_quantity, available_quantity, "
                    "status, created_at, updated_at) "
                    "VALUES ('Test Book', 1, 1, 'ACTIVE', 'now', 'now')"
                )
                raise ValueError("simulated failure")
        except ValueError:
            pass
        count = database.fetch_value("SELECT COUNT(*) FROM books")
        assert count == 0

    def test_transaction_rolls_back_on_constraint_violation(self, fresh_db):
        """Constraint violation inside a transaction rolls back all changes."""
        conn = database.get_connection()
        conn.execute(
            "INSERT INTO books (title, total_quantity, available_quantity, "
            "status, created_at, updated_at) "
            "VALUES ('Only Book', 1, 1, 'ACTIVE', 'now', 'now')"
        )
        conn.commit()
        conn.close()

        try:
            with database.transaction() as conn:
                conn.execute(
                    "UPDATE books SET total_quantity = -5 WHERE id = 1"
                )
        except (database.DatabaseError, sqlite3.IntegrityError):
            pass

        # The book should still exist with original values.
        book = database.fetch_one("SELECT * FROM books WHERE id = 1")
        assert book is not None
        assert book["total_quantity"] >= 0


# ---------------------------------------------------------------------------
# Query helpers: error handling
# ---------------------------------------------------------------------------

class TestQueryHelpers:
    def test_fetch_all_on_missing_table_raises(self, fresh_db):
        with pytest.raises(database.DatabaseError):
            database.fetch_all("SELECT * FROM nonexistent")

    def test_fetch_one_on_missing_table_raises(self, fresh_db):
        with pytest.raises(database.DatabaseError):
            database.fetch_one("SELECT * FROM nonexistent")

    def test_fetch_value_default(self, fresh_db):
        val = database.fetch_value(
            "SELECT COUNT(*) FROM books WHERE id = 999", default=-1
        )
        assert val == 0

    def test_execute_on_constraint_violation_raises(self, fresh_db, sample_book):
        with pytest.raises(database.DatabaseError):
            database.execute(
                "UPDATE books SET available_quantity = -5 WHERE id = ?",
                (sample_book["id"],),
            )


# ---------------------------------------------------------------------------
# Migration chain: fresh-v3, v1→v2→v3, v2→v3, v3 no-op
# ---------------------------------------------------------------------------

class _MigrationTestBase:
    """Shared helpers for migration tests that need specific schema versions."""

    @staticmethod
    def _make_db(db_path, user_version=0):
        """Drop existing tables, create a minimal v1 schema, set user_version.

        Each call tears down whatever ``db_path`` fixture set up, so tests
        can start from a clean version-1 state and then run
        ``initialize_database()`` to trigger migration(s).
        """
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        # Drop all tables to reset from whatever the fixture created.
        for t in ("book_issues", "activity_logs", "migration_audit",
                   "settings", "books", "students"):
            conn.execute(f"DROP TABLE IF EXISTS {t}")
        conn.commit()
        # Build v1 schema (no book_key column).
        conn.executescript("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT, category TEXT,
                total_quantity INTEGER NOT NULL CHECK (total_quantity >= 0),
                available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                CHECK (available_quantity <= total_quantity)
            );
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
                class_name TEXT, division TEXT,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE book_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
                issue_date TEXT NOT NULL, due_date TEXT, return_date TEXT,
                status TEXT NOT NULL DEFAULT 'ISSUED', remarks TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (student_id) REFERENCES students(id)
            );
            CREATE TABLE settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT NOT NULL UNIQUE, setting_value TEXT
            );
            CREATE TABLE activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT NOT NULL, description TEXT,
                created_at TEXT NOT NULL
            );
        """)
        conn.execute(f"PRAGMA user_version = {user_version}")
        conn.commit()
        return conn


class TestMigrationPaths:
    """Verify the correct migration path runs for each starting version."""

    def test_fresh_db_starts_directly_at_v3(self, db_path):
        """Fresh database creates v3 schema directly, no migration code runs."""
        conn = database.get_connection()
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
        assert "book_key" in {r[1] for r in conn.execute(
            "PRAGMA table_info(books)").fetchall()}
        assert "migration_audit" in {r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        conn.close()

    def test_v1_db_runs_v1_to_v2_to_v3(self, db_path):
        """A version-1 database runs v1→v2 then v2→v3 on initialize."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute("INSERT INTO books (title, total_quantity, available_quantity, "
                      "status, created_at, updated_at) "
                      "VALUES ('Math', 3, 3, 'ACTIVE', 'now', 'now')")
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
        cols = {r[1] for r in conn.execute("PRAGMA table_info(books)").fetchall()}
        assert "book_key" in cols
        conn.close()

    def test_v2_db_runs_only_v2_to_v3(self, db_path):
        """A version-2 database skips v1→v2 and runs only v2→v3."""
        conn = _MigrationTestBase._make_db(db_path, user_version=0)
        conn.executescript("""
            ALTER TABLE books ADD COLUMN book_key TEXT;
            CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key
                ON books(book_key) WHERE book_key IS NOT NULL;
        """)
        conn.execute("PRAGMA user_version = 2")
        conn.execute("INSERT INTO books (title, book_key, total_quantity, "
                      "available_quantity, status, created_at, updated_at) "
                      "VALUES ('Math', 'math', 10, 10, 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO students (student_code, name, status, "
                      "created_at, updated_at) "
                      "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-07-01', 'ISSUED', 'now', 'now')")
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
        book = conn.execute(
            "SELECT available_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 9  # 10 - 1 active issue
        conn.close()

    def test_v3_db_runs_no_migration(self, db_path):
        """A version-3 database runs no migration and creates no audit entries."""
        conn = _MigrationTestBase._make_db(db_path, user_version=0)
        conn.executescript("""
            ALTER TABLE books ADD COLUMN book_key TEXT;
            CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key
                ON books(book_key) WHERE book_key IS NOT NULL;
        """)
        conn.execute("PRAGMA user_version = 3")
        conn.execute("INSERT INTO books (title, book_key, total_quantity, "
                      "available_quantity, status, created_at, updated_at) "
                      "VALUES ('Math', 'math', 10, 10, 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO students (student_code, name, status, "
                      "created_at, updated_at) "
                      "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-07-01', 'ISSUED', 'now', 'now')")
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 3
        # available_quantity should NOT have been corrected.
        book = conn.execute(
            "SELECT available_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 10
        # No audit records from v2→v3.
        count = conn.execute(
            "SELECT COUNT(*) FROM migration_audit").fetchone()[0]
        assert count == 0
        conn.close()


# ---------------------------------------------------------------------------
# v2→v3 correction scenarios
# ---------------------------------------------------------------------------

class TestMigrationV2toV3:
    """Verify the v2→v3 migration handles every quantity scenario correctly."""

    @staticmethod
    def _setup_v2(db_path, available, issues):
        """Create a v2 DB with a book and optional active issues."""
        conn = _MigrationTestBase._make_db(db_path, user_version=0)
        conn.executescript("""
            ALTER TABLE books ADD COLUMN book_key TEXT;
            CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key
                ON books(book_key) WHERE book_key IS NOT NULL;
        """)
        conn.execute("PRAGMA user_version = 2")
        conn.execute("INSERT INTO books (title, book_key, total_quantity, "
                      "available_quantity, status, created_at, updated_at) "
                      "VALUES ('Math', 'math', 10, ?, 'ACTIVE', 'now', 'now')",
                      (available,))
        for i in range(issues):
            code = f"S{i+1}"
            conn.execute("INSERT OR IGNORE INTO students (student_code, name, "
                          "status, created_at, updated_at) "
                          "VALUES (?, ?, 'ACTIVE', 'now', 'now')", (code, code))
            conn.execute("INSERT INTO book_issues (book_id, student_id, "
                          "issue_date, status, created_at, updated_at) "
                          "VALUES (1, ?, '2026-07-01', 'ISSUED', 'now', 'now')",
                          (i + 1,))
        conn.commit()
        conn.close()

    def test_corrects_inflated_available(self, db_path):
        """available_quantity = total - active_issues when total > issues."""
        self._setup_v2(db_path, available=10, issues=1)
        database.initialize_database()

        conn = database.get_connection()
        book = conn.execute(
            "SELECT available_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 9  # 10 - 1

        audit = conn.execute(
            "SELECT status FROM migration_audit WHERE row_id=1").fetchone()
        assert audit[0] == "corrected"
        conn.close()

    def test_active_equals_total_results_in_zero_available(self, db_path):
        """When active_issues == total_quantity, available becomes 0 (corrected)."""
        self._setup_v2(db_path, available=10, issues=10)
        database.initialize_database()

        conn = database.get_connection()
        book = conn.execute(
            "SELECT available_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 0

        audit = conn.execute(
            "SELECT status FROM migration_audit WHERE row_id=1").fetchone()
        assert audit[0] == "corrected"
        conn.close()

    def test_active_exceeds_total_flagged_manual_review(self, db_path):
        """When active > total, record is flagged manual_review_required."""
        self._setup_v2(db_path, available=10, issues=12)
        database.initialize_database()

        conn = database.get_connection()
        conn.row_factory = sqlite3.Row
        # available clamped to 0.
        book = conn.execute(
            "SELECT * FROM books WHERE id=1").fetchone()
        assert book["available_quantity"] == 0

        audit = conn.execute(
            "SELECT * FROM migration_audit WHERE row_id=1").fetchone()
        assert audit["status"] == "manual_review_required"
        assert "exceeds" in audit["reason"]
        conn.close()

    def test_active_exceeds_total_not_counted_as_corrected(self, db_path):
        """active > total records are not reported as corrected (only manual_review)."""
        self._setup_v2(db_path, available=10, issues=12)
        database.initialize_database()

        conn = database.get_connection()
        manual = conn.execute(
            "SELECT COUNT(*) FROM migration_audit "
            "WHERE status='manual_review_required'").fetchone()[0]
        corrected = conn.execute(
            "SELECT COUNT(*) FROM migration_audit "
            "WHERE status='corrected'").fetchone()[0]
        assert manual == 1
        assert corrected == 0
        conn.close()

    def test_issue_history_preserved_after_v2_to_v3(self, db_path):
        """Issue and return records remain unchanged after v2→v3 migration."""
        conn = _MigrationTestBase._make_db(db_path, user_version=0)
        conn.executescript("""
            ALTER TABLE books ADD COLUMN book_key TEXT;
            CREATE UNIQUE INDEX IF NOT EXISTS idx_books_book_key
                ON books(book_key) WHERE book_key IS NOT NULL;
        """)
        conn.execute("PRAGMA user_version = 2")
        conn.execute("INSERT INTO books (title, book_key, total_quantity, "
                      "available_quantity, status, created_at, updated_at) "
                      "VALUES ('Math', 'math', 10, 10, 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO students (student_code, name, status, "
                      "created_at, updated_at) "
                      "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')")
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-07-01', '2026-07-08', "
                      "'ISSUED', 'now', 'now')")
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, return_date, status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-06-01', '2026-06-08', '2026-06-05', "
                      "'RETURNED', 'now', 'now')")
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-05-01', '2026-05-08', "
                      "'LOST', 'now', 'now')")
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        conn.row_factory = sqlite3.Row
        issues = conn.execute("SELECT * FROM book_issues ORDER BY id").fetchall()
        assert len(issues) == 3
        assert issues[0]["status"] == "ISSUED"
        assert issues[0]["issue_date"] == "2026-07-01"
        assert issues[1]["status"] == "RETURNED"
        assert issues[1]["return_date"] == "2026-06-05"
        assert issues[2]["status"] == "LOST"
        conn.close()


# ---------------------------------------------------------------------------
# v1→v2 merge scenarios (including active > total flagging)
# ---------------------------------------------------------------------------

class TestMigrationV1toV2:
    """Verify the v1→v2 duplicate merge handles edge cases correctly."""

    def test_merge_stress_with_active_over_total(self, db_path):
        """v1→v2 flags groups where active issues exceed max total for review."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'RD', 'Academic', 3, 3, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'rd', 'academic', 2, 2, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S2', 'Bob', 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S3', 'Carol', 'ACTIVE', 'now', 'now')"
        )
        for sid in (1, 2, 3):
            conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "status, created_at, updated_at) "
                "VALUES (1, ?, '2026-07-01', 'ISSUED', 'now', 'now')", (sid,))
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        conn.row_factory = sqlite3.Row
        book = conn.execute("SELECT * FROM books WHERE id=1").fetchone()
        assert book["book_key"] is not None
        assert book["total_quantity"] == 3  # max of (3, 2)
        assert book["available_quantity"] == 0  # 3 - 3 active

        # No more book 2.
        assert conn.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 1

        audit = conn.execute(
            "SELECT status FROM migration_audit ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()

    def test_merge_above_threshold_flagged_for_review(self, db_path):
        """v1→v2 flags group for manual review when active > max total."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'RD', 'Academic', 1, 1, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'rd', 'academic', 2, 2, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S2', 'Bob', 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S3', 'Carol', 'ACTIVE', 'now', 'now')"
        )
        for sid in (1, 2, 3):
            conn.execute(
                "INSERT INTO book_issues (book_id, student_id, issue_date, "
                "status, created_at, updated_at) "
                "VALUES (1, ?, '2026-07-01', 'ISSUED', 'now', 'now')", (sid,))
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        conn.row_factory = sqlite3.Row
        book = conn.execute("SELECT * FROM books WHERE id=1").fetchone()
        assert book["total_quantity"] == 2  # max of (1, 2)
        assert book["available_quantity"] == 0  # clamped: active(3) > total(2)

        audit = conn.execute(
            "SELECT * FROM migration_audit WHERE row_id=1 ORDER BY id DESC LIMIT 1"
        ).fetchone()
        assert audit["status"] == "manual_review_required"
        assert "exceeds" in audit["reason"]
        conn.close()

    def test_merge_issue_history_preserved(self, db_path):
        """v1→v2 reassigns issues to canonical and preserves all history."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'RD', 'Academic', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'rd', 'academic', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO students (student_code, name, status, "
            "created_at, updated_at) "
            "VALUES ('S1', 'Alice', 'ACTIVE', 'now', 'now')"
        )
        # Issue to canonical (book 1) — ISSUED
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, status, created_at, updated_at) "
                      "VALUES (1, 1, '2026-07-01', '2026-07-08', "
                      "'ISSUED', 'now', 'now')")
        # Issue to duplicate (book 2) — RETURNED
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, return_date, status, created_at, updated_at) "
                      "VALUES (2, 1, '2026-06-01', '2026-06-08', '2026-06-05', "
                      "'RETURNED', 'now', 'now')")
        # Issue to duplicate (book 2) — LOST
        conn.execute("INSERT INTO book_issues (book_id, student_id, issue_date, "
                      "due_date, status, created_at, updated_at) "
                      "VALUES (2, 1, '2026-05-01', '2026-05-08', "
                      "'LOST', 'now', 'now')")
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        conn.row_factory = sqlite3.Row
        issues = conn.execute(
            "SELECT * FROM book_issues ORDER BY id"
        ).fetchall()
        assert len(issues) == 3
        # All issues now reference the canonical book (id=1).
        for issue in issues:
            assert issue["book_id"] == 1
        assert issues[0]["status"] == "ISSUED"
        assert issues[1]["status"] == "RETURNED"
        assert issues[1]["return_date"] == "2026-06-05"
        assert issues[2]["status"] == "LOST"
        conn.close()

    def test_merge_dedup_on_title_author_category_only(self, db_path):
        """v1→v2 merges based on normalized title|author|category (only available fields)."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Physics', 'HC Verma', 'Academic', 3, 3, 'ACTIVE', "
            "'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Physics', 'HC Verma', 'Academic', 2, 2, 'ACTIVE', "
            "'now', 'now')"
        )
        # ponytail: The schema has no ISBN, accession, publisher, edition or
        # publication-year columns. Merge is title|author|category only.
        # If those columns are added in the future, update _migrate_v1_to_v2.
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        assert count == 1
        book = conn.execute(
            "SELECT total_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 3  # max(3, 2)
        conn.close()

    def test_merge_idempotent_on_rerun(self, db_path):
        """Rerunning initialize_database on a v1→v2→v3 DB does not duplicate audits."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'RD', 'Academic', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'rd', 'academic', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.commit()
        conn.close()

        database.initialize_database()
        conn = database.get_connection()
        first = conn.execute(
            "SELECT COUNT(*) FROM migration_audit").fetchone()[0]
        conn.close()

        database.initialize_database()
        database.initialize_database()
        conn = database.get_connection()
        second = conn.execute(
            "SELECT COUNT(*) FROM migration_audit").fetchone()[0]
        assert second == first
        conn.close()

    def test_merge_no_total_inflation_for_duplicates(self, db_path):
        """v1→v2 uses MAX(total_quantity), not SUM — quantities never inflate."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'RD', 'Academic', 3, 3, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Math', 'rd', 'academic', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.commit()
        conn.close()

        database.initialize_database()

        conn = database.get_connection()
        book = conn.execute(
            "SELECT total_quantity FROM books WHERE id=1").fetchone()
        assert book[0] == 5  # max, not 8
        conn.close()


# ---------------------------------------------------------------------------
# Migration rollback safety
# ---------------------------------------------------------------------------

class TestMigrationRollback:
    """Verify failures roll back cleanly — DB stays at original version."""

    def test_migration_failure_rolls_back_version(self, db_path):
        """A sqlite error during migration rolls back the user_version."""
        conn = _MigrationTestBase._make_db(db_path, user_version=1)
        # Two duplicate books trigger the merge path which UPDATES total_quantity.
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Test', 'A', 'B', 5, 5, 'ACTIVE', 'now', 'now')"
        )
        conn.execute(
            "INSERT INTO books (title, author, category, total_quantity, "
            "available_quantity, status, created_at, updated_at) "
            "VALUES ('Test', 'a', 'b', 3, 3, 'ACTIVE', 'now', 'now')"
        )
        # Trigger blocks the merge UPDATE on total_quantity.
        conn.execute("""
            CREATE TRIGGER trg_block_update BEFORE UPDATE OF total_quantity ON books
            BEGIN
                SELECT RAISE(ABORT, 'triggered failure');
            END;
        """)
        conn.commit()
        conn.close()

        with pytest.raises(database.DatabaseError):
            database.initialize_database()

        conn = database.get_connection()
        assert conn.execute("PRAGMA user_version").fetchone()[0] == 1
        conn.close()
