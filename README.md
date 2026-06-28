<img width="950" height="447" alt="Screenshot 2026-06-28 102254" src="https://github.com/user-attachments/assets/6d1cf09a-d94f-41ca-9cf4-8587460195ed" />
# Platformer

A small side-scrolling platformer made with Python and Pygame. The game includes procedurally generated platforms, coins, enemies, spikes, clouds, shadows, a daylight cycle, and optional weather.

<img width="959" height="446" alt="Screenshot 2026-06-28 102409" src="https://github.com/user-attachments/assets/c7ab4c3b-9cd3-4a53-93bf-701529d33fdb" />
<img width="959" height="449" alt="Screenshot 2026-06-28 102320" src="https://github.com/user-attachments/assets/c0a94417-7f88-48ea-abd3-7d625dd02455" />
<img width="959" height="449" alt="Screenshot 2026-06-28 102453" src="https://github.com/user-attachments/assets/0632b730-4fae-4432-85fd-d6969958f0b0" />
## Features

- Side-scrolling movement with camera follow
- Randomly generated platforms as the player moves forward
- Coins, enemies, and spike hazards
- HP, score, distance, and FPS display
- Main menu with settings
- Toggleable shadows, daylight cycle, weather, and clouds
- Rain that changes player movement by making the ground feel slipperier

## Requirements

- Python 3.10 or newer
- Pygame

Install Pygame with:

```bash
pip install pygame
```

## How to Run

From the project folder, run:

```bash
python main.py
```

If your system uses `python3` instead of `python`, run:

```bash
python3 main.py
```

## Controls

### Menu

- `Up` / `Down`: Change selected menu option
- `Enter`: Select menu option
- Mouse: Click menu options and settings
- `Esc`: Go back from the settings screen

### Game

- `A` / `Left Arrow`: Move left
- `D` / `Right Arrow`: Move right
- `W` / `Up Arrow`: Jump

<img width="959" height="449" alt="Screenshot 2026-06-28 102320" src="https://github.com/user-attachments/assets/0d859bd9-ae07-43dd-9322-553515d3677f" />
## Settings

The settings menu lets you turn these systems on or off:

- `Shadows`: Enables dynamic shadow rendering
- `Daylight Cycle`: Changes the sky and lighting over time
- `Weather`: Enables rain
- `Clouds`: Enables moving background clouds

## Project Structure

```text
Platformer/
+-- main.py
+-- menu.py
+-- Assets/
|   +-- Grass Tile.png
|   +-- Coin.png
+-- README.md
```

## Development Notes

- `main.py` contains the main game loop, player movement, world generation, weather, collisions, rendering, and shadow worker thread.
- `menu.py` contains the start menu and settings menu.
- The game window is currently set to `1300x600`.
- Rain can take a little while to start because weather uses a randomized timer.
