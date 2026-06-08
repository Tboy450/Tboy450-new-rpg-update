Dragon's Lair RPG

If you are new to this codebase, start with
`docs/beginner_code_map.md`. It explains which files are active, what each
module owns, and where to safely add characters, enemies, town buildings,
quests, items, saves, and future assets.

## Python App Install

This is the current working install path. It does not use an APK or GitHub
Release file. It starts Python 3, downloads the latest game files, installs the
needed packages, creates a launcher, and runs `main.py`.

Windows PowerShell:

```powershell
py -3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_python_app.py').read().decode())"
```

Mac or Linux terminal:

```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_python_app.py').read().decode())"
```

Android Python option:

1. Install a Python 3 app that can run Pygame, such as Pydroid 3.
2. Open its terminal or editor.
3. Run this:

```python
import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_python_app.py').read().decode())
```

This is closer to the `zoom-loop` style because the README gives one direct
launch path instead of pointing at a missing release download. Chrome/Safari
home-screen install still needs a later browser/PWA port because this repo is a
Python/Pygame game, not a web app yet.

## APK / iPhone Status

- Android APK status: pending. The APK path only works after the `Build Android
  APK` GitHub Action finishes and uploads a release asset.
- iPhone/iPad status: no signed IPA exists yet. A real iPhone install needs a
  signed build through TestFlight, the App Store, or Apple developer signing.

See [docs/android_app.md](docs/android_app.md) and
[docs/ios_app.md](docs/ios_app.md) for packaging notes.

## Windows desktop icon

The Windows-specific installer still exists. It creates a local game folder,
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

## Android APK

This repo includes a Buildozer setup for creating an Android test APK from the
same Python/Pygame game. See `docs/android_app.md`.

Quick build command on Linux or WSL2:

```bash
bash scripts/build_android.sh
```

The APK output goes in `bin/` when the build succeeds.

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
- `docs/` holds beginner-facing code maps and project notes.
- `game_data/` holds active modular data. See `game_data/README.md` for where character, enemy, world, NPC, town interior, mechanic, and progression data belongs.
- `systems/` holds active helper systems such as input mapping and JSON save/load. See `systems/README.md` before changing helper code.
- `assets/` is the intake area for future art/audio ports. Keep raw downloads in `assets/source/`, game-ready files in `assets/processed/`, and non-CC0 attribution in `assets/credits.md`.
- `scripts/` holds setup helpers, including `scripts/build_android.sh`.
- `buildozer.spec` is the Android APK packaging config.
- `archive/` contains older snapshot files and experiments kept for reference only. It is not the active game source.
