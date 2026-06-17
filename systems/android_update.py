"""Android update-link helpers and GitHub version-check logic.

Beginner note:
    This module owns the "update app" plumbing, not the game rules.
    It answers three narrow questions:

    1. Where is the latest APK published?
    2. What Android version code is currently on GitHub?
    3. How should the game ask Android or desktop Python to open that link?

Why this helps:
    The update system is a self-contained runtime feature. Keeping it in its
    own module makes `main.py` smaller and gives future Android packaging work
    one clear place to edit.
"""

import os
import subprocess
import sys
import urllib.request
import webbrowser


# BEGINNER NOTE:
# These URLs are stable app-release endpoints. The APK asset can be replaced on
# GitHub without changing the URL used by the README or by the in-game button.
APP_UPDATE_APK_URL = (
    "https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/"
    "android-latest/dragons-lair-rpg-android.apk"
)
APP_VERSION_SPEC_URL = (
    "https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/"
    "buildozer.spec"
)


def is_android_runtime():
    """Detect Android without importing `main.py`.

    This duplicates the tiny platform check used by the main display setup.
    The duplication is intentional: importing `main.py` from here would create
    a circular dependency.
    """
    return sys.platform.startswith("android") or "ANDROID_ARGUMENT" in os.environ


def fetch_latest_android_numeric_version(timeout=4):
    """Read the newest Android version code from GitHub.

    Beginner note:
        This does not download the APK. It only opens the text version of
        `buildozer.spec` on GitHub and finds the `android.numeric_version`
        line. The start menu uses this to decide whether the app is current.
    """
    request = urllib.request.Request(
        APP_VERSION_SPEC_URL,
        headers={"User-Agent": "DragonsLairRPGUpdateCheck"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        spec_text = response.read(20000).decode("utf-8", errors="replace")

    for line in spec_text.splitlines():
        if line.strip().startswith("android.numeric_version"):
            _, value = line.split("=", 1)
            return int(value.strip())
    raise ValueError("android.numeric_version not found")


def open_external_url(url, mime_type=None):
    """Open a URL from desktop Python or from the Android APK.

    Beginner note:
        Desktop Python can usually rely on `webbrowser.open`.
        Android APK builds are less consistent, so this first tries Android's
        Activity Manager (`am start`) before falling back to the desktop route.
    """
    if is_android_runtime():
        intent_command = [
            "start",
            "-a", "android.intent.action.VIEW",
            "-d", url,
        ]
        if mime_type:
            intent_command.extend(["-t", mime_type])
        for am_path in ("/system/bin/am", "am"):
            try:
                result = subprocess.run(
                    [am_path, *intent_command],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=4,
                    check=False,
                )
            except Exception:
                continue
            if result.returncode == 0:
                return True

    try:
        return bool(webbrowser.open(url))
    except Exception:
        return False
