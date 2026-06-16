# pygame-ce Android Recipe

This folder contains the custom python-for-android recipe for building
`pygame-ce` into the Android APK.

## Files

- `__init__.py`: recipe implementation. It downloads `pygame-ce` 2.5.2, installs it as the `pygame` package, adds SDL2-related dependencies, ensures Cython is available to hostpython, and patches an older `distutils` call that breaks during Android builds.

## Why This Exists

The game imports `pygame`, but the Android build uses `pygame-ce` because it is
the currently working path for this repo's Buildozer/python-for-android setup.
The recipe keeps the game code simple while handling Android-specific compile
details in one place.

## Beginner Rule

If the desktop game runs but the APK build fails while compiling pygame, inspect
this recipe and `docs/android_apk_agent_notes.md`. Do not randomly swap pygame
versions without reading the exact GitHub Actions error first.
