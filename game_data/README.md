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
- `equipment.py`: weapons, armor, accessories, starting gear, blacksmith forge progression, rarity/tier labels, icon filenames, and equipment stat bonuses.
- `interiors.py`: town building interior layouts, props, inspect points, colors, and room prompts.
- `mechanics.py`: combat tuning, elemental status effects, pickup item profiles, and item spawn tables.
- `npcs.py`: town guard template/dialogue, town service NPC metadata, and rotating interior NPC dialogue.
- `progression.py`: boss names, boss hints, final boss level, and player-facing quest status.
- `quests.py`: town errand names, summaries, and rewards.
- `story.py`: opening story text, Lion Sage map placement/dialogue/reward, and Ghost Face area intro dialogue.
- `town.py`: town overworld buildings, boundaries, decorations, smoke sources, and building collision tuning.
- `town_population.py`: outdoor town residents, their rotating dialogue, one-time resident errands, and resident rewards.
- `world.py`: world grid layout, area descriptions, area visuals, area particles, and environmental area effects.

## Beginner Data Glossary

- `x`, `y`: pixel position on the screen. `x` moves right. `y` moves down.
- `width`, `height`: size in pixels.
- `rect`: a rectangle written as `(x, y, width, height)`.
- `color`: an RGB tuple like `(255, 0, 0)`, where each number is 0-255.
- `type`: a short key string used to connect data across modules.
- `style`: a drawing hint used by `main.py` to choose a visual style.
- `sprite`: optional relative PNG filename used when a building or prop should
  draw imported art instead of only Python shapes.
- `sprite_rect`: optional rectangle used to draw a building sprite. This can be
  larger than the collision rectangle when the art includes a roof or sign.
- `npc_sprite_rect`: optional interior-room rectangle used to draw an imported
  service NPC sprite instead of the older simple Python-drawn NPC body.
- `collision`: whether the player should be blocked by an object.
- `entry_depth`: how far the player can visually step into the front or back of a building.
- `door_width`: how wide the entrance trigger should be.
- `interaction_depth`: optional doorway trigger height. Lower this when two
  nearby buildings need separated entrance/action zones.
- `reward`: score, experience, reputation, or item prizes granted by a quest or errand.
- `message`: text shown to the player.
- `map_label`: short doorway label used on the outdoor town map.
- `role`: one- or two-word service category, such as Recovery, Gear, or Lore.
- `purpose`: player-facing reason to visit a town service.
- `first_reward`: what the first one-time building errand can give.
- `repeat_use`: why the service still matters after the first errand is done.

## Cross-File Keys

Some strings must match across modules:

- Town building `type` values in `town.py` should match `TOWN_INTERIORS`, `TOWN_SERVICES`, and optional `TOWN_ERRANDS` keys.
- Enemy element names like `fiery`, `shadow`, and `ice` should match entries in `ELEMENT_PROFILES`.
- Item keys like `health` and `mana` should match entries in `ITEM_PROFILES`.
- Equipment keys like `lion_sage_charm` and `mask_shard_edge` should match entries in `EQUIPMENT_ITEMS`.
- Equipment `icon` filenames in `equipment.py` should match PNG files in `assets/processed/equipment/`.
- Scenery `sprite` filenames in `town.py` and `interiors.py` should match PNG
  files under `assets/processed/scenery/`.
- Interior `npc_sprite_rect` entries in `interiors.py` depend on service keys
  in `systems/assets.py` `TOWN_SERVICE_NPC_SPRITE_PATHS`.
- Area names like `forest`, `town`, and `volcano` should match entries in `WORLD_LAYOUT`, `AREA_VISUALS`, and `AREA_ENEMY_TYPES`.
- Story sprite keys like `lion_sage` and `ghost_face` should match `STORY_SPRITE_PATHS` in `systems/assets.py`.

## Placement Rules

- Enemy or boss resource data belongs in `enemies.py` or `progression.py`, not `world.py`.
- Area visuals or behavior that affect the map belong in `world.py`.
- Town NPC/service text and dialogue belongs in `npcs.py`; town room layout and inspect text belongs in `interiors.py`.
- Outdoor town residents who stand on the town map belong in `town_population.py`.
- Town overworld layout belongs in `town.py`; building room contents belong in `interiors.py`.
- Town errand/reward data belongs in `quests.py`.
- Main quest story beats, one-shot area dialogue, and friendly story NPC placement belong in `story.py`.
- Reusable combat or pickup tuning belongs in `mechanics.py`.
- Wearable weapon/armor/accessory data belongs in `equipment.py`.
- Do not add new active gameplay data to `archive/`.

## Safe Editing Examples

- To make Warrior tougher, raise `Warrior` `max_health` in `characters.py`.
- To make volcano enemies more dangerous by variety, add another element key to `AREA_ENEMY_TYPES["volcano"]` in `enemies.py`.
- To move the shop outdoors, edit the shop record in `TOWN_BUILDINGS` in `town.py`.
- To add a line of shopkeeper dialogue, edit the `shop` `dialogue` tuple in `npcs.py`.
- To make a building clearer on the town map, edit its `map_label`, `role`,
  `purpose`, `first_reward`, or `repeat_use` fields in `TOWN_SERVICES`.
- To add an outdoor town resident, edit `TOWN_RESIDENTS` and optional `TOWN_RESIDENT_ERRANDS` in `town_population.py`.
- To add an inspectable object inside the inn, edit `TOWN_INTERIORS["inn"]["inspect_points"]` in `interiors.py`.
- To tune critical hits, edit `BATTLE_RULES` in `mechanics.py`.
- To tune gear, edit the item record in `EQUIPMENT_ITEMS` in `equipment.py`. The most common fields are `tier`, `rarity`, `icon`, `bonuses`, and `description`.
- To tune blacksmith progression, edit `BLACKSMITH_GEAR_REWARDS` in `equipment.py`.
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
- Lion Sage gives the first real quest direction, a large EXP training reward, a trophy, the first SPECIAL unlock, and the Lion Sage Charm accessory.
- Ghost Face uses one-time area-enter dialogue in the forest, can respawn, and gives a larger first-clear reward than repeat clears. The first clear also equips the Mask-Shard Edge weapon.

## Town Population Map

`town_population.py` is for people outside on the town map, not inside
buildings.

- `TOWN_RESIDENTS`: where each resident stands, how they look, their prompt,
  and their rotating dialogue.
- `TOWN_RESIDENT_ERRANDS`: one-time resident errands, lock requirements, reward
  data, and completion messages.
- Resident errands can reward score, EXP, reputation, consumable items, class
  gear, or normal equipment.
- `systems/town_population_ui.py` draws the residents; the data stays here so
  the drawing helper does not become a second source of truth.

## Asset Intake

Use `assets/source/` for raw downloaded art/audio and `assets/processed/` for files ready to load. Record non-CC0 attribution in `assets/credits.md` before wiring assets into the game.
