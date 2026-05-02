"""
main.py
Entry point for the Racer game.
Run with:  python main.py

Requires:  pygame  (pip install pygame)
Assets:    place all PNG/MP3 files from Practice 10 inside the assets/ folder.
"""

import pygame
import sys
from persistence import load_settings


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((400, 600))
    pygame.display.set_caption("Racer — TSIS 3")

    # Import here so pygame.font is already initialised
    from ui    import MainMenu, NameEntry, GameOverScreen, LeaderboardScreen, SettingsScreen
    from racer import Game

    settings    = load_settings()
    state       = "menu"
    player_name = "Player"
    final       = {"score": 0, "distance": 0.0, "coins": 0}

    # Persistent screen objects (re-created when settings change)
    menu    = MainMenu(screen)
    lb      = LeaderboardScreen(screen)
    s_screen = SettingsScreen(screen, settings)

    while True:
        # ── MAIN MENU ─────────────────────────────────────────────────────────
        if state == "menu":
            action = menu.run()
            if   action == "play":        state = "name_entry"
            elif action == "leaderboard": state = "leaderboard"
            elif action == "settings":    state = "settings"
            elif action == "quit":
                pygame.quit()
                sys.exit()

        # ── NAME ENTRY ────────────────────────────────────────────────────────
        elif state == "name_entry":
            result = NameEntry(screen).run()
            if result:
                player_name = result
                state = "game"
            else:
                state = "menu"

        # ── GAMEPLAY ──────────────────────────────────────────────────────────
        elif state == "game":
            settings = load_settings()          # pick up any saved changes
            final    = Game(screen, settings, player_name).run()
            state    = "game_over"

        # ── GAME OVER ─────────────────────────────────────────────────────────
        elif state == "game_over":
            action = GameOverScreen(
                screen, final["score"], final["distance"], final["coins"]
            ).run()
            state = "game" if action == "retry" else "menu"

        # ── LEADERBOARD ───────────────────────────────────────────────────────
        elif state == "leaderboard":
            lb.run()
            state = "menu"

        # ── SETTINGS ─────────────────────────────────────────────────────────
        elif state == "settings":
            settings  = s_screen.run()
            s_screen  = SettingsScreen(screen, settings)   # rebuild with new vals
            state     = "menu"


if __name__ == "__main__":
    main()
