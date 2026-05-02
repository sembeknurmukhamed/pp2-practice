# 🐍 Snake — Ultimate Edition (TSIS3)

A feature-rich Snake game built with **Pygame** + **PostgreSQL** covering all requirements from Tasks 3.1–3.7.

---

## Project Structure

```
TSIS3/
├── main.py          # Entry point + all game screens
├── game.py          # Core objects: Snake, Apple, PoisonFood, PowerUp, Obstacle
├── db.py            # PostgreSQL persistence (psycopg2)
├── settings.py      # JSON settings manager
├── config.py        # All constants & configuration
├── settings.json    # User preferences (auto-created)
├── assets/          # (sounds, extra images)
└── materials/       # Original sprite folder (glade.jpg, snakehead.png, …)
```

---

## Requirements

```
Python >= 3.10
pygame >= 2.1
psycopg2-binary >= 2.9   (or psycopg2)
```

Install:
```bash
pip install pygame psycopg2-binary
```

---

## Database Setup (PostgreSQL)

1. Create a database:
```sql
CREATE DATABASE snakedb;
```

2. Set environment variables (or edit `config.py`):
```bash
export SNAKE_DB_HOST=localhost
export SNAKE_DB_PORT=5432
export SNAKE_DB_NAME=snakedb
export SNAKE_DB_USER=postgres
export SNAKE_DB_PASS=postgres
```

Tables are created **automatically** on first launch via `db.init_db()`.

Schema:
```sql
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
```

> **Offline mode**: If PostgreSQL is unavailable, the game runs normally without persistence — no crash.

---

## How to Run

```bash
cd TSIS3
python main.py
```

---

## Features

### 3.1 — Leaderboard (PostgreSQL)
- Username entry screen on launch
- Score, level, and timestamp saved after every game
- Top-10 leaderboard screen (rank, name, score, level, date)
- Personal best shown live during gameplay

### 3.2 — Poison Food
- Dark-red tile with ✕ symbol appears alongside regular food
- Eating it **removes 2 tail segments**
- If snake length drops to ≤ 1 → **Game Over**

### 3.3 — Power-ups
| Power-up     | Color  | Effect                                      | Duration |
|-------------|--------|---------------------------------------------|----------|
| ⚡ Speed Boost | Orange | +80% movement speed                        | 5 s      |
| ❄ Slow Motion | Cyan   | −50% movement speed                         | 5 s      |
| 🛡 Shield      | Blue   | Absorbs next wall/self/obstacle collision   | Until triggered |

- Only **one** power-up on field at a time
- Disappears after **8 seconds** if not collected
- Spawns every 15 seconds

### 3.4 — Obstacles
- Wall blocks appear **from Level 3** onwards
- BFS check ensures the snake always has room to move
- Collision = Game Over (unless Shield is active)
- Food and power-ups never spawn on obstacle cells

### 3.5 — Settings (JSON)
| Setting      | Options                            |
|-------------|-------------------------------------|
| Snake color  | 8 presets (Green, Lime, Blue, …)   |
| Grid overlay | On / Off toggle                     |
| Sound        | On / Off toggle                     |

Saved to `settings.json`, loaded on startup.

### 3.6 — Game Screens
- **Main Menu** — Play, Leaderboard, Settings, Quit
- **Username screen** — keyboard entry with cursor
- **Game Over** — score, level, personal best; Retry / Main Menu
- **Leaderboard** — Top-10 table with rank, name, score, level, date
- **Settings** — toggle grid, toggle sound, color picker

---

## Controls

| Key       | Action               |
|-----------|----------------------|
| W/↑       | Move Up              |
| S/↓       | Move Down            |
| A/←       | Move Left            |
| D/→       | Move Right           |
| ESC       | Pause / Back to menu |
| R         | Retry (Game Over)    |
| M         | Main Menu (Game Over)|
