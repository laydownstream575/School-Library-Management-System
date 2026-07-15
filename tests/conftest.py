"""Shared test fixtures: isolated temp database and sample data.

Every test gets a fresh database with the full schema applied.
The production database is never touched.
"""

import os
import shutil
import sqlite3
import tempfile

import pytest

from app import config, database, utils

# ---------------------------------------------------------------------------
# Temporary database management
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db_path():
    """Create a temporary directory and database path for the test.

    Overrides ``config.DATABASE_PATH`` so all queries hit the temp DB.
    Cleans up on teardown.
    """
    tmp_dir = tempfile.mkdtemp(prefix="lib_test_")
    tmp_db = os.path.join(tmp_dir, "test_library.db")

    # Save original paths and override.
    orig_data_dir = config.DATA_DIR
    orig_db_path = config.DATABASE_PATH
    orig_db_dir = config.DATABASE_DIR
    orig_exports_dir = config.EXPORTS_DIR

    config.DATA_DIR = tmp_dir
    config.DATABASE_DIR = tmp_dir
    config.DATABASE_PATH = tmp_db
    config.EXPORTS_DIR = os.path.join(tmp_dir, "exports")
    config.REQUIRED_DIRS = [config.DATABASE_DIR, config.EXPORTS_DIR]

    # Initialise the database schema on the temp DB.
    database.initialize_database()

    yield tmp_db

    # Restore original paths.
    config.DATA_DIR = orig_data_dir
    config.DATABASE_PATH = orig_db_path
    config.DATABASE_DIR = orig_db_dir
    config.EXPORTS_DIR = orig_exports_dir
    config.REQUIRED_DIRS = [orig_db_dir, orig_exports_dir]

    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def fresh_db(db_path):
    """Truncate all tables between tests (clean slate, full schema intact)."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    # Delete order respects FK constraints (book_issues references books/students).
    for table in ("book_issues", "activity_logs", "settings", "books", "students"):
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
    # Re-insert default settings.
    utils.set_setting("school_name", "ABC Public School")
    utils.set_setting("library_name", "School Library")
    utils.set_setting("default_due_days", "7")
    utils.set_setting("low_stock_limit", "2")
    utils.set_setting("backup_path", "backups")
    utils.set_setting("export_path", "exports")
    yield db_path


# ---------------------------------------------------------------------------
# Sample data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_book(fresh_db):
    """Add a single valid book and return it as a dict."""
    from services.book_service import add_book, get_book

    bid = add_book({"title": "Mathematics", "author": "R.D. Sharma",
                    "category": "Academic", "total_quantity": 5})
    return get_book(bid)


@pytest.fixture
def sample_student(fresh_db):
    """Add a single valid student and return it as a dict."""
    from services.student_service import add_student, get_student

    sid = add_student({"student_code": "STU001", "name": "Rahul",
                       "class_name": "10", "division": "A"})
    return get_student(sid)


@pytest.fixture
def sample_issue(fresh_db, sample_book, sample_student):
    """Issue the sample book to the sample student and return the issue dict."""
    from services.issue_service import issue_book

    issue_id = issue_book(
        sample_student["id"], sample_book["id"],
        issue_date="2026-07-01", due_date="2026-07-08",
    )
    from services.issue_service import get_issue
    return get_issue(issue_id)
