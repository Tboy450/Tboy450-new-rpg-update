# Asset Sources

This folder is the intake and storage area for imported art, animation frames,
music, sound effects, and UI assets.

```text
assets/
  source/       raw downloads kept as-is
  processed/    resized / converted files ready for the game
  manifest.json category plan for future asset ports
  credits.md    attribution notes for any non-CC0 items
```

Keep raw uploads under `assets/source/<category>/`, then put converted
game-ready files under `assets/processed/<category>/`.

## Section Map

- `manifest.json`: category status and short notes for what is active or planned.
- `credits.md`: license and attribution notes for imported assets.
- `source/`: original uploads and generated chroma-key files kept for future reprocessing.
- `processed/`: transparent PNGs, resized images, and cut animation frames loaded by the game.
- `source/characters/`: raw Warrior, Mage, and Rogue source images.
- `processed/characters/`: game-ready Warrior, Mage, and Rogue PNGs plus the contact sheet.
- `source/enemies/`: raw enemy source images.
- `processed/enemies/`: game-ready enemy sprites.
- `source/npcs/`: raw story/friendly NPC source images.
- `processed/npcs/`: game-ready story/friendly NPC sprites.
- `source/effects/`: raw GIF/video effect uploads.
- `processed/effects/`: extracted PNG animation frame folders used by combat.
- `source/ui/`: raw UI/title/icon source images.
- `processed/ui/`: game-ready launcher icon and title-screen art.
- `source/music/` and `processed/music/`: future music intake and finished loops.
- `source/sounds/` and `processed/sounds/`: future sound-effect intake and finished WAV/OGG files.
- `processed/scenery/`: active scenery sprites for town buildings and interior props.
- `processed/future_assets/`: transparent future concept assets that are not loaded by the game yet.

Active UI asset:

- `assets/processed/ui/dragon_app_icon.png`: Android launcher icon used by `buildozer.spec`.

Active character assets:

- `assets/processed/characters/warrior.png`: imported Warrior class sprite used in character select, overworld, and battle.
- `assets/processed/characters/mage.png`: generated Mage class sprite used in character select, overworld, and battle.
- `assets/processed/characters/rogue.png`: generated Rogue class sprite used in character select, overworld, and battle.
- `assets/processed/characters/character_contact_sheet.jpg`: preview sheet for checking the three active hero sprites together.

Active enemy asset:

- `assets/processed/enemies/ghost_face.png`: Ghost Face enemy sprite used in the top-center forest area.

Active NPC assets:

- `assets/processed/npcs/lion_sage.png`: Lion Sage story NPC and portrait used in the west swamp area.
- `assets/processed/npcs/town_guard.png`: imported town guard overlay used during the town intro cutscene.
- `assets/processed/npcs/blacksmith.png`: imported Blacksmith interior sprite used in Ironroot Forge.
- `assets/processed/npcs/innkeeper.png`: imported Innkeeper interior sprite used in Warm Hearth Inn.

Active scenery assets:

- `assets/processed/scenery/town_shop/shop_front.png`: imported shop exterior test used on the town map.
- `assets/processed/scenery/town_shop/potion_shelf.png`: imported shop interior shelf prop.
- `assets/processed/scenery/town_shop/shop_counter.png`: imported shop interior service counter prop.
- `assets/processed/scenery/town_shop/scroll_desk.png`: imported shop interior order desk/detail prop.
- `assets/processed/scenery/town_hall/town_hall_front.png`: imported Dragonwatch Hall exterior used on the town map.
- `assets/processed/scenery/town_hall/town_hall_dais.png`: imported Dragonwatch Hall interior command platform.
- `assets/processed/scenery/town_hall/notice_board.png`: imported Dragonwatch Hall interior notice board.
- `assets/processed/scenery/town_stall/food_stall_canopy.png`: imported Food Stall exterior canopy used on the town map.
- `assets/processed/scenery/town_inn/tavern_front.png`: imported Warm Hearth Inn exterior used on the town map.
- `assets/processed/scenery/town_inn/tavern_bar_counter.png`: imported Warm Hearth Inn counter prop.
- `assets/processed/scenery/town_inn/inn_bed.png`: imported Warm Hearth Inn bed prop.
- `assets/processed/scenery/town_inn/hearth_fireplace.png`: imported Warm Hearth Inn fireplace prop.
- `assets/processed/scenery/town_inn/round_tavern_table.png`: imported Warm Hearth Inn table prop.
- `assets/processed/scenery/town_blacksmith/blacksmith_stall.png`: imported Ironroot Forge exterior used on the town map.
- `assets/processed/scenery/town_blacksmith/weapon_rack.png`: imported Ironroot Forge weapon rack prop.
- `assets/processed/scenery/town_blacksmith/armor_stand.png`: imported Ironroot Forge armor stand prop.

Feature map:

- Lion Sage story logic lives in `game_data/story.py`, but his source and processed art live under `assets/source/npcs/` and `assets/processed/npcs/`.
- The start-menu dragon is currently procedural code in `main.py`. The previous generated title dragon was archived under `archive/assets/ui/` because it did not fit the active fire animation.
- The guard is a story-facing NPC visually, so his files live under `assets/source/npcs/` and `assets/processed/npcs/`, even though he appears in the town intro cutscene.
- The Blacksmith and Innkeeper are town-service NPCs, so their active gameplay copies live under `assets/processed/npcs/`, while their future-shelf copies remain under `assets/processed/future_assets/npcs/`.
- The first SPECIAL unlock uses both story data and effect assets:
  `game_data/story.py` grants it, while `assets/processed/effects/flame_tornado/` and `assets/processed/effects/fire_blast/` provide the related imported battle visuals.

Active effect assets:

- `assets/processed/effects/flame_tornado/`: player SPECIAL travel animation.
- `assets/processed/effects/fire_blast/`: Mage Fire Blast impact animation when the special reaches the enemy.
- `assets/processed/effects/mage_magic_fireball/`: Mage normal MAGIC projectile overlay. The older procedural glow, beam, and explosion still run with it.

Future inactive asset pack:

- `assets/processed/future_assets/gear/`: unused future gear concepts.
- `assets/processed/future_assets/scenery/`: unused future scenery/map prop concepts.
- `assets/processed/future_assets/enemies/`: unused future enemy concepts.
- `assets/processed/future_assets/npcs/`: unused future NPC concepts.
- `assets/processed/future_assets/characters/`: unused future class/companion concepts.
- `assets/processed/future_assets/attacks/`: unused future attack/effect concepts.

Active source files:

- `assets/source/characters/warrior_user_supplied.png`: original Warrior reference supplied by the user.
- `assets/source/characters/mage_generated_chroma.png`: generated Mage source on chroma background.
- `assets/source/characters/rogue_generated_chroma.png`: generated Rogue source on chroma background.
- `assets/source/effects/flame_tornado_attack.gif`: raw Fire Tornado special animation source.
- `assets/source/effects/fire_blast_impact.gif`: raw Mage Fire Blast impact source.
- `assets/source/effects/mage_magic_fireball.gif`: raw Mage normal magic projectile source.
- `assets/source/enemies/plague_bat_drake_sheet.png`: user-supplied future enemy sheet for Plague Knight, Crystal Bat, and Ember Drake Hatchling cutouts.
- `assets/source/npcs/blacksmith_innkeeper_sheet.png`: user-supplied future NPC sheet for Blacksmith and Innkeeper cutouts.
- `assets/source/npcs/lion_sage_generated_chroma.png`: generated Lion Sage source on chroma background.
- `assets/source/npcs/town_guard_generated_chroma.png`: generated town guard source on chroma background.

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
