# Recent Commit Walkthrough For Beginners

This guide explains the purpose of the last few larger commits in plain terms.
It is meant for beginner coders and future AI helpers who need to understand why
the newer files and helper modules exist before changing them.

## 65a57d8 - Activate Town Building Scenery Assets

Purpose:

- Turns several town buildings and room props from Python-drawn shapes into
  imported PNG scenery.
- Keeps the older Python drawing code as fallback behavior when an image file is
  missing or fails to load.
- Does not turn the PNG files into collision. Movement and entering buildings
  still use data rectangles from `game_data/town.py`.

Files to read first:

- `game_data/town.py`: outdoor town building positions, collision sizes, and
  sprite rectangles.
- `game_data/interiors.py`: indoor room props, service NPC sprite rectangles,
  and inspect points.
- `assets/processed/scenery/`: active processed building and furniture PNGs.
- `main.py`: still owns the actual drawing loop and fallback shapes.

Important idea: each outdoor building can have two rectangles.

- `x`, `y`, `width`, `height`: gameplay rectangle. This blocks movement and
  places the doorway.
- `sprite_rect`: art rectangle. This draws the imported PNG and can be larger
  than the gameplay rectangle when the art includes a roof, sign, smoke, or
  shadow.

Beginner section breakdown:

- `TOWN_BUILDINGS` in `game_data/town.py`: one dictionary per outdoor building.
  The `type` key connects the outdoor building to its interior room and service.
- `sprite`: relative filename inside `assets/processed/scenery/`.
- `sprite_rect`: where that PNG appears on the town screen.
- `sprite_anchor`: tells the sprite helper how to line up the image. Most town
  buildings use `bottom` so the door/base stays planted.
- `entry_depth`, `door_width`, `interaction_depth`: tune how close the player
  must stand before OK/USE enters that building.

## d6d94bd - Clarify Town Entrances And Touch Controls

Purpose:

- Makes town entrance interaction spaces more obvious and less overlapping.
- Adds the visible doorway marker so the player can tell when a building is
  enterable.
- Moves Android touch layout decisions into `systems/android_controls.py`.
- Stops normal Android movement buttons from covering story/dialogue panels.

Files to read first:

- `main.py`: `WorldArea.get_building_entry_rect`,
  `WorldArea.get_nearby_town_service`, `Game.draw_town_service_marker`, and the
  Android touch block inside `Game.run`.
- `systems/android_controls.py`: builds, draws, and hit-tests Android buttons.
- `game_data/town.py`: stores the doorway tuning fields.

Important idea: entrance rectangles and collision rectangles are separate.

- Collision rectangles stop the player from walking through walls.
- Entrance rectangles decide when OK/USE should enter a building.
- Keeping those separate lets the player stand near a doorway without making the
  entire front wall act like a door.

Beginner section breakdown:

- `WorldArea.get_building_entry_rect(building)`: builds the doorway trigger
  rectangle from `door_width` and `interaction_depth`.
- `WorldArea.get_nearby_town_service(player_x, player_y)`: checks whether the
  player overlaps that doorway trigger, then returns the matching service data.
- `Game.draw_town_service_marker(...)`: draws the pulsing marker from the same
  rectangle that the interaction code uses.
- `build_android_touch_buttons(...)`: chooses which phone buttons should exist
  for the current screen. Dialogue uses `NEXT`; exploration uses movement,
  `OK`, `USE`, and `MENU`.
- `find_android_touch_button_at_positions(...)`: checks more than one touch
  coordinate guess because Android builds can report raw fullscreen pixels or
  the game's 1000x700 virtual pixels.

## d9da1e5 - Improve Battle Mechanics And Modular Helpers

Purpose:

- Moves repeated battle input, battle HUD drawing, and reward formulas into
  smaller modules.
- Keeps battle state and attack math inside `BattleScreen` in `main.py`.
- Makes Android battle buttons easier to show again if they are hidden.

Files to read first:

- `systems/battle_input.py`: keyboard/touch battle event routing.
- `systems/battle_ui.py`: drawing for battle log, gear strip, buttons, and
  result summary.
- `systems/battle_rewards.py`: normal enemy and boss reward formulas.
- `main.py`: `BattleScreen` still owns turn state, selected action, animations,
  damage, and when rewards are applied.

Important idea: the helper modules do not own the whole battle.

- `battle_input.py` decides what a tap or key press means.
- `battle_ui.py` draws reusable panels.
- `battle_rewards.py` calculates reward numbers.
- `BattleScreen` still owns whether it is the player's turn, which buttons
  exist, and what each attack does.

Beginner section breakdown:

- `handle_battle_input(...)` first handles NEXT/summary pauses, then ignores
  input when it is not the player's turn, then handles keyboard, then handles
  touch.
- The `ACTIONS` / `HIDE` button is checked before attack buttons so one tap
  cannot both reveal the row and accidentally attack.
- When the battle buttons are hidden on Android, tapping the lower command lane
  reveals them again.
- `draw_battle_action_buttons(...)` draws the toggle button every player turn,
  then draws either the normal action row or the item row.
- `get_regular_enemy_reward(enemy)` uses enemy health, strength, and speed so
  stronger random fights pay more than weak random fights.

## 46db75a - Improve Town Services And Android Update Link

Purpose:

- Adds richer Inn and Blacksmith service behavior.
- Wires imported Innkeeper and Blacksmith PNGs into their interiors.
- Adds future asset folders for unused imported concepts.
- Makes the in-game Android update link use a stable GitHub release asset URL.

Files to read first:

- `systems/town_services.py`: Inn rest bonus and Blacksmith forge rewards.
- `systems/interior_ui.py`: interior service NPC sprites, service note cards,
  and bottom room message panel.
- `systems/android_update.py`: APK URL constants, remote version check, and URL
  opening helpers.
- `systems/assets.py`: active sprite path labels and future asset path helpers.
- `assets/processed/future_assets/`: inactive PNG concepts not used by gameplay
  yet.

Important idea: the Blacksmith adds gear to Inventory, but does not auto-equip.

That behavior is intentional. The game gives the player new gear, then the
Inventory screen lets the player choose whether to equip it, compare it, or keep
their current item.

Beginner section breakdown:

- `apply_inn_rest_service(player, npc_name)`: fully restores HP/MP every time.
  It also grants a small EXP/supply bonus once per player level.
- `player.town_service_claims`: remembers which once-per-level Inn bonuses were
  already claimed.
- `apply_blacksmith_forge_service(player, npc_name)`: asks equipment data which
  gear is unlocked for the player's class and level, then adds it to Inventory.
- `get_service_hint_lines(...)`: produces the short wall-card text in service
  rooms.
- `open_android_update_download()`: tries the direct APK URL first, then a
  compatibility APK URL, then the GitHub release page.

## Practical Editing Rules From These Commits

- To resize imported outdoor building art, edit `sprite_rect` in
  `game_data/town.py`; do not resize the source PNG first unless the file is
  truly too large.
- To change where a building can be entered, edit `door_width` or
  `interaction_depth` in `game_data/town.py`.
- To change Android overworld buttons, edit `systems/android_controls.py`.
- To change battle button behavior, edit `systems/battle_input.py`.
- To change battle button drawing, edit `systems/battle_ui.py`.
- To change normal monster rewards, edit `systems/battle_rewards.py`.
- To change Inn or Blacksmith rewards, edit `systems/town_services.py` and the
  related data in `game_data/equipment.py`.
- To change the APK update destination, edit `systems/android_update.py`.
- To add new future art without using it yet, place it under
  `assets/processed/future_assets/` and document it in that folder's README.
