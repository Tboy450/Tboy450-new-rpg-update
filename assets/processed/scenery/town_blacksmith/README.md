# Active Blacksmith Scenery

These transparent PNGs are active Ironroot Forge assets.

Beginner note:

- `blacksmith_stall.png` is the outside building sprite.
- `weapon_rack.png` and `armor_stand.png` are interior props.
- The older Python-drawn forge and props still exist as fallbacks.

## Files

- `blacksmith_stall.png`: outdoor Ironroot Forge stall with anvil and fire.
- `weapon_rack.png`: interior weapon rack prop.
- `armor_stand.png`: interior armor display prop.

## Active Data References

- Outdoor reference: `TOWN_BUILDINGS` blacksmith record in `game_data/town.py`.
- Indoor references: `TOWN_INTERIORS["blacksmith"]["props"]` in `game_data/interiors.py`.
