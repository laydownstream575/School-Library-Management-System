"""Shared utility helpers: date/time, settings access, activity logging, data helpers."""

from datetime import datetime, timedelta

from app import config, database

DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


# ---------------------------------------------------------------------------
# Date / time helpers (ISO strings stored in SQLite)
# ---------------------------------------------------------------------------
def now_timestamp() -> str:
    """Current date-time as 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().strftime(DATETIME_FORMAT)


def today_str() -> str:
    """Current date as 'YYYY-MM-DD'."""
    return datetime.now().strftime(DATE_FORMAT)


def parse_date(value: str):
    """Parse a 'YYYY-MM-DD' string into a date, or None if invalid/empty."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip()[:10], DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None


def add_days(date_str: str, days: int) -> str:
    """Return date_str + days as a 'YYYY-MM-DD' string."""
    base = parse_date(date_str) or datetime.now().date()
    return (base + timedelta(days=days)).strftime(DATE_FORMAT)


def overdue_days(due_date: str, reference: str = None) -> int:
    """Number of days a due date is past the reference date (0 if not overdue)."""
    due = parse_date(due_date)
    if due is None:
        return 0
    ref = parse_date(reference) if reference else datetime.now().date()
    if ref is None:
        ref = datetime.now().date()
    delta = (ref - due).days
    return delta if delta > 0 else 0


def format_display_date(value: str) -> str:
    """Format a stored date/datetime for friendly display (e.g. 06 Jul 2026)."""
    if not value:
        return "-"
    parsed = parse_date(value)
    if parsed is None:
        return str(value)
    return parsed.strftime("%d %b %Y")


# ---------------------------------------------------------------------------
# Settings helpers (settings table)
# ---------------------------------------------------------------------------
def get_setting(key: str, default: str = None) -> str:
    """Read a single setting value, falling back to config defaults."""
    row = database.fetch_one(
        "SELECT setting_value FROM settings WHERE setting_key = ?", (key,)
    )
    if row is not None and row["setting_value"] is not None:
        return row["setting_value"]
    if default is not None:
        return default
    return config.DEFAULT_SETTINGS.get(key, "")


def get_setting_int(key: str, default: int = 0) -> int:
    """Read a setting as an integer, tolerating bad values."""
    try:
        return int(str(get_setting(key, str(default))).strip())
    except (ValueError, TypeError):
        return default


def set_setting(key: str, value) -> None:
    """Insert or update a single setting."""
    database.execute(
        "INSERT INTO settings (setting_key, setting_value) VALUES (?, ?) "
        "ON CONFLICT(setting_key) DO UPDATE SET setting_value = excluded.setting_value",
        (key, str(value)),
    )


def get_all_settings() -> dict:
    """Return all settings as a plain dict."""
    rows = database.fetch_all("SELECT setting_key, setting_value FROM settings")
    return {row["setting_key"]: row["setting_value"] for row in rows}


# ---------------------------------------------------------------------------
# Activity log helper
# ---------------------------------------------------------------------------
def log_activity(action_type: str, description: str = "") -> None:
    """Record an entry in activity_logs. Never raises to the caller."""
    try:
        database.execute(
            "INSERT INTO activity_logs (action_type, description, created_at) "
            "VALUES (?, ?, ?)",
            (action_type, description, now_timestamp()),
        )
    except Exception:
        # Logging must never break the main operation.
        pass


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def row_to_dict(row):
    """Convert a sqlite3.Row (or None) to a plain dict.

    Returns ``None`` when the row is ``None``, otherwise a dict copy.
    """
    return dict(row) if row is not None else None
