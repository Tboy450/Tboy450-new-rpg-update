# Processed Enemy Assets

Game-ready enemy sprites.

## Files

- `ghost_face.png`: active Ghost Face enemy sprite. It is used for the top-center forest story enemy and its battle portrait/effects.

## Code Path

`systems/assets.py` exposes `GHOST_FACE_SPRITE_PATH`. Enemy drawing in
`main.py` uses `draw_enemy_sprite` when an enemy has a sprite path.
