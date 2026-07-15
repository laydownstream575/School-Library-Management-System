"""Integration tests for services/book_service.py."""

import pytest

from app import config
from services import ServiceError, book_service


class TestBookService:
    def test_add_valid_book(self, fresh_db):
        bid = book_service.add_book({
            "title": "Mathematics", "author": "R.D. Sharma",
            "category": "Academic", "total_quantity": 5,
        })
        assert bid > 0
        book = book_service.get_book(bid)
        assert book["title"] == "Mathematics"
        assert book["total_quantity"] == 5
        assert book["available_quantity"] == 5
        assert book["status"] == config.STATUS_ACTIVE

    def test_add_book_sets_available_equal_total(self, fresh_db):
        bid = book_service.add_book({"title": "Science", "total_quantity": 10})
        book = book_service.get_book(bid)
        assert book["available_quantity"] == 10

    def test_add_book_without_title_raises(self, fresh_db):
        with pytest.raises(ServiceError, match="title"):
            book_service.add_book({"title": "", "total_quantity": 5})

    def test_add_book_with_negative_quantity_raises(self, fresh_db):
        with pytest.raises(ServiceError):
            book_service.add_book({"title": "Test", "total_quantity": -1})

    def test_get_books_all(self, fresh_db):
        book_service.add_book({"title": "Alpha", "total_quantity": 1})
        book_service.add_book({"title": "Beta", "total_quantity": 1})
        books = book_service.get_books()
        assert len(books) == 2

    def test_search_by_title(self, fresh_db):
        book_service.add_book({"title": "Mathematics", "total_quantity": 1})
        book_service.add_book({"title": "Science", "total_quantity": 1})
        books = book_service.get_books(search="Math")
        assert len(books) == 1
        assert books[0]["title"] == "Mathematics"

    def test_search_by_partial_title(self, fresh_db):
        book_service.add_book({"title": "Mathematics", "total_quantity": 1})
        books = book_service.get_books(search="Mat")
        assert len(books) == 1

    def test_update_book_quantity(self, fresh_db, sample_book):
        book_service.update_book(sample_book["id"], {
            "title": sample_book["title"],
            "total_quantity": 10,
        })
        updated = book_service.get_book(sample_book["id"])
        assert updated["total_quantity"] == 10
        assert updated["available_quantity"] == 10

    def test_update_cannot_reduce_total_below_issued(self, fresh_db, sample_issue):
        book_id = sample_issue["book_id"]
        with pytest.raises(ServiceError, match="issued"):
            book_service.update_book(book_id, {
                "title": sample_issue["book_title"],
                "total_quantity": 0,
            })

    def test_delete_book(self, fresh_db, sample_book):
        book_service.delete_book(sample_book["id"])
        assert book_service.get_book(sample_book["id"]) is None

    def test_delete_book_with_active_issue_raises(self, fresh_db, sample_issue):
        with pytest.raises(ServiceError, match="issued"):
            book_service.delete_book(sample_issue["book_id"])

    def test_get_issued_count(self, fresh_db, sample_issue):
        count = book_service.get_issued_count(sample_issue["book_id"])
        assert count == 1

    def test_availability_label(self, fresh_db, sample_book):
        label = book_service.availability_label(sample_book)
        assert label == "Available"

    def test_get_active_available_books(self, fresh_db, sample_book):
        books = book_service.get_active_available_books()
        assert len(books) >= 1

    @pytest.mark.parametrize("qty,expected", [
        (5, "Available"),
        (0, "Not Available"),
    ])
    def test_availability_label_parametrized(self, fresh_db, qty, expected):
        bid = book_service.add_book({"title": "Test", "total_quantity": qty,
                                      "available_quantity": qty})
        book = book_service.get_book(bid)
        assert book_service.availability_label(book) == expected
