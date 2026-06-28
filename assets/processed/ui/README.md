# Processed UI Assets

Game-ready UI and Android packaging images.

## Files

- `dragon_app_icon.png`: Android launcher icon referenced by `buildozer.spec`.
- `title_dragon.png`: active imported title-screen dragon used by `Dragon.draw`
  in `main.py`. The same PNG is tinted at runtime for boss-progression colors.

## Code Path

`buildozer.spec` uses `dragon_app_icon.png` for the APK icon.

`Dragon.draw` in `main.py` uses `title_dragon.png` first, applies a light
boss-palette tint with `systems/assets.py`, and extends the fire from the
imported dragon's mouth. The older Python-drawn dragon remains in that method
only as fallback code if this PNG cannot load.

## Archived Files

Copies of the generated title dragon source remain in `archive/assets/ui/` for
history. The active game loads the processed copy in this folder.
