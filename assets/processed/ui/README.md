# Processed UI Assets

Game-ready UI and Android packaging images.

## Files

- `dragon_app_icon.png`: Android launcher icon referenced by `buildozer.spec`.
- `title_dragon.png`: imported title-screen dragon used by `Dragon.draw` in `main.py`.

## Code Path

`buildozer.spec` uses `dragon_app_icon.png` for the APK icon.
`systems/assets.py` exposes `TITLE_DRAGON_SPRITE_PATH` for the title menu.
