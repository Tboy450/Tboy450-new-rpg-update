# Processed NPC Assets

Game-ready friendly/story NPC sprites.

## Files

- `lion_sage.png`: active Lion Sage sprite and portrait. Used in the west swamp story area and Lion Sage dialogue box.
- `town_guard.png`: imported town guard overlay. Used during the town entrance cutscene while the older Python-drawn guard remains as fallback.
- `blacksmith.png`: active imported Blacksmith interior sprite. Used in Ironroot Forge instead of the older generic Python-drawn service NPC.
- `innkeeper.png`: active imported Innkeeper interior sprite. Used in Warm Hearth Inn instead of the older generic Python-drawn service NPC.
- `forest_apothecary.png`: active Wren sprite and portrait. Used for the northern forest Mooncap Antidote side-story conversation.
- `plains_ranger.png`: active Elian sprite and portrait. Used for the center plains Waymarks side-story conversation.
- `star_cartographer.png`: active Ivo sprite and portrait. Used for the north-west mountain Star Chart side-story conversation.
- `lantern_guard.png`: active Kael sprite and portrait. Used for the south-east cave Echo Lantern side-story conversation.

## Code Path

`systems/assets.py` exposes the story/town NPC sprite paths,
`get_story_sprite_path`, and `get_town_service_npc_sprite_path`.

`game_data/story.py` decides where the Lion Sage and side-story NPCs appear and
which dialogue/rewards they give. `game_data/interiors.py` decides which town
rooms use the Blacksmith and Innkeeper sprites and where those sprites fit
on-screen.
