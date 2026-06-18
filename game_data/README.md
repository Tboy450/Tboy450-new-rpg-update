# Game Data Module Map

`game_data` is the active data layer for `main.py`. Keep old experiment files in `archive/` as reference only.

Import active data through `game_data/__init__.py` when possible. That file is the compatibility boundary, so data can move between modules without breaking `main.py`.

For beginners: this folder mostly contains Python dictionaries and tuples.
Changing values here usually changes the game without changing control flow.
For example, changing a color tuple changes how something looks, while changing
an enemy list changes what can spawn in an area.

## Modules

- `__init__.py`: re-exports active data so `main.py` can import from one stable place.
- `characters.py`: playable class starting stats. Edit this to tune Warrior, Mage, or Rogue.
- `enemies.py`: enemy names, area enemy spawn tables, and dragon boss color palettes.
- `interiors.py`: town building interior layouts, props, inspect points, colors, and room prompts.
- `mechanics.py`: combat tuning, elemental status effects, pickup item profiles, and item spawn tables.
- `npcs.py`: town guard template/dialogue, town service NPC metadata, and rotating interior NPC dialogue.
- `progression.py`: boss names, boss hints, final boss level, and player-facing quest status.
- `quests.py`: town errand names, summaries, and rewards.
- `story.py`: opening story text, Lion Sage map placement/dialogue/reward, and Ghost Face area intro dialogue.
- `town.py`: town overworld buildings, boundaries, decorations, smoke sources, and building collision tuning.
- `world.py`: world grid layout, area descriptions, area visuals, area particles, and environmental area effects.

## Beginner Data Glossary

- `x`, `y`: pixel position on the screen. `x` moves right. `y` moves down.
- `width`, `height`: size in pixels.
- `rect`: a rectangle written as `(x, y, width, height)`.
- `color`: an RGB tuple like `(255, 0, 0)`, where each number is 0-255.
- `type`: a short key string used to connect data across modules.
- `style`: a drawing hint used by `main.py` to choose a visual style.
- `collision`: whether the player should be blocked by an object.
- `entry_depth`: how far the player can visually step into the front or back of a building.
- `door_width`: how wide the entrance trigger should be.
- `reward`: score, experience, reputation, or item prizes granted by a quest or errand.
- `message`: text shown to the player.

## Cross-File Keys

Some strings must match across modules:

- Town building `type` values in `town.py` should match `TOWN_INTERIORS`, `TOWN_SERVICES`, and optional `TOWN_ERRANDS` keys.
- Enemy element names like `fiery`, `shadow`, and `ice` should match entries in `ELEMENT_PROFILES`.
- Item keys like `health` and `mana` should match entries in `ITEM_PROFILES`.
- Area names like `forest`, `town`, and `volcano` should match entries in `WORLD_LAYOUT`, `AREA_VISUALS`, and `AREA_ENEMY_TYPES`.
- Story sprite keys like `lion_sage` and `ghost_face` should match `STORY_SPRITE_PATHS` in `systems/assets.py`.

## Placement Rules

- Enemy or boss resource data belongs in `enemies.py` or `progression.py`, not `world.py`.
- Area visuals or behavior that affect the map belong in `world.py`.
- Town NPC/service text and dialogue belongs in `npcs.py`; town room layout and inspect text belongs in `interiors.py`.
- Town overworld layout belongs in `town.py`; building room contents belong in `interiors.py`.
- Town errand/reward data belongs in `quests.py`.
- Main quest story beats, one-shot area dialogue, and friendly story NPC placement belong in `story.py`.
- Reusable combat or pickup tuning belongs in `mechanics.py`.
- Do not add new active gameplay data to `archive/`.

## Safe Editing Examples

- To make Warrior tougher, raise `Warrior` `max_health` in `characters.py`.
- To make volcano enemies more dangerous by variety, add another element key to `AREA_ENEMY_TYPES["volcano"]` in `enemies.py`.
- To move the shop outdoors, edit the shop record in `TOWN_BUILDINGS` in `town.py`.
- To add a line of shopkeeper dialogue, edit the `shop` `dialogue` tuple in `npcs.py`.
- To add an inspectable object inside the inn, edit `TOWN_INTERIORS["inn"]["inspect_points"]` in `interiors.py`.
- To tune critical hits, edit `BATTLE_RULES` in `mechanics.py`.
- To move the Lion Sage, edit `STORY_NPCS["lion_sage"]["local_position"]` in `story.py`.
- To change when SPECIAL unlocks, edit the `reward` block in `STORY_AREA_DIALOGUES["lion_sage_swamp"]`.

## Story Data Map

`story.py` is the main beginner entry point for the first quest flow.

- `OPENING_STORY_LINES`: short title-scene text shown before character selection.
  The longer readable parchment pages and their timing live in
  `OpeningCutscene` in `main.py`, because that layout is tied to animation.
- `TOWN_GUARD_STORY_LINES`: extra town-guard warning lines that point the player toward Lion Sage and Ghost Face.
- `STORY_NPCS`: friendly story NPC placement records for the world map.
- `STORY_AREA_DIALOGUES`: one-shot or repeat story scenes, including Lion Sage and Ghost Face.
- `STORY_REWARD_ITEMS`: permanent trophies and story keepsakes shown in the Inventory screen.
- `STORY_ENEMY_REWARDS`: first-clear and repeat-clear rewards for respawning story enemies.

Current first-story path:

- The guard warns about the dragon and sends the player toward Lion Sage.
- Lion Sage gives the first real quest direction, a large EXP training reward, a trophy, and the first SPECIAL unlock.
- Ghost Face uses one-time area-enter dialogue in the forest, can respawn, and gives a larger first-clear reward than repeat clears.

## Asset Intake

Use `assets/source/` for raw downloaded art/audio and `assets/processed/` for files ready to load. Record non-CC0 attribution in `assets/credits.md` before wiring assets into the game.
