"""
ui.py
Pure-Pygame screens: MainMenu, NameEntry, SettingsScreen, GameOverScreen,
LeaderboardScreen.  No external UI libraries are used.
"""

import pygame
import sys
from pygame.locals import *
from persistence import load_leaderboard, save_settings

# ── palette ───────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (90,  90,  90)
LGRAY  = (190, 190, 190)
DGRAY  = (32,  32,  38)
RED    = (210, 45,  45)
GREEN  = (45,  180, 45)
BLUE   = (40,  105, 215)
YELLOW = (255, 210,   0)
ORANGE = (240, 135,   0)
TEAL   = (0,   170, 160)

SCREEN_W, SCREEN_H = 400, 600


# ══════════════════════════════════════════════════════════════════════════════
#   SHARED HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _hover(rect: pygame.Rect) -> bool:
    return rect.collidepoint(pygame.mouse.get_pos())


def draw_button(surface: pygame.Surface,
                rect: pygame.Rect,
                text: str,
                font: pygame.font.Font,
                color=GRAY,
                text_color=WHITE,
                hover: bool = False) -> None:
    bg = tuple(min(255, v + 35) for v in color) if hover else color
    pygame.draw.rect(surface, bg,    rect, border_radius=9)
    pygame.draw.rect(surface, WHITE, rect, 2, border_radius=9)
    lbl = font.render(text, True, text_color)
    surface.blit(lbl, lbl.get_rect(center=rect.center))


def draw_shadow_text(surface: pygame.Surface,
                     text: str,
                     font: pygame.font.Font,
                     color,
                     center: tuple,
                     shadow_color=BLACK) -> None:
    for dx, dy in ((2, 2), (-1, -1)):
        sh = font.render(text, True, shadow_color)
        surface.blit(sh, sh.get_rect(center=(center[0] + dx, center[1] + dy)))
    s = font.render(text, True, color)
    surface.blit(s, s.get_rect(center=center))


# ══════════════════════════════════════════════════════════════════════════════
#   MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════

class MainMenu:
    _BUTTONS = [
        ("play",        "Play",        GREEN),
        ("leaderboard", "Leaderboard", BLUE),
        ("settings",    "Settings",    ORANGE),
        ("quit",        "Quit",        RED),
    ]

    def __init__(self, screen: pygame.Surface):
        self.screen     = screen
        self.font_title = pygame.font.SysFont("Verdana", 46, bold=True)
        self.font_sub   = pygame.font.SysFont("Verdana", 16)
        self.font_btn   = pygame.font.SysFont("Verdana", 21)
        self.rects = {
            key: pygame.Rect(100, 195 + i * 72, 200, 52)
            for i, (key, _, _) in enumerate(self._BUTTONS)
        }

    def run(self) -> str:
        clock = pygame.time.Clock()
        tick  = 0
        while True:
            clock.tick(60)
            tick += 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    for key, _, _ in self._BUTTONS:
                        if self.rects[key].collidepoint(event.pos):
                            return key
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        return "play"
                    if event.key == K_ESCAPE:
                        return "quit"

            # background gradient
            for y in range(SCREEN_H):
                ratio = y / SCREEN_H
                r = int(20 + 15 * ratio)
                g = int(20 + 10 * ratio)
                b = int(35 + 25 * ratio)
                pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_W, y))

            # animated subtitle stripes
            for i in range(8):
                alpha  = abs((tick + i * 15) % 120 - 60) / 60
                color  = tuple(int(c * alpha * 0.4) for c in YELLOW)
                y_pos  = (tick * 2 + i * 80) % (SCREEN_H + 80) - 80
                pygame.draw.line(self.screen, color, (0, y_pos), (SCREEN_W, y_pos + 20), 3)

            draw_shadow_text(self.screen, "RACER", self.font_title, YELLOW,
                             (SCREEN_W // 2, 110))
            sub = self.font_sub.render("Dodge  ·  Collect  ·  Survive", True, LGRAY)
            self.screen.blit(sub, sub.get_rect(center=(SCREEN_W // 2, 160)))

            for key, label, color in self._BUTTONS:
                draw_button(self.screen, self.rects[key], label,
                            self.font_btn, color, hover=_hover(self.rects[key]))

            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#   NAME ENTRY
# ══════════════════════════════════════════════════════════════════════════════

class NameEntry:
    def __init__(self, screen: pygame.Surface):
        self.screen   = screen
        self.font_lg  = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_md  = pygame.font.SysFont("Verdana", 21)
        self.font_sm  = pygame.font.SysFont("Verdana", 15)
        self.name     = ""
        self.box      = pygame.Rect(70, 270, 260, 48)
        self.btn_ok   = pygame.Rect(110, 350, 180, 48)
        self.btn_back = pygame.Rect(110, 415, 180, 44)

    def run(self) -> str | None:
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        name = self.name.strip()
                        return name if name else None
                    elif event.key == K_BACKSPACE:
                        self.name = self.name[:-1]
                    elif event.key == K_ESCAPE:
                        return None
                    elif len(self.name) < 16 and event.unicode.isprintable():
                        self.name += event.unicode
                if event.type == MOUSEBUTTONDOWN:
                    if self.btn_ok.collidepoint(event.pos):
                        name = self.name.strip()
                        return name if name else None
                    if self.btn_back.collidepoint(event.pos):
                        return None

            self.screen.fill(DGRAY)

            draw_shadow_text(self.screen, "Enter Your Name",
                             self.font_lg, YELLOW, (SCREEN_W // 2, 170))

            hint = self.font_sm.render("max 16 characters  ·  press Enter to start",
                                       True, LGRAY)
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_W // 2, 215)))

            # input box
            pygame.draw.rect(self.screen, WHITE,  self.box, border_radius=7)
            pygame.draw.rect(self.screen, YELLOW, self.box, 2, border_radius=7)
            display = self.name + ("|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " ")
            ns = self.font_md.render(display, True, BLACK)
            self.screen.blit(ns, ns.get_rect(center=self.box.center))

            ok_color = GREEN if self.name.strip() else GRAY
            draw_button(self.screen, self.btn_ok,   "Start",   self.font_sm,
                        ok_color, hover=_hover(self.btn_ok))
            draw_button(self.screen, self.btn_back, "Back",    self.font_sm,
                        GRAY,     hover=_hover(self.btn_back))

            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#   GAME OVER SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class GameOverScreen:
    def __init__(self, screen: pygame.Surface,
                 score: int, distance: float, coins: int):
        self.screen   = screen
        self.score    = score
        self.distance = distance
        self.coins    = coins
        self.font_lg  = pygame.font.SysFont("Verdana", 36, bold=True)
        self.font_md  = pygame.font.SysFont("Verdana", 22)
        self.font_sm  = pygame.font.SysFont("Verdana", 16)
        self.btn_retry = pygame.Rect(50,  460, 140, 50)
        self.btn_menu  = pygame.Rect(210, 460, 140, 50)

    def run(self) -> str:
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if self.btn_retry.collidepoint(event.pos):
                        return "retry"
                    if self.btn_menu.collidepoint(event.pos):
                        return "menu"
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        return "retry"
                    if event.key == K_ESCAPE:
                        return "menu"

            self.screen.fill((55, 8, 8))

            draw_shadow_text(self.screen, "GAME OVER",
                             self.font_lg, RED, (SCREEN_W // 2, 120))

            stats = [
                ("Score",    f"{self.score}",         YELLOW),
                ("Distance", f"{self.distance:.0f} m", WHITE),
                ("Coins",    f"{self.coins}",          LGRAY),
            ]
            for i, (label, val, color) in enumerate(stats):
                lbl = self.font_sm.render(label + ":", True, LGRAY)
                self.screen.blit(lbl, (90, 210 + i * 64))
                vs  = self.font_md.render(val, True, color)
                self.screen.blit(vs,  (230, 208 + i * 64))

            pygame.draw.line(self.screen, GRAY, (60, 410), (340, 410), 1)

            draw_button(self.screen, self.btn_retry, "Retry [R]",    self.font_sm,
                        GREEN, hover=_hover(self.btn_retry))
            draw_button(self.screen, self.btn_menu,  "Menu [Esc]",   self.font_sm,
                        GRAY,  hover=_hover(self.btn_menu))

            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#   LEADERBOARD SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class LeaderboardScreen:
    def __init__(self, screen: pygame.Surface):
        self.screen   = screen
        self.font_lg  = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_md  = pygame.font.SysFont("Verdana", 17)
        self.font_sm  = pygame.font.SysFont("Verdana", 14)
        self.btn_back = pygame.Rect(125, 548, 150, 44)

    def run(self) -> None:
        entries = load_leaderboard()
        clock   = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if self.btn_back.collidepoint(event.pos):
                        return
                if event.type == KEYDOWN:
                    if event.key in (K_ESCAPE, K_RETURN, K_BACKSPACE):
                        return

            self.screen.fill(DGRAY)
            draw_shadow_text(self.screen, "LEADERBOARD",
                             self.font_lg, YELLOW, (SCREEN_W // 2, 42))

            # column header
            hdr = self.font_sm.render(
                f"{'#':<3}  {'Name':<15}{'Score':>7}  {'Dist':>6}  {'Coins':>5}",
                True, LGRAY)
            self.screen.blit(hdr, (18, 78))
            pygame.draw.line(self.screen, LGRAY, (18, 96), (382, 96), 1)

            ROW_H   = 40
            MEDALS  = {0: YELLOW, 1: (210, 210, 210), 2: (200, 140, 60)}

            for i, e in enumerate(entries[:10]):
                color = MEDALS.get(i, WHITE)
                row   = self.font_sm.render(
                    (f"{i+1:<3}  "
                     f"{str(e.get('name','?'))[:15]:<15}"
                     f"{e.get('score',0):>7}  "
                     f"{int(e.get('distance',0)):>5}m  "
                     f"{e.get('coins',0):>5}"),
                    True, color)
                self.screen.blit(row, (18, 104 + i * ROW_H))

            if not entries:
                msg = self.font_md.render("No scores yet — go race!", True, GRAY)
                self.screen.blit(msg, msg.get_rect(center=(SCREEN_W // 2, 300)))

            draw_button(self.screen, self.btn_back, "Back [Esc]",
                        self.font_sm, GRAY, hover=_hover(self.btn_back))
            pygame.display.flip()


# ══════════════════════════════════════════════════════════════════════════════
#   SETTINGS SCREEN
# ══════════════════════════════════════════════════════════════════════════════

class SettingsScreen:
    _CYCLES = {
        "difficulty": ["easy", "medium", "hard"],
        "car_color":  ["green", "red"],
    }
    _DIFF_COLORS = {"easy": GREEN, "medium": ORANGE, "hard": RED}

    def __init__(self, screen: pygame.Surface, settings: dict):
        self.screen   = screen
        self.settings = dict(settings)   # work on a copy
        self.font_lg  = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_md  = pygame.font.SysFont("Verdana", 19)
        self.font_sm  = pygame.font.SysFont("Verdana", 16)
        self.btn_save = pygame.Rect(115, 500, 170, 48)

        # Row layout: (setting_key, display_label, type)
        self._rows = [
            ("sound",      "Sound",      "bool"),
            ("difficulty", "Difficulty", "cycle"),
            ("car_color",  "Car Colour", "cycle"),
        ]
        self._rects = {}
        for i, (key, _, _) in enumerate(self._rows):
            self._rects[key] = pygame.Rect(220, 155 + i * 90 - 20, 150, 40)

    def run(self) -> dict:
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit(); sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    for key, _, kind in self._rows:
                        if self._rects[key].collidepoint(event.pos):
                            self._toggle(key, kind)
                    if self.btn_save.collidepoint(event.pos):
                        save_settings(self.settings)
                        return self.settings
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    save_settings(self.settings)
                    return self.settings

            self.screen.fill(DGRAY)
            draw_shadow_text(self.screen, "SETTINGS",
                             self.font_lg, YELLOW, (SCREEN_W // 2, 62))

            for i, (key, label, kind) in enumerate(self._rows):
                y = 155 + i * 90
                # label
                lbl = self.font_md.render(label, True, LGRAY)
                self.screen.blit(lbl, (30, y - 10))

                # description hint
                if key == "sound":
                    hint = "Coin collect sound effect"
                elif key == "difficulty":
                    hint = "Affects speed & spawn rates"
                else:
                    hint = "Your player car colour"
                h = self.font_sm.render(hint, True, GRAY)
                self.screen.blit(h, (30, y + 14))

                # toggle button
                val   = self.settings.get(key)
                txt   = self._display_val(key, kind, val)
                color = self._button_color(key, kind, val)
                draw_button(self.screen, self._rects[key], txt, self.font_sm,
                            color, hover=_hover(self._rects[key]))

            pygame.draw.line(self.screen, GRAY, (30, 468), (370, 468), 1)
            hint2 = self.font_sm.render("Click a setting to cycle through options",
                                        True, GRAY)
            self.screen.blit(hint2, hint2.get_rect(center=(SCREEN_W // 2, 486)))

            draw_button(self.screen, self.btn_save, "Save & Back",
                        self.font_sm, TEAL, hover=_hover(self.btn_save))
            pygame.display.flip()

    def _toggle(self, key: str, kind: str):
        if kind == "bool":
            self.settings[key] = not self.settings.get(key, True)
        else:
            opts = self._CYCLES[key]
            cur  = self.settings.get(key, opts[0])
            idx  = opts.index(cur) if cur in opts else 0
            self.settings[key] = opts[(idx + 1) % len(opts)]

    @staticmethod
    def _display_val(key: str, kind: str, val) -> str:
        if kind == "bool":
            return "ON" if val else "OFF"
        return str(val).capitalize()

    def _button_color(self, key: str, kind: str, val) -> tuple:
        if kind == "bool":
            return GREEN if val else RED
        if key == "difficulty":
            return self._DIFF_COLORS.get(str(val), ORANGE)
        if key == "car_color":
            return (50, 160, 50) if val == "green" else (200, 50, 50)
        return BLUE
