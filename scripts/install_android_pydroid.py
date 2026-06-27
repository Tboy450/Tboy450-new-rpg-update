#!/usr/bin/env python3
"""Install or update Dragon's Lair RPG from inside Pydroid 3.

Open this file in Pydroid 3 and press Run, or paste the one-line command from
README.md into Pydroid. It downloads the current GitHub `main` branch into
shared storage so `play_android.py` and the launcher icon stay in one known
folder:

    /sdcard/Download/DragonLairRPG

If Pydroid has not been granted shared-storage access, the shared folder may be
blocked. In that case the installer falls back to Pydroid's private home folder
and prints the exact path it used.

Beginner note:
    This is a tiny bootstrapper. It downloads the current installer script from
    GitHub, then executes that installer. The larger install/update logic lives
    in `scripts/install_python_app.py`.
"""

from __future__ import annotations

import sys
import urllib.request


INSTALLER_URL = (
    "https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/"
    "main/scripts/install_python_app.py"
)


def main() -> None:
    print("Installing/updating Dragon's Lair RPG for Pydroid 3...")
    code = urllib.request.urlopen(INSTALLER_URL).read().decode("utf-8")
    sys.argv = ["install_python_app.py"]
    exec(compile(code, INSTALLER_URL, "exec"), {"__name__": "__main__"})


if __name__ == "__main__":
    main()
