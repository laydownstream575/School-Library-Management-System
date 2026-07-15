"""Unit tests for app/validators.py."""

from app import validators


class TestRequireText:
    def test_empty_string_fails(self):
        result = validators.require_text("", "Title")
        assert not result
        assert "Title is required" in result.message

    def test_whitespace_only_fails(self):
        result = validators.require_text("   ", "Title")
        assert not result

    def test_none_fails(self):
        result = validators.require_text(None, "Title")
        assert not result

    def test_valid_text_passes(self):
        result = validators.require_text("Math", "Title")
        assert result


class TestValidateQuantity:
    def test_empty_fails(self):
        result = validators.validate_quantity("", "Quantity")
        assert not result

    def test_non_numeric_fails(self):
        result = validators.validate_quantity("abc", "Quantity")
        assert not result

    def test_negative_fails(self):
        result = validators.validate_quantity("-1", "Quantity")
        assert not result

    def test_zero_passes(self):
        result = validators.validate_quantity("0", "Quantity")
        assert result

    def test_positive_passes(self):
        result = validators.validate_quantity("5", "Quantity")
        assert result


class TestValidateBookForm:
    def test_empty_title_fails(self):
        result = validators.validate_book_form("", "5")
        assert not result

    def test_invalid_quantity_fails(self):
        result = validators.validate_book_form("Math", "abc")
        assert not result

    def test_available_exceeds_total_fails(self):
        result = validators.validate_book_form("Math", "5", "10")
        assert not result

    def test_valid_book_passes(self):
        result = validators.validate_book_form("Math", "5", "3")
        assert result

    def test_valid_book_no_available_passes(self):
        result = validators.validate_book_form("Math", "5")
        assert result


class TestValidateStudentForm:
    def test_empty_code_fails(self):
        result = validators.validate_student_form("", "Rahul")
        assert not result

    def test_empty_name_fails(self):
        result = validators.validate_student_form("STU001", "")
        assert not result

    def test_valid_student_passes(self):
        result = validators.validate_student_form("STU001", "Rahul")
        assert result


class TestValidateIssueDates:
    def test_empty_issue_date_fails(self):
        result = validators.validate_issue_dates("", "2026-07-08")
        assert not result

    def test_due_before_issue_fails(self):
        result = validators.validate_issue_dates("2026-07-10", "2026-07-08")
        assert not result

    def test_valid_dates_pass(self):
        result = validators.validate_issue_dates("2026-07-01", "2026-07-08")
        assert result

    def test_no_due_date_passes(self):
        result = validators.validate_issue_dates("2026-07-01", "")
        assert result


class TestValidateReturnDate:
    def test_empty_return_date_fails(self):
        result = validators.validate_return_date("2026-07-01", "")
        assert not result

    def test_return_before_issue_fails(self):
        result = validators.validate_return_date("2026-07-10", "2026-07-08")
        assert not result

    def test_valid_return_date_passes(self):
        result = validators.validate_return_date("2026-07-01", "2026-07-05")
        assert result
