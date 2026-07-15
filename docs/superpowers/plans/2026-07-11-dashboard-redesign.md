# Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign dashboard (sidebar, top bar, dashboard page) to match reference image using PySide6.

**Architecture:** Three UI files modified. Sidebar/top bar in `main_window.py`, reusable widgets in `theme.py`, dashboard content in `dashboard.py`. Zero business logic changes.

**Tech Stack:** PySide6 (Qt6), QPainter for charts, Unicode for icons.

## Global Constraints

- No changes to database, services, validators, or non-UI code.
- All navigation callbacks (`_select_page`, `navigate()`) must remain identical.
- All data sources (`report_service.dashboard_summary()`, `recent_issues()`, `recent_returns()`) must remain identical.
- No external icon or chart libraries.
- No new database tables or columns.

---

### Task 1: Sidebar Redesign (main_window.py)

**Files:**
- Modify: `ui/main_window.py` — full rewrite of `_build_sidebar()`

**Interfaces:**
- Consumes: `LogoLabel` from `theme.py`, `config.APP_VERSION`
- Produces: Sidebar with dark navy bg, nav icons, decorative bottom panel

- [ ] **Step 1: Rewrite imports and color constants**

Add at the top of `main_window.py`:
```python
SIDEBAR_BG = "#071C43"
SIDEBAR_SECONDARY = "#0B2858"
NAV_ACTIVE_BG = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #246BFD, stop:1 #1556D8)"
```

- [ ] **Step 2: Rewrite `_build_sidebar()` with navy colors, nav icons, decorative panel**

```python
def _build_sidebar(self) -> QWidget:
    sidebar = QFrame()
    sidebar.setObjectName("sidebar")
    sidebar.setFixedWidth(240)
    sidebar.setStyleSheet(f"background: {SIDEBAR_BG};")

    layout = QVBoxLayout(sidebar)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Brand area
    logo = LogoLabel(56)
    layout.addWidget(logo, alignment=Qt.AlignCenter)

    brand = QLabel("School Library")
    brand.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 700; padding: 8px 18px 0;")
    brand.setAlignment(Qt.AlignCenter)
    layout.addWidget(brand)

    sub = QLabel("Management System")
    sub.setStyleSheet("color: #9CA3AF; font-size: 12px; padding: 2px 18px 12px;")
    sub.setAlignment(Qt.AlignCenter)
    layout.addWidget(sub)

    # Decorative divider
    divider = QFrame()
    divider.setFrameShape(QFrame.HLine)
    divider.setStyleSheet("background: #1E3A6F; max-height: 1px; margin: 4px 18px;")
    layout.addWidget(divider)

    # Navigation buttons
    self.nav_group = QButtonGroup(self)
    self.nav_group.setExclusive(True)
    nav_icons = {
        "Dashboard": "◆",
        "Books Management": "📚",
        "Student Management": "👥",
        "Issue Book": "📖",
        "Return Book": "↩",
        "Reports": "📊",
        "Settings": "⚙",
    }
    for index, (label, _) in enumerate(NAV_ITEMS):
        btn_text = f"  {nav_icons.get(label, '•')}  {label}"
        button = QPushButton(btn_text)
        button.setObjectName("navButton")
        button.setCheckable(True)
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet(
            f"""
            QPushButton#navButton {{
                color: #B0BEC5; background: transparent; border: none;
                text-align: left; padding: 11px 18px; font-size: 13px;
                margin: 2px 10px; border-radius: 8px;
            }}
            QPushButton#navButton:hover {{
                background: #0F2D5E; color: #FFFFFF;
            }}
            QPushButton#navButton:checked {{
                background: {NAV_ACTIVE_BG}; color: #FFFFFF; font-weight: 600;
            }}
            """
        )
        button.clicked.connect(lambda _=False, i=index: self._select_page(i))
        self.nav_group.addButton(button, index)
        layout.addWidget(button)

    layout.addStretch()

    # Decorative info card (visual-only)
    info_card = QFrame()
    info_card.setStyleSheet(
        f"background: {SIDEBAR_SECONDARY}; border-radius: 10px; "
        "margin: 10px 14px; padding: 14px;"
    )
    info_layout = QVBoxLayout(info_card)
    info_layout.setContentsMargins(12, 10, 12, 10)
    info_layout.setSpacing(4)
    info_title = QLabel("📖 Library Assistant")
    info_title.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 600; background: transparent;")
    info_layout.addWidget(info_title)
    info_text = QLabel("Manage your library resources efficiently.")
    info_text.setStyleSheet("color: #9CA3AF; font-size: 11px; background: transparent;")
    info_text.setWordWrap(True)
    info_layout.addWidget(info_text)
    layout.addWidget(info_card)

    version = QLabel(f"Version {config.APP_VERSION}")
    version.setStyleSheet("color: #6B7280; font-size: 11px; padding: 12px 18px;")
    layout.addWidget(version)

    return sidebar
```

- [ ] **Step 3: Compile and verify**

```bash
python -m py_compile "ui/main_window.py"
```

---

### Task 2: Top Bar Redesign (main_window.py)

**Files:**
- Modify: `ui/main_window.py` — rewrite `_build_top_bar()` and `_refresh_top_bar()`

- [ ] **Step 1: Rewrite `_build_top_bar()`**

```python
def _build_top_bar(self) -> QWidget:
    bar = QFrame()
    bar.setObjectName("topBar")
    bar.setFixedHeight(64)
    bar.setStyleSheet("background: #FFFFFF; border-bottom: 1px solid #E3EAF5;")
    layout = QHBoxLayout(bar)
    layout.setContentsMargins(24, 0, 24, 0)

    # Search field (visual placeholder)
    search = QLineEdit()
    search.setPlaceholderText("Search books, students, issues...")
    search.setStyleSheet(
        "background: #F6F9FE; border: 1px solid #E3EAF5; border-radius: 8px; "
        "padding: 8px 14px; font-size: 13px; min-width: 280px; max-width: 380px;"
    )
    layout.addWidget(search)

    layout.addStretch()

    # Notification bell + badge
    notif_container = QWidget()
    notif_layout = QHBoxLayout(notif_container)
    notif_layout.setContentsMargins(0, 0, 0, 0)
    notif_layout.setSpacing(4)

    notif_bell = QLabel("🔔")
    notif_bell.setStyleSheet("font-size: 20px;")
    notif_layout.addWidget(notif_bell)

    badge = QLabel("3")
    badge.setStyleSheet(
        "background: #EF4444; color: #FFFFFF; border-radius: 8px; "
        "font-size: 10px; font-weight: 700; padding: 2px 6px; min-width: 16px;"
    )
    badge.setAlignment(Qt.AlignCenter)
    notif_layout.addWidget(badge)

    layout.addWidget(notif_container)

    # Separator
    sep = QLabel("|")
    sep.setStyleSheet("color: #E3EAF5; padding: 0 8px;")
    layout.addWidget(sep)

    # Logo thumbnail
    logo_small = LogoLabel(36)
    layout.addWidget(logo_small)

    # School name + date
    school = utils.get_setting("school_name", "DVNS")
    library = utils.get_setting("library_name", "School Library")
    school_text = f"{school} · {library}"
    self.top_right = QLabel()
    self.top_right.setTextFormat(Qt.RichText)
    self.top_right.setStyleSheet("color: #10234A; font-size: 13px; font-weight: 600;")
    layout.addWidget(self.top_right)

    self._refresh_top_bar()

    return bar
```

- [ ] **Step 2: Update `_refresh_top_bar()`**

```python
def _refresh_top_bar(self):
    school = utils.get_setting("school_name", "DVNS")
    library = utils.get_setting("library_name", "School Library")
    today = utils.format_display_date(utils.today_str())
    self.top_right.setText(
        f'<div style="text-align:right">'
        f'<span style="font-weight:600">{school} · {library}</span><br>'
        f'<span style="font-size:11px;color:#6B7894">{today}</span>'
        f'</div>'
    )
```

- [ ] **Step 3: Add QLineEdit to imports**

In the import block at the top of main_window.py, ensure `QLineEdit` is imported from `PySide6.QtWidgets`.

- [ ] **Step 4: Compile and verify**

```bash
python -m py_compile "ui/main_window.py"
```

---

### Task 3: Reusable Dashboard Widgets (theme.py)

**Files:**
- Modify: `ui/theme.py` — add `DashboardCard`, `ActionButton`, `DonutChart`, `LineChart`

- [ ] **Step 1: Add `DashboardCard` widget**

```python
class DashboardCard(QFrame):
    """A stat card with icon circle, label, value, and description."""

    def __init__(self, icon: str, label: str, value: str = "0",
                 description: str = "", accent: str = "#246BFD", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumSize(180, 130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet(
            "DashboardCard#card {"
            "  background: #FFFFFF; border: 1px solid #E3EAF5;"
            "  border-radius: 14px; padding: 16px;"
            "}"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        # Icon circle
        icon_container = QLabel(icon)
        icon_container.setFixedSize(48, 48)
        icon_container.setAlignment(Qt.AlignCenter)
        icon_container.setStyleSheet(
            f"background: {accent}15; color: {accent};"
            "font-size: 22px; border-radius: 24px; font-weight: 700;"
        )
        layout.addWidget(icon_container)

        # Text area
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self.label_widget = QLabel(label)
        self.label_widget.setStyleSheet("color: #6B7894; font-size: 13px; background: transparent;")
        text_col.addWidget(self.label_widget)

        self.value_widget = QLabel(str(value))
        self.value_widget.setStyleSheet(f"color: {accent}; font-size: 28px; font-weight: 700; background: transparent;")
        text_col.addWidget(self.value_widget)

        self.desc_widget = QLabel(description)
        self.desc_widget.setStyleSheet("color: #9CA3AF; font-size: 11px; background: transparent;")
        text_col.addWidget(self.desc_widget)

        layout.addLayout(text_col)
        layout.addStretch()

    def set_value(self, value):
        self.value_widget.setText(str(value))
```

- [ ] **Step 2: Add `ActionButton` widget**

```python
class ActionButton(QPushButton):
    """Compact action button with icon and label for Quick Actions."""

    def __init__(self, icon: str, label: str, accent: str = "#246BFD", parent=None):
        super().__init__(parent)
        self.setText(f"{icon}  {label}")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(110, 52)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background: #FFFFFF; border: 1px solid #E3EAF5;
                border-radius: 10px; color: #10234A; font-size: 13px;
                font-weight: 600; text-align: left; padding: 10px 14px;
            }}
            QPushButton:hover {{
                background: #F6F9FE; border-color: {accent};
            }}
            QPushButton:pressed {{
                background: #EEF2F8;
            }}
            """
        )
```

- [ ] **Step 3: Add `DonutChart` widget**

```python
class DonutChart(QWidget):
    """A simple donut chart rendered with QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)
        self.segments = []

    def set_data(self, segments: list):
        """segments: list of (label, value, color) tuples"""
        self.segments = segments
        self.update()

    def paintEvent(self, event):
        if not self.segments:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        total = sum(s[1] for s in self.segments) or 1
        rect = self.rect().adjusted(10, 10, -10, -10)
        side = min(rect.width(), rect.height())
        chart_rect = QRectF(0, 0, side * 0.7, side * 0.7)
        chart_rect.moveCenter(rect.center() - QPointF(0, 20))

        start_angle = 90 * 16
        pen = QPen()
        pen.setWidth(28)
        for label, value, color in self.segments:
            span = int(360 * value / total * 16)
            if span == 0:
                continue
            pen.setColor(QColor(color))
            painter.setPen(pen)
            painter.drawArc(chart_rect, start_angle, -span)
            start_angle -= span

        painter.end()
```

- [ ] **Step 4: Add `LineChart` widget (stub)**

```python
class LineChart(QWidget):
    """Placeholder line chart showing a fallback message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 160)
        self.setStyleSheet("background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor("#9CA3AF"))
        painter.setFont(QFont("Segoe UI", 12))
        painter.drawText(self.rect(), Qt.AlignCenter, "No monthly trend data available")
        painter.end()

    def set_data(self, data: list):
        pass
```

- [ ] **Step 5: Add imports to theme.py**

At the top of `theme.py`, add:
```python
from PySide6.QtGui import QFont, QPainter, QPen, QColor
from PySide6.QtCore import QRectF, QPointF
```

- [ ] **Step 6: Compile and verify**

```bash
python -m py_compile "ui/theme.py"
```

---

### Task 4: Dashboard Page Rewrite (dashboard.py)

**Files:**
- Rewrite: `ui/dashboard.py` — full rewrite keeping `refresh()` + `report_service` calls identical

- [ ] **Step 1: Write the full dashboard.py**

```python
"""Dashboard page: headline statistics, recent activity, and charts."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget,
)

from app import utils
from services import report_service
from ui.theme import (
    ActionButton, DashboardCard, DonutChart, LineChart,
    LogoLabel, make_badge,
)


# Accent colors per stat card
_CARD_ACCENTS = {
    "total_books": "#7657F6",
    "available_books": "#22B96B",
    "issued_books": "#246BFD",
    "total_students": "#FF9800",
    "pending_returns": "#FF9800",
    "overdue_books": "#EF4444",
    "low_stock_books": "#16A9D5",
}

_CARD_ICONS = {
    "total_books": "📚",
    "available_books": "✅",
    "issued_books": "📖",
    "total_students": "👥",
    "pending_returns": "⏳",
    "overdue_books": "⚠️",
    "low_stock_books": "📦",
}

_CARD_DESCRIPTIONS = {
    "total_books": "All books in library",
    "available_books": "Ready to issue",
    "issued_books": "Currently issued",
    "total_students": "Registered students",
    "pending_returns": "Books to be returned",
    "overdue_books": "Past due date",
    "low_stock_books": "Need more copies",
}

STATUS_BADGE_COLORS = {
    "ISSUED": ("#22B96B", "#FFFFFF"),
    "RETURNED": ("#246BFD", "#FFFFFF"),
    "OVERDUE": ("#EF4444", "#FFFFFF"),
    "LOST": ("#FF9800", "#FFFFFF"),
    "DAMAGED": ("#FF9800", "#FFFFFF"),
}


class DashboardPage(QWidget):
    """First screen after startup. Reloads its data via ``refresh()``."""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.setStyleSheet("background: #F6F9FE;")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        outer.addWidget(scroll)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(20)

        # Welcome area
        layout.addWidget(self._build_welcome())

        # Stat cards (8 items: 7 stats + 1 quick actions)
        layout.addWidget(self._build_stat_grid())

        # Quick actions card
        layout.addWidget(self._build_quick_actions())

        # Tables row
        tables_row = QHBoxLayout()
        tables_row.setSpacing(18)
        tables_row.addWidget(self._build_table_block(
            "Recent Issues", self.issues_table := self._make_table(
                ["Student", "Book", "Issue Date", "Due Date", "Status"]
            ), "issues"
        ), 1)
        tables_row.addWidget(self._build_table_block(
            "Recent Returns", self.returns_table := self._make_table(
                ["Student", "Book", "Issue Date", "Return Date"]
            ), "returns"
        ), 1)
        layout.addLayout(tables_row)

        # Bottom row: charts + notice
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(18)
        bottom_row.addWidget(self._build_chart_card("Books Overview", self.donut := DonutChart()), 1)
        bottom_row.addWidget(self._build_chart_card("Monthly Issue Trend", self.line := LineChart()), 1)
        bottom_row.addWidget(self._build_notice_board(), 1)
        layout.addLayout(bottom_row)

        layout.addStretch()

    def _build_welcome(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        left = QVBoxLayout()
        left.setSpacing(4)
        title = QLabel("Welcome back! 📚")
        title.setStyleSheet("font-size: 26px; font-weight: 700; color: #10234A; background: transparent;")
        left.addWidget(title)
        subtitle = QLabel("Here's what's happening in your library today.")
        subtitle.setStyleSheet("font-size: 14px; color: #6B7894; background: transparent;")
        left.addWidget(subtitle)
        layout.addLayout(left)
        layout.addStretch()

        # Date card
        date_card = QFrame()
        date_card.setStyleSheet(
            "background: #FFFFFF; border: 1px solid #E3EAF5; border-radius: 12px; padding: 14px 20px;"
        )
        date_layout = QHBoxLayout(date_card)
        date_layout.setContentsMargins(16, 10, 16, 10)
        date_layout.setSpacing(12)
        cal = QLabel("📅")
        cal.setStyleSheet("font-size: 28px; background: transparent;")
        date_layout.addWidget(cal)
        date_text = QVBoxLayout()
        date_text.setSpacing(2)
        day = QLabel(utils.format_display_date(utils.today_str()))
        day.setStyleSheet("font-size: 15px; font-weight: 600; color: #10234A; background: transparent;")
        date_text.addWidget(day)
        msg = QLabel("Good day for learning!")
        msg.setStyleSheet("font-size: 12px; color: #9CA3AF; background: transparent;")
        date_text.addWidget(msg)
        date_layout.addLayout(date_text)
        layout.addWidget(date_card)

        return container

    def _build_stat_grid(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        grid = QGridLayout(container)
        grid.setSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)

        self.cards = {}
        card_defs = [
            "total_books", "available_books", "issued_books", "total_students",
            "pending_returns", "overdue_books", "low_stock_books",
        ]
        for idx, key in enumerate(card_defs):
            card = DashboardCard(
                icon=_CARD_ICONS.get(key, "📊"),
                label=key.replace("_", " ").title(),
                value="0",
                description=_CARD_DESCRIPTIONS.get(key, ""),
                accent=_CARD_ACCENTS.get(key, "#246BFD"),
            )
            self.cards[key] = card
            grid.addWidget(card, idx // 4, idx % 4)

        return container

    def _build_quick_actions(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #FFFFFF; border: 1px solid #E3EAF5; border-radius: 14px; padding: 16px; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        header = QLabel("Quick Actions")
        header.setStyleSheet("font-size: 15px; font-weight: 600; color: #10234A; background: transparent;")
        layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(10)
        actions = [
            ("📖", "Issue Book", "#246BFD", 3),
            ("↩", "Return Book", "#22B96B", 4),
            ("➕", "Add Book", "#7657F6", 1),
            ("👤", "Add Student", "#FF9800", 2),
        ]
        for i, (icon, label, accent, nav_idx) in enumerate(actions):
            btn = ActionButton(icon, label, accent)
            btn.clicked.connect(lambda _=False, idx=nav_idx: self.main_window.navigate(idx))
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        return card

    def _build_table_block(self, title: str, table: QTableWidget, view_key: str) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #FFFFFF; border: 1px solid #E3EAF5; border-radius: 14px; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)

        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(18, 14, 14, 8)
        header_label = QLabel(title)
        header_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #10234A; background: transparent;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        view_all = QPushButton("View All")
        view_all.setStyleSheet(
            "QPushButton { color: #246BFD; font-size: 12px; font-weight: 600; "
            "background: transparent; border: none; padding: 4px 8px; }"
            "QPushButton:hover { color: #1556D8; }"
        )
        view_all.clicked.connect(lambda: self.main_window.navigate(5))
        header_layout.addWidget(view_all)
        layout.addWidget(header_widget)

        layout.addWidget(table)
        return card

    def _make_table(self, headers) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionMode(QTableWidget.NoSelection)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setMinimumHeight(220)
        table.setStyleSheet(
            "QTableWidget { background: transparent; border: none; border-radius: 0 0 14px 14px; "
            "gridline-color: #F1F5F9; }"
            "QHeaderView::section { background: #F6F9FE; color: #6B7894; padding: 10px 12px; "
            "border: none; font-weight: 600; font-size: 12px; text-align: center; }"
            "QTableWidget::item { padding: 8px 12px; border: none; "
            "border-bottom: 1px solid #F1F5F9; min-height: 28px; }"
            "QTableView { alternate-background-color: #FAFCFE; outline: none; }"
        )
        return table

    def _build_chart_card(self, title: str, chart_widget) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #FFFFFF; border: 1px solid #E3EAF5; border-radius: 14px; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)
        label = QLabel(title)
        label.setStyleSheet("font-size: 15px; font-weight: 600; color: #10234A; background: transparent;")
        layout.addWidget(label)
        layout.addWidget(chart_widget)
        return card

    def _build_notice_board(self) -> QWidget:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background: #FFFFFF; border: 1px solid #E3EAF5; border-radius: 14px; }"
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)
        label = QLabel("Notice Board")
        label.setStyleSheet("font-size: 15px; font-weight: 600; color: #10234A; background: transparent;")
        layout.addWidget(label)

        notices = [
            ("🕐", "Library Timings", "Mon–Fri: 8:00 AM – 5:00 PM"),
            ("📅", "Book Return Reminder", "Return books within 7 days"),
        ]
        for icon, n_title, desc in notices:
            item = QFrame()
            item.setStyleSheet(
                "QFrame { background: #F6F9FE; border-radius: 10px; padding: 12px; }"
            )
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(12, 10, 12, 10)
            item_layout.setSpacing(12)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px; background: transparent;")
            item_layout.addWidget(icon_lbl)
            text_layout = QVBoxLayout()
            text_layout.setSpacing(2)
            t = QLabel(n_title)
            t.setStyleSheet("font-size: 13px; font-weight: 600; color: #10234A; background: transparent;")
            text_layout.addWidget(t)
            d = QLabel(desc)
            d.setStyleSheet("font-size: 12px; color: #6B7894; background: transparent;")
            text_layout.addWidget(d)
            item_layout.addLayout(text_layout)
            item_layout.addStretch()
            layout.addWidget(item)

        layout.addStretch()
        return card

    def refresh(self):
        summary = report_service.dashboard_summary()
        for key, card in self.cards.items():
            card.set_value(summary.get(key, 0))

        issues = report_service.recent_issues()
        self._fill_issues_table(issues)

        returns = report_service.recent_returns()
        self._fill_returns_table(returns)

        # Donut chart data
        total = summary.get("total_books", 0)
        available = summary.get("available_books", 0)
        issued = summary.get("issued_books", 0)
        other = max(0, total - available - issued)
        segments = []
        if available:
            segments.append(("Available", available, "#22B96B"))
        if issued:
            segments.append(("Issued", issued, "#246BFD"))
        if other:
            segments.append(("Other", other, "#7657F6"))
        if not segments:
            segments.append(("No Data", 1, "#E3EAF5"))
        self.donut.set_data(segments)

    def _fill_issues_table(self, rows):
        self.issues_table.setRowCount(0)
        if not rows:
            self.issues_table.setRowCount(1)
            item = QTableWidgetItem("No issues recorded yet.")
            item.setForeground(Qt.gray)
            self.issues_table.setSpan(0, 0, 1, self.issues_table.columnCount())
            self.issues_table.setItem(0, 0, item)
            return
        for row in rows:
            r = self.issues_table.rowCount()
            self.issues_table.insertRow(r)
            self.issues_table.setItem(r, 0, QTableWidgetItem(row.get("student_name", "")))
            self.issues_table.setItem(r, 1, QTableWidgetItem(row.get("book_title", "")))
            self.issues_table.setItem(r, 2, QTableWidgetItem(utils.format_display_date(row.get("issue_date"))))
            self.issues_table.setItem(r, 3, QTableWidgetItem(utils.format_display_date(row.get("due_date"))))
            status = row.get("status", "")
            badge = make_badge(status, STATUS_BADGE_COLORS)
            self.issues_table.setCellWidget(r, 4, badge)

    def _fill_returns_table(self, rows):
        self.returns_table.setRowCount(0)
        if not rows:
            self.returns_table.setRowCount(1)
            item = QTableWidgetItem("No returns recorded yet.")
            item.setForeground(Qt.gray)
            self.returns_table.setSpan(0, 0, 1, self.returns_table.columnCount())
            self.returns_table.setItem(0, 0, item)
            return
        for row in rows:
            r = self.returns_table.rowCount()
            self.returns_table.insertRow(r)
            self.returns_table.setItem(r, 0, QTableWidgetItem(row.get("student_name", "")))
            self.returns_table.setItem(r, 1, QTableWidgetItem(row.get("book_title", "")))
            self.returns_table.setItem(r, 2, QTableWidgetItem(utils.format_display_date(row.get("issue_date"))))
            self.returns_table.setItem(r, 3, QTableWidgetItem(utils.format_display_date(row.get("return_date"))))
```

- [ ] **Step 2: Update `make_badge` in theme.py to support custom colors**

Modify `make_badge()` to accept an optional `colors` tuple override:
```python
def make_badge(text: str, colors: tuple = None) -> QLabel:
    label = QLabel(text)
    label.setAlignment(Qt.AlignCenter)
    label.setStyleSheet(
        f"color: {colors[1] if colors else '#FFFFFF'}; "
        f"background: {colors[0] if colors else '#E5E7EB'}; "
        f"border-radius: 10px; padding: 4px 10px; "
        f"font-weight: 600; font-size: 11px;"
    )
    return label
```

- [ ] **Step 3: Compile and verify**

```bash
python -m py_compile "ui/dashboard.py"
```

---

### Task 5: Global Stylesheet Adjustments

**Files:**
- Modify: `ui/theme.py` — remove conflicting old styles

- [ ] **Step 1: Remove `#cardTitle`, `#cardValue` from global stylesheet if they conflict with new DashboardCard**

In `global_stylesheet()`, remove these lines if present:
```python
#cardTitle {{ color: {c['text_secondary']}; font-size: 12px; }}
#cardValue {{ font-size: 26px; font-weight: 700; }}
```

- [ ] **Step 2: Compile and verify**

```bash
python -m py_compile "ui/theme.py"
```

---

### Task 6: Full Application Test

**Files:** (none)

- [ ] **Step 1: Verify all Python files compile**

```bash
python -m py_compile "main.py"
python -m py_compile "ui/main_window.py"
python -m py_compile "ui/theme.py"
python -m py_compile "ui/dashboard.py"
```

- [ ] **Step 2: Run the application**

```bash
python main.py
```

Verify:
- Dashboard opens without errors
- Stat cards show correct values
- Sidebar navigation works for all 7 items
- Quick action buttons navigate correctly
- Tables show real data with colored status badges
- Charts render without errors

- [ ] **Step 3: Check all pages still load**

Navigate to every page (Books, Students, Issue, Return, Reports, Settings) and verify they work.
