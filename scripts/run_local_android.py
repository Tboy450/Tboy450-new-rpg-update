#!/usr/bin/env python3
"""Run the locally copied Android/Pydroid version of Dragon's Lair RPG.

Open this file from a Python app such as Pydroid 3, or run it from a terminal:

    python scripts/run_local_android.py

It uses the game files already on the phone instead of downloading from GitHub.
"""

from __future__ import annotations

import sys

from install_python_app import main


sys.argv = ["install_python_app.py", "--local"]
raise SystemExit(main())
