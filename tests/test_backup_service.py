"""Tests for services/backup_service.py — backup, restore, integrity checks."""

import os
import sqlite3
import tempfile

import pytest

from app import config
from services import ServiceError, backup_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_invalid_sqlite(path: str):
    with open(path, "wb") as f:
        f.write(b"not a sqlite database")


def _make_empty_sqlite(path: str):
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE dummy (id INTEGER)")
    conn.close()


def _make_partial_sqlite(path: str):
    """Create a DB missing one required table."""
    conn = sqlite3.connect(path)
    conn.executescript("""
        CREATE TABLE books (id INTEGER PRIMARY KEY);
        CREATE TABLE students (id INTEGER PRIMARY KEY);
        CREATE TABLE book_issues (id INTEGER PRIMARY KEY);
        CREATE TABLE settings (key TEXT PRIMARY KEY);
        -- Missing activity_logs table
    """)
    conn.close()


# ---------------------------------------------------------------------------
# Backup tests
# ---------------------------------------------------------------------------

class TestBackup:
    def test_backup_creates_file(self, fresh_db, sample_book):
        path = backup_service.backup_database()
        assert os.path.isfile(path)
        assert path.endswith(".db")
        # Backup should contain the sample data.
        conn = sqlite3.connect(path)
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        conn.close()
        assert count == 1

    def test_backup_without_db_raises(self, fresh_db):
        os.remove(config.DATABASE_PATH)
        with pytest.raises(ServiceError, match="No database"):
            backup_service.backup_database()

    def test_backup_custom_directory(self, fresh_db):
        custom_dir = tempfile.mkdtemp(prefix="backup_test_")
        path = backup_service.backup_database(custom_dir)
        assert custom_dir in path
        assert os.path.isfile(path)

    def test_backup_timestamped_filename(self, fresh_db):
        import re
        path = backup_service.backup_database()
        assert re.search(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", path)


# ---------------------------------------------------------------------------
# Restore tests
# ---------------------------------------------------------------------------

class TestRestore:
    def test_valid_restore(self, fresh_db, sample_book, sample_student):
        backup_path = backup_service.backup_database()
        # Delete a book to simulate data loss.
        conn = sqlite3.connect(config.DATABASE_PATH)
        conn.execute("DELETE FROM books")
        conn.commit()
        conn.close()
        # Restore from backup.
        safety = backup_service.restore_database(backup_path)
        conn = sqlite3.connect(config.DATABASE_PATH)
        count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
        conn.close()
        assert count == 1
        if safety:
            assert os.path.isfile(safety)

    def test_nonexistent_backup_raises(self, fresh_db):
        with pytest.raises(ServiceError, match="not be found"):
            backup_service.restore_database("/nonexistent/path.db")

    def test_invalid_sqlite_file_raises(self, fresh_db):
        path = tempfile.mktemp(suffix=".db")
        _make_invalid_sqlite(path)
        with pytest.raises(ServiceError, match="not a valid"):
            backup_service.restore_database(path)
        os.unlink(path)

    def test_integrity_check_failure_raises(self, fresh_db):
        """A corrupted backup file should be rejected with an error."""
        path = tempfile.mktemp(suffix=".db")
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE books (id INTEGER)")
        conn.execute("PRAGMA integrity_check")
        conn.close()
        # Remove the SQLite header so it fails the integrity / header check.
        with open(path, "wb") as f:
            f.write(b"\x00" * 512)
        with pytest.raises(ServiceError, match="valid|corrupt"):
            backup_service.restore_database(path)
        os.unlink(path)

    def test_missing_required_tables_raises(self, fresh_db):
        path = tempfile.mktemp(suffix=".db")
        _make_partial_sqlite(path)
        with pytest.raises(ServiceError, match="missing required"):
            backup_service.restore_database(path)
        os.unlink(path)

    def test_after_restore_initialize_database_succeeds(self, fresh_db, sample_book):
        """Restore calls initialize_database; schema remains intact."""
        backup_path = backup_service.backup_database()
        os.remove(config.DATABASE_PATH)
        backup_service.restore_database(backup_path)
        conn = sqlite3.connect(config.DATABASE_PATH)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        conn.close()
        for t in ("books", "students", "book_issues", "settings", "activity_logs"):
            assert t in tables


# ---------------------------------------------------------------------------
# List / display tests
# ---------------------------------------------------------------------------

class TestListBackups:
    def test_list_backups(self, fresh_db):
        backup_service.backup_database()
        backups = backup_service.list_backups()
        assert len(backups) >= 1
        assert all(os.path.isfile(p) for p in backups)

    def test_list_backups_from_missing_dir(self, fresh_db):
        backups = backup_service.list_backups("c:\\nonexistent_path_xyz")
        assert backups == []

    def test_last_backup_display_no_backups(self, fresh_db):
        display = backup_service.last_backup_display()
        assert "No backup" in display
