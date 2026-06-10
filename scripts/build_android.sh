#!/usr/bin/env bash
set -euo pipefail

# Build the Android APK for Dragon's Lair RPG.
#
# Beginner note:
# - Run this from the repository root with: bash scripts/build_android.sh
# - The APK appears in the `bin/` folder if the build succeeds.
# - Buildozer works best on Linux or WSL2. It downloads Android SDK/NDK tools.

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

# User-level Python tools such as Cython are often installed here by pip.
export PATH="$HOME/.local/bin:$PATH"

if [[ ! -f "main.py" || ! -f "buildozer.spec" ]]; then
    echo "Run this script from the game repository root."
    exit 1
fi

if command -v buildozer >/dev/null 2>&1; then
    BUILDOZER_CMD=(buildozer)
elif python3 -m buildozer --version >/dev/null 2>&1; then
    BUILDOZER_CMD=(python3 -m buildozer)
elif python -m buildozer --version >/dev/null 2>&1; then
    BUILDOZER_CMD=(python -m buildozer)
else
    cat <<'EOF'
Buildozer is not installed.

On Ubuntu, Debian, or WSL2, install the system packages first:

  sudo apt update
  sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv autoconf automake libtool libltdl-dev pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

Then install Buildozer:

  python3 -m pip install --user --upgrade buildozer cython

After that, run:

  bash scripts/build_android.sh
EOF
    exit 1
fi

BUILD_MODE="${ANDROID_BUILD_MODE:-release}"
if [[ "$BUILD_MODE" == "release" ]]; then
    export P4A_RELEASE_KEYSTORE="${P4A_RELEASE_KEYSTORE:-$REPO_DIR/android-signing/dragons-lair-rpg-dev.keystore}"
    export P4A_RELEASE_KEYSTORE_PASSWD="${P4A_RELEASE_KEYSTORE_PASSWD:-dragonslair}"
    export P4A_RELEASE_KEYALIAS="${P4A_RELEASE_KEYALIAS:-dragonslairrpg}"
    export P4A_RELEASE_KEYALIAS_PASSWD="${P4A_RELEASE_KEYALIAS_PASSWD:-dragonslair}"
    if [[ ! -f "$P4A_RELEASE_KEYSTORE" ]]; then
        echo "Release keystore was not found: $P4A_RELEASE_KEYSTORE"
        exit 1
    fi
    BUILDOZER_ARGS=(android release)
else
    BUILDOZER_ARGS=(android debug)
fi

echo "Building Android $BUILD_MODE APK..."
if [[ "${ANDROID_ACCEPT_SDK_LICENSES:-0}" == "1" ]]; then
    # CI cannot answer Android SDK license prompts, so feed Buildozer a stream of
    # "yes" responses while it installs Android build tools. Disable pipefail so
    # a normal SIGPIPE from `yes` does not override Buildozer's exit code.
    set +o pipefail
    yes | "${BUILDOZER_CMD[@]}" "${BUILDOZER_ARGS[@]}"
    set -o pipefail
else
    "${BUILDOZER_CMD[@]}" "${BUILDOZER_ARGS[@]}"
fi

ANDROID_APK="bin/dragons-lair-rpg-android.apk"
ANDROID_COMPAT_APK="bin/dragons-lair-rpg-android-debug.apk"
if [[ "$BUILD_MODE" == "release" ]]; then
    FOUND_APK="$(find bin -maxdepth 1 -type f -name '*release*.apk' ! -name "$(basename "$ANDROID_APK")" | sort | tail -n 1)"
    if [[ "$FOUND_APK" == *"unsigned"* ]]; then
        echo "Build produced an unsigned release APK. Check release signing env vars."
        exit 1
    fi
else
    FOUND_APK="$(find bin -maxdepth 1 -type f -name '*debug*.apk' ! -name "$(basename "$ANDROID_COMPAT_APK")" | sort | tail -n 1)"
fi

if [[ -z "$FOUND_APK" ]]; then
    echo "Build finished, but no $BUILD_MODE APK was found in bin/."
    exit 1
fi

cp "$FOUND_APK" "$ANDROID_APK"
cp "$FOUND_APK" "$ANDROID_COMPAT_APK"

echo
echo "Build complete: $ANDROID_APK"
echo "Compatibility copy: $ANDROID_COMPAT_APK"
echo "Upload those files to a GitHub Release for the README direct download link."
