# Android App Build Guide

This project can be packaged as an Android APK with Buildozer. The game remains
the same Python/Pygame game in `main.py`; Buildozer wraps it with
python-for-android and SDL2.

## What Was Added

- `buildozer.spec`: Android app configuration.
- `scripts/build_android.sh`: helper script that runs the APK build.
- `assets/processed/ui/dragon_app_icon.png`: dragon launcher icon used by the Android app.
- `.github/workflows/android-apk.yml`: GitHub Actions build that publishes the APK release asset.

## What You Need

Use a Linux PC or WSL2 on Windows. Building directly inside a normal Android
phone browser is not realistic because Android APK packaging needs the Android
SDK, Android NDK, Java, and native compilation tools.

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

## Install On Android

Target release URL once an APK is uploaded:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

This URL is expected to return 404 until the `Build Android APK` GitHub Action
finishes successfully and uploads `dragons-lair-rpg-android-debug.apk` to the
`android-latest` release.

Connect your phone with USB debugging enabled:

```bash
adb install -r bin/*debug.apk
```

Or copy the APK to the phone and open it from the Android file manager. Android
may ask you to allow installs from unknown sources.

## Important Notes

- This creates a debug APK for testing, not a Play Store release.
- The current game uses Pygame and generated art/audio, so the APK may be large.
- Touch buttons already exist in `main.py` and are shown when Android is detected.
- Saves use app/private storage, so uninstalling the app can remove local saves.

## If The APK Build Fails

Common fixes:

- Run the build on Linux or WSL2 instead of a phone browser.
- Make sure Java 17 is installed.
- Delete `.buildozer/` and retry if an SDK/NDK download was interrupted.
- Keep `requirements = python3,pygame,numpy` in `buildozer.spec` unless you know
  the python-for-android recipe supports the package you are adding.

## Future Polish

- Add a proper Android app icon.
- Add a release signing config for a shareable release APK.
- Tune screen scaling for more phone aspect ratios.
- Replace generated sounds/sprites with files from `assets/processed/`.
