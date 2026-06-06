# Runtime Systems

`systems/` contains active helper modules that are small enough to split out of `main.py` without moving core gameplay classes yet.

- `input_actions.py`: maps keyboard and Android virtual button inputs to gameplay actions.
- `save_load.py`: serializes and loads JSON save data for the player, score, boss progress, visited areas, and town interaction progress.

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
