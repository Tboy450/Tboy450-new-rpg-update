# Runtime Systems

`systems/` contains active helper modules that are small enough to split out of `main.py` without moving core gameplay classes yet.

- `input_actions.py`: maps keyboard and Android virtual button inputs to gameplay actions.
- `save_load.py`: serializes and loads JSON save data for the player, score, boss progress, and visited areas.

Keep this folder for reusable runtime systems. Pure tuning data still belongs in `game_data/`.
