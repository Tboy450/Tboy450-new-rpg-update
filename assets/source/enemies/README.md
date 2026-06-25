# Source Enemy Assets

Raw enemy images belong here before they are converted into transparent
game-ready sprites.

## Files

- `plague_bat_drake_sheet.png`: user-supplied green-screen sheet with the plague
  knight on the left, crystal bat in the center, and ember drake hatchling on
  the right.

## Current Status

The processed Ghost Face sprite exists in `assets/processed/enemies/`.
Future inactive enemy cutouts from `plague_bat_drake_sheet.png` live in
`assets/processed/future_assets/enemies/`.

## Beginner Rule

Put future enemy source art here first. After cleanup or resizing, save the
finished PNG in `assets/processed/enemies/` and add its path to the code that
loads that enemy.
