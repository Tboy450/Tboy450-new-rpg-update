Dragon's Lair RPG

[![Build Android APK](https://github.com/Tboy450/Tboy450-new-rpg-update/actions/workflows/android-apk.yml/badge.svg)](https://github.com/Tboy450/Tboy450-new-rpg-update/actions/workflows/android-apk.yml)

If you are new to this codebase, start with
`docs/beginner_code_map.md`. It explains which files are active, what each
module owns, and where to safely add characters, enemies, town buildings,
quests, items, saves, and future assets.

This repository is intentionally labeled for beginner coders, future readers,
and future AI/code assistants. The active modules and helper systems are
documented on purpose so the project is easier to extend without guessing.

Contributor note: when project requests mention **beginner labeling**, that
means explanatory code comments, docstrings, README notes, and file maps for
beginner programmers. Do not turn that phrase into new player-facing beginner
controls or tutorials unless the request explicitly asks for player help UI.

## Android Install / Update

The installable Android app is published here after the **Build Android APK**
workflow finishes successfully:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android.apk
```

If that link returns 404, the APK workflow has not published a green build yet.
Use the badge above to open the build status.

The app also checks this GitHub build version from the beginning menu and can
open the same APK update link from inside the game. On Android, the game tries
known browser apps first so the APK downloads normally. If that fails, it opens
the GitHub Android app release page before giving up.

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
- `J`: quest log
- `M`: world map
- `F5`: save
- `F9`: load
- `ESC`: pause/menu during active gameplay

Android touch controls:

- Touch buttons keep a small phone-edge margin and forgiving tap targets.
- `MENU`: opens the shared pause menu.
- `USE`: interact, use town services, or advance town cutscene dialogue.
- `OK`: confirm, talk, inspect, or advance story dialogue.
- Inside town buildings, `USE` opens a small service menu with buttons for the
  building action, Talk, Log, Leave, and Back.
- Battle uses a small `ACTIONS` / `HIDE` button near the upper-right of the
  battle screen. Tap `ACTIONS` to show attack buttons, tap an attack to choose
  it, and tap `HIDE` when you want the lower battlefield clear. If the action
  row is hidden, tapping the lower command area also brings it back.
- Pause-menu buttons expose `Log`, `Map`, `Save`, and `Load` without a hardware keyboard.
- Inventory opens from the pause menu. In Inventory, use `SLOT <` / `SLOT >`
  to switch weapon, armor, and charm slots; arrows to choose owned gear;
  `EQUIP` to equip it; and `UNEQUIP` to clear the active slot.

The default save file is stored at `~/.dragons_lair_rpg_save.json`. Set `DRAGONS_LAIR_SAVE` to choose a different save path.

Town services now act as a clearer hub: every enterable building has a visible
doorway marker, short map label, service role, first-reward hint, repeat-use
hint, one-time errand, reputation, experience, potions, gear, and town keepsake.
If two doorway action spaces ever overlap, the game chooses the closest doorway
instead of whichever building appears first in code. The pause-menu Log tracks
town progress, open building errands, and nearby service purpose without
opening a separate board from the OK button. It also shows the next unfinished
resident errand and whether that errand is ready or still locked. Inspecting
marked details inside interiors grants a small one-time insight reward. Outdoor
town residents also have rotating dialogue and one-time errands; some resident
rewards grant gear that waits in Inventory until equipped.

Inventory now shows and manages real equipped gear. Starter weapons/armor are
automatic, Lion Sage awards a charm accessory, and Ghost Face's first clear
awards a Mask-Shard weapon. The blacksmith now grants level-gated standard gear
that stays in Inventory until the player equips it. Standard progression gear
and future rare/special gear are stored in `game_data/equipment.py`, with
matching icons in `assets/processed/equipment/`. The center overworld area is
`plains`; beach/sand details are visual town scenery rather than a separate map
area.

Repository layout:

- `main.py` is the active game file.
- `docs/` holds beginner-facing code maps and project notes.
- `game_data/` holds active modular data. See `game_data/README.md` for where character, enemy, world scenery/music/particles, NPC, town interior, mechanic, and progression data belongs.
- `systems/` holds active helper systems such as input mapping, JSON save/load, update-link helpers, and reusable story/pause UI drawing. See `systems/README.md` before changing helper code.
- `assets/` is the intake area for future art/audio ports. Keep raw downloads in `assets/source/`, game-ready files in `assets/processed/`, and non-CC0 attribution in `assets/credits.md`.
- `assets/processed/future_assets/` holds inactive future gear, scenery, enemy, and NPC PNG concepts. These are not loaded by the game until moved into an active folder and wired into data/code.
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
- `scripts/run_windows.ps1`: Windows launcher/update helper; it skips GitHub
  auto-sync when active game files have local edits.
- `README.md`: this project overview and install/update guide.
