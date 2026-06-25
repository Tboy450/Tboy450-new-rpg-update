# Documentation Section

`docs/` holds human-facing notes for editing, building, and understanding the
project. These files are not loaded by the game at runtime.

## Files

- `beginner_code_map.md`: the main beginner guide. Start here to learn what each active module owns and where to edit common features.
- `android_app.md`: Android install, APK update, Pydroid status, and build notes for normal users/editors.
- `android_apk_agent_notes.md`: detailed packaging history and guardrails for Codex or other AI agents working on Android builds.
- `ios_app.md`: current iPhone/iPad packaging status and what would be needed for a real iOS install.
- `future_design_notes.md`: parked ideas that should not be implemented yet, including the future Warm Hearth Inn mini-game.

## Beginner Rule

Use this folder for explanations, build notes, and project maps. Do not put
gameplay data here. Gameplay data belongs in `game_data/`, reusable code belongs
in `systems/`, and imported files belong in `assets/`.
