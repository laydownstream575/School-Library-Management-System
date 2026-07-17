"""Large-dataset smoke tests: 10k students, 10k books, 50k issues.

These verify that searching, reports, and exports remain functional with
realistic data volumes. They are marked with 'slow' and can be skipped
with ``pytest -m 'not slow'``.
"""

import time

import pytest

pytestmark = pytest.mark.slow


def _insert_many(conn, table, columns, rows):
    placeholders = ", ".join("?" for _ in columns)
    col_names = ", ".join(columns)
    conn.executemany(
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})",
        rows,
    )
    conn.commit()


def _generate_students(n: int, start: int = 1):
    for i in range(start, start + n):
        yield (
            f"STU{i:06d}",
            f"Student_{i}",
            str((i % 12) + 1),
            chr(65 + (i % 26)),
            "ACTIVE",
            "2026-01-01 00:00:00",
            "2026-01-01 00:00:00",
        )


def _generate_books(n: int, start: int = 1):
    for i in range(start, start + n):
        yield (
            f"Book_{i}",
            f"Author_{i % 500}",
            f"Category_{i % 20}",
            10,
            10,
            "ACTIVE",
            "2026-01-01 00:00:00",
            "2026-01-01 00:00:00",
        )


def _generate_issues(n: int, book_ids: list, student_ids: list, start: int = 1):
    import random
    rng = random.Random(42)
    for i in range(start, start + n):
        bid = rng.choice(book_ids)
        sid = rng.choice(student_ids)
        yield (
            bid, sid,
            f"2026-01-{((i-1) % 28) + 1:02d}",
            f"2026-02-{((i-1) % 28) + 1:02d}",
            None if i % 3 == 0 else f"2026-03-{((i-1) % 28) + 1:02d}",
            "ISSUED" if i % 3 == 0 else "RETURNED",
            "",
            "2026-01-01 00:00:00",
            "2026-01-01 00:00:00",
        )


# ---------------------------------------------------------------------------
# Fixture: large dataset in a fresh database
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def large_db():
    """Populate a fresh database with 10k students, 10k books, 50k issues."""
    import os
    import shutil
    import sqlite3
    import tempfile

    from app import config, database

    tmp_dir = tempfile.mkdtemp(prefix="lib_large_")
    tmp_db = os.path.join(tmp_dir, "test_large.db")

    # Override paths.
    orig = {k: getattr(config, k) for k in
            ("DATA_DIR", "DATABASE_PATH", "DATABASE_DIR", "EXPORTS_DIR")}
    config.DATA_DIR = tmp_dir
    config.DATABASE_DIR = tmp_dir
    config.DATABASE_PATH = tmp_db
    config.EXPORTS_DIR = os.path.join(tmp_dir, "exports")
    config.REQUIRED_DIRS = [config.DATABASE_DIR, config.EXPORTS_DIR]

    database.initialize_database()

    conn = sqlite3.connect(tmp_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    print("\nGenerating 10,000 students...")
    _insert_many(conn, "students",
                 ["student_code", "name", "class_name", "division",
                  "status", "created_at", "updated_at"],
                 list(_generate_students(10000)))

    print("Generating 10,000 books...")
    _insert_many(conn, "books",
                 ["title", "author", "category", "total_quantity",
                  "available_quantity", "status", "created_at", "updated_at"],
                 list(_generate_books(10000)))

    conn.execute("UPDATE books SET available_quantity = 5 WHERE id % 2 = 0")
    conn.commit()

    book_ids = [r["id"] for r in conn.execute("SELECT id FROM books").fetchall()]
    student_ids = [r["id"] for r in conn.execute("SELECT id FROM students").fetchall()]

    print("Generating 50,000 issue records...")
    _insert_many(conn, "book_issues",
                 ["book_id", "student_id", "issue_date", "due_date",
                  "return_date", "status", "remarks", "created_at", "updated_at"],
                 list(_generate_issues(50000, book_ids, student_ids)))

    conn.close()
    print("Large dataset ready.\n")

    yield tmp_db

    # Cleanup.
    for k, v in orig.items():
        setattr(config, k, v)
    shutil.rmtree(tmp_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Student service tests
# ---------------------------------------------------------------------------

class TestLargeStudentService:
    def test_get_students_all(self, large_db):
        from services.student_service import get_students
        students = get_students()
        assert len(students) == 10000

    def test_get_students_search(self, large_db):
        from services.student_service import get_students
        students = get_students(search="STU005000")
        assert len(students) == 1
        assert students[0]["student_code"] == "STU005000"

    def test_get_student_by_id(self, large_db):
        from services.student_service import get_student
        st = get_student(5000)
        assert st is not None
        assert st["student_code"] == "STU005000"

    def test_get_active_students(self, large_db):
        from services.student_service import get_active_students
        active = get_active_students()
        assert len(active) == 10000

    def test_get_pending_count(self, large_db):
        from services.student_service import get_pending_count
        # Student 1 should have some issues.
        count = get_pending_count(1)
        assert isinstance(count, int)


# ---------------------------------------------------------------------------
# Book service tests
# ---------------------------------------------------------------------------

class TestLargeBookService:
    def test_get_books_all(self, large_db):
        from services.book_service import get_books
        books = get_books()
        assert len(books) == 10000

    def test_get_books_search(self, large_db):
        from services.book_service import get_books
        books = get_books(search="Book_500")
        assert len(books) >= 1

    def test_get_book_by_id(self, large_db):
        from services.book_service import get_book
        b = get_book(5000)
        assert b is not None
        assert "Book_5000" in b["title"]

    def test_get_active_available_books(self, large_db):
        from services.book_service import get_active_available_books
        available = get_active_available_books()
        assert len(available) > 0

    def test_get_issued_count(self, large_db):
        from services.book_service import get_issued_count
        count = get_issued_count(1)
        assert isinstance(count, int)


# ---------------------------------------------------------------------------
# Issue service tests
# ---------------------------------------------------------------------------

class TestLargeIssueService:
    def test_get_pending_returns(self, large_db):
        from services.issue_service import get_pending_returns
        pending = get_pending_returns()
        # About 1/3 of 50000 = ~16667 should be ISSUED.
        assert len(pending) > 10000

    def test_get_pending_returns_search(self, large_db):
        from services.issue_service import get_pending_returns
        pending = get_pending_returns("STU000001")
        assert len(pending) >= 0

    def test_get_overdue_books(self, large_db):
        from services.issue_service import get_overdue_books
        overdue = get_overdue_books()
        # With 2026 dates, all should be overdue by now.
        assert len(overdue) > 0


# ---------------------------------------------------------------------------
# Report service tests
# ---------------------------------------------------------------------------

class TestLargeReportService:
    def test_dashboard_summary(self, large_db):
        from services.report_service import dashboard_summary
        summary = dashboard_summary()
        assert summary["total_books"] == 100000  # 10000 * 10
        assert summary["total_students"] == 10000
        assert summary["issued_books"] > 10000

    def test_report_all_books(self, large_db):
        from services.report_service import report_all_books
        cols, rows = report_all_books()
        assert len(rows) == 10000

    def test_report_students(self, large_db):
        from services.report_service import report_students
        cols, rows = report_students()
        assert len(rows) == 10000


# ---------------------------------------------------------------------------
# Excel export with large data
# ---------------------------------------------------------------------------

class TestLargeExcelExport:
    def test_export_books_to_excel(self, large_db):
        import os
        from app import config
        from services import excel_service

        os.makedirs(config.EXPORTS_DIR, exist_ok=True)
        t0 = time.time()
        path = excel_service.export_books()
        elapsed = time.time() - t0
        assert os.path.isfile(path)
        # Should complete within 30 seconds.
        assert elapsed < 30, f"Export took {elapsed:.1f}s"

    def test_export_full_backup(self, large_db):
        import os
        from app import config
        from services import excel_service

        os.makedirs(config.EXPORTS_DIR, exist_ok=True)
        t0 = time.time()
        path = excel_service.export_full_backup()
        elapsed = time.time() - t0
        assert os.path.isfile(path)
        assert elapsed < 60, f"Full backup took {elapsed:.1f}s"


# ---------------------------------------------------------------------------
# Backup with large data
# ---------------------------------------------------------------------------

class TestLargeBackup:
    def test_backup_large_db(self, large_db):
        from services import backup_service
        t0 = time.time()
        path = backup_service.backup_database()
        elapsed = time.time() - t0
        import os
        assert os.path.isfile(path)
        assert elapsed < 30, f"Backup took {elapsed:.1f}s"

    def test_restore_large_db(self, large_db):
        from services import backup_service
        backup_path = backup_service.backup_database()
        t0 = time.time()
        backup_service.restore_database(backup_path)
        elapsed = time.time() - t0
        assert elapsed < 30, f"Restore took {elapsed:.1f}s"
