# Asset Sources

This game is still using procedural shapes and generated audio. When we start replacing that with real assets, use this folder as the intake point:

```text
assets/
  source/       raw downloads kept as-is
  processed/    resized / converted files ready for the game
  manifest.json category plan for future asset ports
  credits.md    attribution notes for any non-CC0 items
```

The current placeholder folders are split into `characters`, `enemies`, `sounds`, `music`, and `ui`. Keep raw packs under `assets/source/<category>/`, then copy converted game-ready files to `assets/processed/<category>/`.

Active UI asset:

- `assets/processed/ui/dragon_app_icon.png`: Android launcher icon used by `buildozer.spec`.

Active character assets:

- `assets/processed/characters/warrior.png`: imported Warrior class sprite used in character select, overworld, and battle.
- `assets/processed/characters/mage.png`: generated Mage class sprite used in character select, overworld, and battle.
- `assets/processed/characters/rogue.png`: generated Rogue class sprite used in character select, overworld, and battle.

Active enemy asset:

- `assets/processed/enemies/ghost_face.png`: Ghost Face enemy sprite used in the top-center forest area.

## Character Animation Sources

Prefer CC0 assets first so we do not have to manage attribution for every import.

| Source | Best for | License / notes |
| --- | --- | --- |
| [Kenney Platformer Characters](https://kenney.nl/assets/platformer-characters) | Simple character sprites, placeholders, NPCs | CC0 |
| [Kenney Animated Characters Retro](https://kenney.nl/assets/animated-characters-retro) | Retro-style animated characters | CC0 |
| [Kenney Animated Characters 1](https://kenney.nl/assets/animated-characters-1) | Extra character variety | CC0 |
| [Kenney Animated Characters Protagonists](https://kenney.nl/assets/animated-characters-protagonists) | Hero variants and class replacements | CC0 |
| [OpenGameArt: The Knight - Free Sprite](https://opengameart.org/content/the-knight-free-sprite) | Warrior/paladin-style animation set | CC0 |
| [OpenGameArt: Puny Characters](https://opengameart.org/content/puny-characters) | Lightweight RPG characters, walk/attack/death cycles | Free asset pack, no credit required |
| [OpenGameArt: OPP2017 - Sprites, characters, objects, effects](https://opengameart.org/content/opp2017-sprites-characters-objects-effects) | NPCs, enemies, effects, props | Public domain |
| [OpenGameArt: Adventurer and Slime game Sprites](https://opengameart.org/content/adventurer-and-slime-game-sprites) | Simple hero and monster animation sets | CC0 |

## Sound Sources

Use these for UI clicks, attacks, magic, footsteps, ambience, and victory/game-over stings.

| Source | Best for | License / notes |
| --- | --- | --- |
| [Kenney RPG Audio](https://kenney.nl/assets/rpg-audio) | Footsteps, weapons, basic RPG foley | CC0 |
| [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | Hits, damage, collisions, combat impacts | CC0 |
| [OpenGameArt: 80 CC0 RPG SFX](https://opengameart.org/content/80-cc0-rpg-sfx) | Broad fantasy SFX pack | CC0 |
| [OpenGameArt: GUI Sound Effects](https://opengameart.org/content/gui-sound-effects) | Menu clicks, confirm/error sounds | CC0 |
| [OpenGameArt: Click sounds(6)](https://opengameart.org/content/click-sounds6) | UI confirm/cancel variations | CC0 |
| [OpenGameArt: Platformer Sounds](https://opengameart.org/content/platformer-sounds-terminal-interaction-door-shots-bang-and-footsteps/) | Footsteps, doors, interaction sounds | CC0 |
| [Mixkit sound effects](https://mixkit.co/free-sound-effects/) | Extra free SFX and stings | Free license; check item page |
| [Freesound FAQ](https://freesound.org/help/faq/) | Search for unusual sounds with per-file licenses | License depends on each item |
| [Pixabay sound effects](https://pixabay.com/sound-effects/) | Free-to-use sound library with commercial-use options | Check item license details |
| [ZapSplat license](https://www.zapsplat.com/license-type/standard-license/) | Large backup sound library | Basic vs premium account terms apply |

## Porting Plan

When we start importing assets, keep the naming consistent with gameplay usage:

```text
characters/
  hero_idle.png
  hero_walk_01.png
  hero_attack_01.png
  hero_hurt_01.png
enemies/
  fiery_idle_01.png
  shadow_attack_01.png
  ice_death_01.png
sounds/
  ui_confirm.wav
  ui_cancel.wav
  attack_slash.wav
  magic_cast.wav
  hit_heavy.wav
  footstep_stone.wav
  boss_roar.wav
```

If you download anything that is not CC0, add the source URL and license note to `assets/credits.md` before using it in the game.
