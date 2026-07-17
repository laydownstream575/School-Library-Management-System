"""Dashboard page: headline statistics and recent activity."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app import utils
from app.config import COLORS
from services import ServiceError, report_service
from ui import theme


class DashboardPage(QWidget):
    """First screen after startup. Reloads its data via ``refresh()``."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()
        self.refresh()

    # -- UI construction ---------------------------------------------------
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Dashboard")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Manage and monitor library activity.")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Statistic cards
        self.cards = {}
        card_defs = [
            ("total_books", "Total Books", COLORS["primary"]),
            ("available_books", "Available Books", COLORS["secondary"]),
            ("issued_books", "Issued Books", COLORS["primary"]),
            ("total_students", "Total Students", COLORS["text_primary"]),
            ("pending_returns", "Pending Returns", COLORS["warning"]),
            ("overdue_books", "Overdue Books", COLORS["danger"]),
            ("low_stock_books", "Low Stock Books", COLORS["warning"]),
        ]
        grid = QGridLayout()
        grid.setSpacing(14)
        for index, (key, label, accent) in enumerate(card_defs):
            card = theme.StatCard(label, "0", accent)
            self.cards[key] = card
            grid.addWidget(card, index // 4, index % 4)
        layout.addLayout(grid)

        # Recent activity tables side by side
        tables_row = QHBoxLayout()
        tables_row.setSpacing(16)

        tables_row.addWidget(self._recent_issues_block(), 1)
        tables_row.addWidget(self._recent_returns_block(), 1)
        layout.addLayout(tables_row)
        layout.addStretch()

    def _recent_issues_block(self) -> QWidget:
        block = QWidget()
        v = QVBoxLayout(block)
        v.setContentsMargins(0, 8, 0, 0)
        header = QLabel("Recent Issues")
        header.setObjectName("sectionTitle")
        v.addWidget(header)
        self.issues_table = self._make_table(
            ["Student", "Book", "Issue Date", "Due Date", "Status"]
        )
        v.addWidget(self.issues_table)
        return block

    def _recent_returns_block(self) -> QWidget:
        block = QWidget()
        v = QVBoxLayout(block)
        v.setContentsMargins(0, 8, 0, 0)
        header = QLabel("Recent Returns")
        header.setObjectName("sectionTitle")
        v.addWidget(header)
        self.returns_table = self._make_table(
            ["Student", "Book", "Issue Date", "Return Date"]
        )
        v.addWidget(self.returns_table)
        return block

    def _make_table(self, headers) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(220)
        return table

    # -- Data --------------------------------------------------------------
    def refresh(self):
        """Reload all dashboard data from the database."""
        try:
            summary = report_service.dashboard_summary()
            for key, card in self.cards.items():
                card.set_value(summary.get(key, 0))

            issues = report_service.recent_issues()
            self._fill_table(
                self.issues_table,
                issues,
                lambda r: [
                    r.get("student_name", ""),
                    r.get("book_title", ""),
                    utils.format_display_date(r.get("issue_date")),
                    utils.format_display_date(r.get("due_date")),
                    r.get("status", ""),
                ],
                empty_text="No issues recorded yet.",
            )

            returns = report_service.recent_returns()
            self._fill_table(
                self.returns_table,
                returns,
                lambda r: [
                    r.get("student_name", ""),
                    r.get("book_title", ""),
                    utils.format_display_date(r.get("issue_date")),
                    utils.format_display_date(r.get("return_date")),
                ],
                empty_text="No returns recorded yet.",
            )
        except ServiceError:
            pass  # keep previous values visible

    def _fill_table(self, table, rows, row_mapper, empty_text):
        table.setRowCount(0)
        if not rows:
            table.setRowCount(1)
            item = QTableWidgetItem(empty_text)
            item.setForeground(Qt.gray)
            table.setSpan(0, 0, 1, table.columnCount())
            table.setItem(0, 0, item)
            return
        for row in rows:
            values = row_mapper(row)
            r = table.rowCount()
            table.insertRow(r)
            for col, value in enumerate(values):
                table.setItem(r, col, QTableWidgetItem(str(value)))
