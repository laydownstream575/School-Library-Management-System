"""Application configuration: paths, constants, colors, and default settings.

All filesystem paths are resolved relative to the project root so the app
works both when run from source (``python main.py``) and when frozen with
PyInstaller.
"""

import os
import sys
from pathlib import Path


def _project_root() -> str:
    """Return the project root when running from source."""
    # app/config.py -> app -> project root
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_data_dir() -> str:
    """Return a writable directory for persistent data (database, exports,
    backups). Uses %LOCALAPPDATA% when frozen, or the project root in
    development so existing data is reused."""
    if getattr(sys, "frozen", False):
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
        app_dir = base / "School Library Management System"
        app_dir.mkdir(parents=True, exist_ok=True)
        return str(app_dir)
    return _project_root()


def resource_path(relative_path: str) -> str:
    """Resolve a path to a bundled asset.

    When frozen by PyInstaller, data files live in sys._MEIPASS.
    When running from source, the path is relative to the project root.
    """
    base = getattr(sys, "_MEIPASS", _project_root())
    return os.path.join(base, relative_path)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
APP_NAME = "School Library Management System"
APP_VERSION = "1.0.1"
BUILD_DATE = "2026-07-13"

# Writable data (database, exports, backups)
DATA_DIR = get_app_data_dir()
DATABASE_DIR = os.path.join(DATA_DIR, "database")
DATABASE_PATH = os.path.join(DATABASE_DIR, "library.db")
SCHEMA_PATH = resource_path(os.path.join("database", "schema.sql"))
EXPORTS_DIR = os.path.join(DATA_DIR, "exports")
BACKUPS_DIR = os.path.join(DATA_DIR, "backups")

# Bundled assets (read-only, resolved via resource_path)
ASSETS_DIR = resource_path("assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
LOGO_PATH = os.path.join(IMAGES_DIR, "logo.png")
APP_ICON_PATH = os.path.join(ICONS_DIR, "app_icon.ico")

# Folders that must exist on first run.
REQUIRED_DIRS = [DATABASE_DIR, EXPORTS_DIR, BACKUPS_DIR]


# ---------------------------------------------------------------------------
# Status constants
# ---------------------------------------------------------------------------
STATUS_ACTIVE = "ACTIVE"
STATUS_INACTIVE = "INACTIVE"

ISSUE_STATUS_ISSUED = "ISSUED"
ISSUE_STATUS_RETURNED = "RETURNED"
ISSUE_STATUS_LOST = "LOST"
ISSUE_STATUS_DAMAGED = "DAMAGED"

# ---------------------------------------------------------------------------
# Default settings (mirrors schema.sql defaults; used as a fallback)
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS = {
    "school_name": "ABC Public School",
    "library_name": "School Library",
    "default_due_days": "7",
    "low_stock_limit": "2",
    "backup_path": "backups",
    "export_path": "exports",
}

# ---------------------------------------------------------------------------
    # Color palette (from docs/design.md) — used to build Qt stylesheets
# ---------------------------------------------------------------------------
COLORS = {
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "secondary": "#16A34A",
    "warning": "#F59E0B",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "success": "#22C55E",
    "success_hover": "#16A34A",
    "background": "#F8FAFC",
    "surface": "#FFFFFF",
    "border": "#E5E7EB",
    "text_primary": "#111827",
    "text_secondary": "#6B7280",
    "sidebar_bg": "#111827",
    "sidebar_text": "#E5E7EB",
    "sidebar_active": "#2563EB",
}
