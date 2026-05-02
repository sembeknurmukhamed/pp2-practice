# Racer — TSIS 3

## Setup

1. **Install pygame**
   ```
   pip install pygame
   ```

2. **Copy your assets** into the `assets/` folder:
   ```
   assets/
     CarGreenFront.png
     CarRedFront.png
     pixel_art_road_green_land.png
     KBGU4713.PNG
     DRGF5324.PNG
     FURF8350.PNG
     GXNF9041.PNG
     coin_recieved.mp3
   ```

3. **Run the game**
   ```
   python main.py
   ```

---

## File structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point — screen state machine |
| `racer.py` | All sprite classes + `Game` loop |
| `ui.py` | All Pygame screens (Menu, Settings, etc.) |
| `persistence.py` | JSON save/load for settings & leaderboard |
| `settings.json` | Saved player preferences |
| `leaderboard.json` | Top-10 scores |

---

## Controls

| Key | Action |
|-----|--------|
| ← / → | Steer |
| ESC (in-game) | Quit to Game Over |
| R (Game Over) | Retry |
| ESC (menus) | Back |

---

## Features added (Tasks 3.1 – 3.5)

### 3.1 Lane Hazards & Road Events
- **Oil Spill** — dark puddle; slows the player for ~3 s  
- **Nitro Strip** — gold chevron painted on the road; grants a 2 s speed burst  

### 3.2 Dynamic Traffic & Obstacles
- **Enemy cars** — spawn at the top, move downward; collision ends run  
- **Barrier** — orange bollard; deadly on contact  
- **Pothole** — dark pit; deadly on contact  
- **Moving Barrier** — red bar that sweeps left–right across the road  
- **Safe spawn logic** — new sprites spawn far above the player  
- **Difficulty scaling** — speed increases every 5 s; extra enemies/obstacles spawn as score grows  

### 3.3 Power-Ups
| Icon | Name | Effect | Duration |
|------|------|--------|----------|
| **N** | Nitro | +2 speed | 4 s |
| **S** | Shield | Absorbs one deadly collision | Until hit |
| **R** | Repair | Instantly clears Oil Slow | Instant |

- Only one power-up active at a time  
- Power-ups vanish if not collected within 8 s  
- Active power-up and remaining time shown in HUD  

### 3.4 Score, Distance & Leaderboard
- **Score** = coins × 10 + distance bonus (metres)  
- **Distance meter** shown in HUD  
- **leaderboard.json** — top-10 saved automatically after each run  
- **Name entry** screen before each game  
- **Leaderboard screen** shows rank, name, score, distance, coins  

### 3.5 Screens & Settings
- **Main Menu** — Play, Leaderboard, Settings, Quit  
- **Settings** — toggle sound, car colour (green/red), difficulty (easy/medium/hard)  
- **Game Over** — score, distance, coins; Retry or Menu  
- **Leaderboard** — top-10 with medals for 1st/2nd/3rd  
- `settings.json` saved on exit from Settings screen and loaded at startup  
