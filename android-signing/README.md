This folder contains the public development signing key for sideload APKs.

It is intentionally committed so GitHub Actions can sign every Android build
with the same key. That makes APK updates install over previous APK updates.
Do not use this key for Play Store distribution.

## Files

- `dragons-lair-rpg-dev.keystore`: public development keystore used by `scripts/build_android.sh` and the GitHub APK workflow.

## Beginner Rule

Do not replace this file unless you are intentionally starting a new Android
signing identity. Changing the key means Android will no longer update over APKs
signed with the old key; users would have to uninstall first.
