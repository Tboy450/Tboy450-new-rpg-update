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
source.include_exts = py,json,txt,md

# Keep old experiments and local build/cache output out of the Android package.
source.exclude_dirs = archive,.git,.github,.pytest_cache,__pycache__,.buildozer,bin

# Python dependencies for python-for-android.
# `python3` is the interpreter, `pygame` runs the game, and `numpy` is used for
# generated audio waveforms.
requirements = python3,pygame,numpy

# App version fields.
version = 0.1.0

# The game is designed for a 1000x700 landscape screen.
orientation = landscape
fullscreen = 1

# Android build targets. Buildozer will download matching Android SDK/NDK tools
# when the build machine is prepared.
android.api = 35
android.minapi = 23
android.ndk = 25b

# SDL2 bootstrap is the standard route for Pygame on Android.
p4a.bootstrap = sdl2

# No special permissions are needed for the current game. Saves use app/private
# storage through Python's home path.
android.permissions =

# Build output goes into `bin/`.

[buildozer]

# Raise this when debugging build logs.
log_level = 2

# Reuse downloaded SDK/NDK/cache data between builds.
warn_on_root = 1
