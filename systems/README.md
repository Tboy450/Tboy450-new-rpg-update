# Runtime Systems

`systems/` contains active helper modules that are small enough to split out of `main.py` without moving core gameplay classes yet.

- `input_actions.py`: maps keyboard and Android virtual button inputs to gameplay actions.
- `assets.py`: centralizes imported art paths, sprite caching, animation frame loading, and reusable sprite drawing.
- `save_load.py`: serializes and loads JSON save data for the player, score, boss progress, visited areas, and town interaction progress.
- `__init__.py`: marks this folder as a Python package so helpers can be imported as `systems.assets`, `systems.input_actions`, and `systems.save_load`.

Keep this folder for reusable runtime systems. Pure tuning data still belongs in `game_data/`.

## Beginner Rule

Use `systems/` when the code performs a reusable job. Use `game_data/` when the
file is mostly facts, numbers, colors, text, or tuning values.

## `input_actions.py`

This module gives input a shared vocabulary.

- Pygame sends raw key constants such as `pygame.K_UP`.
- `input_actions.py` translates those raw keys into action strings such as `move_up`.
- `main.py` can then ask for actions instead of checking every possible key in every place.
- Android virtual buttons also map into the same actions, so keyboard and touch controls stay aligned.

When adding a new control:

- Add a new action string constant.
- Add keyboard keys to `KEY_ACTIONS`.
- Add Android button keys to `ANDROID_BUTTON_KEYS` if needed.
- Update `main.py` to react to the new action.

## `assets.py`

This module keeps imported-art plumbing out of `main.py`.

- Asset path constants point to the active processed PNG files and frame folders.
- `load_scaled_sprite` loads square enemy/UI-style sprites.
- `load_sprite_by_height` loads tall character/effect sprites without squashing them.
- `load_animation_frames` loads numbered PNG frame folders such as `frame_00.png`.
- `draw_character_sprite` draws Warrior/Mage/Rogue imported sprites with a shared foot anchor.
- `draw_enemy_sprite` draws enemies that have an imported sprite path.
- `get_story_sprite_path` maps story keys such as `lion_sage` and `ghost_face` to the active PNG files.

Active imported art paths:

- `GHOST_FACE_SPRITE_PATH`: processed Ghost Face enemy sprite.
- `LION_SAGE_SPRITE_PATH`: processed Lion Sage story NPC and portrait sprite.
- `TOWN_GUARD_SPRITE_PATH`: processed imported town guard overlay for the intro cutscene.
- `TITLE_DRAGON_SPRITE_PATH`: processed imported title-screen dragon.
- `FLAME_TORNADO_FRAME_DIR`: player SPECIAL travel animation frames.
- `FIRE_BLAST_FRAME_DIR`: Mage SPECIAL impact animation frames.
- `MAGE_MAGIC_FIREBALL_FRAME_DIR`: Mage normal MAGIC projectile overlay frames.

When adding a new imported effect:

- Save the raw upload under `assets/source/<category>/`.
- Save transparent game-ready PNG frames under `assets/processed/<category>/<effect_name>/`.
- Add the processed path constant to `assets.py`.
- Call `load_animation_frames` from the gameplay code that owns the timing.

## `save_load.py`

This module is responsible for turning live game objects into JSON-safe data.

- `build_save_data(game)` reads the current `Game` object and creates plain dictionaries, lists, strings, and numbers.
- `save_game_state(game)` writes that JSON-safe data to disk.
- `load_game_state()` reads the JSON file and checks the save version.
- `Game.load_saved_game` in `main.py` applies the loaded values back onto the live game objects.

When adding a new saved feature:

- Add the value to `build_save_data`.
- Add load/apply logic in `Game.load_saved_game`.
- Keep values JSON-safe: use strings, numbers, booleans, lists, and dictionaries.
