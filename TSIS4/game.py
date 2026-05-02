"""
game.py — Core game objects:
    Snake, Apple, PoisonFood, PowerUp, Obstacle, draw_hud, draw_grid
"""

from __future__ import annotations
import os
import random
import pygame

from config import (
    COLS, ROWS, TILE, SCREEN_WIDTH, SCREEN_HEIGHT,
    RIGHT, LEFT, UP, DOWN,
    BLACK, WHITE, YELLOW, RED, DARK_RED, GREEN, GREY, GOLD, DARK_GREY,
    PU_SPEED, PU_SLOW, PU_SHIELD, POWERUP_COLORS, POWERUP_LABELS,
    POWERUP_FIELD_TTL, POWERUP_EFFECT_TTL,
    SPEED_BOOST_FACTOR, SLOW_FACTOR,
    POISON_SHORTEN,
    MATERIALS_DIR,
)
import settings as S


# ── helpers ───────────────────────────────────────────────────────────────────

def rot_img(surf: pygame.Surface, angle: float) -> pygame.Surface:
    return pygame.transform.rotate(surf, angle)


def _load_scale(path: str) -> pygame.Surface:
    return pygame.transform.scale(pygame.image.load(path), (TILE, TILE))


def _try_load(path: str, fallback_color=(0, 150, 0)) -> pygame.Surface:
    """Load sprite; fall back to a solid-color tile if missing."""
    if os.path.isfile(path):
        return _load_scale(path)
    surf = pygame.Surface((TILE, TILE))
    surf.fill(fallback_color)
    return surf


# ── Sprite paths (from materials/ folder) ─────────────────────────────────────
_SNAKE_PATHS = [
    os.path.join(MATERIALS_DIR, "snakehead.png"),
    os.path.join(MATERIALS_DIR, "snakebody.png"),
    os.path.join(MATERIALS_DIR, "snakeside1.png"),
    os.path.join(MATERIALS_DIR, "snakeside2.png"),
    os.path.join(MATERIALS_DIR, "snakeside3.png"),
    os.path.join(MATERIALS_DIR, "snakeside4.png"),
    os.path.join(MATERIALS_DIR, "snaketale.png"),
]
_APPLE_PATHS = [
    os.path.join(MATERIALS_DIR, "XLYI5953.PNG"),
    os.path.join(MATERIALS_DIR, "MAWA5410.PNG"),
    os.path.join(MATERIALS_DIR, "JVYL6650.PNG"),
    os.path.join(MATERIALS_DIR, "LVLP4508.PNG"),
    os.path.join(MATERIALS_DIR, "NBUN0214.PNG"),
]
_BG_PATH = os.path.join(MATERIALS_DIR, "glade.jpg")

# ── Background ─────────────────────────────────────────────────────────────────

def load_background() -> pygame.Surface:
    if os.path.isfile(_BG_PATH):
        return pygame.transform.scale(
            pygame.image.load(_BG_PATH), (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill((34, 90, 34))
    return surf


# ═════════════════════════════════════════════════════════════════════════════
# APPLE (animated)
# ═════════════════════════════════════════════════════════════════════════════

class Apple:
    ANIM_SPEED = 7

    def __init__(self):
        frames_raw = [_try_load(p, (220, 30, 30)) for p in _APPLE_PATHS]
        self.frames: list[pygame.Surface] = frames_raw
        self.frame_idx  = 0
        self.anim_timer = 0
        self.grid_pos   = (0, 0)
        self.rect       = pygame.Rect(0, 0, TILE, TILE)

    @property
    def image(self) -> pygame.Surface:
        return self.frames[self.frame_idx]

    def respawn(self, occupied: list, obstacles: list = None):
        blocked = set(occupied)
        if obstacles:
            blocked.update(obstacles)
        free = [
            (c, r)
            for c in range(1, COLS - 1)
            for r in range(1, ROWS - 1)
            if (c, r) not in blocked
        ]
        self.grid_pos = random.choice(free) if free else (COLS // 2, ROWS // 2)
        self.rect.topleft = (self.grid_pos[0] * TILE, self.grid_pos[1] * TILE)

    def update(self):
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer = 0
            self.frame_idx  = (self.frame_idx + 1) % len(self.frames)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)


# ═════════════════════════════════════════════════════════════════════════════
# POISON FOOD
# ═════════════════════════════════════════════════════════════════════════════

class PoisonFood:
    """Dark-red skull-looking tile that shortens the snake."""

    def __init__(self):
        # Draw a distinctive poison tile procedurally
        self.surf = self._make_surf()
        self.grid_pos = None
        self.rect     = pygame.Rect(0, 0, TILE, TILE)
        self.active   = False

    @staticmethod
    def _make_surf() -> pygame.Surface:
        surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        # dark red background
        pygame.draw.rect(surf, (110, 0, 0), (0, 0, TILE, TILE), border_radius=4)
        # white 'X'
        pygame.draw.line(surf, (230, 230, 230), (3, 3), (TILE-4, TILE-4), 2)
        pygame.draw.line(surf, (230, 230, 230), (TILE-4, 3), (3, TILE-4), 2)
        # outer glow ring
        pygame.draw.rect(surf, (180, 0, 0), (0, 0, TILE, TILE), 1, border_radius=4)
        return surf

    def respawn(self, occupied: list, obstacles: list = None):
        blocked = set(occupied)
        if obstacles:
            blocked.update(obstacles)
        free = [
            (c, r)
            for c in range(1, COLS - 1)
            for r in range(1, ROWS - 1)
            if (c, r) not in blocked
        ]
        if free:
            self.grid_pos = random.choice(free)
            self.rect.topleft = (self.grid_pos[0] * TILE, self.grid_pos[1] * TILE)
            self.active = True
        else:
            self.active = False

    def draw(self, surface: pygame.Surface):
        if self.active:
            surface.blit(self.surf, self.rect)


# ═════════════════════════════════════════════════════════════════════════════
# POWER-UP
# ═════════════════════════════════════════════════════════════════════════════

class PowerUp:
    """
    One power-up on the field at a time.
    Tracks its own spawn time and disappears after POWERUP_FIELD_TTL ms.
    """

    TYPES = [PU_SPEED, PU_SLOW, PU_SHIELD]

    def __init__(self):
        self.kind:      str | None = None
        self.grid_pos:  tuple | None = None
        self.rect:      pygame.Rect = pygame.Rect(0, 0, TILE, TILE)
        self.active:    bool = False
        self._spawn_ms: int  = 0
        # pre-render tiles
        self._surfs: dict[str, pygame.Surface] = {
            k: self._make_surf(k) for k in self.TYPES
        }

    @staticmethod
    def _make_surf(kind: str) -> pygame.Surface:
        color = POWERUP_COLORS[kind]
        surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, TILE, TILE), border_radius=5)
        pygame.draw.rect(surf, (255, 255, 255, 160), (0, 0, TILE, TILE), 1, border_radius=5)
        # small symbol
        font = pygame.font.SysFont("Segoe UI Emoji", 10)
        label = font.render(POWERUP_LABELS[kind], True, (255, 255, 255))
        surf.blit(label, (TILE//2 - label.get_width()//2,
                          TILE//2 - label.get_height()//2))
        return surf

    def spawn(self, occupied: list, obstacles: list = None):
        blocked = set(occupied)
        if obstacles:
            blocked.update(obstacles)
        free = [
            (c, r)
            for c in range(1, COLS - 1)
            for r in range(1, ROWS - 1)
            if (c, r) not in blocked
        ]
        if not free:
            return
        self.kind     = random.choice(self.TYPES)
        self.grid_pos = random.choice(free)
        self.rect.topleft = (self.grid_pos[0] * TILE, self.grid_pos[1] * TILE)
        self.active    = True
        self._spawn_ms = pygame.time.get_ticks()

    def update(self):
        """Expire from field after TTL."""
        if self.active:
            if pygame.time.get_ticks() - self._spawn_ms > POWERUP_FIELD_TTL:
                self.active = False

    def draw(self, surface: pygame.Surface):
        if self.active:
            surf = self._surfs[self.kind]
            surface.blit(surf, self.rect)
            # pulsing border
            age = (pygame.time.get_ticks() - self._spawn_ms) / POWERUP_FIELD_TTL
            alpha = int(128 + 127 * abs(((age * 4) % 2) - 1))
            glow = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            color = POWERUP_COLORS[self.kind]
            pygame.draw.rect(glow, (*color, alpha), (0, 0, TILE, TILE), 2, border_radius=5)
            surface.blit(glow, self.rect)


# ═════════════════════════════════════════════════════════════════════════════
# OBSTACLES
# ═════════════════════════════════════════════════════════════════════════════

class ObstacleManager:
    """Static wall blocks inside the arena (appear from level 3)."""

    def __init__(self):
        self.blocks: list[tuple] = []
        self._surf = self._make_surf()

    @staticmethod
    def _make_surf() -> pygame.Surface:
        surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.rect(surf, (70, 50, 30), (0, 0, TILE, TILE))
        # brick pattern
        pygame.draw.line(surf, (50, 30, 10), (0, TILE//2), (TILE, TILE//2), 1)
        pygame.draw.line(surf, (50, 30, 10), (TILE//2, 0), (TILE//2, TILE//2), 1)
        pygame.draw.line(surf, (50, 30, 10), (TILE//4, TILE//2), (TILE//4, TILE), 1)
        pygame.draw.line(surf, (50, 30, 10), (3*TILE//4, TILE//2), (3*TILE//4, TILE), 1)
        pygame.draw.rect(surf, (100, 80, 50), (0, 0, TILE, TILE), 1)
        return surf

    def reset(self):
        self.blocks.clear()

    def generate_for_level(self, level: int, snake_body: list, n: int):
        """
        Add n new wall blocks, avoiding snake body, border, and existing blocks.
        BFS ensures snake head has a reachable path to at least one free cell.
        """
        from config import OBSTACLE_START_LEVEL
        if level < OBSTACLE_START_LEVEL:
            return

        occupied = set(snake_body) | set(self.blocks)
        # border is already a wall (out of 0..COLS-1 bounds)
        candidates = [
            (c, r)
            for c in range(2, COLS - 2)
            for r in range(2, ROWS - 2)
            if (c, r) not in occupied
        ]
        random.shuffle(candidates)

        added = 0
        for pos in candidates:
            if added >= n:
                break
            test = set(self.blocks) | {pos}
            if self._snake_has_room(snake_body[0], snake_body, test):
                self.blocks.append(pos)
                added += 1

    def _snake_has_room(self, start: tuple, snake_body: list, walls: set) -> bool:
        """BFS: check snake head can reach at least 10 free cells."""
        visited = set()
        queue   = [start]
        blocked = walls | set(snake_body[1:])
        count   = 0
        while queue and count < 10:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            count += 1
            for dx, dy in [RIGHT, LEFT, UP, DOWN]:
                nx, ny = cx + dx, cy + dy
                if (0 <= nx < COLS and 0 <= ny < ROWS
                        and (nx, ny) not in blocked
                        and (nx, ny) not in visited):
                    queue.append((nx, ny))
        return count >= 5

    def hits(self, pos: tuple) -> bool:
        return pos in self.blocks

    def draw(self, surface: pygame.Surface):
        for col, row in self.blocks:
            surface.blit(self._surf, (col * TILE, row * TILE))


# ═════════════════════════════════════════════════════════════════════════════
# SNAKE
# ═════════════════════════════════════════════════════════════════════════════

class Snake:
    HEAD = 0; BODY = 1; S1 = 2; S2 = 3; S3 = 4; S4 = 5; TAIL = 6

    def __init__(self):
        self.raw: list[pygame.Surface] = [
            _try_load(p) for p in _SNAKE_PATHS
        ]
        # tinted copies cache
        self._tint_cache: dict = {}
        self.reset()

    def reset(self):
        cx, cy = COLS // 2, ROWS // 2
        self.body:       list[tuple] = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction:  tuple = RIGHT
        self.next_dir:   tuple = RIGHT
        self.grew:        bool = False
        # power-up state
        self.shield_active: bool = False
        self.effect:         str | None = None
        self.effect_end_ms:  int = 0

    # ── input ──────────────────────────────────────────────────────────────
    def handle_key(self, key: int):
        from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_d, K_a, K_w, K_s
        mapping = {
            K_RIGHT: RIGHT, K_d: RIGHT,
            K_LEFT:  LEFT,  K_a: LEFT,
            K_UP:    UP,    K_w: UP,
            K_DOWN:  DOWN,  K_s: DOWN,
        }
        new = mapping.get(key)
        if new is None:
            return
        if new[0] + self.direction[0] != 0 or new[1] + self.direction[1] != 0:
            self.next_dir = new

    # ── movement ───────────────────────────────────────────────────────────
    def move(self):
        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy  = self.direction
        new_head = (hx + dx, hy + dy)
        self.body.insert(0, new_head)
        if self.grew:
            self.grew = False
        else:
            self.body.pop()

    def grow(self):
        self.grew = True

    def shorten(self, n: int) -> bool:
        """Remove n tail segments. Returns False if snake dies (len ≤ 1)."""
        for _ in range(n):
            if len(self.body) <= 1:
                return False
            self.body.pop()
        return len(self.body) > 1

    # ── power-up ───────────────────────────────────────────────────────────
    def apply_effect(self, kind: str):
        self.effect        = kind
        self.effect_end_ms = pygame.time.get_ticks() + POWERUP_EFFECT_TTL
        if kind == PU_SHIELD:
            self.shield_active = True
            self.effect        = None   # shield has no timed expiry display

    def tick_effect(self):
        if self.effect and pygame.time.get_ticks() > self.effect_end_ms:
            self.effect = None

    def speed_multiplier(self) -> float:
        if self.effect == PU_SPEED:
            return SPEED_BOOST_FACTOR
        if self.effect == PU_SLOW:
            return SLOW_FACTOR
        return 1.0

    # ── collision ──────────────────────────────────────────────────────────
    def hits_wall(self) -> bool:
        hx, hy = self.body[0]
        return not (0 <= hx < COLS and 0 <= hy < ROWS)

    def hits_self(self) -> bool:
        return self.body[0] in self.body[1:]

    def is_dead(self, obstacles: ObstacleManager | None = None) -> bool:
        if self.hits_wall() or self.hits_self():
            if obstacles and obstacles.hits(self.body[0]):
                # obstacle collision ignored by shield
                pass
            if self.shield_active:
                # absorb one fatal hit
                self.shield_active = False
                # teleport head back by reversing last move
                self.body.pop(0)
                return False
            return True
        if obstacles and obstacles.hits(self.body[0]):
            if self.shield_active:
                self.shield_active = False
                self.body.pop(0)
                return False
            return True
        return False

    # ── rendering ──────────────────────────────────────────────────────────
    def _tinted(self, surf: pygame.Surface, color: tuple) -> pygame.Surface:
        key = (id(surf), color)
        if key not in self._tint_cache:
            tinted = surf.copy()
            tinted.fill(color, special_flags=pygame.BLEND_MULT)
            self._tint_cache[key] = tinted
        return self._tint_cache[key]

    def _choose_segment(self, idx: int) -> pygame.Surface:
        raw = self.raw
        if idx == 0:
            angle_map = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: -90}
            return rot_img(raw[self.HEAD], angle_map[self.direction])
        if idx == len(self.body) - 1:
            px, py = self.body[idx - 1]
            tx, ty = self.body[idx]
            d = (tx - px, ty - py)
            angle_map = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: -90}
            return rot_img(raw[self.TAIL], angle_map.get(d, 0))
        prev  = self.body[idx - 1]
        curr  = self.body[idx]
        nxt   = self.body[idx + 1]
        from_d = (curr[0] - prev[0], curr[1] - prev[1])
        to_d   = (nxt[0]  - curr[0], nxt[1]  - curr[1])
        if from_d == to_d:
            return rot_img(raw[self.BODY], 0 if from_d in (RIGHT, LEFT) else 90)
        pair = (from_d, to_d)
        if pair in ((RIGHT, DOWN), (UP,    LEFT )):  return rot_img(raw[self.S2], 0)
        if pair in ((RIGHT, UP  ), (DOWN,  LEFT )):  return rot_img(raw[self.S3], 90)
        if pair in ((LEFT,  DOWN), (UP,    RIGHT)):  return rot_img(raw[self.S3], -90)
        if pair in ((LEFT,  UP  ), (DOWN,  RIGHT)):  return rot_img(raw[self.S2], 180)
        return rot_img(raw[self.BODY], 0)

    def draw(self, surface: pygame.Surface):
        color = S.snake_color()
        shield_flash = self.shield_active and (pygame.time.get_ticks() // 200 % 2 == 0)
        for i, (col, row) in enumerate(self.body):
            sprite = self._choose_segment(i)
            # apply tint only if color differs from white
            if color != (255, 255, 255):
                sprite = self._tinted(sprite, color)
            if shield_flash:
                glow = sprite.copy()
                glow.fill((80, 160, 255), special_flags=pygame.BLEND_ADD)
                sprite = glow
            surface.blit(sprite, (col * TILE, row * TILE))


# ═════════════════════════════════════════════════════════════════════════════
# HUD helpers
# ═════════════════════════════════════════════════════════════════════════════

def draw_hud(surface: pygame.Surface, score: int, level: int,
             personal_best: int = 0,
             snake: Snake = None):
    font_big   = pygame.font.SysFont("Verdana", 16, bold=True)
    font_small = pygame.font.SysFont("Verdana", 12)

    lines = [
        (font_big,   f"Score: {score}",     YELLOW),
        (font_small, f"Level: {level}",      WHITE),
        (font_small, f"Best:  {personal_best}", (180, 255, 180)),
    ]
    shadow = 1
    y = 4
    for font, text, color in lines:
        # shadow
        sh = font.render(text, True, BLACK)
        surface.blit(sh, (5 + shadow, y + shadow))
        # main
        tx = font.render(text, True, color)
        surface.blit(tx, (5, y))
        y += tx.get_height() + 2

    # Active effect indicator
    if snake and snake.effect:
        eff_colors = {PU_SPEED: (255, 140, 0), PU_SLOW: (0, 220, 220)}
        eff_labels = {PU_SPEED: "SPEED BOOST", PU_SLOW: "SLOW MOTION"}
        remaining  = max(0, snake.effect_end_ms - pygame.time.get_ticks()) // 1000
        label = f"{eff_labels.get(snake.effect, snake.effect)} {remaining}s"
        ef = font_small.render(label, True, eff_colors.get(snake.effect, WHITE))
        surface.blit(ef, (SCREEN_WIDTH - ef.get_width() - 4, 4))

    # Shield indicator
    if snake and snake.shield_active:
        sh_label = font_small.render("🛡 SHIELD", True, (80, 160, 255))
        surface.blit(sh_label, (SCREEN_WIDTH - sh_label.get_width() - 4, 18))


def draw_grid(surface: pygame.Surface):
    """Thin dark grid overlay (toggled in settings)."""
    grid_color = (0, 0, 0, 40)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for x in range(0, SCREEN_WIDTH, TILE):
        pygame.draw.line(overlay, grid_color, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, TILE):
        pygame.draw.line(overlay, grid_color, (0, y), (SCREEN_WIDTH, y))
    surface.blit(overlay, (0, 0))
