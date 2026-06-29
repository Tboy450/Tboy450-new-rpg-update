# Runtime Systems

`systems/` contains active helper modules that are small enough to split out of `main.py` without moving core gameplay classes yet.

- `input_actions.py`: maps keyboard and Android virtual button inputs to gameplay actions.
- `android_controls.py`: builds and draws the state-aware Android touch layout, including dialogue-safe button placement.
- `android_update.py`: owns the GitHub APK link, remote version check, and Android/desktop URL opening helpers.
- `assets.py`: centralizes imported art paths, sprite caching, animation frame loading, and reusable sprite drawing.
- `battle_input.py`: routes battle keyboard/touch events into the active action row or item row.
- `battle_rewards.py`: calculates scaled normal-enemy and boss rewards.
- `battle_ui.py`: draws reusable battle HUD pieces such as gear status, battle log, action buttons, and summary panels.
- `interior_ui.py`: draws reusable town-interior UI pieces such as service NPCs, service note cards, and the bottom prompt panel.
- `save_load.py`: serializes and loads JSON save data for the player, score, boss progress, visited areas, and town interaction progress.
- `story_ui.py`: draws reusable overlays such as the story dialogue box and shared pause menu.
- `town_services.py`: applies reusable town service mechanics and formats shared service labels, purpose text, and hint-card lines.
- `town_population_ui.py`: draws outdoor town residents, quest markers, names, and nearby talk prompts.
- `__init__.py`: marks this folder as a Python package so helpers can be imported as `systems.assets`, `systems.input_actions`, `systems.android_controls`, `systems.android_update`, `systems.interior_ui`, `systems.story_ui`, `systems.town_services`, `systems.town_population_ui`, and `systems.save_load`.

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
- `find_android_touch_button(...)` hit-tests the buttons with a small extra tap
  target. Keep this padding modest because stacked Android buttons can overlap
  mechanically if the hitboxes are too large.
- `find_android_touch_button_at_positions(...)` checks more than one coordinate
  guess. The APK sometimes reports real phone-display coordinates and
  sometimes reports the 1000x700 virtual game coordinates.
- `main.py` decides whether this module is active through `is_touch_ui_runtime`.
  That detector is broader than `sys.platform == "android"` because some APK
  launch paths do not report the same platform string.

Current touch-layout rules:

- Normal overworld/interior play uses a d-pad, `USE`, `OK`, and `MENU`.
- When the interior service menu is open, Android controls return an empty
  list because those service buttons are drawn and clicked by `main.py`.
- Story dialogue and the town-guard cutscene swap that layout for `NEXT` + `MENU`.
- Log and world map use close buttons instead of the movement pad.
- Battle action buttons are owned by `BattleScreen` in `main.py`, but input
  routing now lives in `systems/battle_input.py`. Combat still needs to know
  whether `SPECIAL` is unlocked and which turn is active, so the buttons are not
  part of the generic overworld Android d-pad system.
- The battle screen has its own small `ACTIONS` / `HIDE` toggle and a separate
  item row for Health/Mana/BACK. `battle_input.py` checks both raw and scaled
  Android tap coordinates so the buttons remain usable across APK launch paths.
- The shared pause menu still runs game actions through `main.py`, but the
  overlay drawing now lives in `systems/story_ui.py`.

## `android_update.py`

This module owns the APK update plumbing.

- `APP_UPDATE_APK_URL` is the stable GitHub release asset URL.
- `APP_UPDATE_APK_COMPAT_URL` is the older debug filename kept as a fallback.
- `APP_UPDATE_RELEASE_PAGE_URL` is the release page fallback if direct APK
  opening fails.
- `APP_UPDATE_GITHUB_APP_INTENT_URL` and `GITHUB_ANDROID_PACKAGE` are the
  GitHub Android app fallback when normal browser/download intents fail.
- `ANDROID_BROWSER_PACKAGES` lists browser package names to try before GitHub
  intercepts the APK URL.
- `APP_VERSION_SPEC_URL` points at the live `buildozer.spec` file on GitHub.
- `fetch_latest_android_numeric_version()` reads the remote version code.
- `open_android_update_download()` tries known Android browsers for the direct
  APK first, then the compatibility APK URL, then the GitHub Android app release
  fallback, then the release page.
- `open_external_url()` asks Android's Activity Manager to open links as normal
  browser/download URLs first, then falls back to Python's browser support.

Use this module when changing update links, version-check behavior, or Android
intent opening. Keep gameplay menu logic in `main.py`, but keep APK-link logic
here.

## `assets.py`

This module keeps imported-art plumbing out of `main.py`.

- Asset path constants point to the active processed PNG files and frame folders.
- `load_scaled_sprite` loads square enemy/UI-style sprites.
- `load_sprite_by_height` loads tall character/effect sprites without squashing them.
- `load_tinted_sprite_by_height` loads one PNG and applies a cached color tint.
  The title/opening dragon uses this so boss progression colors share one
  imported dragon asset.
- `load_animation_frames` loads numbered PNG frame folders such as `frame_00.png`.
- `draw_character_sprite` draws Warrior/Mage/Rogue imported sprites with a shared foot anchor.
- `draw_enemy_sprite` draws enemies that have an imported sprite path.
- `get_story_sprite_path` maps story keys such as `lion_sage`, `forest_apothecary`, `plains_ranger`, `star_cartographer`, `lantern_guard`, and `ghost_face` to active PNG files.
- `get_equipment_icon_path` maps equipment icon filenames to the processed equipment icon folder.
- `get_town_service_npc_sprite_path` maps town service keys such as `inn` and
  `blacksmith` to active imported service NPC sprites.

Active imported art paths:

- `GHOST_FACE_SPRITE_PATH`: processed Ghost Face enemy sprite.
- `LION_SAGE_SPRITE_PATH`: processed Lion Sage story NPC and portrait sprite.
- `FOREST_APOTHECARY_SPRITE_PATH`, `PLAINS_RANGER_SPRITE_PATH`,
  `STAR_CARTOGRAPHER_SPRITE_PATH`, and `LANTERN_GUARD_SPRITE_PATH`: processed
  side-story NPC sprites and portraits.
- `TOWN_GUARD_SPRITE_PATH`: processed imported town guard overlay for the intro cutscene.
- `SCENERY_ASSET_DIR`: processed active scenery sprite folder used by town
  buildings and interior props.
- `TITLE_DRAGON_SPRITE_PATH`: processed imported title-screen dragon.
- `FLAME_TORNADO_FRAME_DIR`: player SPECIAL travel animation frames.
- `FIRE_BLAST_FRAME_DIR`: Mage SPECIAL impact animation frames.
- `MAGE_MAGIC_FIREBALL_FRAME_DIR`: Mage normal MAGIC projectile overlay frames.
- `EQUIPMENT_ICON_DIR`: processed Inventory equipment icons.
- `TOWN_SERVICE_NPC_SPRITE_PATHS`: active imported NPC sprites used by town
  service interiors such as Warm Hearth Inn and Ironroot Forge.

Beginner feature map:

- Lion Sage portrait and overworld sprite use `LION_SAGE_SPRITE_PATH`.
- The town intro imported knight uses `TOWN_GUARD_SPRITE_PATH`.
- Innkeeper and Blacksmith interior sprites use
  `TOWN_SERVICE_NPC_SPRITE_PATHS`; their screen placement lives in
  `game_data/interiors.py`.
- The start-menu dragon loads `TITLE_DRAGON_SPRITE_PATH` first and then draws
  a boss-palette tint and animated fire extension from the imported dragon's
  mouth. The opening cutscene uses the same imported dragon path now. The older
  procedural dragon remains as fallback/archive code in `Dragon.draw`.
- The SPECIAL unlock is gameplay state, but `assets.py` is where the related story/effect art file paths are clearly labeled.
- Inventory gear uses icon filenames from `game_data/equipment.py`; those filenames are joined to `EQUIPMENT_ICON_DIR` by `get_equipment_icon_path`.

When adding a new imported effect:

- Save the raw upload under `assets/source/<category>/`.
- Save transparent game-ready PNG frames under `assets/processed/<category>/<effect_name>/`.
- Add the processed path constant to `assets.py`.
- Call `load_animation_frames` from the gameplay code that owns the timing.

## `battle_input.py`

This module owns battle-specific input routing.

- `handle_battle_input(...)` handles battle pauses, NEXT/ENTER continuation,
  action row navigation, the ACTIONS/HIDE toggle, item-row taps, and Android
  coordinate fallback checks.
- `get_touch_positions(...)` checks both raw and scaled coordinates because APK
  launch paths can report touch positions differently.
- `play_game_sound(...)` safely plays optional sound effects from `Game`.

Keep turn rules and action math in `BattleScreen`; use this module when a
keyboard/touch battle input path needs to change.

## `battle_ui.py`

This module draws reusable battle panels.

- `draw_battle_gear_strip(...)` draws the equipped weapon and effective stats.
- `draw_battle_log_panel(...)` draws the top battle log and fitted long lines.
- `draw_battle_action_buttons(...)` draws the action row, item row, potion
  counts, special MP cost, and escape chance.
- `draw_battle_summary(...)` draws the victory/defeat/escape overlay.
- `set_button_text(...)` updates button labels such as `HEALTH x2`.

Keep character sprites, projectiles, and attack effects in `BattleScreen` until
those animation systems are split out separately.

## `battle_rewards.py`

This module keeps reward formulas out of the game loop.

- `get_regular_enemy_reward(...)` scales normal enemy EXP/score from enemy
  health, strength, and speed instead of using a flat value for every fight.
- `get_boss_reward(...)` reads boss reward fields and provides safe fallback
  numbers if a future boss forgets to define them.

Story enemy first-clear/repeat rewards still live in `game_data/story.py`
because they are quest-specific reward tables.

## `story_ui.py`

This module owns two beginner-visible overlays that used to sit directly inside
`Game`:

- `draw_story_dialogue_overlay(...)`: draws the portrait, speaker name, wrapped text, and NEXT/keyboard prompt for Lion Sage, Ghost Face, and future story scenes.
- `draw_pause_menu_overlay(...)`: draws the dim background, pause panel, subtitle text, and the already-built pause buttons.

Keep story timing, menu commands, and save/load behavior in `main.py`. Use
`story_ui.py` when the change is only about how those overlays look.

## `interior_ui.py`

This module draws reusable town-interior UI pieces that were split out of
`main.py`.

- `draw_interior_npc(...)` draws imported service NPC sprites for rooms like the
  Inn and Blacksmith, with the older simple Python NPC as fallback.
- `draw_interior_service_card(...)` draws the small service note card on the
  room wall.
- `draw_interior_service_menu(...)` draws the clickable service/talk/log/leave
  menu that opens inside town buildings.
- `draw_interior_message_panel(...)` wraps room messages and draws the
  Android/keyboard prompt line.

Keep movement, collision, inspecting objects, and activating services in
`main.py`. Use `interior_ui.py` when the change is only about how an interior UI
piece looks.

## `town_services.py`

This module owns town service effects that should not keep growing inside
`main.py`.

- `apply_inn_rest_service(...)` restores HP/MP and grants a small once-per-level
  rest bonus using the already-saved `town_service_claims` set.
- `apply_blacksmith_forge_service(...)` grants level-gated forge gear and sends
  it to Inventory without auto-equipping it.
- `get_service_hint_lines(...)` gives the interior wall card short preview text
  for richer rooms.
- `get_service_action_label(...)` names the first interior service-menu button,
  such as REST, FORGE, STUDY, REPORT, or STEW.
- `get_service_map_label(...)`, `get_service_completion_label(...)`, and
  `get_service_overview_lines(...)` let outdoor markers, interiors, and the Log
  reuse the same building labels and purpose text.

Future inn mini-games should start here or in a nearby module, then connect to
the Inn room through `Game.use_current_town_service` or a new interior action.

## `town_population_ui.py`

This module draws outdoor town residents.

- Resident names, positions, colors, dialogue, and errand rewards live in
  `game_data/town_population.py`.
- `draw_town_residents(...)` draws the small resident sprite, quest marker,
  name label, and nearby talk prompt.
- `Game.draw_town_population` in `main.py` decides when to call this helper and
  which resident is currently nearby.
- Resident Log guidance is calculated in `game_data/town_population.py` so the
  same ready/locked rules are used by both the Log and the actual talk action.

Use this module when changing how outdoor town residents look. Use
`game_data/town_population.py` when changing who they are, where they stand, or
what rewards they give.

## `save_load.py`

This module is responsible for turning live game objects into JSON-safe data.

- `build_save_data(game)` reads the current `Game` object and creates plain dictionaries, lists, strings, and numbers.
- `save_game_state(game)` writes that JSON-safe data to disk.
- `load_game_state()` reads the JSON file and checks the save version.
- `Game.load_saved_game` in `main.py` applies the loaded values back onto the live game objects.
- Story trophies live on `Character.story_items` and are saved under the player data.
- Equipped gear lives on `Character.equipment`, owned gear lives on
  `Character.owned_equipment`, and both are saved under player data.
- Story enemy first-clear/repeat counts live on `Game.story_enemy_defeats` and are saved under story data.
- Outdoor town resident errands live on `Game.completed_resident_errands` and
  are saved under town data.

When adding a new saved feature:

- Add the value to `build_save_data`.
- Add load/apply logic in `Game.load_saved_game`.
- Keep values JSON-safe: use strings, numbers, booleans, lists, and dictionaries.
