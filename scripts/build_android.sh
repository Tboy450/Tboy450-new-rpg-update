#!/usr/bin/env bash
set -euo pipefail

# Build the Android debug APK for Dragon's Lair RPG.
#
# Beginner note:
# - Run this from the repository root with: bash scripts/build_android.sh
# - The APK appears in the `bin/` folder if the build succeeds.
# - Buildozer works best on Linux or WSL2. It downloads Android SDK/NDK tools.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

if [[ ! -f "main.py" || ! -f "buildozer.spec" ]]; then
    echo "Run this script from the game repository root."
    exit 1
fi

if ! command -v buildozer >/dev/null 2>&1; then
    cat <<'EOF'
Buildozer is not installed.

On Ubuntu, Debian, or WSL2, install the system packages first:

  sudo apt update
  sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

Then install Buildozer:

  python3 -m pip install --user --upgrade buildozer cython

After that, run:

  bash scripts/build_android.sh
EOF
    exit 1
fi

echo "Building Android debug APK..."
if [[ "${ANDROID_ACCEPT_SDK_LICENSES:-0}" == "1" ]]; then
    # CI cannot answer Android SDK license prompts, so feed Buildozer a stream of
    # "yes" responses while it installs Android build tools.
    yes | buildozer android debug
else
    buildozer android debug
fi

ANDROID_APK="bin/dragons-lair-rpg-android-debug.apk"
FOUND_APK="$(find bin -maxdepth 1 -type f -name '*debug*.apk' ! -name "$(basename "$ANDROID_APK")" | sort | tail -n 1)"

if [[ -z "$FOUND_APK" ]]; then
    echo "Build finished, but no debug APK was found in bin/."
    exit 1
fi

cp "$FOUND_APK" "$ANDROID_APK"

echo
echo "Build complete: $ANDROID_APK"
echo "Upload that file to a GitHub Release with the same filename for the README direct download link."
