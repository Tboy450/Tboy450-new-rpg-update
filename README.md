Dragon's Lair RPG

If you are new to this codebase, start with
`docs/beginner_code_map.md`. It explains which files are active, what each
module owns, and where to safely add characters, enemies, town buildings,
quests, items, saves, and future assets.

## Install Links

- Android APK direct download: [dragons-lair-rpg-android-debug.apk](https://github.com/Tboy450/Tboy450-new-rpg-update/releases/latest/download/dragons-lair-rpg-android-debug.apk)
- iPhone/iPad direct download placeholder: [dragons-lair-rpg-ios.ipa](https://github.com/Tboy450/Tboy450-new-rpg-update/releases/latest/download/dragons-lair-rpg-ios.ipa)

Android note: the direct link works after `dragons-lair-rpg-android-debug.apk` is uploaded to the latest GitHub Release.
iPhone note: the IPA link will not work until a signed iOS build exists. iPhone installs normally need TestFlight, App Store, or a signed IPA. See [docs/ios_app.md](docs/ios_app.md).

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
