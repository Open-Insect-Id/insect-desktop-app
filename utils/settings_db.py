"""
settings_db.py – SQLite-backed persistence for theme/color settings.
All other modules should import get_theme() / set_color() from here.
"""

import sqlite3
import config
from ui.theme import Theme

# convenient value to use across this file
# _ mean private, but as python is shitty, we can't really make private variables/values
# use Kotlin instead :)
_defaults = config.DEFAULTS_COLORS


def _connect() -> sqlite3.Connection:
    """Opens a Sqlite connection with the database"""
    conn = sqlite3.connect(config.SETTINGS_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the settings table and populate defaults if it is empty."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS theme (
                key   TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )
        conn.commit()
        for key, value in _defaults.items():
            conn.execute(
                "INSERT OR IGNORE INTO theme (key, value) VALUES (?, ?)",
                (key, value),
            )
        conn.commit()


def get_theme() -> Theme:
    """Return all theme colors as a plain dict."""
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT key, value FROM theme").fetchall()
    theme = dict(_defaults)  # start from defaults so no key is ever missing
    theme.update({row["key"]: row["value"] for row in rows})
    return Theme(theme)


def set_lang(lang_code: str) -> None:
    """Persist the language code (fr, en, etc) in the theme table under key 'language'."""
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO theme (key, value) VALUES (?, ?)",
            ("language", lang_code),
        )
        conn.commit()

    from ui.i18n import I18N

    i18n = I18N()
    i18n.refresh_from_db()  # force reload of the language in the I18N singleton after changing it in the DB


def get_lang() -> str:
    """Return the language code stored in the theme table, or 'fr' if not set."""
    init_db()
    with _connect() as conn:
        row = conn.execute(
            "SELECT value FROM theme WHERE key = ?", ("language",)
        ).fetchone()
    return row["value"] if row else "fr"


def set_color(key: str, value: str) -> None:
    """Persist a single color value."""
    if key not in _defaults:
        raise ValueError(f"Unknown theme key: {key!r}")
    init_db()
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO theme (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()


def reset_color(key: str) -> str:
    """Reset a single color to its default and return the default value."""
    default = _defaults[key]
    set_color(key, default)
    return default


def reset_all() -> None:
    """Reset every color to factory defaults."""
    for key, value in _defaults.items():
        set_color(key, value)
