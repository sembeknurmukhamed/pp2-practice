import os

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(__file__)
ASSETS_DIR    = os.path.join(BASE_DIR, "assets")
MATERIALS_DIR = os.path.join(BASE_DIR, "materials")   # original sprite folder
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# ── Screen ────────────────────────────────────────────────────────────────────
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 400
TILE          = 20
COLS          = SCREEN_WIDTH  // TILE   # 20
ROWS          = SCREEN_HEIGHT // TILE   # 20

# ── Gameplay ──────────────────────────────────────────────────────────────────
FPS_RENDER    = 60
FPS_BASE      = 10          # starting logic ticks / sec
SPEED_STEP    = 1           # +1 tick/sec per level
FOOD_PER_LVL  = 4           # apples per level-up
OBSTACLE_START_LEVEL = 3    # obstacles appear from this level
OBSTACLES_PER_LEVEL  = 3    # wall blocks added each level
MAX_OBSTACLES        = 30

# ── Power-up timing (ms) ─────────────────────────────────────────────────────
POWERUP_FIELD_TTL    = 8_000   # disappears from field after 8 s
POWERUP_EFFECT_TTL   = 5_000   # effect lasts 5 s
SPEED_BOOST_FACTOR   = 1.8     # multiplier when boosted
SLOW_FACTOR          = 0.5     # multiplier when slowed

# ── Poison food ───────────────────────────────────────────────────────────────
POISON_SHORTEN = 2          # segments removed on eating poison

# ── Directions ────────────────────────────────────────────────────────────────
RIGHT = ( 1,  0)
LEFT  = (-1,  0)
UP    = ( 0, -1)
DOWN  = ( 0,  1)

# ── Colors ────────────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
YELLOW     = (255, 215,  0)
RED        = (200,  30,  30)
DARK_RED   = (120,   0,   0)   # poison food
GREEN      = ( 50, 200,  50)
CYAN       = (  0, 220, 220)
ORANGE     = (255, 140,   0)
BLUE       = ( 40, 100, 220)
GREY       = (100, 100, 100)
DARK_GREY  = ( 40,  40,  40)
GOLD       = (255, 200,   0)
SHIELD_COL = ( 80, 160, 255)

# ── Power-up types ────────────────────────────────────────────────────────────
PU_SPEED  = "speed"
PU_SLOW   = "slow"
PU_SHIELD = "shield"

POWERUP_COLORS = {
    PU_SPEED:  ORANGE,
    PU_SLOW:   CYAN,
    PU_SHIELD: SHIELD_COL,
}

POWERUP_LABELS = {
    PU_SPEED:  "⚡",
    PU_SLOW:   "❄",
    PU_SHIELD: "🛡",
}

# ── DB (override with env vars if needed) ─────────────────────────────────────
DB_HOST = os.environ.get("SNAKE_DB_HOST", "localhost")
DB_PORT = os.environ.get("SNAKE_DB_PORT", "5432")
DB_NAME = os.environ.get("SNAKE_DB_NAME", "snakedb")
DB_USER = os.environ.get("SNAKE_DB_USER", "postgres")
DB_PASS = os.environ.get("SNAKE_DB_PASS", "postgres")
