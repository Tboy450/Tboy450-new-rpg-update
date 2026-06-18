# Runtime Systems

`systems/` contains active helper modules that are small enough to split out of `main.py` without moving core gameplay classes yet.

- `input_actions.py`: maps keyboard and Android virtual button inputs to gameplay actions.
- `android_controls.py`: builds and draws the state-aware Android touch layout, including dialogue-safe button placement.
- `android_update.py`: owns the GitHub APK link, remote version check, and Android/desktop URL opening helpers.
- `assets.py`: centralizes imported art paths, sprite caching, animation frame loading, and reusable sprite drawing.
- `save_load.py`: serializes and loads JSON save data for the player, score, boss progress, visited areas, and town interaction progress.
- `story_ui.py`: draws reusable overlays such as the story dialogue box and shared pause menu.
- `__init__.py`: marks this folder as a Python package so helpers can be imported as `systems.assets`, `systems.input_actions`, `systems.android_controls`, `systems.android_update`, `systems.story_ui`, and `systems.save_load`.

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
- Add a preferred key to `ACTION_PRIMARY_KEYS` if touch buttons should be able to post the same action.
- Update `main.py` to react to the new action.

## `android_controls.py`

This module owns the Android touch-button layout.

- `build_android_touch_buttons(game, screen_width, screen_height)` decides which touch buttons should exist for the current UI state.
- `draw_android_touch_buttons(...)` draws those buttons.
- `find_android_touch_button(...)` hit-tests the buttons with a slightly larger tap target.
- `main.py` decides whether this module is active through `is_touch_ui_runtime`.
  That detector is broader than `sys.platform == "android"` because some APK
  launch paths do not report the same platform string.

Current touch-layout rules:

- Normal overworld/interior play uses a d-pad, `USE`, `OK`, and `MENU`.
- Story dialogue and the town-guard cutscene swap that layout for `NEXT` + `MENU`.
- Journal and world map use close buttons instead of the movement pad.
- The shared pause menu still runs game actions through `main.py`, but the
  overlay drawing now lives in `systems/story_ui.py`.

## `android_update.py`

This module owns the APK update plumbing.

- `APP_UPDATE_APK_URL` is the stable GitHub release asset URL.
- `APP_VERSION_SPEC_URL` points at the live `buildozer.spec` file on GitHub.
- `fetch_latest_android_numeric_version()` reads the remote version code.
- `open_external_url()` asks Android's Activity Manager to open the APK link when possible, then falls back to Python's browser support.

Use this module when changing update links, version-check behavior, or Android
intent opening. Keep gameplay menu logic in `main.py`, but keep APK-link logic
here.

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
- `FLAME_TORNADO_FRAME_DIR`: player SPECIAL travel animation frames.
- `FIRE_BLAST_FRAME_DIR`: Mage SPECIAL impact animation frames.
- `MAGE_MAGIC_FIREBALL_FRAME_DIR`: Mage normal MAGIC projectile overlay frames.

Beginner feature map:

- Lion Sage portrait and overworld sprite use `LION_SAGE_SPRITE_PATH`.
- The town intro imported knight uses `TOWN_GUARD_SPRITE_PATH`.
- The start-menu dragon is currently procedural code in `Dragon.draw` inside
  `main.py`; the mismatched generated title dragon is archived.
- The SPECIAL unlock is gameplay state, but `assets.py` is where the related story/effect art file paths are clearly labeled.

When adding a new imported effect:

- Save the raw upload under `assets/source/<category>/`.
- Save transparent game-ready PNG frames under `assets/processed/<category>/<effect_name>/`.
- Add the processed path constant to `assets.py`.
- Call `load_animation_frames` from the gameplay code that owns the timing.

## `story_ui.py`

This module owns two beginner-visible overlays that used to sit directly inside
`Game`:

- `draw_story_dialogue_overlay(...)`: draws the portrait, speaker name, wrapped text, and NEXT/keyboard prompt for Lion Sage, Ghost Face, and future story scenes.
- `draw_pause_menu_overlay(...)`: draws the dim background, pause panel, subtitle text, and the already-built pause buttons.

Keep story timing, menu commands, and save/load behavior in `main.py`. Use
`story_ui.py` when the change is only about how those overlays look.

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
