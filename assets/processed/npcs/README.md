# Processed NPC Assets

Game-ready friendly/story NPC sprites.

## Files

- `lion_sage.png`: active Lion Sage sprite and portrait. Used in the west swamp story area and Lion Sage dialogue box.
- `town_guard.png`: imported town guard overlay. Used during the town entrance cutscene while the older Python-drawn guard remains as fallback.

## Code Path

`systems/assets.py` exposes `LION_SAGE_SPRITE_PATH`, `TOWN_GUARD_SPRITE_PATH`,
and `get_story_sprite_path`. `game_data/story.py` decides where the Lion Sage
appears and which dialogue/reward he gives.
