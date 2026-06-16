# Python-For-Android Recipes

`p4a-recipes/` contains custom recipes used by python-for-android while building
the APK. These recipes are build-system code, not gameplay code.

## Folders

- `pygame-ce/`: custom recipe that builds `pygame-ce` for Android while still installing it as the importable `pygame` package.

## Beginner Rule

Do not change recipes while tuning gameplay, dialogue, art placement, or battle
balance. Touch this folder only when the Android APK build fails inside a native
Python package compile step.
