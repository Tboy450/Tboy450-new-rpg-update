# Future NPC Assets

These transparent PNGs are unused future NPC concepts.

Beginner note:

- Once an NPC is implemented in the game, remove its duplicate from this folder
  and keep the active gameplay copy under `assets/processed/npcs/`.
- The Blacksmith and Innkeeper were moved into the active NPC folder as
  `assets/processed/npcs/blacksmith.png` and
  `assets/processed/npcs/innkeeper.png`.
- The PNGs still listed below are unused generated placeholder concepts and can
  be replaced later as better imported art arrives.

- `ribbon_sentinel.png`: a town guard / medical-ribbon sentinel concept.
- `forest_apothecary.png`: a forest healer or herbalist concept.
- `star_cartographer.png`: a map keeper or route scholar concept.
- `lantern_guard.png`: a patrol guard NPC concept.
- `plains_ranger.png`: a plains scout NPC concept.

To activate one later, move or copy it into `assets/processed/npcs/`, then add
the NPC data in `game_data/story.py`, `game_data/npcs.py`, or
`game_data/town_population.py`, depending on how that character should behave.
