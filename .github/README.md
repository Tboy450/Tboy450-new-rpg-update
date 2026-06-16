# GitHub Automation Section

`.github/` stores repository automation. These files affect GitHub behavior, not
the local game loop.

## Folders

- `workflows/`: GitHub Actions workflow files that run in GitHub's hosted build environment.

## Beginner Rule

Only edit this folder when changing automation such as APK builds, release
publishing, tests, or CI checks. Gameplay changes belong in `main.py`,
`game_data/`, `systems/`, and `assets/`.
