# Processed UI Assets

Game-ready UI and Android packaging images.

## Files

- `dragon_app_icon.png`: Android launcher icon referenced by `buildozer.spec`.

## Code Path

`buildozer.spec` uses `dragon_app_icon.png` for the APK icon.

## Archived Files

The generated title dragon was moved to `archive/assets/ui/` because it did
not line up with the active start-menu fire animation. The start menu now uses
the procedural `Dragon.draw` art in `main.py`.
