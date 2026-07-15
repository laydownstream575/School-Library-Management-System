"""Integration tests for services/issue_service.py."""

import pytest

from services import ServiceError, book_service, issue_service, student_service


class TestIssueService:
    def test_issue_book(self, fresh_db, sample_book, sample_student):
        issue_id = issue_service.issue_book(
            sample_student["id"], sample_book["id"],
            issue_date="2026-07-01", due_date="2026-07-08",
        )
        assert issue_id > 0
        issue = issue_service.get_issue(issue_id)
        assert issue["status"] == "ISSUED"

    def test_issue_decreases_availability(self, fresh_db, sample_book, sample_student):
        before = book_service.get_book(sample_book["id"])
        issue_service.issue_book(
            sample_student["id"], sample_book["id"],
            issue_date="2026-07-01", due_date="2026-07-08",
        )
        after = book_service.get_book(sample_book["id"])
        assert after["available_quantity"] == before["available_quantity"] - 1

    def test_issue_unavailable_book_raises(self, fresh_db, sample_student):
        bid = book_service.add_book({"title": "Zero", "total_quantity": 0,
                                      "available_quantity": 0})
        with pytest.raises(ServiceError, match="not available"):
            issue_service.issue_book(
                sample_student["id"], bid,
                issue_date="2026-07-01", due_date="2026-07-08",
            )

    def test_duplicate_issue_raises(self, fresh_db, sample_book, sample_student):
        issue_service.issue_book(
            sample_student["id"], sample_book["id"],
            issue_date="2026-07-01", due_date="2026-07-08",
        )
        with pytest.raises(ServiceError, match="already has"):
            issue_service.issue_book(
                sample_student["id"], sample_book["id"],
                issue_date="2026-07-01", due_date="2026-07-08",
            )

    def test_issue_inactive_book_raises(self, fresh_db, sample_student, sample_book):
        book_service.update_book(sample_book["id"], {
            "title": sample_book["title"],
            "total_quantity": sample_book["total_quantity"],
            "status": "INACTIVE",
        })
        with pytest.raises(ServiceError, match="inactive"):
            issue_service.issue_book(
                sample_student["id"], sample_book["id"],
                issue_date="2026-07-01", due_date="2026-07-08",
            )

    def test_issue_to_inactive_student_raises(self, fresh_db, sample_book, sample_student):
        student_service.update_student(sample_student["id"], {
            "student_code": sample_student["student_code"],
            "name": sample_student["name"],
            "status": "INACTIVE",
        })
        with pytest.raises(ServiceError, match="inactive"):
            issue_service.issue_book(
                sample_student["id"], sample_book["id"],
                issue_date="2026-07-01", due_date="2026-07-08",
            )

    def test_issue_to_different_students(self, fresh_db, sample_book):
        s1 = _add_student(fresh_db, "S1", "Alpha")
        s2 = _add_student(fresh_db, "S2", "Beta")
        issue_service.issue_book(s1, sample_book["id"],
                                  issue_date="2026-07-01", due_date="2026-07-08")
        issue_service.issue_book(s2, sample_book["id"],
                                  issue_date="2026-07-01", due_date="2026-07-08")
        assert book_service.get_book(sample_book["id"])["available_quantity"] == 3

    def test_return_book(self, fresh_db, sample_issue):
        issue_service.return_book(
            sample_issue["id"], return_date="2026-07-05",
        )
        returned = issue_service.get_issue(sample_issue["id"])
        assert returned["status"] == "RETURNED"
        assert returned["return_date"] == "2026-07-05"

    def test_return_increases_availability(self, fresh_db, sample_book, sample_issue):
        before = book_service.get_book(sample_book["id"])
        issue_service.return_book(sample_issue["id"], return_date="2026-07-05")
        after = book_service.get_book(sample_book["id"])
        assert after["available_quantity"] == before["available_quantity"] + 1

    def test_return_already_returned_raises(self, fresh_db, sample_issue):
        issue_service.return_book(sample_issue["id"], return_date="2026-07-05")
        with pytest.raises(ServiceError, match="already been returned"):
            issue_service.return_book(sample_issue["id"], return_date="2026-07-06")

    def test_return_with_date_before_issue_raises(self, fresh_db, sample_issue):
        with pytest.raises(ServiceError, match="earlier than"):
            issue_service.return_book(
                sample_issue["id"], return_date="2026-06-01",
            )

    def test_get_pending_returns(self, fresh_db, sample_issue):
        pending = issue_service.get_pending_returns()
        assert len(pending) >= 1
        assert pending[0]["issue_id"] == sample_issue["id"]

    def test_pending_returns_empty_after_return(self, fresh_db, sample_issue):
        issue_service.return_book(sample_issue["id"], return_date="2026-07-05")
        pending = issue_service.get_pending_returns()
        assert len(pending) == 0

    def test_get_overdue_books(self, fresh_db, sample_book, sample_student):
        # Issue with a past due date to ensure it appears overdue.
        issue_service.issue_book(
            sample_student["id"], sample_book["id"],
            issue_date="2020-01-01", due_date="2020-01-08",
        )
        overdue = issue_service.get_overdue_books()
        assert len(overdue) >= 1

    def test_has_active_issue_true(self, fresh_db, sample_issue):
        assert issue_service.has_active_issue(
            sample_issue["student_id"], sample_issue["book_id"]
        )

    def test_has_active_issue_false_after_return(self, fresh_db, sample_issue):
        issue_service.return_book(sample_issue["id"], return_date="2026-07-05")
        assert not issue_service.has_active_issue(
            sample_issue["student_id"], sample_issue["book_id"]
        )

    def test_issue_without_student_raises(self, fresh_db, sample_book):
        with pytest.raises(ServiceError, match="select a student"):
            issue_service.issue_book(
                0, sample_book["id"],
                issue_date="2026-07-01", due_date="2026-07-08",
            )

    def test_issue_without_book_raises(self, fresh_db, sample_student):
        with pytest.raises(ServiceError, match="select a book"):
            issue_service.issue_book(
                sample_student["id"], 0,
                issue_date="2026-07-01", due_date="2026-07-08",
            )


def _add_student(db, code, name):
    return student_service.add_student({
        "student_code": code,
        "name": name,
        "class_name": "10",
        "division": "A",
    })
