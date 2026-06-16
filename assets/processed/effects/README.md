# Processed Effect Assets

Game-ready PNG animation frames for combat effects.

## Folders

- `flame_tornado/`: player SPECIAL travel animation used by Warrior/Rogue and as the travel phase for Mage Fire Blast.
- `fire_blast/`: Mage-only SPECIAL impact animation shown when Fire Blast reaches the enemy.
- `mage_magic_fireball/`: Mage normal MAGIC projectile overlay.

## Code Path

`systems/assets.py` exposes one frame-directory constant for each folder.
`BattleScreen` in `main.py` loads these frames with `load_animation_frames`.
