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

## How To Build The APK (For Editors)

This project uses **Buildozer** through **GitHub Actions** to compile the
Pygame RPG into an Android APK in the cloud. You do not need a local Linux
setup to produce a test APK.

The workflow file already exists at `.github/workflows/android-apk.yml`. The
workflow name in GitHub Actions is **Build Android APK** (not "Build APK").

### Trigger an automatic build

1. Edit game code (`main.py`, `game_data/`, `assets/`, `systems/`, etc.).
2. Do **not** change `buildozer.spec` to `requirements = python3,pygame`. The
   working config is `requirements = python3,pygame-ce` with the local recipe in
   `p4a-recipes/pygame-ce/`. See
   [docs/android_apk_agent_notes.md](docs/android_apk_agent_notes.md) before
   touching Android packaging.
3. Commit and push to `main`.
4. Open the repo **Actions** tab and watch **Build Android APK**.
5. When the run succeeds, download the APK from the `android-latest` release:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

You can also start a build manually: Actions -> **Build Android APK** ->
**Run workflow**.

Pushes only auto-trigger the workflow when Android-related paths change (for
example `main.py`, `buildozer.spec`, `p4a-recipes/`, `assets/`, `game_data/`).

### Install the APK on a phone

1. Download `dragons-lair-rpg-android-debug.apk` from the release link above.
2. Copy it to the phone and open it from the file manager.
3. Allow installs from unknown sources if Android asks.

If the release link returns 404, the latest build has not finished yet.

**Fallback only (Pydroid):** If APK install is not possible, use Pydroid 3. Open
`run_android.py` once to install packages, then `play_android.py` to play. Do
not type `scripts/run_local_android.py` into the Python editor.

More detail: [docs/android_app.md](docs/android_app.md).

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
