"""Unit tests for app/utils.py."""

from datetime import date

from app import utils


class TestDateHelpers:
    def test_today_str_format(self):
        result = utils.today_str()
        assert len(result) == 10
        assert result.count("-") == 2

    def test_now_timestamp_format(self):
        result = utils.now_timestamp()
        assert " " in result
        assert result.count("-") == 2
        assert result.count(":") == 2

    def test_parse_date_valid(self):
        result = utils.parse_date("2026-07-01")
        assert result == date(2026, 7, 1)

    def test_parse_date_empty(self):
        assert utils.parse_date("") is None

    def test_parse_date_none(self):
        assert utils.parse_date(None) is None

    def test_parse_date_invalid(self):
        assert utils.parse_date("not-a-date") is None

    def test_format_display_date(self):
        assert utils.format_display_date("2026-07-01") == "01 Jul 2026"

    def test_format_display_date_empty(self):
        assert utils.format_display_date("") == "-"

    def test_format_display_date_none(self):
        assert utils.format_display_date(None) == "-"

    def test_add_days(self):
        result = utils.add_days("2026-07-01", 7)
        assert result == "2026-07-08"

    def test_add_days_negative(self):
        result = utils.add_days("2026-07-08", -3)
        assert result == "2026-07-05"

    def test_overdue_days_zero_when_not_overdue(self):
        assert utils.overdue_days("2099-12-31") == 0

    def test_overdue_days_positive(self):
        overdue = utils.overdue_days("2020-01-01")
        assert overdue > 0

    def test_overdue_days_none(self):
        assert utils.overdue_days(None) == 0

    def test_overdue_days_empty(self):
        assert utils.overdue_days("") == 0


class TestRowToDict:
    def test_row_to_dict_with_none(self):
        assert utils.row_to_dict(None) is None

    def test_row_to_dict_with_dict(self):
        d = {"a": 1}
        result = utils.row_to_dict(d)
        assert result == d
        assert result is not d  # should be a copy
