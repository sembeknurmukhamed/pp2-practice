"""
persistence.py
Handles reading/writing leaderboard.json and settings.json.
"""

import json
import os

_BASE            = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE    = os.path.join(_BASE, "settings.json")
LEADERBOARD_FILE = os.path.join(_BASE, "leaderboard.json")

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "green",   # "green" | "red"
    "difficulty": "medium",  # "easy"  | "medium" | "hard"
}


# ── settings ───────────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**DEFAULT_SETTINGS, **data}
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)


# ── leaderboard ────────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_leaderboard(entries: list) -> None:
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def add_score(name: str, score: int, distance: float, coins: int) -> list:
    """Insert a new score, keep only top-10, return sorted list."""
    entries = load_leaderboard()
    entries.append({
        "name":     name,
        "score":    score,
        "distance": int(distance),
        "coins":    coins,
    })
    entries.sort(key=lambda x: x["score"], reverse=True)
    entries = entries[:10]
    save_leaderboard(entries)
    return entries
