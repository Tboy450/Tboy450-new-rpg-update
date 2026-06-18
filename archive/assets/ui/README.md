# Archived UI Assets

`archive/assets/ui/` stores UI and title-screen art that was removed from the
active game path.

## Files

- `title_dragon.png`: archived copy of the generated title dragon. The active
  processed copy now lives at `assets/processed/ui/title_dragon.png`.
- `title_dragon_generated_chroma.png`: original generated chroma-background source for `title_dragon.png`.

## Why These Are Archived

The old procedural title dragon and old right-facing fire animation now remain
as fallback/archive code inside `Dragon.draw` in `main.py`. The start menu
loads the imported dragon PNG first and adds a left-facing animated fire
extension from that sprite's mouth.
