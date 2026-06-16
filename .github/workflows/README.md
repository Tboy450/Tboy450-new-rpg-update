# GitHub Workflows

This folder contains GitHub Actions workflow definitions.

## Files

- `android-apk.yml`: builds the Android APK whenever relevant files are pushed to `main` or when the workflow is manually started. It installs Android/Buildozer dependencies, runs `scripts/build_android.sh`, and publishes the APK files to the `android-latest` GitHub Release.

## Beginner Rule

If the APK update link 404s, check this workflow first. The link only works
after this workflow finishes successfully and publishes the release asset.
