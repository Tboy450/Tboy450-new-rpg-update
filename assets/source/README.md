# Source Asset Intake

`assets/source/` keeps original uploads, downloaded files, and generated
chroma-key images. These files are preserved so assets can be reprocessed later.

## Folders

- `characters/`: raw or generated hero character sources.
- `effects/`: raw GIF/video effect sources before frame extraction.
- `enemies/`: raw enemy sprite sources.
- `npcs/`: raw friendly/story NPC sources.
- `ui/`: raw launcher, title, and interface sources.
- `music/`: future raw music sources.
- `sounds/`: future raw sound-effect sources.
- Future generated PNG concepts may live directly under
  `assets/processed/future_assets/` when there is no separate raw/source file.

## Beginner Rule

Do not load source files directly in the game unless there is a specific reason.
Convert them into game-ready files under `assets/processed/` first, then point
`systems/assets.py` at the processed version.
