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
- `story.py`: opening story lines, Lion Sage placement and reward, Ghost Face area dialogue, and other first-quest story data.
- `town.py`: outdoor town buildings, walls, decorations, smoke sources, and collision tuning fields.
- `world.py`: 3x3 world layout, area descriptions, colors, particles, and environmental effects.

## `systems/` Modules

- `assets.py`: imported-art paths, sprite caches, animation frame loading, and reusable sprite drawing.
- `android_controls.py`: state-aware Android touch button layout, drawing, and tap hit-testing.
- `android_update.py`: APK update URL constants, GitHub version-check helper, and Android/desktop link opening helper.
- `input_actions.py`: translates keyboard or virtual Android button input into action names like `move_up`.
- `save_load.py`: converts the current `Game` object into JSON and loads saved JSON back later.
- `story_ui.py`: draws the reusable story dialogue panel and the shared pause-menu overlay.

## Story + Asset Quick Map

Use this when you know the feature name but not the file.

- Lion Sage story logic:
  `game_data/story.py` stores his world-map placement, dialogue, repeat lines, reward, and the `unlock_special` flag.
- Lion Sage art:
  `assets/processed/npcs/lion_sage.png` is the active sprite and portrait.
  `systems/assets.py` labels the path.
  `Game.draw_story_npcs` and `Game.draw_story_dialogue` in `main.py` draw it.
- Town guard story warning:
  `game_data/npcs.py` stores the base guard template.
  `game_data/story.py` stores the newer warning lines about the dragon, Ghost Face, and Lion Sage.
  `main.py` appends those story lines onto the guard dialogue during town setup.
- Town guard imported art:
  `assets/processed/npcs/town_guard.png` is the imported overlay.
  `WorldArea.draw_cutscene` in `main.py` draws it on top of the old procedural guard.
- Title dragon imported art:
  `assets/processed/ui/title_dragon.png` is the active title-screen dragon art.
  `Dragon.draw` in `main.py` uses it first and keeps the older procedural dragon as fallback.
- SPECIAL unlock flow:
  `game_data/story.py` grants the first unlock through the Lion Sage reward.
  `Game.apply_story_reward` in `main.py` sets `player.special_unlocked = True`.
  `systems/save_load.py` stores that flag in the save file.
  `BattleScreen.__init__` only creates the `SPECIAL` button if that flag is true.
- Imported effect art tied to that flow:
  `assets/processed/effects/flame_tornado/` is the SPECIAL travel animation.
  `assets/processed/effects/fire_blast/` is the Mage impact animation.
  `assets/processed/effects/mage_magic_fireball/` is the Mage normal magic overlay.

## Pause + Touch Control Map

Use this when you want to change Android controls, the pause menu, or the
beginner-facing control labels.

- Keyboard action names and primary key mappings:
  `systems/input_actions.py`
- Android touch layout and draw rules:
  `systems/android_controls.py`
- Shared pause-menu logic and button commands:
  `Game.build_pause_menu_entries`, `Game.toggle_pause_menu`, and `Game.activate_pause_menu_command` in `main.py`
- Shared pause-menu drawing:
  `systems/story_ui.py`
- Journal control text:
  `Game.draw_journal` in `main.py`
- Story dialogue box, portrait, and `NEXT` prompt:
  `systems/story_ui.py`, called by `Game.draw_story_dialogue` in `main.py`
- Overworld corner control legend:
  `Game.draw` in `main.py`

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

## How To Edit Lion Sage

1. Change Lion Sage story text, repeat lines, reward, or SPECIAL unlock behavior in `game_data/story.py`.
2. Move him on the world map by editing `STORY_NPCS["lion_sage"]["local_position"]`.
3. Change his sprite by replacing `assets/processed/npcs/lion_sage.png`.
4. If you rename the sprite file or add another story sprite key, update `STORY_SPRITE_PATHS` in `systems/assets.py`.
5. If you want him easier or harder to interact with, tune `Game.get_nearby_story_npc` in `main.py`.

## How To Edit The Guard + Title Dragon

1. Replace `assets/processed/npcs/town_guard.png` to change the imported guard look.
2. Replace `assets/processed/ui/title_dragon.png` to change the imported title dragon look.
3. `WorldArea.draw_cutscene` handles the imported guard overlay and still keeps the procedural guard behind it as fallback.
4. `Dragon.draw` handles the imported title dragon and still keeps the procedural title dragon as fallback.

## How To Tune Fire Tornado

Fire Tornado is the player's `SPECIAL` battle action.
Mage uses the same SPECIAL button, but its displayed name is `Fire Blast` and
it adds a second imported impact animation when the tornado reaches the enemy.

1. Change the displayed attack name in `SPECIAL_ATTACK_NAME` near the top of `main.py`.
2. Change the Mage-only displayed name in `MAGE_SPECIAL_ATTACK_NAME`.
3. Change MP cost in `SPECIAL_ATTACK_MANA_COST`.
4. Change animation wait time in `SPECIAL_ATTACK_DURATION`.
5. Change visual motion, glow, title text, and impact lines in `BattleScreen.draw_player_special_fx`.
6. Change startup particles in `BattleScreen.start_special_animation`.
7. Change damage in `BattleScreen.execute_special_attack`.
8. Replace the imported frames in `assets/processed/effects/flame_tornado/` if you want a different animation.
9. Replace Mage Fire Blast impact frames in `assets/processed/effects/fire_blast/`.
10. Add new imported effect folder paths in `systems/assets.py`, not directly in `main.py`.

## How To Tune Mage Normal Magic Graphics

Mage's normal `MAGIC` button still uses the older procedural magic ring, beam,
particles, and explosion. The imported projectile is an extra overlay.

1. Replace frames in `assets/processed/effects/mage_magic_fireball/` to change the imported fireball overlay.
2. Change the overlay size in `BattleScreen.start_magic_animation`, where it calls `load_animation_frames(MAGE_MAGIC_FIREBALL_FRAME_DIR, target_height=82)`.
3. Change how the cutout is positioned in the fireball drawing block inside `BattleScreen.draw`.
4. Keep the old procedural circles in that same draw block if you want the fallback to remain visible.
5. Add future imported magic frame folder paths in `systems/assets.py`.

## Future Asset Import Wishlist

These would give the biggest visible upgrade next:

1. Overworld walk cycles for Warrior, Mage, and Rogue: idle/down/up/left/right frames so movement feels animated instead of sliding one still sprite.
2. Battle idle, hurt, attack, and victory poses for each hero class.
3. Enemy sprites for common area enemies: fire, ice, shadow, and crystal variants so random battles stop relying on drawn circles.
4. Boss dragon sprites: idle, wing flap, roar, bite/claw, fire breath, hurt, and defeat.
5. Town and building tiles: grass, dirt paths, walls, roofs, doors, signs, windows, fountains, trees, and interior furniture.
6. UI icons: health potion, mana potion, sword, staff, dagger, shield, gold, quest marker, save marker, and update/download marker.
7. Attack effects by class: Warrior slash arcs, Mage lightning/ice/fire variants, Rogue knife trails, poison clouds, smoke bombs, and critical-hit bursts.
8. Status effect icons and overlays: burn, chill, poison, stun, shield, haste, and low-health warning.
9. Item pickup sprites: treasure chest, potion bottle, mana crystal, key, scroll, and rare relic.
10. Audio imports: menu confirm/cancel, footsteps, sword hit, staff cast, dagger throw, enemy hit, boss roar, victory sting, game-over sting, and loopable town/battle/boss music.
11. App/UI polish assets: cleaner launcher icon variants, title logo, start-menu background, loading/update screen art, and Android notification icon.

## How To Tune Ghost Face

1. Change Ghost Face's shared colors/status in `game_data/mechanics.py`, under `ELEMENT_PROFILES["ghost_face"]`.
2. Change its battle move list in `BattleScreen.choose_ghostface_attack` in `main.py`.
3. Add a new attack effect by adding a new `fx` name in `choose_ghostface_attack`, a matching case in `draw_enemy_attack_fx`, and a drawing method.
4. Keep `ghost_face` out of `AREA_ENEMY_TYPES` unless you want it to spawn randomly like a normal enemy.

## How To Replace Player Character Sprites

The active imported character art lives in `assets/processed/characters/`.

1. Replace `warrior.png`, `mage.png`, or `rogue.png` with a transparent PNG.
2. Keep the class names in `CHARACTER_SPRITE_PATHS` in `systems/assets.py` unchanged unless you also rename the character class.
3. `systems/assets.py` has `load_sprite_by_height`, which loads and resizes each PNG while keeping its original shape.
4. `systems/assets.py` has `draw_character_sprite`, which places the sprite by its center and feet so it lines up in both world and battle screens.
5. `Character.draw` calls `draw_character_sprite` first. If the imported PNG cannot load, the older Python-drawn character code below it still draws a fallback hero.
6. The world map uses `sprite_mode="world"` and battle uses `sprite_mode="battle"` to choose different sprite heights.

## How The Android Update Button Works

1. `APP_NUMERIC_VERSION` in `main.py` is the installed app's current version code.
2. `android.numeric_version` in `buildozer.spec` is the version code Android uses when installing the APK.
3. Both numbers must increase before publishing a new APK.
4. `systems/android_update.py` stores the stable APK URL and the GitHub `buildozer.spec` URL.
5. `fetch_latest_android_numeric_version` in that module reads `buildozer.spec` from GitHub.
6. `check_for_updates` in `main.py` compares the GitHub version code with the installed version code.
7. `open_update_link` in `main.py` calls `open_external_url` from `systems/android_update.py`. Android still requires the player to approve the install/update prompt.

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

## iPhone / iPad Install Status

Read `docs/ios_app.md`. iPhone support needs a signed TestFlight, App Store, or
IPA build before there can be a real install link.
