Dragon's Lair RPG

## Windows desktop icon

The easiest Windows setup is the installer script. It creates a local game folder,
installs the needed Python packages, and adds a desktop shortcut named
`Dragon's Lair RPG`.

Open PowerShell and run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_windows.ps1 -UseBasicParsing | iex"
```

After that, double-click `Dragon's Lair RPG` on the desktop.

The desktop shortcut runs `scripts/run_windows.ps1`, which checks GitHub for the
latest `main` branch files before launching the game. When this repository is
updated, the desktop version updates the next time the icon is opened.

Requirements:

- Git for Windows: https://git-scm.com/download/win
- Python 3: https://www.python.org/downloads/

Run the game with:

```bash
python main.py
```

On Windows, use `Run Dragons Lair RPG.cmd` to auto-update active game files, set up the local Python environment, install requirements, and launch the game.

Controls:

- `ARROWS/WASD`: move
- `SPACE/ENTER`: interact or confirm
- `ENTER` inside buildings: talk, inspect nearby marked details, or exit
- `J`: quest journal
- `M`: world map
- `F5`: save
- `F9`: load
- `ESC`: back/menu

The default save file is stored at `~/.dragons_lair_rpg_save.json`. Set `DRAGONS_LAIR_SAVE` to choose a different save path.

Town services now also complete one-time errands for town reputation, score, experience, and occasional potion rewards. Inspecting marked details inside interiors grants a small one-time insight reward.

Repository layout:

- `main.py` is the active game file.
- `game_data/` holds active modular data. See `game_data/README.md` for where character, enemy, world, NPC, town interior, mechanic, and progression data belongs.
- `systems/` holds active helper systems such as input mapping and JSON save/load.
- `assets/` is the intake area for future art/audio ports. Keep raw downloads in `assets/source/`, game-ready files in `assets/processed/`, and non-CC0 attribution in `assets/credits.md`.
- `scripts/` holds setup helpers.
- `archive/` contains older snapshot files and experiments kept for reference only. It is not the active game source.
