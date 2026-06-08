# Android APK Notes For Codex / AI Agents

Read this before changing Android packaging. It documents the failure loop this
repo was stuck in and the fix that actually works.

## Primary Android Install Path (Option B)

The supported phone install path is the **GitHub-built APK**, not Pydroid.

1. Push changes to `main` that touch Android build files.
2. Wait for the `Build Android APK` GitHub Action to finish.
3. Install from the `android-latest` release asset:
   `dragons-lair-rpg-android-debug.apk`

Release URL:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

Pydroid (`run_android.py` / `play_android.py`) is only a fallback note. Do not
treat it as the main Android deliverable.

Human editors should read the **How To Build The APK (For Editors)** section in
`README.md`. Do not paste generic instructions that say
`requirements = python3,pygame` or tell people to create a new
`.github/workflows/build.yml` file. This repo already uses
`.github/workflows/android-apk.yml` named **Build Android APK**.

## What Was Breaking CI (Do Not Reintroduce)

The repo failed **9 consecutive** `Build Android APK` runs with variations of
the same mistake:

| Bad change | Why it fails |
|------------|--------------|
| Use upstream p4a `pygame` recipe (pygame 2.1.0) | Breaks against modern Python headers in CI |
| Local `p4a-recipes/pygame` with pygame **2.6.x** + `Cython>=3.2` | CI installs `Cython<0.30`; python-for-android is not Cython 3 ready |
| Bump `android.api` to 35 without testing | Adds SDK friction; **34** is the current stable target |
| Add `libtinfo5` to CI apt packages | Package is unavailable on current `ubuntu-latest`; apt step fails immediately |
| Change `requirements` back to `python3,pygame` | Drops the working local recipe mapping |

**Loop pattern to avoid:** tweak pygame version -> CI fails -> try another pygame
version -> CI fails again -> repeat. Stop changing pygame versions randomly.

## Working Configuration (Keep These)

These files must stay aligned:

### `buildozer.spec`

```ini
requirements = python3,pygame-ce
android.api = 34
android.minapi = 24
android.ndk = 25b
android.accept_sdk_license = True
p4a.bootstrap = sdl2
p4a.local_recipes = ./p4a-recipes
p4a.branch = develop
android.archs = arm64-v8a
```

### `p4a-recipes/pygame-ce/__init__.py`

- Recipe name: `pygame-ce`
- Source: pygame-community **2.5.2** tag
- `site_packages_name = "pygame"` so `main.py` keeps `import pygame`
- **No** `hostpython_prerequisites` forcing Cython 3.x

### `.github/workflows/android-apk.yml`

- apt: do **not** add `libtinfo5` on `ubuntu-latest` (package removed); keep `libncurses5-dev` / `libncursesw5-dev`
- pip: `"Cython>=0.29.36,<0.30"` (not `Cython==3.x`)
- env: `ANDROID_ACCEPT_SDK_LICENSES=1`

### `requirements.txt`

- `pygame-ce>=2.5.0` for desktop/Pydroid pip installs (imports as `pygame`)

## If CI Still Fails

1. Open the latest failed run of `Build Android APK` on GitHub Actions.
2. Read only the **Build Android debug APK** step log.
3. If the error is SDK/NDK download or license related: retry the workflow; do
   not rewrite the pygame recipe.
4. If the error mentions Cython or pygame compile headers: verify the three
   config blocks above were not reverted.
5. If the error is unrelated to pygame (Java, gradle, disk space): fix that
   specific error only. Do not change pygame packaging at the same time.

## Safe Change Checklist

Before pushing another Android packaging commit, confirm:

- [ ] `requirements` is still `python3,pygame-ce`
- [ ] `p4a-recipes/pygame-ce/` exists; `p4a-recipes/pygame/` does not
- [ ] No `Cython>=3` pins were added anywhere
- [ ] CI workflow still installs `Cython<0.30`
- [ ] README still lists APK install as the primary Android path

## Success Criteria

The Android packaging task is done when:

1. `Build Android APK` workflow completes with a green check.
2. `android-latest` release contains `dragons-lair-rpg-android-debug.apk`.
3. The release download URL returns the APK (not 404).

Do not declare Android "fixed" based only on local doc edits or Pydroid scripts.
