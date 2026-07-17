"""Shared UI theme, reusable widgets, and helpers.

    Centralizes the light professional look from docs/design.md: color palette, the
global Qt stylesheet, status badges, dashboard cards, and small message
helpers. Pages import from here so the app stays visually consistent.
"""

import os
from contextlib import contextmanager

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, LOGO_PATH

# ---------------------------------------------------------------------------
# Badge color mapping (background, text) per status label
# ---------------------------------------------------------------------------
_BADGE_STYLES = {
    "Available": ("#DCFCE7", "#166534"),
    "Low Stock": ("#FEF3C7", "#92400E"),
    "Not Available": ("#FEE2E2", "#991B1B"),
    "Inactive": ("#E5E7EB", "#374151"),
    "ACTIVE": ("#DCFCE7", "#166534"),
    "INACTIVE": ("#E5E7EB", "#374151"),
    "ISSUED": ("#DBEAFE", "#1E40AF"),
    "RETURNED": ("#DCFCE7", "#166534"),
    "OVERDUE": ("#FEE2E2", "#991B1B"),
    "LOST": ("#FEE2E2", "#991B1B"),
    "DAMAGED": ("#FEF3C7", "#92400E"),
}


def global_stylesheet() -> str:
    """Return the application-wide Qt stylesheet."""
    c = COLORS
    return f"""
    QWidget {{
        font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
        font-size: 13px;
        color: {c['text_primary']};
    }}
    QMainWindow, #contentArea {{
        background: {c['background']};
    }}

    /* Sidebar */
    #sidebar {{
        background: {c['sidebar_bg']};
    }}
    #sidebarTitle {{
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 600;
        padding: 18px 16px 6px 16px;
    }}
    #sidebarSubtitle {{
        color: #9CA3AF;
        font-size: 11px;
        padding: 0 16px 12px 16px;
    }}
    QPushButton#navButton {{
        color: {c['sidebar_text']};
        background: transparent;
        border: none;
        text-align: left;
        padding: 11px 18px;
        font-size: 13px;
        border-radius: 0px;
    }}
    QPushButton#navButton:hover {{
        background: #1F2937;
    }}
    QPushButton#navButton:checked {{
        background: {c['sidebar_active']};
        color: #FFFFFF;
        font-weight: 600;
    }}

    /* Top bar */
    #topBar {{
        background: {c['surface']};
        border-bottom: 1px solid {c['border']};
    }}
    #topBarTitle {{ font-size: 16px; font-weight: 600; }}
    #topBarRight {{ color: {c['text_secondary']}; font-size: 12px; }}

    /* Page headings */
    #pageTitle {{ font-size: 22px; font-weight: 600; }}
    #pageSubtitle {{ color: {c['text_secondary']}; font-size: 13px; }}
    #sectionTitle {{ font-size: 15px; font-weight: 600; }}

    /* Cards */
    #card {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 12px;
    }}
    #cardTitle {{ color: {c['text_secondary']}; font-size: 12px; }}
    #cardValue {{ font-size: 26px; font-weight: 700; }}

    /* Inputs */
    QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 7px 10px;
        min-height: 20px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {{
        border: 1px solid {c['primary']};
    }}
    QComboBox::drop-down {{ border: none; width: 22px; }}
    QLabel#fieldLabel {{ color: {c['text_primary']}; font-weight: 600; font-size: 12px; }}
    QLabel#errorLabel {{ color: {c['danger']}; font-size: 12px; }}
    QLabel#hintLabel {{ color: {c['text_secondary']}; font-size: 12px; }}

    /* Buttons */
    QPushButton {{
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        min-height: 20px;
    }}
    QPushButton#primaryButton {{ background: {c['primary']}; color: #FFFFFF; border: none; }}
    QPushButton#primaryButton:hover {{ background: {c['primary_hover']}; }}
    QPushButton#primaryButton:disabled {{ background: #93C5FD; color: #EFF6FF; }}
    QPushButton#successButton {{ background: {c['secondary']}; color: #FFFFFF; border: none; }}
    QPushButton#successButton:hover {{ background: {c['success_hover']}; }}
    QPushButton#dangerButton {{ background: {c['danger']}; color: #FFFFFF; border: none; }}
    QPushButton#dangerButton:hover {{ background: {c['danger_hover']}; }}
    QPushButton#secondaryButton {{
        background: {c['surface']}; color: {c['text_primary']};
        border: 1px solid {c['border']};
    }}
    QPushButton#secondaryButton:hover {{ background: #F3F4F6; }}

    /* Tables */
    QTableWidget {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 10px;
        gridline-color: {c['border']};
        selection-background-color: #DBEAFE;
        selection-color: {c['text_primary']};
    }}
    QHeaderView::section {{
        background: #F1F5F9;
        color: {c['text_secondary']};
        padding: 10px 12px;
        border: none;
        border-bottom: 1px solid {c['border']};
        border-right: 1px solid {c['border']};
        font-weight: 600;
        min-height: 24px;
        text-align: center;
    }}
    QHeaderView::section:last {{
        border-right: none;
    }}
    QTableWidget::item {{
        padding: 10px 12px;
        min-height: 28px;
        border: none;
        border-bottom: 1px solid {c['border']};
        text-align: center;
    }}
    QTableView {{ alternate-background-color: #F9FAFB; outline: none; }}

    #statusBadge {{
        border-radius: 12px;
        padding: 5px 10px;
        font-weight: 700;
    }}

    /* Tabs */
    QTabBar::tab {{
        background: transparent; padding: 8px 16px; margin-right: 4px;
        border-top-left-radius: 8px; border-top-right-radius: 8px;
        color: {c['text_secondary']};
    }}
    QTabBar::tab:selected {{ background: {c['surface']}; color: {c['primary']}; font-weight: 600; }}
    QTabWidget::pane {{ border: 1px solid {c['border']}; border-radius: 8px; top: -1px; }}

    QScrollArea {{ border: none; background: transparent; }}
    """


# ---------------------------------------------------------------------------
# Reusable widgets
# ---------------------------------------------------------------------------
class StatCard(QFrame):
    """A dashboard statistic card with a title and a large value."""

    def __init__(self, title: str, value: str = "0", accent: str = None):
        super().__init__()
        self.setObjectName("card")
        self.setMinimumWidth(150)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("cardTitle")
        self.value_label = QLabel(str(value))
        self.value_label.setObjectName("cardValue")
        if accent:
            self.value_label.setStyleSheet(f"color: {accent};")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

    def set_value(self, value):
        self.value_label.setText(str(value))


def make_badge(text: str) -> QLabel:
    """Return a colored status badge label for the given status text."""
    label = QLabel(text)
    label.setObjectName("statusBadge")
    label.setAlignment(Qt.AlignCenter)
    bg, fg = _BADGE_STYLES.get(text, ("#E5E7EB", "#374151"))
    label.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 12px; "
        f"padding: 5px 10px; font-weight: 700; font-size: 12px;"
    )
    return label


def badge_in_cell(text: str) -> QWidget:
    """Wrap a badge in a centered container suitable for a table cell."""
    container = QWidget()
    layout = QHBoxLayout(container)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.addWidget(make_badge(text))
    layout.setAlignment(Qt.AlignCenter)
    return container


def make_button(text: str, kind: str = "primary") -> QPushButton:
    """Create a styled button. kind: primary|success|danger|secondary."""
    button = QPushButton(text)
    button.setObjectName(f"{kind}Button")
    button.setCursor(Qt.PointingHandCursor)
    return button


# ---------------------------------------------------------------------------
# Reusable logo widget
# ---------------------------------------------------------------------------
class LogoLabel(QLabel):
    """A fixed-size logo that preserves aspect ratio.

    Usage::

        logo = LogoLabel(64)
        layout.addWidget(logo)
    """

    def __init__(self, size: int = 64, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self._load(size)

    def _load(self, size: int):
        if os.path.exists(LOGO_PATH):
            pixmap = QPixmap(LOGO_PATH)
            if not pixmap.isNull():
                self.setPixmap(
                    pixmap.scaled(
                        size, size,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                )
                return
        self.hide()

    def set_size(self, size: int):
        self.setFixedSize(size, size)
        self._load(size)


# ---------------------------------------------------------------------------
# Wait cursor helper for long operations
# ---------------------------------------------------------------------------
@contextmanager
def wait_cursor():
    """Show a wait cursor while a slow synchronous operation runs."""
    try:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        yield
    finally:
        QApplication.restoreOverrideCursor()


# ---------------------------------------------------------------------------
# Styled message boxes (visible on dark backgrounds)
# ---------------------------------------------------------------------------
def _style_message_box(box: QMessageBox) -> None:
    """Apply dark-theme styling so all text is clearly readable."""
    box.setStyleSheet("""
        QMessageBox {
            background-color: #1F1F1F;
        }
        QMessageBox QLabel {
            color: #FFFFFF;
            background-color: transparent;
            font-size: 14px;
        }
        QMessageBox QPushButton {
            min-width: 80px;
            min-height: 34px;
            padding: 6px 14px;
            border-radius: 6px;
            border: 1px solid #D1D5DB;
            background-color: #FFFFFF;
            color: #111827;
            font-weight: 600;
        }
        QMessageBox QPushButton:hover {
            background-color: #F3F4F6;
        }
        QMessageBox QPushButton:pressed {
            background-color: #E5E7EB;
        }
        QMessageBox QCheckBox {
            color: #FFFFFF;
        }
        QMessageBox QTextEdit {
            background-color: #2B2B2B;
            color: #FFFFFF;
            border: 1px solid #4B5563;
        }
    """)


def show_error(parent, message: str, title: str = "Error"):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    _style_message_box(box)
    return box.exec()


def show_success(parent, message: str, title: str = "Success"):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    _style_message_box(box)
    return box.exec()


def show_info(parent, message: str, title: str = "Information"):
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Information)
    box.setWindowTitle(title)
    box.setText(message)
    box.setStandardButtons(QMessageBox.Ok)
    _style_message_box(box)
    return box.exec()


def confirm(parent, message: str, title: str = "Please Confirm",
            ok_text: str = "Confirm") -> bool:
    """Show a Yes/No confirmation. Returns True if the user confirms."""
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Question)
    box.setWindowTitle(title)
    box.setText(message)
    yes = box.addButton(ok_text, QMessageBox.AcceptRole)
    box.addButton("Cancel", QMessageBox.RejectRole)
    _style_message_box(box)
    box.exec()
    return box.clickedButton() is yes
