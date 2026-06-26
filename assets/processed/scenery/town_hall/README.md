# Active Town Hall Scenery

These transparent PNGs are active Dragonwatch Hall assets.

Beginner note:

- Outdoor town data points at `town_hall_front.png`.
- Interior room data points at `town_hall_dais.png` and `notice_board.png`.
- The older Python-drawn town hall still exists in `main.py` as a fallback.

## Files

- `town_hall_front.png`: outdoor Dragonwatch Hall facade used on the town map.
- `town_hall_dais.png`: interior meeting platform / command desk prop.
- `notice_board.png`: interior notice board prop for quest and warning notes.

## Active Data References

- Outdoor reference: `TOWN_BUILDINGS` town hall record in `game_data/town.py`.
- Indoor references: `TOWN_INTERIORS["town_hall"]["props"]` in `game_data/interiors.py`.
