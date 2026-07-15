"""Integration tests for services/report_service.py."""

from services import report_service


class TestReportService:
    def test_dashboard_summary_empty(self, fresh_db):
        summary = report_service.dashboard_summary()
        assert summary["total_books"] == 0
        assert summary["available_books"] == 0
        assert summary["issued_books"] == 0
        assert summary["total_students"] == 0
        assert summary["pending_returns"] == 0
        assert summary["overdue_books"] == 0
        assert summary["low_stock_books"] == 0

    def test_dashboard_summary_with_data(self, fresh_db, sample_issue):
        summary = report_service.dashboard_summary()
        assert summary["total_books"] > 0
        assert summary["issued_books"] >= 1
        assert summary["total_students"] >= 1

    def test_recent_issues(self, fresh_db, sample_issue):
        issues = report_service.recent_issues()
        assert len(issues) >= 1
        assert issues[0]["book_title"] == sample_issue["book_title"]

    def test_recent_returns(self, fresh_db, sample_issue):
        from services.issue_service import return_book
        return_book(sample_issue["id"], return_date="2026-07-05")
        returns = report_service.recent_returns()
        assert len(returns) >= 1

    def test_report_all_books(self, fresh_db, sample_book):
        columns, rows = report_service.report_all_books()
        assert len(rows) >= 1
        assert "Title" in columns
        assert "Total Qty" in columns

    def test_report_available_books(self, fresh_db, sample_book):
        columns, rows = report_service.report_available_books()
        assert len(rows) >= 1

    def test_report_issued_books(self, fresh_db, sample_issue):
        columns, rows = report_service.report_issued_books()
        assert len(rows) >= 1

    def test_report_returned_books(self, fresh_db, sample_issue):
        from services.issue_service import return_book
        return_book(sample_issue["id"], return_date="2026-07-05")
        columns, rows = report_service.report_returned_books()
        assert len(rows) >= 1

    def test_report_pending_returns(self, fresh_db, sample_issue):
        columns, rows = report_service.report_pending_returns()
        assert len(rows) >= 1

    def test_report_overdue(self, fresh_db, sample_book, sample_student):
        from services.issue_service import issue_book
        issue_book(sample_student["id"], sample_book["id"],
                    issue_date="2020-01-01", due_date="2020-01-08")
        columns, rows = report_service.report_overdue()
        assert len(rows) >= 1

    def test_report_students(self, fresh_db, sample_student):
        columns, rows = report_service.report_students()
        assert len(rows) >= 1

    def test_report_student_history(self, fresh_db, sample_issue):
        columns, rows = report_service.report_student_history(
            sample_issue["student_id"]
        )
        assert len(rows) >= 1
        assert rows[0]["book_title"] == sample_issue["book_title"]

    def test_report_low_stock(self, fresh_db):
        columns, rows = report_service.report_low_stock()
        # No low stock books by default.
        assert isinstance(rows, list)

    def test_date_wise_issue(self, fresh_db, sample_issue):
        columns, rows = report_service.report_date_wise_issue(
            date_from="2026-07-01", date_to="2026-07-31"
        )
        assert len(rows) >= 1
