"""Issue Book page: select a student, select a book, set dates, and issue."""

import logging

from PySide6.QtCore import QDate, QTimer, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app import utils
from services import ServiceError, book_service, issue_service, student_service
from app.config import DEFAULT_SETTINGS
from ui import theme

logger = logging.getLogger(__name__)


class IssueBookPage(QWidget):
    """Two-panel selector (student / book) plus issue details form."""

    STUDENT_COLUMNS = ["Student ID", "Name", "Class", "Division"]
    BOOK_COLUMNS = ["Title", "Author", "Category", "Available"]

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.selected_student = None
        self.selected_book = None
        self._students = []
        self._books = []
        self.default_due_days = int(utils.get_setting("default_due_days", DEFAULT_SETTINGS["default_due_days"]))
        self._student_debounce = QTimer(self)
        self._student_debounce.setSingleShot(True)
        self._student_debounce.timeout.connect(self._reload_students)
        self._book_debounce = QTimer(self)
        self._book_debounce.setSingleShot(True)
        self._book_debounce.timeout.connect(self._reload_books)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Issue Book")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Select a student and an available book to issue.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        panels = QHBoxLayout()
        panels.setSpacing(16)
        panels.addWidget(self._student_panel(), 1)
        panels.addWidget(self._book_panel(), 1)
        layout.addLayout(panels, 1)

        layout.addWidget(self._details_panel())

    # -- Student panel -----------------------------------------------------

    def _student_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 14, 16, 16)
        v.setSpacing(8)

        header = QLabel("1. Select Student")
        header.setObjectName("sectionTitle")
        v.addWidget(header)

        self.student_search = QLineEdit()
        self.student_search.setPlaceholderText(
            "Search by student ID, name, class, or division"
        )
        self.student_search.textChanged.connect(lambda: self._student_debounce.start(250))
        v.addWidget(self.student_search)

        self.student_table = QTableWidget(0, len(self.STUDENT_COLUMNS))
        self.student_table.setHorizontalHeaderLabels(self.STUDENT_COLUMNS)
        self.student_table.verticalHeader().setVisible(False)
        self.student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.student_table.setSelectionMode(QTableWidget.SingleSelection)
        self.student_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.student_table.itemSelectionChanged.connect(self._on_student_selected)
        v.addWidget(self.student_table)

        self.student_card = QWidget()
        self.student_card.setObjectName("card")
        sc = QVBoxLayout(self.student_card)
        sc.setContentsMargins(14, 10, 14, 10)
        sc.setSpacing(2)
        self.student_card_label = QLabel("No student selected.")
        self.student_card_label.setObjectName("hintLabel")
        self.student_card_label.setWordWrap(True)
        sc.addWidget(self.student_card_label)
        self.student_card.setVisible(False)
        v.addWidget(self.student_card)

        return frame

    # -- Book panel --------------------------------------------------------

    def _book_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 14, 16, 16)
        v.setSpacing(8)

        header = QLabel("2. Select Book")
        header.setObjectName("sectionTitle")
        v.addWidget(header)

        self.book_search = QLineEdit()
        self.book_search.setPlaceholderText(
            "Search by title, author, or category"
        )
        self.book_search.textChanged.connect(lambda: self._book_debounce.start(250))
        v.addWidget(self.book_search)

        self.book_table = QTableWidget(0, len(self.BOOK_COLUMNS))
        self.book_table.setHorizontalHeaderLabels(self.BOOK_COLUMNS)
        self.book_table.verticalHeader().setVisible(False)
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SingleSelection)
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.book_table.itemSelectionChanged.connect(self._on_book_selected)
        v.addWidget(self.book_table)

        self.book_card = QWidget()
        self.book_card.setObjectName("card")
        bc = QVBoxLayout(self.book_card)
        bc.setContentsMargins(14, 10, 14, 10)
        bc.setSpacing(2)
        self.book_card_label = QLabel("No book selected.")
        self.book_card_label.setObjectName("hintLabel")
        self.book_card_label.setWordWrap(True)
        bc.addWidget(self.book_card_label)
        self.book_card.setVisible(False)
        v.addWidget(self.book_card)

        return frame

    # -- Details panel -----------------------------------------------------

    def _details_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 14, 16, 16)
        v.setSpacing(10)

        header = QLabel("3. Issue Details")
        header.setObjectName("sectionTitle")
        v.addWidget(header)

        row = QHBoxLayout()
        row.setSpacing(16)

        issue_box = QVBoxLayout()
        issue_box.addWidget(self._field_label("Issue Date *"))
        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDisplayFormat("yyyy-MM-dd")
        self.issue_date.setDate(QDate.currentDate())
        issue_box.addWidget(self.issue_date)
        row.addLayout(issue_box)

        due_box = QVBoxLayout()
        due_box.addWidget(self._field_label("Due Date *"))
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setDate(QDate.currentDate().addDays(self.default_due_days))
        due_box.addWidget(self.due_date)
        row.addLayout(due_box)

        remarks_box = QVBoxLayout()
        remarks_box.addWidget(self._field_label("Remarks"))
        self.remarks = QLineEdit()
        self.remarks.setPlaceholderText("Optional")
        remarks_box.addWidget(self.remarks)
        row.addLayout(remarks_box, 1)
        v.addLayout(row)

        bottom = QHBoxLayout()
        self.warning_label = QLabel("")
        self.warning_label.setObjectName("hintLabel")
        bottom.addWidget(self.warning_label, 1)
        self.issue_button = theme.make_button("Issue Book", "primary")
        self.issue_button.setEnabled(False)
        self.issue_button.clicked.connect(self._issue)
        bottom.addWidget(self.issue_button)
        v.addLayout(bottom)

        return frame

    def _field_label(self, text) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def set_default_due_days(self, days: int):
        self.default_due_days = int(days)
        self.due_date.setDate(QDate.currentDate().addDays(self.default_due_days))

    # -- Data loading ------------------------------------------------------

    def refresh(self):
        self.selected_student = None
        self.selected_book = None
        self.student_card.setVisible(False)
        self.student_card_label.setText("No student selected.")
        self.book_card.setVisible(False)
        self.book_card_label.setText("No book selected.")
        self._reload_students()
        self._reload_books()
        self._update_issue_enabled()

    def _reload_students(self):
        try:
            students = student_service.get_active_students(self.student_search.text())
        except ServiceError:
            logger.exception("Failed to load students")
            return
        self._students = students
        self.student_table.setRowCount(0)
        for st in students:
            r = self.student_table.rowCount()
            self.student_table.insertRow(r)
            self.student_table.setItem(r, 0, QTableWidgetItem(st.get("student_code") or ""))
            self.student_table.setItem(r, 1, QTableWidgetItem(st.get("name") or ""))
            self.student_table.setItem(r, 2, QTableWidgetItem(st.get("class_name") or ""))
            self.student_table.setItem(r, 3, QTableWidgetItem(st.get("division") or ""))
        self.student_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def _reload_books(self):
        try:
            books = book_service.get_active_available_books(self.book_search.text())
        except ServiceError:
            logger.exception("Failed to load books")
            return
        self._books = books
        self.book_table.setRowCount(0)
        for b in books:
            r = self.book_table.rowCount()
            self.book_table.insertRow(r)
            self.book_table.setItem(r, 0, QTableWidgetItem(b.get("title") or ""))
            self.book_table.setItem(r, 1, QTableWidgetItem(b.get("author") or ""))
            self.book_table.setItem(r, 2, QTableWidgetItem(b.get("category") or ""))
            self.book_table.setItem(
                r, 3, QTableWidgetItem(str(b.get("available_quantity", 0)))
            )
        self.book_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

    # -- Selection handlers ------------------------------------------------

    def _on_student_selected(self):
        row = self.student_table.currentRow()
        if row < 0 or row >= len(self._students):
            self.selected_student = None
            self.student_card.setVisible(False)
            self._update_issue_enabled()
            return
        self.selected_student = self._students[row]
        st = self.selected_student
        try:
            pending = student_service.get_pending_count(st["id"])
        except ServiceError:
            logger.exception("Failed to load pending count")
            pending = "?"
        self.student_card_label.setText(
            f"Name: {st.get('name')}\n"
            f"ID: {st.get('student_code')}\n"
            f"Class: {st.get('class_name') or '-'}  "
            f"Division: {st.get('division') or '-'}\n"
            f"Pending Books: {pending}"
        )
        self.student_card.setVisible(True)
        self._update_issue_enabled()

    def _on_book_selected(self):
        row = self.book_table.currentRow()
        if row < 0 or row >= len(self._books):
            self.selected_book = None
            self.book_card.setVisible(False)
            self._update_issue_enabled()
            return
        self.selected_book = self._books[row]
        b = self.selected_book
        self.book_card_label.setText(
            f"Title: {b.get('title')}\n"
            f"Author: {b.get('author') or '-'}\n"
            f"Category: {b.get('category') or '-'}\n"
            f"Available: {b.get('available_quantity', 0)}"
        )
        self.book_card.setVisible(True)
        self._update_issue_enabled()

    def _update_issue_enabled(self):
        reasons = []
        if self.selected_student is None:
            reasons.append("select a student")
        if self.selected_book is None:
            reasons.append("select a book")
        elif self.selected_book.get("available_quantity", 0) <= 0:
            reasons.append("book is not available")
        can_issue = not reasons
        self.issue_button.setEnabled(can_issue)
        self.warning_label.setText(
            "" if can_issue else "Please " + " and ".join(reasons) + "."
        )

    # -- Issue action ------------------------------------------------------

    def _issue(self):
        if self.selected_student is None or self.selected_book is None:
            return
        issue_date = self.issue_date.date().toString("yyyy-MM-dd")
        due_date = self.due_date.date().toString("yyyy-MM-dd")
        try:
            issue_service.issue_book(
                self.selected_student["id"],
                self.selected_book["id"],
                issue_date,
                due_date,
                self.remarks.text(),
            )
            theme.show_success(self, "Book issued successfully.")
            self.remarks.clear()
            self.main_window.refresh_all()
            self.refresh()
        except ServiceError as exc:
            theme.show_error(self, str(exc))
