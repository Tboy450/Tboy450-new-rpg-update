# Android App Build Guide

This project can be packaged as an Android APK with Buildozer. The game remains
the same Python/Pygame game in `main.py`; Buildozer wraps it with
python-for-android and SDL2.

## What Was Added

- `buildozer.spec`: Android app configuration.
- `scripts/build_android.sh`: helper script that runs the APK build.
- `scripts/install_android_pydroid.py`: Pydroid 3 installer/updater for phone debugging.
- `assets/processed/ui/dragon_app_icon.png`: dragon launcher icon used by the Android app.
- `.github/workflows/android-apk.yml`: GitHub Actions build that publishes the APK release asset.

## Android Debugging Today

The native APK is the target Android debugging path. The release asset is
published by GitHub Actions when the **Build Android APK** workflow turns green:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

Pydroid 3 is only a source-file updater unless its **Quick Install** screen
offers a prebuilt `pygame` package. The normal **Search libraries** result for
`pygame` uses PyPI and tries to compile pygame from source, which fails on
Android with missing SDL build tools.

Pydroid source updater:

```python
import urllib.request; exec(urllib.request.urlopen("https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_android_pydroid.py").read().decode())
```

That downloads the latest GitHub `main` branch to:

```text
/sdcard/Download/DragonLairRPG
```

If Pydroid has not been granted shared-storage access, the installer falls back
to Pydroid's private home folder and prints the exact path it used.

If Pydroid has a working prebuilt pygame package, open:

```text
/sdcard/Download/DragonLairRPG/play_android.py
```

To update source files, run the one-line installer again. The icon file used by
the APK is:

```text
/sdcard/Download/DragonLairRPG/assets/processed/ui/dragon_app_icon.png
```

## What You Need

Use a Linux PC or WSL2 on Windows. Building directly inside a normal Android
phone browser is not realistic because Android APK packaging needs the Android
SDK, Android NDK, Java, and native compilation tools.

Do not try to use this phone's aarch64 proot shell as the primary APK builder.
Google's Linux Android SDK/NDK host tools downloaded by Buildozer are x86_64
binaries, so they do not execute normally in this environment.

Required tools:

- Python 3
- Git
- Java 17 JDK
- Buildozer
- Android SDK/NDK tools downloaded by Buildozer

## Build The APK

From the repository root:

```bash
bash scripts/build_android.sh
```

If Buildozer is missing, the script prints the install commands.

When the build succeeds, look in:

```text
bin/
```

The debug APK will have a name similar to:

```text
dragons-lair-rpg-android-debug.apk
```

## Install On Android (Primary Path)

Download the latest CI-built APK:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

If that URL returns 404, no green APK has been published to the `android-latest`
release yet. Keep debugging the APK workflow until `Build Android APK` is green
on `main`.

Install options:

- Copy the APK to the phone and open it from the file manager.
- Or with USB debugging: `adb install -r bin/*debug.apk`

Android may ask you to allow installs from unknown sources.

## Important Notes

- This creates a debug APK for testing, not a Play Store release.
- The current game uses Pygame and generated art/audio, so the APK may be large.
- Android touch controls are now split between `systems/android_controls.py` and the shared pause-menu logic in `main.py`.
- For APK updates, both `APP_NUMERIC_VERSION` in `main.py` and `android.numeric_version` in `buildozer.spec` must increase.
- Saves use app/private storage, so uninstalling the app can remove local saves.

## If The APK Build Fails

Common fixes:

- Run the build on Linux or WSL2 instead of a phone browser.
- Make sure Java 17 is installed.
- Delete `.buildozer/` and retry if an SDK/NDK download was interrupted.
- Keep `requirements = python3,pygame-ce` in `buildozer.spec`. The local
  `p4a-recipes/pygame-ce` recipe is required because upstream p4a still pins
  an older pygame recipe that fails on modern Python headers.
- Keep `Cython` below `0.30` for Buildozer/python-for-android compatibility.
- Read [android_apk_agent_notes.md](android_apk_agent_notes.md) before changing
  Android packaging. It documents the pygame/Cython failure loop and what not to
  revert.

## Future Polish

- Resize/compress the Android app icon if APK packaging reports resource or size errors.
- Add a release signing config for a shareable release APK.
- Tune screen scaling for more phone aspect ratios.
- Replace generated sounds/sprites with files from `assets/processed/`.
