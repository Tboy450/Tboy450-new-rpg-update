# Scripts Section

`scripts/` contains helper commands for installing, updating, launching, and
building the game. The active game logic is not here; these files support setup
and packaging.

## Files

- `build_android.sh`: builds the Android APK with Buildozer. It also exports `PIP_BREAK_SYSTEM_PACKAGES=1` so local Debian/Ubuntu Python installs do not block Buildozer helper installs.
- `create_android_shortcut.bsh`: BeanShell helper for creating an Android/Pydroid launcher shortcut. This is legacy support and not the preferred APK path.
- `generate_future_town_assets.py`: creates unused transparent PNG town scenery sprites for `assets/processed/future_assets/scenery/indoor/` and `assets/processed/future_assets/scenery/outdoor/`.
- `install_android_pydroid.py`: downloads/copies source files into a Pydroid-friendly folder on Android. It is useful only when Pydroid has a working prebuilt `pygame`.
- `install_packages.py`: general Python package installer helper for desktop setup.
- `install_packages_strict.py`: stricter installer helper for environments where package versions matter more.
- `install_python_app.py`: desktop/source install helper for the Python version of the game.
- `install_windows.ps1`: Windows PowerShell setup helper.
- `process_uploaded_enemy_sheet.py`: splits a user-supplied green-screen enemy sheet into future transparent enemy PNGs.
- `process_uploaded_npc_sheet.py`: splits a user-supplied green-screen NPC sheet into future transparent NPC PNGs.
- `run_local_android.py`: Android/Pydroid runtime launcher helper for source installs.
- `run_windows.ps1`: Windows PowerShell launcher helper. It auto-syncs active
  game files from GitHub only when those files are clean locally, so uncommitted
  work is not overwritten.

## Beginner Rule

Use scripts when you need a repeatable command. If a change affects gameplay,
edit `main.py`, `game_data/`, or `systems/` instead.

## Android Build Path

The preferred Android path is the APK built from `build_android.sh` locally or
from `.github/workflows/android-apk.yml` on GitHub Actions. The Pydroid scripts
are fallback source-install tools and should not be treated as the main app
update system.
