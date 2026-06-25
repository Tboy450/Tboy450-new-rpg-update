# Processed NPC Assets

Game-ready friendly/story NPC sprites.

## Files

- `lion_sage.png`: active Lion Sage sprite and portrait. Used in the west swamp story area and Lion Sage dialogue box.
- `town_guard.png`: imported town guard overlay. Used during the town entrance cutscene while the older Python-drawn guard remains as fallback.
- `blacksmith.png`: active imported Blacksmith interior sprite. Used in Ironroot Forge instead of the older generic Python-drawn service NPC.
- `innkeeper.png`: active imported Innkeeper interior sprite. Used in Warm Hearth Inn instead of the older generic Python-drawn service NPC.

## Code Path

`systems/assets.py` exposes `LION_SAGE_SPRITE_PATH`, `TOWN_GUARD_SPRITE_PATH`,
`get_story_sprite_path`, and `get_town_service_npc_sprite_path`.

`game_data/story.py` decides where the Lion Sage appears and which
dialogue/reward he gives. `game_data/interiors.py` decides which town rooms use
the Blacksmith and Innkeeper sprites and where those sprites fit on-screen.
