# Active Scenery Assets

This folder contains processed scenery PNGs that the game can load directly.

Beginner note:

- These are active gameplay-ready sprites, not Python drawings.
- Most older town scenery is still drawn with Python in `main.py`.
- New scenery sprites should be grouped by where they are used, so a beginner
  can find the art without searching every file.

## Folders

- `town_shop/`: first active test set for replacing one Python-drawn town
  building with imported sprite assets.
- `town_hall/`: active Dragonwatch Hall exterior and interior command-room props.
- `town_stall/`: active Food Stall exterior canopy.
- `town_inn/`: active Warm Hearth Inn exterior and interior props.
- `town_blacksmith/`: active Ironroot Forge exterior and interior gear props.

## Code Path

- `game_data/town.py` chooses the outdoor building sprites.
- `game_data/interiors.py` chooses the indoor prop sprites.
- `systems/assets.py` loads and scales the PNGs.
- `main.py` decides when to draw outdoor buildings and indoor props.
