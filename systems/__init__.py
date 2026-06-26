"""Runtime helper systems for Dragon's Lair RPG.

Beginner note:
    This package contains reusable helper logic that has been split out of
    `main.py`. It is different from `game_data/`, which is mostly tables of
    values, text, colors, and tuning data.

Modules:
    assets: imported art paths, caches, sprite drawing, and frame loading.
    android_controls: state-aware Android touch button layout and drawing.
    android_update: GitHub APK update URLs, version checks, and external link opening.
    battle_input: battle keyboard/touch routing.
    battle_rewards: scaled battle reward calculations.
    battle_ui: reusable battle HUD, log, button, and summary panels.
    input_actions: keyboard/touch input mapping.
    interior_ui: shared indoor room drawing helpers for NPCs and message panels.
    save_load: JSON save/load helpers.
    story_ui: reusable dialogue and pause-menu overlay drawing.
    town_population_ui: outdoor town resident drawing helpers.
    town_services: inn and blacksmith reward/service logic.
"""
