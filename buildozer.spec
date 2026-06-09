[app]

# Beginner note:
# Buildozer reads this file to turn the Python/Pygame game into an Android APK.
# The game still starts from `main.py`; this file only describes the Android app
# package, included files, dependencies, screen settings, and build options.

# App name shown on Android.
title = Dragon's Lair RPG

# Python package identifiers used by Android. Keep these lowercase.
package.name = dragonslairrpg
package.domain = org.tboy450

# Main source folder. `.` means the repository root.
source.dir = .

# File types to copy into the APK.
source.include_exts = py,json,txt,md,png

# Launcher icon shown on Android home screens and app lists.
icon.filename = assets/processed/ui/dragon_app_icon.png

# Keep old experiments and local build/cache output out of the Android package.
source.exclude_dirs = archive,.git,.github,.pytest_cache,__pycache__,.buildozer,bin

# Python dependencies for python-for-android.
# `python3` is the interpreter. `pygame-ce` installs as `pygame` in the APK.
requirements = python3,pygame-ce

# App version fields.
version = 0.1.0

# The game is designed for a 1000x700 landscape screen.
orientation = landscape
fullscreen = 1

# Android build targets. Buildozer will download matching Android SDK/NDK tools
# when the build machine is prepared.
android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True

# SDL2 bootstrap is the standard route for Pygame on Android.
p4a.bootstrap = sdl2

# Use the repo-local pygame-ce recipe. Upstream p4a still pins pygame 2.1.0,
# which fails against modern Python headers during CI builds.
# Agent note: read docs/android_apk_agent_notes.md before changing Android deps.
p4a.local_recipes = ./p4a-recipes
# Pin p4a so the python3 recipe stays on Python 3.11. Floating `develop`
# currently uses Python 3.14, which pygame-ce 2.5.2 cannot compile against.
p4a.branch = v2024.01.21

# Target modern 64-bit Android phones first. The user's device is arm64, and a
# single architecture keeps debug builds much faster while this project is early.
android.archs = arm64-v8a

# No special permissions are needed for the current game. Saves use app/private
# storage through Python's home path.
android.permissions =

# Build output goes into `bin/`.

[buildozer]

# Raise this when debugging build logs.
log_level = 2

# Container/CI builds may run as root, so keep this non-interactive.
warn_on_root = 0
