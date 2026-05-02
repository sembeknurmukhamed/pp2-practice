"""
settings.py — Load / save user preferences from settings.json.

Default settings:
    snake_color : [0, 200, 80]   (RGB list — stored as JSON array)
    grid_overlay: false
    sound       : true
"""

import json
import os
from config import SETTINGS_FILE

_DEFAULTS = {
    "snake_color":  [0, 200, 80],
    "grid_overlay": False,
    "sound":        True,
}

_data: dict = {}


def load() -> dict:
    """Load settings.json; fall back to defaults on any error."""
    global _data
    if os.path.isfile(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            # merge with defaults so new keys are always present
            _data = {**_DEFAULTS, **loaded}
        except Exception as e:
            print(f"[Settings] load error: {e}; using defaults")
            _data = dict(_DEFAULTS)
    else:
        _data = dict(_DEFAULTS)
    return _data


def save() -> None:
    """Persist current settings to disk."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(_data, f, indent=2)
    except Exception as e:
        print(f"[Settings] save error: {e}")


def get(key: str):
    """Return a setting value (load first if not done yet)."""
    if not _data:
        load()
    return _data.get(key, _DEFAULTS.get(key))


def set_value(key: str, value) -> None:
    """Update a setting in memory (call save() to persist)."""
    if not _data:
        load()
    _data[key] = value


def snake_color() -> tuple:
    c = get("snake_color")
    return tuple(c) if isinstance(c, (list, tuple)) else (0, 200, 80)


def grid_overlay() -> bool:
    return bool(get("grid_overlay"))


def sound_on() -> bool:
    return bool(get("sound"))
