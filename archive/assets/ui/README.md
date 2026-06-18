# Archived UI Assets

`archive/assets/ui/` stores UI and title-screen art that was removed from the
active game path.

## Files

- `title_dragon.png`: processed generated title dragon that used to be loaded by `Dragon.draw`.
- `title_dragon_generated_chroma.png`: original generated chroma-background source for `title_dragon.png`.

## Why These Are Archived

The generated dragon did not line up with the active title-screen fire-breath
animation. The start menu now uses the procedural dragon and extended fire in
`Dragon.draw` inside `main.py`.
