# Processed Character Assets

Game-ready transparent hero sprites.

## Files

- `warrior.png`: active Warrior sprite used in character select, overworld, and battle.
- `mage.png`: active Mage sprite used in character select, overworld, and battle.
- `rogue.png`: active Rogue sprite used in character select, overworld, and battle.
- `character_contact_sheet.jpg`: preview image for comparing the three hero sprites together.

## Code Path

`systems/assets.py` stores these paths in `CHARACTER_SPRITE_PATHS`.
`Character.draw` in `main.py` calls `draw_character_sprite` first, then falls
back to older Python-drawn characters if a PNG cannot load.
