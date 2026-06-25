# Processed Game Assets

`assets/processed/` contains files that the game can load directly.

## Folders

- `characters/`: transparent hero PNGs for Warrior, Mage, and Rogue.
- `equipment/`: game-ready weapon, armor, and charm icons used by the Inventory equipment menu.
- `effects/`: PNG animation frame folders for attacks and magic.
- `enemies/`: transparent enemy sprites.
- `npcs/`: transparent friendly/story NPC sprites.
- `scenery/`: active scenery sprites for town buildings and room props.
- `ui/`: launcher icon and title-screen art.
- `music/`: future finished loopable music files.
- `sounds/`: future finished WAV/OGG sound effects.
- `future_assets/`: transparent PNG concepts, including attacks and class gear, that are not loaded by the game yet.

## Beginner Rule

Files in this folder should already be resized, converted, cut out, or extracted
into the format the game expects. `systems/assets.py` is the central place that
points code at these processed files.

`future_assets/` is the exception: those PNGs are intentionally game-ready but
inactive. Move or copy a future asset into an active folder before wiring it
into code or data. The first examples are `scenery/town_shop/`, which contains
active copies used by the shop exterior and shop interior, and
`npcs/blacksmith.png` / `npcs/innkeeper.png`, which are active copies of future
NPC cutouts now used in town interiors.
