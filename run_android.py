#!/usr/bin/env python3
"""Pydroid-friendly launcher for Dragon's Lair RPG.

Open this file in Pydroid 3 and press Run. Do not type the filename into the
Python editor; Python treats text like `scripts/run_local_android.py` as code.
"""

from __future__ import annotations

import sys
from pathlib import Path


def find_repo_root() -> Path:
    """Find the local game folder that contains main.py and scripts/."""
    starts = []
    if "__file__" in globals():
        starts.append(Path(__file__).resolve().parent)
    if sys.argv and sys.argv[0]:
        starts.append(Path(sys.argv[0]).resolve().parent)
    starts.append(Path.cwd().resolve())

    for start in starts:
        for folder in (start, *start.parents):
            if (folder / "main.py").exists() and (folder / "scripts" / "install_python_app.py").exists():
                return folder

    raise RuntimeError(
        "Could not find the Dragon's Lair RPG folder. Open run_android.py from "
        "inside the repo folder, or run this from the folder that contains main.py."
    )


repo_root = find_repo_root()
scripts_dir = repo_root / "scripts"
sys.path.insert(0, str(scripts_dir))

from install_python_app import main  # noqa: E402


sys.argv = [
    "install_python_app.py",
    "--local",
    "--source-dir",
    str(repo_root),
    "--install-dir",
    str(repo_root),
]
raise SystemExit(main())
