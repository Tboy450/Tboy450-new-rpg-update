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

## Current Status (Read This Before Changing Anything)

As of run **#11**, the APK is **still not green**.

| Run | Change | Failed at | Time | Meaning |
|-----|--------|-----------|------|---------|
| #1-#9 | pygame 2.1.0 / 2.6.1 recipe tweaks | Build APK | ~8-9 min | Native pygame compile still broken |
| #10 | Added `libtinfo5` to apt | Install deps | ~20 sec | Bad CI package on `ubuntu-latest` |
| #11 | pygame-ce 2.5.2 recipe | Build APK | ~8.7 min | **pygame-ce swap did not fix the core failure** |

**Important:** swapping pygame -> pygame-ce with the same p4a recipe shape is not proven to
work for this repo yet. Do not treat that change as "the fix" just because it sounds newer.

## Stop The Debug Loop

Do **not** keep doing this:

1. Guess a new pygame/pygame-ce version
2. Push
3. Wait 9 minutes
4. Fail
5. Repeat

That is exactly what Codex already did for 11 runs.

Before the next packaging commit, someone with repo access must copy the **last 50-100
lines** of the failed **Build Android debug APK** step from GitHub Actions. Without that
exact error text, another recipe tweak is just guessing.

## Working Configuration (Current Best Attempt, Not Proven Green)

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
3. Classify the failure from the **exact last error line**:
   - `longintrepr.h` / Python header errors -> old pygame recipe problem
   - `clang failed with exit code 1` during `pygame` / `pygame-ce` build -> recipe/version/NDK mismatch
   - `aapt` / `icon` / `drawable` / gradle resource errors -> fix `assets/processed/ui/dragon_app_icon.png` (currently 1254x1254, ~2.6 MB)
   - SDK/NDK/license errors -> retry workflow or fix apt/SDK config only
4. Apply **one** targeted fix for that class of error. Do not also change pygame version in the same commit.

## Evidence-Based Next Steps (In Order)

Only do these after reading the log tail:

1. **If compile fails in pygame-ce build:** try the known-working reference setup from
   [Potato-Bird](https://github.com/cbdj/Potato-Bird):
   - `pygame-ce` version **2.4.1**
   - URL format `https://github.com/pygame-community/pygame-ce/archive/{version}.tar.gz`
   - `p4a.branch = master` (not `develop`)
   - Match their `p4a-recipes/pygame-ce/__init__.py` closely
2. **If packaging fails after compile:** resize/compress `dragon_app_icon.png` to a normal
   launcher size (for example 512x512, under ~500 KB) before touching pygame again.
3. **If the project only needs playability today:** use Pydroid (`run_android.py` once,
   then `play_android.py`). That path is already working on desktop with `pygame-ce`.
4. **If repeated native compile failures continue:** consider Docker/WSL build using the
   Emerson MX gist workflow instead of more GitHub recipe roulette.

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
