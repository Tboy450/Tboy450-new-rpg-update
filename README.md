Dragon's Lair RPG

[![Build Android APK](https://github.com/Tboy450/Tboy450-new-rpg-update/actions/workflows/android-apk.yml/badge.svg)](https://github.com/Tboy450/Tboy450-new-rpg-update/actions/workflows/android-apk.yml)

If you are new to this codebase, start with
`docs/beginner_code_map.md`. It explains which files are active, what each
module owns, and where to safely add characters, enemies, town buildings,
quests, items, saves, and future assets.

## Android Install / Update

The installable Android app is published here after the **Build Android APK**
workflow finishes successfully:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android.apk
```

If that link returns 404, the APK workflow has not published a green build yet.
Use the badge above to open the build status.

The app also checks this GitHub build version from the beginning menu and can
open the same APK update link from inside the game.

Older links still work through this compatibility filename:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

The APK uses the dragon launcher icon from:

```text
assets/processed/ui/dragon_app_icon.png
```

### Pydroid Status

Pydroid 3 can still copy/update the source files, but it only runs the game if
Pydroid's **Quick Install** screen includes a prebuilt `pygame` package. Do not
use Pydroid's normal **Search libraries** result for `pygame`; that path tries
to compile pygame from source on Android and fails with missing SDL tools.
If a Pydroid home-screen shortcut opens with an
`ExternalStorageProvider` permission denial, delete that shortcut and install
the APK above. That shortcut is Pydroid trying to open a source file through
Android's document provider; it is not the installable game app.

File updater:

[install_android_pydroid.py](https://github.com/Tboy450/Tboy450-new-rpg-update/raw/main/scripts/install_android_pydroid.py)

One-line updater:

```python
import urllib.request; exec(urllib.request.urlopen("https://github.com/Tboy450/Tboy450-new-rpg-update/raw/main/scripts/install_android_pydroid.py").read().decode())
```

When it can run, the updater installs to:

```text
/sdcard/Download/DragonLairRPG
```

If Pydroid 3 has not been granted shared-storage access, the installer falls
back to Pydroid's private home folder and prints the exact path it used.

```text
/sdcard/Download/DragonLairRPG/assets/processed/ui/dragon_app_icon.png
```

Then open this file in Pydroid 3:

```text
/sdcard/Download/DragonLairRPG/play_android.py
```

More detail: [docs/android_app.md](docs/android_app.md).

## iPhone Status

- iPhone/iPad status: no signed IPA exists yet. A real iPhone install needs a
  signed build through TestFlight, the App Store, or Apple developer signing.

See [docs/ios_app.md](docs/ios_app.md) for packaging notes.

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
- `.github/` holds GitHub Actions automation, including the APK build workflow.
- `android-signing/` holds the public development signing key for sideload APK updates.
- `p4a-recipes/` holds Android build recipes, including the custom `pygame-ce` recipe.
- `bin/` is where local APK builds place generated files.
- `buildozer.spec` is the Android APK packaging config.
- `archive/` contains older snapshot files and experiments kept for reference only. It is not the active game source.

Root files:

- `main.py`: active Pygame RPG source.
- `buildozer.spec`: Android package name, icon, version, dependencies, SDK/NDK, and APK build settings.
- `requirements.txt`: desktop Python dependency list.
- `play_android.py`: Android/Pydroid source-launch helper.
- `run_android.py`: Android/Pydroid runtime launcher.
- `Run Dragons Lair RPG.cmd`: Windows double-click launcher.
- `README.md`: this project overview and install/update guide.
