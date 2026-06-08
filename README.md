Dragon's Lair RPG

If you are new to this codebase, start with
`docs/beginner_code_map.md`. It explains which files are active, what each
module owns, and where to safely add characters, enemies, town buildings,
quests, items, saves, and future assets.

## Python App Install

This is the current working install path. It does not use an APK or GitHub
Release file. It starts Python 3, uses your local game files or downloads the
latest copy, installs the needed packages, creates a launcher, and runs
`main.py`.

Windows PowerShell:

```powershell
py -3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_python_app.py').read().decode())"
```

Mac or Linux terminal:

```bash
python3 -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_python_app.py').read().decode())"
```

## Android Install (APK)

The primary Android install path is the GitHub-built debug APK.

1. Wait for the `Build Android APK` GitHub Action on `main` to finish.
2. Download and install:
   `https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk`
3. Open the APK on your phone. Android may ask you to allow installs from
   unknown sources.

If that URL returns 404, the latest APK build has not finished yet. Check
Actions on GitHub for the `Build Android APK` workflow.

Build details and troubleshooting: [docs/android_app.md](docs/android_app.md).
Agent/Codex packaging notes (read before changing Android build files):
[docs/android_apk_agent_notes.md](docs/android_apk_agent_notes.md).

**Fallback only (Pydroid):** If you cannot install an APK, you can use Pydroid 3.
Open `run_android.py` once to install packages, then `play_android.py` to play.
Do not type `scripts/run_local_android.py` into the Python editor.

## iPhone Status

- iPhone/iPad status: no signed IPA exists yet. A real iPhone install needs a
  signed build through TestFlight, the App Store, or Apple developer signing.

See [docs/ios_app.md](docs/ios_app.md) for packaging notes.

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

## Build Android APK Locally

This repo packages the same Python/Pygame game into an Android APK with
Buildozer. CI on GitHub is the normal build path; local builds need Linux or
WSL2.

```bash
bash scripts/build_android.sh
```

The APK output goes in `bin/` when the build succeeds. See
`docs/android_app.md` and `docs/android_apk_agent_notes.md`.

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
