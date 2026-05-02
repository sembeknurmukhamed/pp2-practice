"""
db.py — PostgreSQL persistence layer.

Schema (auto-created on first connect):

    CREATE TABLE players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );
    CREATE TABLE game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
"""

from __future__ import annotations
import datetime
from typing import Optional

try:
    import psycopg2
    import psycopg2.extras
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

# ─────────────────────────────────────────────────────────────────────────────
_conn = None   # module-level connection (lazy)


def _get_conn():
    """Return (or create) a live psycopg2 connection."""
    global _conn
    if not HAS_PSYCOPG2:
        return None
    if _conn is None or _conn.closed:
        try:
            _conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT,
                dbname=DB_NAME, user=DB_USER, password=DB_PASS,
                connect_timeout=3,
            )
            _conn.autocommit = False
        except Exception as e:
            print(f"[DB] connection failed: {e}")
            _conn = None
    return _conn


def init_db() -> bool:
    """Create tables if they don't exist. Returns True on success."""
    conn = _get_conn()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id       SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id            SERIAL PRIMARY KEY,
                    player_id     INTEGER REFERENCES players(id),
                    score         INTEGER   NOT NULL,
                    level_reached INTEGER   NOT NULL,
                    played_at     TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        conn.rollback()
        return False


def get_or_create_player(username: str) -> Optional[int]:
    """Return player.id, creating the row if absent."""
    conn = _get_conn()
    if conn is None:
        return None
    username = username.strip()[:50]
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players (username) VALUES (%s) "
                "ON CONFLICT (username) DO NOTHING;",
                (username,)
            )
            cur.execute("SELECT id FROM players WHERE username = %s;", (username,))
            row = cur.fetchone()
        conn.commit()
        return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        conn.rollback()
        return None


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Insert a completed game session."""
    conn = _get_conn()
    if conn is None or player_id is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO game_sessions (player_id, score, level_reached) "
                "VALUES (%s, %s, %s);",
                (player_id, score, level_reached),
            )
        conn.commit()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        conn.rollback()
        return False


def get_personal_best(player_id: int) -> int:
    """Return the player's all-time best score (0 if none)."""
    conn = _get_conn()
    if conn is None or player_id is None:
        return 0
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s;",
                (player_id,),
            )
            row = cur.fetchone()
        return row[0] if row else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


def get_top10() -> list[dict]:
    """
    Return top-10 all-time scores as list of dicts:
        {rank, username, score, level_reached, played_at}
    """
    conn = _get_conn()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT 10;
            """)
            rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB] get_top10 error: {e}")
        return []


def close_db():
    """Close the connection gracefully."""
    global _conn
    if _conn and not _conn.closed:
        _conn.close()
    _conn = None
