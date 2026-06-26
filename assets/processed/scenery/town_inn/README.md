# Active Inn Scenery

These transparent PNGs are active Warm Hearth Inn assets.

Beginner note:

- `tavern_front.png` is the outside building sprite.
- The other files are interior props used inside the inn room.
- The older Python-drawn inn and props still exist as fallbacks.

## Files

- `tavern_front.png`: outdoor Warm Hearth Inn facade used on the town map.
- `tavern_bar_counter.png`: interior service counter where the Innkeeper stands.
- `inn_bed.png`: interior bed prop used for both beds.
- `hearth_fireplace.png`: interior hearth/fireplace prop.
- `round_tavern_table.png`: interior round table prop.

## Active Data References

- Outdoor reference: `TOWN_BUILDINGS` inn record in `game_data/town.py`.
- Indoor references: `TOWN_INTERIORS["inn"]["props"]` in `game_data/interiors.py`.
