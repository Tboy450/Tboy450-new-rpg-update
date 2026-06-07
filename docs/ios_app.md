# iPhone / iPad Install Status

There is no active public iPhone install link yet.

Placeholder direct IPA URL:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/latest/download/dragons-lair-rpg-ios.ipa
```

That link will only work after a signed IPA is built and uploaded to the latest
GitHub Release with the exact filename `dragons-lair-rpg-ios.ipa`.

## Why

iPhone apps cannot be installed from a normal loose Python file or unsigned APK.
iOS requires one of these signed distribution paths:

- App Store listing
- TestFlight invite link
- Signed `.ipa` installed through Apple developer tooling

This game is currently a Python/Pygame project. The Android path uses Buildozer
and python-for-android, but the repo does not yet contain an iOS packaging setup
or signed iPhone build.

## Future iPhone Install Link Placeholder

When an iPhone build exists, replace this placeholder in `README.md` with one of
these:

```text
Direct signed IPA:
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/latest/download/dragons-lair-rpg-ios.ipa

TestFlight:
https://testflight.apple.com/join/YOUR_INVITE_CODE

App Store:
https://apps.apple.com/app/YOUR_APP_ID
```

## What Has To Be Done First

1. Choose an iOS packaging route for Python/Pygame or port the game to an iOS-friendly engine.
2. Create an Apple Developer account for signing.
3. Build a signed `.ipa`.
4. Test on a real iPhone or iPad.
5. Publish through TestFlight or the App Store.
6. Update the README install link.

## Practical Recommendation

Use the Android APK route first because this repo already has Android packaging
files. Treat iPhone support as a later porting task, not a quick install-link
task.
