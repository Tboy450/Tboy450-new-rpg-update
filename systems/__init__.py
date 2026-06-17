"""Runtime helper systems for Dragon's Lair RPG.

Beginner note:
    This package contains reusable helper logic that has been split out of
    `main.py`. It is different from `game_data/`, which is mostly tables of
    values, text, colors, and tuning data.

Modules:
    assets: imported art paths, caches, sprite drawing, and frame loading.
    android_controls: state-aware Android touch button layout and drawing.
    android_update: GitHub APK update URLs, version checks, and external link opening.
    input_actions: keyboard/touch input mapping.
    save_load: JSON save/load helpers.
"""
