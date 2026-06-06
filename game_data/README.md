# Game Data Module Map

`game_data` is the active data layer for `main.py`. Keep old experiment files in `archive/` as reference only.

Import active data through `game_data/__init__.py` when possible. That file is the compatibility boundary, so data can move between modules without breaking `main.py`.

## Modules

- `characters.py`: playable class starting stats.
- `enemies.py`: enemy names, area enemy spawn tables, and dragon boss color palettes.
- `interiors.py`: town building interior layouts, props, inspect points, colors, and room prompts.
- `mechanics.py`: combat tuning, elemental status effects, pickup item profiles, and item spawn tables.
- `npcs.py`: town guard template/dialogue, town service NPC metadata, and rotating interior NPC dialogue.
- `progression.py`: boss names, boss hints, final boss level, and player-facing quest status.
- `quests.py`: town errand names, summaries, and rewards.
- `town.py`: town overworld buildings, boundaries, decorations, and smoke sources.
- `world.py`: world grid layout, area descriptions, area visuals, area particles, and environmental area effects.

## Placement Rules

- Enemy or boss resource data belongs in `enemies.py` or `progression.py`, not `world.py`.
- Area visuals or behavior that affect the map belong in `world.py`.
- Town NPC/service text and dialogue belongs in `npcs.py`; town room layout and inspect text belongs in `interiors.py`.
- Town overworld layout belongs in `town.py`; building room contents belong in `interiors.py`.
- Town errand/reward data belongs in `quests.py`.
- Reusable combat or pickup tuning belongs in `mechanics.py`.
- Do not add new active gameplay data to `archive/`.

## Asset Intake

Use `assets/source/` for raw downloaded art/audio and `assets/processed/` for files ready to load. Record non-CC0 attribution in `assets/credits.md` before wiring assets into the game.
