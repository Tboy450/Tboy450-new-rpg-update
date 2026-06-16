# Source Character Assets

Raw or generated source images for playable heroes.

## Files

- `warrior_user_supplied.png`: original Warrior image supplied by the user. This is the source for the active Warrior style.
- `mage_generated_chroma.png`: generated Mage source image on a removable chroma-key background.
- `rogue_generated_chroma.png`: generated Rogue source image on a removable chroma-key background.

## Game-Ready Output

Processed transparent PNGs live in `assets/processed/characters/`.
`systems/assets.py` points the game at those processed files.
