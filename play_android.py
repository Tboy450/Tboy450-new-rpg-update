#!/usr/bin/env python3
"""Direct Pydroid launcher for Dragon's Lair RPG.

Use this after `run_android.py` has installed the packages once. This file is
meant to be opened directly by Pydroid or by the Android home-screen shortcut.
It avoids re-running pip each time you want to play.

Beginner note:
    This file launches `main.py` in the same Python process Pydroid opened.
    That matters because Android/Pydroid gives pygame its display access through
    the original process.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


KNOWN_ANDROID_FOLDERS = (
    Path("/sdcard/Download/DragonLairRPG"),
    Path("/storage/emulated/0/Download/DragonLairRPG"),
)


def find_repo_root() -> Path:
    """Find the folder that contains the active game files."""
    starts = []
    if "__file__" in globals():
        starts.append(Path(__file__).resolve().parent)
    if sys.argv and sys.argv[0]:
        starts.append(Path(sys.argv[0]).resolve().parent)
    starts.append(Path.cwd().resolve())
    starts.extend(KNOWN_ANDROID_FOLDERS)

    for start in starts:
        if not start.exists():
            continue
        for folder in (start, *start.parents):
            if (folder / "main.py").exists() and (folder / "game_data" / "__init__.py").exists():
                return folder

    raise RuntimeError(
        "Could not find Dragon's Lair RPG. Keep play_android.py inside the "
        "folder that contains main.py."
    )


repo_root = find_repo_root()
game_file = repo_root / "main.py"

os.chdir(repo_root)
repo_path = str(repo_root)
if repo_path not in sys.path:
    sys.path.insert(0, repo_path)

sys.argv = [str(game_file)]
globals()["__file__"] = str(game_file)
globals()["__package__"] = None
globals()["__cached__"] = None

exec(compile(game_file.read_text(encoding="utf-8"), str(game_file), "exec"), globals())
