"""Return Book page: search pending issues, select one, and return it."""

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
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
from services import ServiceError, issue_service
from ui import theme


class ReturnBookPage(QWidget):
    """Pending returns table + selected issue detail + return form."""

    COLUMNS = [
        "Issue ID", "Student Code", "Student Name", "Book Title",
        "Issue Date", "Due Date", "Overdue Days", "Status", "Action",
    ]

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.selected_issue = None
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Return Book")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Search pending returns and record book returns.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Student ID, Student Name, or Book Title")
        self.search_input.textChanged.connect(self.refresh)
        layout.addWidget(self.search_input)

        self.table = QTableWidget(0, len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(64)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Fixed)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        header.setSectionResizeMode(8, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(6, 140)
        self.table.setColumnWidth(7, 130)
        self.table.setColumnWidth(8, 150)
        self.table.itemSelectionChanged.connect(self._on_selected)
        layout.addWidget(self.table, 1)

        self.status_label = QLabel("")
        self.status_label.setObjectName("hintLabel")
        layout.addWidget(self.status_label)

        layout.addWidget(self._detail_panel())

    def _detail_panel(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        v = QVBoxLayout(frame)
        v.setContentsMargins(16, 14, 16, 16)
        v.setSpacing(10)

        header = QLabel("Return Details")
        header.setObjectName("sectionTitle")
        v.addWidget(header)

        info_grid = QHBoxLayout()
        info_grid.setSpacing(24)

        left = QVBoxLayout()
        left.setSpacing(4)
        self.detail_student = QLabel("Student: —")
        self.detail_student.setObjectName("fieldLabel")
        self.detail_book = QLabel("Book: —")
        self.detail_book.setObjectName("fieldLabel")
        left.addWidget(self.detail_student)
        left.addWidget(self.detail_book)
        info_grid.addLayout(left)

        right = QVBoxLayout()
        right.setSpacing(4)
        self.detail_issue_date = QLabel("Issue Date: —")
        self.detail_issue_date.setObjectName("fieldLabel")
        self.detail_due_date = QLabel("Due Date: —")
        self.detail_due_date.setObjectName("fieldLabel")
        right.addWidget(self.detail_issue_date)
        right.addWidget(self.detail_due_date)
        info_grid.addLayout(right)

        v.addLayout(info_grid)

        form_row = QHBoxLayout()
        form_row.setSpacing(16)

        date_box = QVBoxLayout()
        date_box.addWidget(self._field_label("Return Date *"))
        self.return_date = QDateEdit()
        self.return_date.setCalendarPopup(True)
        self.return_date.setDisplayFormat("yyyy-MM-dd")
        self.return_date.setDate(QDate.currentDate())
        date_box.addWidget(self.return_date)
        form_row.addLayout(date_box)

        remarks_box = QVBoxLayout()
        remarks_box.addWidget(self._field_label("Remarks"))
        self.remarks_input = QLineEdit()
        self.remarks_input.setPlaceholderText("Optional")
        remarks_box.addWidget(self.remarks_input)
        form_row.addLayout(remarks_box, 1)

        v.addLayout(form_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.return_button = theme.make_button("Return Book", "primary")
        self.return_button.setEnabled(False)
        self.return_button.clicked.connect(self._return)
        btn_row.addWidget(self.return_button)
        v.addLayout(btn_row)

        return frame

    def _field_label(self, text) -> QLabel:
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        return label

    def refresh(self):
        self.selected_issue = None
        self.return_button.setEnabled(False)
        self._clear_detail()
        rows = issue_service.get_pending_returns(self.search_input.text())
        self._rows = rows
        self.table.setRowCount(0)
        for rec in rows:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setRowHeight(r, 64)
            overdue = rec.get("overdue_days", 0)
            values = [
                str(rec.get("issue_id")),
                rec.get("student_code") or "",
                rec.get("student_name") or "",
                rec.get("book_title") or "",
                utils.format_display_date(rec.get("issue_date")),
                utils.format_display_date(rec.get("due_date")),
                str(overdue) if overdue else "-",
            ]
            for col, value in enumerate(values):
                item = self._centered_item(value)
                if col == 6 and overdue > 0:
                    item.setForeground(QColor("#991B1B"))
                self.table.setItem(r, col, item)
            badge = "OVERDUE" if overdue > 0 else "ISSUED"
            self.table.setCellWidget(r, 7, theme.badge_in_cell(badge))
            self.table.setCellWidget(r, 8, self._return_action_cell(rec))
            if overdue > 0:
                for col in range(7):
                    cell = self.table.item(r, col)
                    if cell:
                        cell.setBackground(QColor("#FEF2F2"))
        self._fix_column_widths()
        self.status_label.setText(
            "No pending returns. All issued books are returned."
            if not rows else f"{len(rows)} pending return(s)."
        )

    def _fix_column_widths(self):
        h = self.table.horizontalHeader()
        h.setSectionResizeMode(3, QHeaderView.Stretch)
        fixed = ((1, 140), (2, 180), (6, 140), (7, 130), (8, 150))
        for col, width in fixed:
            h.setSectionResizeMode(col, QHeaderView.Fixed)
            if h.sectionSize(col) < width:
                self.table.setColumnWidth(col, width)

    @staticmethod
    def _centered_item(text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        return item

    def _return_action_cell(self, rec) -> QWidget:
        container = QWidget()
        row = QHBoxLayout(container)
        row.setContentsMargins(8, 8, 8, 8)
        row.setAlignment(Qt.AlignCenter)
        btn = theme.make_button("Return", "primary")
        btn.setMinimumHeight(38)
        btn.setMinimumWidth(100)
        btn.clicked.connect(lambda _=False, r=rec: self._select_and_return(r))
        row.addWidget(btn)
        return container

    def _select_and_return(self, rec):
        for r in range(self.table.rowCount()):
            if self.table.item(r, 0) and self.table.item(r, 0).text() == str(rec.get("issue_id")):
                self.table.selectRow(r)
                break

    def _on_selected(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._rows):
            self.selected_issue = None
            self.return_button.setEnabled(False)
            self._clear_detail()
            return
        self.selected_issue = self._rows[row]
        self.return_button.setEnabled(True)
        rec = self.selected_issue
        overdue = rec.get("overdue_days", 0)
        overdue_text = f" (Overdue by {overdue} day{'s' if overdue != 1 else ''})" if overdue else ""
        self.detail_student.setText(f"Student: {rec.get('student_name')} ({rec.get('student_code')})")
        self.detail_book.setText(f"Book: {rec.get('book_title')}")
        self.detail_issue_date.setText(f"Issue Date: {utils.format_display_date(rec.get('issue_date'))}")
        self.detail_due_date.setText(f"Due Date: {utils.format_display_date(rec.get('due_date'))}{overdue_text}")

    def _clear_detail(self):
        self.detail_student.setText("Student: —")
        self.detail_book.setText("Book: —")
        self.detail_issue_date.setText("Issue Date: —")
        self.detail_due_date.setText("Due Date: —")

    def _return(self):
        if self.selected_issue is None:
            return
        return_date = self.return_date.date().toString("yyyy-MM-dd")
        remarks = self.remarks_input.text().strip() or None
        try:
            issue_service.return_book(
                self.selected_issue["issue_id"], return_date, remarks
            )
            theme.show_success(self, "Book returned successfully.")
            self.remarks_input.clear()
            self.main_window.refresh_all()
            self.selected_issue = None
            self.return_button.setEnabled(False)
            self._clear_detail()
            self.table.clearSelection()
            self.refresh()
        except ServiceError as exc:
            theme.show_error(self, str(exc))
