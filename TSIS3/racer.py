"""
racer.py
Sprite classes (Player, Enemy, Coin, hazards, power-ups) and the Game class
that runs one play session and returns the final result dict.
"""

import pygame
import random
import os
from pygame.locals import *

# ── asset helper ───────────────────────────────────────────────────────────────
# Always resolve paths relative to THIS file, regardless of where the script
# is launched from (e.g. python TSIS3/main.py from the parent folder).
_BASE   = os.path.dirname(os.path.abspath(__file__))
ASSETS  = os.path.join(_BASE, "assets")


def asset(name: str) -> str:
    return os.path.join(ASSETS, name)


# ── layout constants ───────────────────────────────────────────────────────────
SCREEN_W   = 400
SCREEN_H   = 600
FPS        = 60
ROAD_LEFT  = 72
ROAD_RIGHT = 328
ROAD_MID   = (ROAD_LEFT + ROAD_RIGHT) // 2

COINS_FOR_SPEED  = 10   # coin milestones that trigger a speed bump
POWERUP_LIFETIME = 480  # frames a power-up stays on screen
NITRO_DURATION   = 240  # frames for nitro boost (4 s)
OIL_DURATION     = 200  # frames of slow from oil spill

# ── colors ─────────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (210, 45,  45)
GREEN  = (45,  180, 45)
BLUE   = (45,  110, 220)
YELLOW = (255, 215,   0)
ORANGE = (255, 140,   0)
PURPLE = (150,  30, 230)
GRAY   = (110, 110, 110)
LGRAY  = (190, 190, 190)
TEAL   = (0,   175, 165)
DARK   = (25,  25,  25)

# ── difficulty profiles ────────────────────────────────────────────────────────
DIFF = {
    "easy":   {"speed": 4,   "speed_inc": 0.20, "enemy_every": 280, "obs_every": 450, "max_enemies": 2, "max_obs": 2},
    "medium": {"speed": 5,   "speed_inc": 0.35, "enemy_every": 200, "obs_every": 300, "max_enemies": 3, "max_obs": 3},
    "hard":   {"speed": 7,   "speed_inc": 0.55, "enemy_every": 120, "obs_every": 190, "max_enemies": 5, "max_obs": 5},
}


# ══════════════════════════════════════════════════════════════════════════════
#   UTILITY
# ══════════════════════════════════════════════════════════════════════════════

def rand_road_x(margin: int = 22) -> int:
    return random.randint(ROAD_LEFT + margin, ROAD_RIGHT - margin)


def rand_x_clear_of(px: int, radius: int = 55) -> int:
    """Return a road x-coord that is not within *radius* pixels of *px*."""
    for _ in range(25):
        x = rand_road_x()
        if abs(x - px) > radius:
            return x
    return rand_road_x()   # fallback (very rare)


def rand_top_y() -> int:
    return random.randint(-350, -60)


# ══════════════════════════════════════════════════════════════════════════════
#   SPRITES — traffic / collectibles
# ══════════════════════════════════════════════════════════════════════════════

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color: str = "green"):
        super().__init__()
        fname = "CarGreenFront.png" if car_color == "green" else "CarRedFront.png"
        self.image = pygame.image.load(asset(fname)).convert_alpha()
        self.rect  = self.image.get_rect(center=(ROAD_MID, 520))

        self.shielded  = False
        self.oiled     = False
        self._oil_tmr  = 0

    # ── movement ───────────────────────────────────────────────────────────────
    def move(self):
        pressed = pygame.key.get_pressed()
        step    = 3 if self.oiled else 5
        if pressed[K_LEFT]  and self.rect.left  > ROAD_LEFT:
            self.rect.x -= step
        if pressed[K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.x += step
        # oil countdown
        if self.oiled:
            self._oil_tmr -= 1
            if self._oil_tmr <= 0:
                self.oiled = False

    def apply_oil(self):
        if not self.shielded:
            self.oiled    = True
            self._oil_tmr = OIL_DURATION

    def repair(self):
        """Instant-clear oil slow."""
        self.oiled    = False
        self._oil_tmr = 0

    def consume_shield(self) -> bool:
        """Use the shield to survive a collision. Returns True if it was active."""
        if self.shielded:
            self.shielded = False
            return True
        return False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed: float, px: int):
        super().__init__()
        self.image = pygame.image.load(asset("CarRedFront.png")).convert_alpha()
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._place(px)

    def _place(self, px: int = ROAD_MID):
        self.rect.center = (rand_x_clear_of(px), rand_top_y())

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            self.rect.center = (rand_road_x(), rand_top_y())


class Coin(pygame.sprite.Sprite):
    _FRAMES = ["KBGU4713.PNG", "DRGF5324.PNG", "FURF8350.PNG", "GXNF9041.PNG"]

    def __init__(self, speed: float, px: int):
        super().__init__()
        self.frames      = [pygame.image.load(asset(f)).convert_alpha() for f in self._FRAMES]
        self.frame_i     = 0
        self.anim_timer  = 0
        self.anim_speed  = 7
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect()
        self.speed       = speed
        self.value       = 1
        self._font       = pygame.font.SysFont("Verdana", 15, bold=True)
        self._place(px)

    def _place(self, px: int = ROAD_MID):
        self.value        = random.choices([1, 3, 5], weights=[70, 20, 10])[0]
        self.rect.center  = (rand_x_clear_of(px, 40), rand_top_y())

    def respawn(self, speed: float, px: int):
        self.speed = speed
        self._place(px)

    def update(self):
        self.rect.y     += self.speed
        self.anim_timer += 1
        if self.anim_timer >= self.anim_speed:
            self.anim_timer  = 0
            self.frame_i     = (self.frame_i + 1) % len(self.frames)
            self.image       = self.frames[self.frame_i]
        if self.rect.top > SCREEN_H + 10:
            self._place()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)
        lbl = self._font.render(str(self.value), True, BLACK)
        surface.blit(lbl, (self.rect.x + 1, self.rect.y - 16))


# ══════════════════════════════════════════════════════════════════════════════
#   SPRITES — hazards
# ══════════════════════════════════════════════════════════════════════════════

class OilSpill(pygame.sprite.Sprite):
    """Slows the player for OIL_DURATION frames."""

    def __init__(self, speed: float):
        super().__init__()
        self.image = pygame.Surface((52, 26), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (18, 18, 18, 210), (0, 0, 52, 26))
        pygame.draw.ellipse(self.image, (90, 0, 140, 90),  (7, 5, 38, 16))
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._place()

    def _place(self):
        self.rect.center = (rand_road_x(28), rand_top_y())

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            self._place()


class Barrier(pygame.sprite.Sprite):
    """Orange road barrier — deadly on contact."""

    def __init__(self, speed: float):
        super().__init__()
        self.image = pygame.Surface((13, 42))
        self.image.fill(ORANGE)
        pygame.draw.rect(self.image, WHITE, (2, 4, 9, 34), 2)
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._place()

    def _place(self):
        self.rect.center = (rand_road_x(18), rand_top_y())

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            self._place()


class Pothole(pygame.sprite.Sprite):
    """Dark pit in the road — deadly on contact."""

    def __init__(self, speed: float):
        super().__init__()
        self.image = pygame.Surface((34, 22), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (22, 12, 4, 235), (0, 0, 34, 22))
        pygame.draw.ellipse(self.image, (10, 5,  0, 160), (6, 4, 22, 14))
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._place()

    def _place(self):
        self.rect.center = (rand_road_x(18), rand_top_y())

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            self._place()


class MovingBarrier(pygame.sprite.Sprite):
    """Red barrier that sweeps left–right across the road."""

    def __init__(self, speed: float):
        super().__init__()
        self.image = pygame.Surface((62, 16))
        self.image.fill(RED)
        pygame.draw.rect(self.image, WHITE, (0, 6, 62, 4))
        self.rect    = self.image.get_rect()
        self.speed   = speed
        self.h_dir   = random.choice([-1, 1])
        self.h_speed = 2
        self._place()

    def _place(self):
        self.rect.center = (ROAD_MID, rand_top_y())

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.h_dir * self.h_speed
        if self.rect.left < ROAD_LEFT or self.rect.right > ROAD_RIGHT:
            self.h_dir *= -1
        if self.rect.top > SCREEN_H + 10:
            self._place()


class NitroStrip(pygame.sprite.Sprite):
    """Yellow chevron strip painted on the road — grants a nitro boost."""

    def __init__(self, speed: float):
        super().__init__()
        w = ROAD_RIGHT - ROAD_LEFT
        self.image = pygame.Surface((w, 16), pygame.SRCALPHA)
        for i in range(0, w, 22):
            pygame.draw.rect(self.image, (255, 215, 0, 190), (i, 0, 13, 16))
        self.rect  = self.image.get_rect()
        self.speed = speed
        self._hide()

    def _hide(self):
        """Push far above screen; only ~30% chance to respawn after passing."""
        self.rect.topleft = (ROAD_LEFT, -SCREEN_H * 4)

    def activate(self):
        """Spawn on screen."""
        self.rect.topleft = (ROAD_LEFT, rand_top_y() - 200)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_H + 10:
            if random.random() < 0.30:
                self.activate()
            else:
                self._hide()


# ══════════════════════════════════════════════════════════════════════════════
#   SPRITES — power-ups
# ══════════════════════════════════════════════════════════════════════════════

class PowerUp(pygame.sprite.Sprite):
    _INFO = {
        "nitro":  (BLUE,  "N"),
        "shield": (TEAL,  "S"),
        "repair": (GREEN, "R"),
    }
    _FONT = None

    def __init__(self, speed: float):
        super().__init__()
        if PowerUp._FONT is None:
            PowerUp._FONT = pygame.font.SysFont("Verdana", 16, bold=True)
        self.speed = speed
        self.life  = POWERUP_LIFETIME
        self.ptype = "nitro"
        self._respawn()

    def _respawn(self):
        self.ptype = random.choice(list(self._INFO.keys()))
        color, letter = self._INFO[self.ptype]
        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (17, 17), 17)
        pygame.draw.circle(self.image, WHITE, (17, 17), 17, 2)
        lbl = self._FONT.render(letter, True, WHITE)
        self.image.blit(lbl, lbl.get_rect(center=(17, 17)))
        self.rect       = self.image.get_rect(center=(rand_road_x(20), rand_top_y()))
        self.life       = POWERUP_LIFETIME

    def update(self):
        self.rect.y += self.speed
        self.life   -= 1
        if self.rect.top > SCREEN_H + 10 or self.life <= 0:
            self._respawn()

    # Expose respawn publicly so Game can call it after collection
    def respawn(self):
        self._respawn()


# ══════════════════════════════════════════════════════════════════════════════
#   GAME
# ══════════════════════════════════════════════════════════════════════════════

class Game:
    def __init__(self, screen: pygame.Surface, settings: dict, player_name: str):
        self.screen      = screen
        self.settings    = settings
        self.player_name = player_name
        self.clock       = pygame.time.Clock()

        cfg              = DIFF[settings.get("difficulty", "medium")]
        self.speed       = cfg["speed"]
        self.speed_inc   = cfg["speed_inc"]
        self.enemy_every = cfg["enemy_every"]
        self.obs_every   = cfg["obs_every"]
        self.max_enemies = cfg["max_enemies"]
        self.max_obs     = cfg["max_obs"]

        self._load_assets()
        self._build_scene()

    # ── asset loading ──────────────────────────────────────────────────────────
    def _load_assets(self):
        self.bg        = pygame.image.load(asset("pixel_art_road_green_land.png")).convert()
        self.bg_h      = self.bg.get_height()
        self.bg_y      = 0
        self.sound_on  = self.settings.get("sound", True)
        if self.sound_on:
            try:
                pygame.mixer.music.load(asset("coin_recieved.mp3"))
                pygame.mixer.music.set_volume(0.15)
            except Exception:
                self.sound_on = False
        self.fnt_sm = pygame.font.SysFont("Verdana", 15)
        self.fnt_md = pygame.font.SysFont("Verdana", 20)
        self.fnt_lg = pygame.font.SysFont("Verdana", 32, bold=True)

    # ── scene / sprite initialisation ─────────────────────────────────────────
    def _build_scene(self):
        px  = ROAD_MID
        col = self.settings.get("car_color", "green")

        self.player = Player(col)

        # traffic
        self.enemies = pygame.sprite.Group()
        for _ in range(2):
            self.enemies.add(Enemy(self.speed, px))

        # coins
        self.coins = pygame.sprite.Group()
        for _ in range(3):
            self.coins.add(Coin(self.speed, px))

        # static hazards  (start minimal — extras spawn gradually)
        self.oil_spills = pygame.sprite.Group(OilSpill(self.speed))
        self.barriers   = pygame.sprite.Group()
        self.potholes   = pygame.sprite.Group()

        # dynamic hazards
        self.mov_barriers  = pygame.sprite.Group()
        self.nitro_strips  = pygame.sprite.Group(NitroStrip(self.speed))

        # power-ups
        self.powerups = pygame.sprite.Group(PowerUp(self.speed))

        # counters / timers
        self.score           = 0
        self.coins_collected = 0
        self.distance        = 0.0
        self.frame           = 0
        self.enemy_tmr       = 0
        self.obs_tmr         = 0

        # active power-up state
        self.active_pu   = None   # "nitro" | "shield" | "repair" | None
        self.nitro_on    = False
        self.nitro_tmr   = 0

    # ── speed management ───────────────────────────────────────────────────────
    def _set_speed(self, new_speed: float):
        self.speed = max(3.0, new_speed)
        for grp in (self.enemies, self.coins, self.oil_spills, self.barriers,
                    self.potholes, self.mov_barriers, self.nitro_strips, self.powerups):
            for spr in grp:
                spr.speed = self.speed

    # ── obstacle spawner ───────────────────────────────────────────────────────
    def _free_lane_x(self) -> int:
        """Return an x coord in whichever road lane has the fewest deadly obstacles."""
        # Three rough lane centres across the road
        lanes = [ROAD_LEFT + 44, ROAD_MID, ROAD_RIGHT - 44]
        lane_w = 48
        counts = [0, 0, 0]
        for grp in (self.barriers, self.potholes, self.mov_barriers, self.enemies):
            for spr in grp:
                if spr.rect.bottom < 0:   # still above screen
                    continue
                for i, cx in enumerate(lanes):
                    if abs(spr.rect.centerx - cx) < lane_w:
                        counts[i] += 1
        # Choose among lanes with minimum occupancy
        min_c = min(counts)
        choices = [lanes[i] for i, c in enumerate(counts) if c == min_c]
        cx = random.choice(choices)
        return int(cx + random.randint(-18, 18))

    def _spawn_obstacle(self):
        r = random.random()
        if r < 0.30:
            self.oil_spills.add(OilSpill(self.speed))
        elif r < 0.55:
            b = Barrier(self.speed)
            b.rect.centerx = self._free_lane_x()
            self.barriers.add(b)
        elif r < 0.75:
            p = Pothole(self.speed)
            p.rect.centerx = self._free_lane_x()
            self.potholes.add(p)
        else:
            self.mov_barriers.add(MovingBarrier(self.speed))

    def _total_obstacles(self) -> int:
        return (len(self.oil_spills) + len(self.barriers) +
                len(self.potholes)   + len(self.mov_barriers))

    # ── main game loop ─────────────────────────────────────────────────────────
    def run(self) -> dict:
        from persistence import add_score

        running = True
        while running:
            self.clock.tick(FPS)
            self.frame += 1

            # ── quit / input events ───────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == QUIT:
                    import sys
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False  # treat ESC as instant death → game over

            # ── scroll background ─────────────────────────────────────────────
            self.bg_y += self.speed
            if self.bg_y >= self.bg_h:
                self.bg_y = 0
            self.screen.blit(self.bg, (0, self.bg_y))
            self.screen.blit(self.bg, (0, self.bg_y - self.bg_h))

            # ── distance & base score ─────────────────────────────────────────
            self.distance += self.speed / FPS   # metres

            # ── nitro countdown ───────────────────────────────────────────────
            if self.nitro_on:
                self.nitro_tmr -= 1
                if self.nitro_tmr <= 0:
                    self.nitro_on  = False
                    self.active_pu = None
                    self._set_speed(self.speed - 2.0)

            # ── auto-clear shield display ─────────────────────────────────────
            if self.active_pu == "shield" and not self.player.shielded:
                self.active_pu = None

            # ── difficulty scaling (every 5 seconds) ─────────────────────────
            if self.frame % (FPS * 5) == 0:
                self._set_speed(self.speed + self.speed_inc)

            # ── spawn extra enemies over time ─────────────────────────────────
            self.enemy_tmr += 1
            if self.enemy_tmr >= self.enemy_every:
                self.enemy_tmr = 0
                if len(self.enemies) < self.max_enemies:
                    self.enemies.add(Enemy(self.speed, self.player.rect.centerx))

            # ── spawn extra obstacles over time ───────────────────────────────
            self.obs_tmr += 1
            if self.obs_tmr >= self.obs_every:
                self.obs_tmr = 0
                if self._total_obstacles() < self.max_obs:
                    self._spawn_obstacle()

            # ── occasionally activate a nitro strip ───────────────────────────
            if self.frame % (FPS * 20) == 0:
                for ns in self.nitro_strips:
                    ns.activate()

            # ── update all sprites ────────────────────────────────────────────
            self.player.move()
            self.enemies.update()
            self.coins.update()
            self.oil_spills.update()
            self.barriers.update()
            self.potholes.update()
            self.mov_barriers.update()
            self.nitro_strips.update()
            self.powerups.update()

            # ── keep coins/powerups from spawning on top of obstacles ─────────
            _obs_rects = [
                s.rect.inflate(16, 16)
                for g in (self.barriers, self.potholes, self.mov_barriers, self.enemies)
                for s in g
                if s.rect.bottom < 0        # only compare off-screen sprites
            ]
            if _obs_rects:
                for coin in self.coins:
                    if coin.rect.bottom < 0 and any(coin.rect.colliderect(r) for r in _obs_rects):
                        coin.rect.center = (rand_road_x(), rand_top_y())
                for pu in self.powerups:
                    if pu.rect.bottom < 0 and any(pu.rect.colliderect(r) for r in _obs_rects):
                        pu.rect.center = (rand_road_x(), rand_top_y())

            px = self.player.rect.centerx

            # ── coin collection ───────────────────────────────────────────────
            for coin in pygame.sprite.spritecollide(self.player, self.coins, False):
                if self.sound_on:
                    try:
                        pygame.mixer.music.play()
                    except Exception:
                        pass
                prev = self.coins_collected
                self.coins_collected += coin.value
                self.score           += coin.value * 10
                # milestone speed bump
                if (prev // COINS_FOR_SPEED) < (self.coins_collected // COINS_FOR_SPEED):
                    self._set_speed(self.speed + 0.30)
                coin.respawn(self.speed, px)

            # ── power-up collection ───────────────────────────────────────────
            for pu in pygame.sprite.spritecollide(self.player, self.powerups, False):
                # only one active at a time
                if self.active_pu is None or pu.ptype == "repair":
                    if pu.ptype == "nitro" and not self.nitro_on:
                        self.nitro_on    = True
                        self.nitro_tmr   = NITRO_DURATION
                        self.active_pu   = "nitro"
                        self._set_speed(self.speed + 2.0)
                    elif pu.ptype == "shield" and not self.player.shielded:
                        self.player.shielded = True
                        self.active_pu       = "shield"
                    elif pu.ptype == "repair":
                        self.player.repair()
                        self.active_pu = None
                    pu.respawn()

            # ── hazard: oil spill ─────────────────────────────────────────────
            if pygame.sprite.spritecollideany(self.player, self.oil_spills):
                if not self.player.oiled:
                    self.player.apply_oil()

            # ── hazard: nitro strip ───────────────────────────────────────────
            if pygame.sprite.spritecollideany(self.player, self.nitro_strips):
                if not self.nitro_on:
                    self.nitro_on  = True
                    self.nitro_tmr = 120          # 2-second road boost
                    self.active_pu = "nitro"
                    self._set_speed(self.speed + 2.0)

            # ── deadly collisions (barriers, potholes, moving barriers, enemies)
            dead = False
            for grp in (self.barriers, self.potholes, self.mov_barriers, self.enemies):
                if pygame.sprite.spritecollideany(self.player, grp):
                    dead = True
                    break
            if dead:
                if not self.player.consume_shield():
                    running = False
                    continue   # skip draw this frame

            # ── draw: hazards & road features ────────────────────────────────
            for grp in (self.nitro_strips, self.oil_spills, self.barriers,
                         self.potholes, self.mov_barriers, self.enemies, self.powerups):
                grp.draw(self.screen)

            # coins have custom draw (shows value label)
            for coin in self.coins:
                coin.draw(self.screen)

            # player
            self.screen.blit(self.player.image, self.player.rect)

            # shield aura
            if self.player.shielded:
                pygame.draw.circle(self.screen, TEAL,
                                   self.player.rect.center, 30, 3)

            # oil overlay
            if self.player.oiled:
                ov = pygame.Surface(self.player.rect.size, pygame.SRCALPHA)
                ov.fill((30, 0, 60, 90))
                self.screen.blit(ov, self.player.rect.topleft)

            # ── HUD ──────────────────────────────────────────────────────────
            self._draw_hud()

            pygame.display.flip()

        # ── session ended ─────────────────────────────────────────────────────
        self.score += int(self.distance)   # distance bonus
        add_score(self.player_name, self.score, self.distance, self.coins_collected)
        return {
            "score":    self.score,
            "distance": self.distance,
            "coins":    self.coins_collected,
        }

    # ── HUD draw ───────────────────────────────────────────────────────────────
    def _draw_hud(self):
        def label(txt, color, pos):
            s = self.fnt_sm.render(txt, True, BLACK)
            self.screen.blit(s, (pos[0] + 1, pos[1] + 1))   # shadow
            s = self.fnt_sm.render(txt, True, color)
            self.screen.blit(s, pos)

        label(f"Score:  {self.score}",           WHITE, (8,  8))
        label(f"Coins:  {self.coins_collected}",  WHITE, (8, 26))
        label(f"Dist:   {self.distance:.0f} m",  WHITE, (8, 44))
        label(f"Speed:  {self.speed:.1f}",        LGRAY, (8, 62))

        # active power-up badge
        if self.active_pu == "nitro" and self.nitro_on:
            secs = max(1, self.nitro_tmr // FPS)
            txt  = self.fnt_sm.render(f"NITRO  {secs}s", True, YELLOW)
            self.screen.blit(txt, (SCREEN_W - 100, 8))
        elif self.active_pu == "shield" and self.player.shielded:
            txt = self.fnt_sm.render("SHIELD", True, TEAL)
            self.screen.blit(txt, (SCREEN_W - 80, 8))

        # oil indicator
        if self.player.oiled:
            txt = self.fnt_sm.render("OILED", True, PURPLE)
            self.screen.blit(txt, (SCREEN_W - 72, 26))
