# Local Copy Inventory

This note tracks older local Dragon's Lair RPG folders before they are updated,
merged, archived, or deleted. It exists because one older checkout has useful
local-only work that should not be overwritten by a normal pull.

## Current Safe Checkout

- Path: `C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update 2`
- Git state checked on 2026-07-16: clean `main`, matching `origin/main`.
- Latest checked commit: `341fe17 Add Dragon icon Windows shortcut`.
- Use this checkout for new Codex work unless the user asks to migrate a
  specific old copy.

## Older Copies Found

| Folder | Git state | Why it matters | Safe next step |
| --- | --- | --- | --- |
| `C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update` | `main` was ahead 1 and behind 33 in its local tracking view. HEAD was `07d4a22 Add equipment system and visual polish`. | Contains a local-only equipment/visual-polish commit that is not in the current checkout. | Preserve as a Git bundle, then compare/cherry-pick only after reading the diff and running tests. Do not pull over it first. |
| `C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update-windows` | Older `main` checkout at `7661220 Fix Windows updater active paths`; working tree had deleted `archive/` files plus untracked `.venv/` and cache folders. | Dirty folder may contain local environment files or old experiments. | Inventory/back up before cleanup. Do not run mass restore, delete, pull, or reset without a specific decision. |
| `C:\Users\Heemi\Documents\Codex\2026-06-08\tboy450-new-rpg-update\work\Tboy450-new-rpg-update` | Older clean checkout at `6533048 Docs: record APK failure analysis and stop recipe roulette.` | Historical Codex work folder; useful for reference, not current development. | Leave read-only unless a specific commit or file is needed. |
| `C:\Users\Heemi\Documents\Codex\2026-06-08\tboy450-new-rpg-update` | Parent folder, not a Git repo. | Contains old Codex output/work folders. | Leave alone unless the user asks to archive old Codex folders. |
| `C:\Users\Heemi\Documents\Codex\2026-06-08\tboy450-new-rpg-update-fix` | Parent folder, not a Git repo in the first scan. | Old fix workspace shell. | Leave alone unless a later scan finds useful files. |

## Beginner-Safe Migration Rule

Do not "update all local copies" as one big operation. That can erase the clues
that show which folder has unique work.

Use this safer order:

1. Inventory each folder with `scripts/inventory_local_copies.ps1`.
2. Preserve any unique commit or dirty folder before editing it.
3. Read the diff for one old change at a time.
4. Cherry-pick or manually port only the useful pieces into the current clean
   checkout.
5. Run desktop tests and any Android-safe checks before pushing.
6. Archive or delete old folders only after the user confirms they are no
   longer needed.

## Preserving The Equipment Commit

The older OneDrive checkout has the local-only commit
`07d4a2257b26819e8403b553b32ca52feda34b85`. A safe backup command is:

```powershell
git -c safe.directory="C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update" -C "C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update" bundle create "C:\Users\Heemi\OneDrive\Documents\Tboy450-new-rpg-update 2\.local_backups\equipment-07d4a22.bundle" HEAD
```

The bundle belongs in `.local_backups/`, which is ignored by Git. It is a local
safety copy, not a file to commit.

## Codex Top-Bar Run Button Note

Codex desktop supports project-specific local environment actions that appear in
the top bar and can have an icon. The public manual says to create these through
the Codex desktop settings pane, then check in the generated `.codex`
configuration. Do not invent a `.codex` action shape from scratch.

This project now includes `.codex/environments/environment.toml`, using the
verified action shape from bundled Codex run-button references. It adds a
`Run Game` top-bar action that launches `scripts/run_windows.ps1`.

The action uses the verified built-in `run` icon. A custom dragon image for this
top-bar slot was not documented in the local references.
