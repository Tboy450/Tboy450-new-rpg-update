# Archive Folder

`archive/` stores old experiments, single-file snapshots, and historical
versions that are not part of the active game anymore.

## Beginner Rule

Do not add new gameplay here and do not wire files from this folder back into
the live game unless you intentionally want to recover an old experiment.

The active project lives in:

- `main.py`
- `game_data/`
- `systems/`
- `assets/`

## Why This Folder Exists

Before the project was split into modular folders, several versions of the game
were saved as standalone Python files. This folder keeps those old checkpoints
for reference so ideas can be copied forward without mixing old code into the
current runtime.

## Files

- `cursor game final edit befor shut down for supicious b.s`
  Older full-game single-file RPG snapshot. It uses Windows audio environment
  settings and `numpy`, which suggests it was one of the later pre-modular
  drafts before the current cleaned structure.

- `deepseek_python 3.py`
  Older single-file RPG version with the same general 1000x700 game layout.
  Useful only as a historical checkpoint for how the game looked before the
  active modular split.

- `latest version 1.1`
  Archived RPG snapshot saved without a `.py` file extension. It is still a
  Python script, but the filename is an old manual save name rather than a
  structured source file name.

- `pgu music update 1.1.py`
  Archived single-file RPG version focused on music/audio work. It imports
  `numpy`, `tempfile`, `wave`, and `io`, which indicates it was used during a
  procedural music update pass.

- `progressive boss update 1.0.py`
  Archived RPG snapshot from an earlier boss-progression pass. Keep it only as
  reference for older boss ideas or balancing experiments.

- `progressive boss update 1.1 (and somewhat fixed if you run from all of them).py`
  Follow-up archived boss-progression snapshot. The long filename suggests it
  was a manual "fixed" save after the `1.0` version above.

- `rubks 2.py`
  Separate Pygame Rubik's cube experiment. This is not part of the RPG code
  path and should be treated as an unrelated side project kept for reference.

- `updates latest code version 1.0`
  Older RPG checkpoint saved without a `.py` extension. Like `latest version
  1.1`, this is still Python code but preserved under an old manual filename.

## Filename Notes

- Two files have no `.py` extension: `latest version 1.1` and
  `updates latest code version 1.0`.
- Those files are still Python scripts according to the file type check.
- The unusual names are preserved because this folder is a historical archive,
  not a cleaned active source tree.
