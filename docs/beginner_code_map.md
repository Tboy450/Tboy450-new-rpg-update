# Beginner Code Map

This guide explains where the active game code lives and what each module is
responsible for. Read this before editing if you are new to Python or this repo.

## Active Source Vs Archive

- `main.py`: the active game program. Run this file to start the game.
- `game_data/`: active data tables for characters, enemies, towns, quests, and world tuning.
- `systems/`: active helper systems that can be reused by `main.py`.
- `assets/`: planned home for imported art, animation, sounds, music, and UI files.
- `scripts/`: install and launch helpers, mostly for Windows setup.
- `buildozer.spec`: Android APK packaging settings.
- `archive/`: old snapshots and experiments. Use it for reference only; do not add active gameplay there.

## How The Game Starts

1. Python runs `main.py`.
2. `main.py` imports active data through `game_data/__init__.py`.
3. Pygame creates the window, fonts, and audio helpers.
4. The `Game` class is created. This is the main controller.
5. The game loop reads input, updates the current state, and draws the screen.

## Main Game States

- `start_menu`: title screen and load/start buttons.
- `opening_cutscene`: story intro before character selection.
- `character_select`: choose Warrior, Mage, or Rogue.
- `overworld`: explore the 3x3 map.
- `interior`: walk inside town buildings.
- `battle`: turn-based combat.
- `game_over`: defeat or final result screen.

## Main Classes In `main.py`

- `Game`: owns the current state, player, world map, save/load actions, menus, and overall loop.
- `WorldMap`: owns the 3x3 grid of `WorldArea` objects and handles area transitions.
- `WorldArea`: owns one map screen, including terrain color, enemies, town layout, and particles.
- `Character`: the player hero, including stats, inventory, level, and battle actions.
- `Enemy`: normal monsters, including scaling, element type, and combat behavior.
- `Dragon`: boss-style dragon drawing and behavior.
- `BattleScreen`: turn-based battle menu, animations, damage, items, and victory/defeat handling.
- `ParticleSystem`: small visual effects such as smoke, sparks, snow, and magic particles.
- `OpeningCutscene`: the intro story sequence.

## `game_data/` Modules

- `characters.py`: starting stats for playable classes.
- `enemies.py`: enemy name pools, enemy area spawning, and dragon boss color palettes.
- `interiors.py`: room layouts for town buildings, including props and inspect points.
- `mechanics.py`: combat math tuning, item effects, element visuals, and pickup rules.
- `npcs.py`: town guard data and NPC service dialogue.
- `progression.py`: boss progression, quest status text, and final boss level.
- `quests.py`: town errands and reward data.
- `town.py`: outdoor town buildings, walls, decorations, smoke sources, and collision tuning fields.
- `world.py`: 3x3 world layout, area descriptions, colors, particles, and environmental effects.

## `systems/` Modules

- `input_actions.py`: translates keyboard or virtual Android button input into action names like `move_up`.
- `save_load.py`: converts the current `Game` object into JSON and loads saved JSON back later.

## Important Data Patterns

- A `dict` stores named values, such as `{"health": 30, "mana": 10}`.
- A `tuple` stores fixed ordered values, such as `(255, 0, 0)` for a red RGB color.
- A `rect` means `(x, y, width, height)`.
- Screen positions use pixels. `x` grows to the right and `y` grows downward.
- Colors use RGB values from 0 to 255: `(red, green, blue)`.

## Safe Editing Rules

- Add or tune character stats in `game_data/characters.py`, not in `main.py`.
- Add enemy names or area enemy lists in `game_data/enemies.py`.
- Add town outdoor buildings in `game_data/town.py`.
- Add town room furniture or inspect points in `game_data/interiors.py`.
- Add NPC dialogue in `game_data/npcs.py`.
- Add boss names or boss hints in `game_data/progression.py`.
- Add save fields in both `systems/save_load.py` and the matching load code in `Game.load_saved_game`.
- Do not edit `archive/` unless you are intentionally preserving an old experiment.

## How To Add A New Town Building

1. Add the outdoor building record to `TOWN_BUILDINGS` in `game_data/town.py`.
2. Add its room layout to `TOWN_INTERIORS` in `game_data/interiors.py`.
3. Add its NPC/service text to `TOWN_SERVICES` in `game_data/npcs.py`.
4. Optional: add an errand in `TOWN_ERRANDS` in `game_data/quests.py`.
5. Make sure the building `type` string is the same in every file.

## How To Add A New Area Type

1. Add the area name to `WORLD_LAYOUT` in `game_data/world.py` if it should appear on the 3x3 map.
2. Add a readable label in `AREA_DESCRIPTIONS`.
3. Add colors in `AREA_VISUALS`.
4. Optional: add particles in `AREA_PARTICLE_PROFILES`.
5. Optional: add environmental effects in `AREA_MECHANICS`.
6. Optional: add enemies in `AREA_ENEMY_TYPES` in `game_data/enemies.py`.

## How To Add A New Item

1. Add the item profile to `ITEM_PROFILES` in `game_data/mechanics.py`.
2. Add the item key to `ITEM_SPAWN_TABLE` if it should appear in the world.
3. Make sure `Character.apply_item_effect` in `main.py` knows how to handle the item `effect`.

## How To Add Imported Art Or Sound Later

1. Put raw downloads in `assets/source/<category>/`.
2. Put converted game-ready files in `assets/processed/<category>/`.
3. Record non-CC0 licenses in `assets/credits.md`.
4. Update `assets/manifest.json` when a category changes from planned to active.
5. Only wire files into `main.py` after the path and license are clear.

## How To Build The Android App

1. Read `docs/android_app.md`.
2. Use Linux or WSL2, not a phone browser.
3. Run `bash scripts/build_android.sh` from the repository root.
4. Find the debug APK in `bin/`.
5. Install it on Android with `adb install -r bin/*debug.apk` or by opening the APK on the phone.
