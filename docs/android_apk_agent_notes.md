# Android APK Notes For Codex / AI Agents

Read this before changing Android packaging. It documents the failure loop this
repo was stuck in and the fix that actually works.

## Current Android Debugging Path

The target phone debugging path is the GitHub-built APK. Pydroid 3 is not a
reliable runtime on the user's phone because `pygame` is not available in
Pydroid's **Quick Install** list. The normal **Search libraries** result pulls
PyPI source and fails with missing `sdl2-config`.

Pydroid 3 can still update source files with:

```python
import urllib.request; exec(urllib.request.urlopen("https://raw.githubusercontent.com/Tboy450/Tboy450-new-rpg-update/main/scripts/install_android_pydroid.py").read().decode())
```

That installs/updates the game at `/sdcard/Download/DragonLairRPG` when Pydroid
has shared-storage access. Otherwise it falls back to Pydroid's private home
folder and prints the path it used. The dragon icon is copied with the rest of
`assets/processed/ui/`. It only runs the game if that Pydroid install has a
working prebuilt pygame package.

## Target APK Install Path

1. Push changes to `main` that touch Android build files.
2. Wait for the `Build Android APK` GitHub Action to finish.
3. Install from the `android-latest` release asset:
   `dragons-lair-rpg-android-debug.apk`

Release URL:

```text
https://github.com/Tboy450/Tboy450-new-rpg-update/releases/download/android-latest/dragons-lair-rpg-android-debug.apk
```

If that URL returns 404, the APK workflow is not green yet. Do not tell users it
is a working APK link until the release asset exists.

Human editors should read the **How To Build The APK (For Editors)** section in
`README.md`. Do not paste generic instructions that say
`requirements = python3,pygame` or tell people to create a new
`.github/workflows/build.yml` file. This repo already uses
`.github/workflows/android-apk.yml` named **Build Android APK**.

## What Was Breaking CI (Do Not Reintroduce)

The repo failed **12 consecutive** `Build Android APK` runs with variations of
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

As of run **#12**, the APK is **still not green**.

| Run | Change | Failed at | Time | Meaning |
|-----|--------|-----------|------|---------|
| #1-#9 | pygame 2.1.0 / 2.6.1 recipe tweaks | Build APK | ~8-9 min | Native pygame compile still broken |
| #10 | Added `libtinfo5` to apt | Install deps | ~20 sec | Bad CI package on `ubuntu-latest` |
| #11 | pygame-ce 2.5.2 recipe | Build APK | ~8.7 min | hostpython lacked Cython during `pygame-ce` `setup.py build_ext` |
| #12 | Installed hostpython Cython | Build APK | ~9.7 min | `pygame-ce` calls removed `distutils.ccompiler.spawn` |
| #13 | Patched `distutils.ccompiler.spawn` | Build APK | ~8.3 min | Floating p4a `develop` used Python 3.14; pygame-ce generated C code is not Python 3.14 compatible |

**Important:** swapping pygame -> pygame-ce with the same p4a recipe shape is not enough by
itself. The local recipe must install Cython into p4a's hostpython, pinned below 0.30, and
patch pygame-ce's old `distutils.ccompiler.spawn(...)` call for the current host Python.

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
p4a.branch = v2024.01.21
android.archs = arm64-v8a
```

Do not float `p4a.branch` to `develop` unless the pygame-ce recipe is updated
for Python 3.14. As of run #13, p4a `develop` used Python 3.14.2 and failed in
pygame-ce C compilation at `_PyLong_AsByteArray`.

### `p4a-recipes/pygame-ce/__init__.py`

- Recipe name: `pygame-ce`
- Source: pygame-community **2.5.2** tag
- `site_packages_name = "pygame"` so `main.py` keeps `import pygame`
- `hostpython_prerequisites = ["setuptools", "Cython>=0.29.36,<0.30"]`
- Prebuild patch replaces `distutils.ccompiler.spawn(cmd, dry_run=self.dry_run, **kwargs)`
  with `distutils.ccompiler.CCompiler.__spawn(self, cmd, **kwargs)`

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

1. **If compile still fails in pygame-ce build after hostpython Cython is installed:** keep p4a pinned to
   `v2024.01.21` first. Only then try the known-working reference setup from
   [Potato-Bird](https://github.com/cbdj/Potato-Bird):
   - `pygame-ce` version **2.4.1**
   - URL format `https://github.com/pygame-community/pygame-ce/archive/{version}.tar.gz`
   - `p4a.branch = master` (not `develop`)
   - Match their `p4a-recipes/pygame-ce/__init__.py` closely
2. **If packaging fails after compile:** resize/compress `dragon_app_icon.png` to a normal
   launcher size (for example 512x512, under ~500 KB) before touching pygame again.
3. **If the project only needs playability today:** build/install the APK. Do not rely on
   Pydroid unless `pygame` is present in Pydroid **Quick Install**.
4. **If repeated native compile failures continue:** consider Docker/WSL build using the
   Emerson MX gist workflow instead of more GitHub recipe roulette.

## Safe Change Checklist

Before pushing another Android packaging commit, confirm:

- [ ] `requirements` is still `python3,pygame-ce`
- [ ] `p4a-recipes/pygame-ce/` exists; `p4a-recipes/pygame/` does not
- [ ] No `Cython>=3` pins were added anywhere
- [ ] CI workflow still installs `Cython<0.30`
- [ ] README still lists APK as the target Android path and Pydroid only as a limited source updater

## Success Criteria

The Android packaging task is done when:

1. `Build Android APK` workflow completes with a green check.
2. `android-latest` release contains `dragons-lair-rpg-android-debug.apk`.
3. The release download URL returns the APK (not 404).

Do not declare Android "fixed" based only on local doc edits or Pydroid scripts.
