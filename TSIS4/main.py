"""
main.py — Entry point.

Screens implemented (pure Pygame, no external UI libs):
    MainMenuScreen      — Play, Leaderboard, Settings, Quit
    UsernameScreen      — keyboard text entry
    GameScreen          — the actual game
    GameOverScreen      — score, level, personal best; Retry / Main Menu
    LeaderboardScreen   — Top-10 table; Back
    SettingsScreen      — grid toggle, sound toggle, snake color picker; Save & Back
"""

from __future__ import annotations
import sys
import random
import pygame
from pygame.locals import *

# ── project modules ───────────────────────────────────────────────────────────
import settings as S
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE, COLS, ROWS,
    FPS_RENDER, FPS_BASE, SPEED_STEP, FOOD_PER_LVL,
    OBSTACLE_START_LEVEL, OBSTACLES_PER_LEVEL, MAX_OBSTACLES,
    RIGHT, LEFT, UP, DOWN,
    BLACK, WHITE, YELLOW, RED, GREEN, GREY, DARK_GREY, GOLD,
    PU_SPEED, PU_SLOW, PU_SHIELD,
)
from game import (
    Snake, Apple, PoisonFood, PowerUp, ObstacleManager,
    load_background, draw_hud, draw_grid,
)
import db

pygame.init()
pygame.display.set_caption("Snake")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock  = pygame.time.Clock()

# ── Fonts ─────────────────────────────────────────────────────────────────────
F_TITLE  = pygame.font.SysFont("Verdana", 28, bold=True)
F_BIG    = pygame.font.SysFont("Verdana", 20, bold=True)
F_MED    = pygame.font.SysFont("Verdana", 16)
F_SMALL  = pygame.font.SysFont("Verdana", 13)

# ── Color palette ─────────────────────────────────────────────────────────────
BG_DARK   = (15,  25,  15)
BG_PANEL  = (25,  45,  25)
ACCENT    = (80, 200,  80)
ACCENT2   = (200, 220, 80)
HOVER_COL = (50, 130,  50)
TEXT_DIM  = (140, 170, 140)
BORDER    = (60,  100,  60)


# ══════════════════════════════════════════════════════════════════════════════
# Utility helpers
# ══════════════════════════════════════════════════════════════════════════════

def draw_text_centered(surface, text, font, color, cy, shadow=True):
    rendered = font.render(text, True, color)
    x = (SCREEN_WIDTH - rendered.get_width()) // 2
    if shadow:
        sh = font.render(text, True, BLACK)
        surface.blit(sh, (x + 1, cy + 1))
    surface.blit(rendered, (x, cy))
    return rendered.get_height()


def draw_panel(surface, rect, radius=8):
    pygame.draw.rect(surface, BG_PANEL, rect, border_radius=radius)
    pygame.draw.rect(surface, BORDER,   rect, 1, border_radius=radius)


class Button:
    def __init__(self, text, cx, cy, w=160, h=34, font=None):
        self.text   = text
        self.rect   = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.font   = font or F_MED
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        color = HOVER_COL if self.hovered else BG_PANEL
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, ACCENT, self.rect, 1, border_radius=6)
        txt = self.font.render(self.text, True, WHITE if self.hovered else ACCENT)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                            self.rect.centery - txt.get_height() // 2))

    def clicked(self, event) -> bool:
        return (event.type == MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


# ══════════════════════════════════════════════════════════════════════════════
# MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════

def main_menu_screen() -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    bg = load_background()
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))

    cx = SCREEN_WIDTH // 2
    btns = {
        "play":        Button("Play",        cx, 190),
        "leaderboard": Button("Leaderboard",  cx, 232, w=180),
        "settings":    Button("Settings",     cx, 274, w=160),
        "quit":        Button("Quit",          cx, 316),
    }

    # snake decoration — simple animated snake
    deco_x = 0
    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                pygame.quit(); sys.exit()
            for key, btn in btns.items():
                if btn.clicked(event):
                    return key

        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))

        # Title
        draw_text_centered(screen, "SNAKE", F_TITLE, ACCENT,  60)
        draw_text_centered(screen, "ULTIMATE EDITION", F_SMALL, TEXT_DIM, 96)

        # Animated deco dots
        deco_x = (deco_x + 1) % SCREEN_WIDTH
        for i in range(8):
            xi = (deco_x + i * 40) % SCREEN_WIDTH
            pygame.draw.circle(screen, (30, 100, 30), (xi, 140), 3)

        for btn in btns.values():
            btn.update(mouse)
            btn.draw(screen)

        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# USERNAME ENTRY
# ══════════════════════════════════════════════════════════════════════════════

def username_screen(default: str = "") -> str:
    """Blocking text-input screen. Returns entered username."""
    username = list(default)
    cursor_vis = True
    cursor_timer = 0
    error = ""

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    name = "".join(username).strip()
                    if name:
                        return name
                    error = "Please enter a name!"
                elif event.key == K_BACKSPACE:
                    if username:
                        username.pop()
                    error = ""
                elif event.key == K_ESCAPE:
                    return default or "Player"
                elif len(username) < 20:
                    ch = event.unicode
                    if ch.isprintable() and ch not in ('"', "'", "/", "\\"):
                        username.append(ch)
                        error = ""

        screen.fill(BG_DARK)
        panel = pygame.Rect(60, 130, 280, 140)
        draw_panel(screen, panel, radius=10)

        draw_text_centered(screen, "Enter Your Name", F_BIG, ACCENT, 145)

        # text box
        box = pygame.Rect(80, 192, 240, 34)
        pygame.draw.rect(screen, (10, 30, 10), box, border_radius=5)
        pygame.draw.rect(screen, ACCENT, box, 1, border_radius=5)

        cursor_timer += 1
        if cursor_timer > 30:
            cursor_vis   = not cursor_vis
            cursor_timer = 0

        display_text = "".join(username) + ("|" if cursor_vis else " ")
        txt_surf = F_MED.render(display_text, True, WHITE)
        screen.blit(txt_surf, (box.x + 6, box.y + 7))

        hint = F_SMALL.render("Press ENTER to confirm", True, TEXT_DIM)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 238))

        if error:
            err_surf = F_SMALL.render(error, True, RED)
            screen.blit(err_surf, (SCREEN_WIDTH // 2 - err_surf.get_width() // 2, 258))

        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# GAME SCREEN
# ══════════════════════════════════════════════════════════════════════════════

def game_screen(player_id: int, personal_best: int) -> dict:
    """
    Run one game session.
    Returns dict: {score, level, personal_best}
    """
    bg = load_background()

    snake   = Snake()
    apple   = Apple()
    poison  = PoisonFood()
    powerup = PowerUp()
    obs     = ObstacleManager()

    apple.respawn(snake.body)

    score      = 0
    level      = 1
    food_count = 0
    logic_fps  = FPS_BASE
    pb         = personal_best

    LOGIC_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(LOGIC_EVENT, 1000 // logic_fps)

    # spawn poison after 3 apples
    poison_threshold = 3

    # power-up spawn: every 15 s
    POWERUP_SPAWN_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(POWERUP_SPAWN_EVENT, 15_000)

    def _occupied():
        return snake.body + ([poison.grid_pos] if poison.active else []) + obs.blocks

    def _recalc_speed():
        nonlocal logic_fps
        base = FPS_BASE + (level - 1) * SPEED_STEP
        logic_fps = max(1, int(base * snake.speed_multiplier()))
        pygame.time.set_timer(LOGIC_EVENT, 1000 // logic_fps)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                snake.handle_key(event.key)
                if event.key == K_ESCAPE:
                    pygame.time.set_timer(LOGIC_EVENT, 0)
                    pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                    return {"score": score, "level": level, "personal_best": pb}

            if event.type == POWERUP_SPAWN_EVENT:
                if not powerup.active:
                    powerup.spawn(_occupied() + ([apple.grid_pos] if apple else []),
                                  obs.blocks)

            if event.type == LOGIC_EVENT:
                snake.tick_effect()
                _recalc_speed()   # re-evaluate speed each tick

                snake.move()

                # ── death check ───────────────────────────────────────────
                if snake.is_dead(obs):
                    pygame.time.set_timer(LOGIC_EVENT, 0)
                    pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                    # draw last frame
                    screen.blit(bg, (0, 0))
                    if S.grid_overlay(): draw_grid(screen)
                    obs.draw(screen)
                    apple.draw(screen)
                    if poison.active: poison.draw(screen)
                    if powerup.active: powerup.draw(screen)
                    snake.draw(screen)
                    draw_hud(screen, score, level, pb, snake)
                    pygame.display.update()
                    pygame.time.wait(300)
                    # save to DB
                    db.save_session(player_id, score, level)
                    pb = max(pb, score)
                    return {"score": score, "level": level, "personal_best": pb}

                head = snake.body[0]

                # ── apple ──────────────────────────────────────────────────
                if head == apple.grid_pos:
                    snake.grow()
                    score      += 10 * level
                    food_count += 1
                    pb = max(pb, score)

                    if food_count >= FOOD_PER_LVL:
                        level      += 1
                        food_count  = 0
                        # new obstacles
                        if level >= OBSTACLE_START_LEVEL:
                            n = min(OBSTACLES_PER_LEVEL,
                                    MAX_OBSTACLES - len(obs.blocks))
                            obs.generate_for_level(level, snake.body, n)
                        _recalc_speed()

                    apple.respawn(_occupied(), obs.blocks)

                    # maybe spawn poison
                    if score // (10 * level) >= poison_threshold and not poison.active:
                        poison.respawn(_occupied() + [apple.grid_pos], obs.blocks)

                # ── poison ─────────────────────────────────────────────────
                if poison.active and head == poison.grid_pos:
                    poison.active = False
                    if not snake.shorten(2):
                        # snake too short → game over
                        pygame.time.set_timer(LOGIC_EVENT, 0)
                        pygame.time.set_timer(POWERUP_SPAWN_EVENT, 0)
                        db.save_session(player_id, score, level)
                        pb = max(pb, score)
                        return {"score": score, "level": level, "personal_best": pb}

                # ── power-up ───────────────────────────────────────────────
                if powerup.active and head == powerup.grid_pos:
                    snake.apply_effect(powerup.kind)
                    powerup.active = False
                    _recalc_speed()

        # ── update ────────────────────────────────────────────────────────
        apple.update()
        powerup.update()

        # ── render ────────────────────────────────────────────────────────
        screen.blit(bg, (0, 0))
        if S.grid_overlay():
            draw_grid(screen)
        obs.draw(screen)
        apple.draw(screen)
        if poison.active:
            poison.draw(screen)
        if powerup.active:
            powerup.draw(screen)
        snake.draw(screen)
        draw_hud(screen, score, level, pb, snake)

        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# GAME OVER
# ══════════════════════════════════════════════════════════════════════════════

def game_over_screen(score: int, level: int, personal_best: int) -> str:
    """Returns 'retry' | 'menu'"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    cx = SCREEN_WIDTH // 2
    btn_retry = Button("Retry",    cx - 90, 290, w=150)
    btn_menu  = Button("Main Menu", cx + 90, 290, w=150)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.clicked(event) or (event.type == KEYDOWN and event.key == K_r):
                return "retry"
            if btn_menu.clicked(event) or (event.type == KEYDOWN and event.key == K_m):
                return "menu"
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return "menu"

        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(70, 100, 260, 210)
        draw_panel(screen, panel, radius=12)

        draw_text_centered(screen, "GAME OVER",        F_TITLE, RED,    115)
        draw_text_centered(screen, f"Score : {score}", F_BIG,   YELLOW, 155)
        draw_text_centered(screen, f"Level : {level}", F_MED,   WHITE,  183)
        draw_text_centered(screen, f"Best  : {personal_best}", F_MED, (180, 255, 180), 207)

        btn_retry.update(mouse); btn_retry.draw(screen)
        btn_menu.update(mouse);  btn_menu.draw(screen)

        hint = F_SMALL.render("R — Retry   M — Menu", True, TEXT_DIM)
        screen.blit(hint, (cx - hint.get_width() // 2, 320))

        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# LEADERBOARD
# ══════════════════════════════════════════════════════════════════════════════

def leaderboard_screen():
    rows = db.get_top10()
    btn_back = Button("Back", SCREEN_WIDTH // 2, 370, w=120)

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if btn_back.clicked(event):
                return
            if event.type == KEYDOWN and event.key in (K_ESCAPE, K_b):
                return

        screen.fill(BG_DARK)
        draw_text_centered(screen, "LEADERBOARD", F_BIG, GOLD, 12)

        # table header
        header_y = 50
        cols_x   = [18, 48, 138, 228, 298]
        headers  = ["#", "Name", "Score", "Lvl", "Date"]
        for i, (hx, hdr) in enumerate(zip(cols_x, headers)):
            hs = F_SMALL.render(hdr, True, ACCENT)
            screen.blit(hs, (hx, header_y))
        pygame.draw.line(screen, BORDER, (10, 66), (SCREEN_WIDTH - 10, 66), 1)

        if not rows:
            no_data = F_MED.render("No records yet.", True, TEXT_DIM)
            screen.blit(no_data, (SCREEN_WIDTH // 2 - no_data.get_width() // 2, 160))
        else:
            for i, row in enumerate(rows):
                y    = 72 + i * 28
                bg_c = (20, 40, 20) if i % 2 == 0 else (15, 30, 15)
                pygame.draw.rect(screen, bg_c, (10, y, SCREEN_WIDTH - 20, 26),
                                 border_radius=3)

                date_str = (row["played_at"].strftime("%m/%d")
                            if row["played_at"] else "—")
                rank_col = GOLD if row["rank"] <= 3 else WHITE
                cells    = [
                    (str(row["rank"]),         rank_col),
                    (row["username"][:12],      WHITE),
                    (str(row["score"]),         YELLOW),
                    (str(row["level_reached"]), GREEN),
                    (date_str,                  TEXT_DIM),
                ]
                for cx_, (text, color) in zip(cols_x, cells):
                    ts = F_SMALL.render(text, True, color)
                    screen.blit(ts, (cx_, y + 6))

        btn_back.update(mouse)
        btn_back.draw(screen)
        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════════════════════════

_COLOR_PRESETS = [
    ("Green",   (0,   200,  80)),
    ("Lime",    (120, 255,  50)),
    ("Blue",    (40,  120, 255)),
    ("Yellow",  (255, 215,   0)),
    ("Orange",  (255, 140,   0)),
    ("Pink",    (255,  80, 180)),
    ("White",   (230, 230, 230)),
    ("Red",     (220,  60,  60)),
]


def settings_screen():
    S.load()
    grid_on  = S.grid_overlay()
    sound_on = S.sound_on()
    chosen   = list(S.snake_color())

    btn_save = Button("Save & Back", SCREEN_WIDTH // 2, 360, w=180)

    # color swatches
    swatch_rects = []
    swatch_y = 240
    for idx, (name, color) in enumerate(_COLOR_PRESETS):
        col = idx % 4
        row = idx // 4
        rx = 30 + col * 86
        ry = swatch_y + row * 44
        swatch_rects.append(pygame.Rect(rx, ry, 70, 32))

    while True:
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # toggle grid
                if grid_toggle_rect.collidepoint(event.pos):
                    grid_on = not grid_on
                # toggle sound
                if sound_toggle_rect.collidepoint(event.pos):
                    sound_on = not sound_on
                # color swatch
                for idx, sr in enumerate(swatch_rects):
                    if sr.collidepoint(event.pos):
                        chosen = list(_COLOR_PRESETS[idx][1])
            if btn_save.clicked(event):
                S.set_value("grid_overlay", grid_on)
                S.set_value("sound",        sound_on)
                S.set_value("snake_color",  chosen)
                S.save()
                return

        screen.fill(BG_DARK)
        draw_text_centered(screen, "SETTINGS", F_BIG, ACCENT, 12)

        # ── Grid overlay toggle ─────────────────────────────────────────
        y = 60
        lbl = F_MED.render("Grid Overlay", True, WHITE)
        screen.blit(lbl, (30, y))
        grid_toggle_rect = pygame.Rect(SCREEN_WIDTH - 80, y - 2, 60, 28)
        gc = (50, 180, 50) if grid_on else DARK_GREY
        pygame.draw.rect(screen, gc, grid_toggle_rect, border_radius=14)
        pygame.draw.rect(screen, ACCENT, grid_toggle_rect, 1, border_radius=14)
        ts = F_SMALL.render("ON" if grid_on else "OFF", True, WHITE)
        screen.blit(ts, (grid_toggle_rect.centerx - ts.get_width() // 2,
                          grid_toggle_rect.centery - ts.get_height() // 2))

        # ── Sound toggle ────────────────────────────────────────────────
        y = 108
        lbl = F_MED.render("Sound", True, WHITE)
        screen.blit(lbl, (30, y))
        sound_toggle_rect = pygame.Rect(SCREEN_WIDTH - 80, y - 2, 60, 28)
        sc = (50, 180, 50) if sound_on else DARK_GREY
        pygame.draw.rect(screen, sc, sound_toggle_rect, border_radius=14)
        pygame.draw.rect(screen, ACCENT, sound_toggle_rect, 1, border_radius=14)
        ts2 = F_SMALL.render("ON" if sound_on else "OFF", True, WHITE)
        screen.blit(ts2, (sound_toggle_rect.centerx - ts2.get_width() // 2,
                           sound_toggle_rect.centery - ts2.get_height() // 2))

        # ── Color picker ─────────────────────────────────────────────────
        y = 156
        lbl = F_MED.render("Snake Color", True, WHITE)
        screen.blit(lbl, (30, y))

        # preview swatch
        prev = pygame.Surface((40, 20))
        prev.fill(chosen)
        screen.blit(prev, (SCREEN_WIDTH - 70, y))
        pygame.draw.rect(screen, ACCENT, (SCREEN_WIDTH - 71, y - 1, 42, 22), 1)

        hint = F_SMALL.render("Pick a color:", True, TEXT_DIM)
        screen.blit(hint, (30, 218))

        for idx, (name, color) in enumerate(_COLOR_PRESETS):
            sr = swatch_rects[idx]
            pygame.draw.rect(screen, color, sr, border_radius=5)
            is_chosen = list(color) == list(chosen)
            border_c  = WHITE if is_chosen else BORDER
            thickness = 2 if is_chosen else 1
            pygame.draw.rect(screen, border_c, sr, thickness, border_radius=5)
            n_surf = F_SMALL.render(name, True, WHITE if is_chosen else TEXT_DIM)
            screen.blit(n_surf, (sr.x + sr.w // 2 - n_surf.get_width() // 2,
                                  sr.y + sr.h // 2 - n_surf.get_height() // 2))

        btn_save.update(mouse)
        btn_save.draw(screen)
        pygame.display.update()
        clock.tick(FPS_RENDER)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    S.load()
    db.init_db()

    # Ask for username once
    username   = username_screen()
    player_id  = db.get_or_create_player(username)
    pb         = db.get_personal_best(player_id)

    while True:
        action = main_menu_screen()

        if action == "quit":
            break
        elif action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings_screen()
        elif action == "play":
            while True:
                result = game_screen(player_id, pb)
                pb     = result["personal_best"]
                action = game_over_screen(result["score"], result["level"], pb)
                if action == "menu":
                    break
                # else retry → loop

    db.close_db()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
