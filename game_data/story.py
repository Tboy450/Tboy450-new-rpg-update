"""Story intro, map NPCs, and one-shot area dialogue.

Beginner note:
    This module is intentionally data-only. It answers questions like:

    - Which story NPCs should appear on the world map?
    - Which dialogue should start when the player enters a special area?
    - What extra town-guard lines should foreshadow those characters?
    - Which trophies or story rewards should be granted by major story beats?

    The drawing, input handling, and reward code still live in `main.py`.
    Keeping the text here makes future story edits safer because a beginner can
    change dialogue without hunting through the whole game loop.

    Plain-language terms:
    - NPC means "non-player character": a person in the game who is not the hero.
    - Sprite means the picture used to draw a character, enemy, item, or prop.
    - Key means a short nickname the code uses to find a larger group of data.
"""

# ============================================================================
# OPENING CUTSCENE SUMMARY LINES
# ============================================================================
# These short lines are the compact version of the opening story. The large
# `main.py` file reads them and shows them during the animated intro. Change the
# words here when the story changes. Change timing or screen placement in
# `OpeningCutscene` in `main.py`.
OPENING_STORY_LINES = (
    "Malakor's shadow did not rise alone.",
    "A white mask began walking the northern pines.",
    "The town knight guards the last road.",
    "The Lion Sage holds the first true quest.",
)

# ============================================================================
# TOWN GUARD STORY BRIDGE
# ============================================================================
# `game_data/npcs.py` owns the basic town guard greeting. These extra lines are
# added onto that greeting when the town is created. In plain terms: this lets
# the guard mention world-story events without mixing all guard, shop, and quest
# text into one giant file.
TOWN_GUARD_STORY_LINES = (
    "The dragon is not only a beast. Malakor is a test the world keeps failing.",
    "Do not chase his fire first. A white mask stalks the northern pines.",
    "Seek the Lion Sage in the western marsh. He knows how fear and healing both begin.",
    "Earn his blessing, then choose which threat you are ready to face.",
    "And listen for smaller troubles on the side roads. A saved stranger can change a whole map.",
)

# ============================================================================
# FRIENDLY OVERWORLD STORY NPC PLACEMENT
# ============================================================================
# Each named group below creates one friendly person on the 3x3 overworld map.
# Programmers often call one named group of settings a "record" or "dictionary."
#
# Field guide for one NPC group:
# - `name`: short name painted over the sprite.
# - `title`: longer role label for humans reading this data file.
# - `area`: which square of the 3-by-3 world map this person stands in.
#   `(0, 0)` means top-left. `(2, 2)` means bottom-right.
# - `local_position`: where the person's feet touch the ground inside that map
#   square. This is not the top-left of the picture.
# - `sprite_key`: a short nickname for the picture file. The real file path is
#   listed in `systems/assets.py` under `STORY_SPRITE_PATHS`.
# - `sprite_height`: how tall the imported sprite should be when drawn.
# - `aura_color`: color used for the ring/marker around that NPC.
# - `prompt`: text shown when the player is close enough to interact.
# - `dialogue_key`: a short nickname for this person's conversation below.
STORY_NPCS = {
    "lion_sage": {
        "name": "Lion Sage",
        "title": "Guardian Healer",
        "area": (0, 1),  # west-middle tile, currently the swamp biome
        # BEGINNER NOTE: Keep the Lion Sage near the east side of the swamp so
        # players arriving from town see him quickly instead of wandering.
        "local_position": (760, 390),
        "sprite_key": "lion_sage",
        "sprite_height": 176,
        "aura_color": (80, 220, 170),
        "prompt": "ENTER: seek Lion Sage guidance",
        "dialogue_key": "lion_sage_swamp",
    },
    "forest_apothecary": {
        "name": "Wren",
        "title": "Forest Apothecary",
        "area": (1, 0),  # northern forest, same tile where Ghost Face appears
        # BEGINNER NOTE: Wren stays near the lower-left trail, away from the
        # Ghost Face enemy in the center, so players can choose conversation or
        # combat instead of being forced into both at once.
        "local_position": (245, 525),
        "sprite_key": "forest_apothecary",
        "sprite_height": 140,
        "aura_color": (130, 230, 150),
        "prompt": "ENTER: talk to Wren",
        "dialogue_key": "forest_apothecary_mooncap",
    },
    "plains_ranger": {
        "name": "Elian",
        "title": "Road Ranger",
        "area": (1, 1),  # center plains tile
        "local_position": (350, 360),
        "sprite_key": "plains_ranger",
        "sprite_height": 148,
        "aura_color": (235, 210, 110),
        "prompt": "ENTER: talk to Elian",
        "dialogue_key": "plains_ranger_waymarks",
    },
    "star_cartographer": {
        "name": "Ivo",
        "title": "Star Cartographer",
        "area": (0, 0),  # north-west mountain tile
        "local_position": (755, 410),
        "sprite_key": "star_cartographer",
        "sprite_height": 146,
        "aura_color": (160, 185, 255),
        "prompt": "ENTER: talk to Ivo",
        "dialogue_key": "star_cartographer_chart",
    },
    "lantern_guard": {
        "name": "Kael",
        "title": "Lantern Guard",
        "area": (2, 2),  # south-east cave tile
        "local_position": (265, 470),
        "sprite_key": "lantern_guard",
        "sprite_height": 150,
        "aura_color": (255, 190, 95),
        "prompt": "ENTER: talk to Kael",
        "dialogue_key": "lantern_guard_echo",
    },
}

# ============================================================================
# STORY DIALOGUE RECORDS
# ============================================================================
# Each named group below controls a first conversation, optional repeat lines,
# and optional one-time rewards.
#
# Field guide for one conversation group:
# - `trigger`: `"enter_area"` starts automatically when the player enters the
#   area. `"talk_npc"` only starts when the player talks to the matching person.
# - `area`: same map square where the scene belongs.
# - `speaker` / `title`: text shown at the top of the dialogue panel.
# - `portrait`: short nickname for the portrait picture shown in the panel.
# - `color`: border/accent color for the dialogue panel.
# - `lines`: first-time dialogue shown one line at a time.
# - `repeat_lines`: shorter dialogue used after the first conversation is done.
# - `reward`: optional one-time reward block applied by `Game.apply_story_reward`.
STORY_AREA_DIALOGUES = {
    "ghost_face_forest": {
        "trigger": "enter_area",
        "area": (1, 0),  # top-center forest tile
        "speaker": "Ghost Face",
        "title": "The Mask In The Pines",
        "portrait": "ghost_face",
        "color": (255, 105, 180),
        "lines": (
            "The trees stop moving. Even the wind seems to hold its breath.",
            "A white mask turns toward you from the center of the forest.",
            "Ghost Face: You brought a heartbeat into my woods. I can hear it.",
            "Ghost Face: The lion sent you with courage. I wonder how loud it breaks.",
        ),
        "repeat_lines": (
            "Ghost Face: The mask is still waiting.",
            "Ghost Face: Courage is only useful after it starts shaking.",
        ),
    },
    "lion_sage_swamp": {
        "trigger": "enter_area",
        "area": (0, 1),  # west-middle swamp tile
        "speaker": "Lion Sage",
        "title": "The Guardian Healer",
        "portrait": "lion_sage",
        "color": (80, 220, 170),
        "lines": (
            "The swamp mist curls into colored ribbons before your eyes.",
            "Lion Sage: Strength without care becomes another kind of wound.",
            "Lion Sage: Your first quest is the mask in the northern pines. Ghost Face feeds on panic.",
            "Lion Sage: Your second quest is the dragon path. Defeat the lesser drakes, grow, then face Malakor.",
            "Lion Sage: Black endures. Crimson protects life. Blue stays calm. Teal listens. Green recovers. Purple studies.",
            "Lion Sage: I awaken your special technique. Use it when ordinary courage is not enough.",
        ),
        "repeat_lines": (
            "Lion Sage: Return when your courage feels tired. Healing is not weakness.",
            "Lion Sage: Study the enemy, then protect what still has a chance to grow.",
        ),
        "reward": {
            # Reward field guide in plain language:
            # - `exp`: experience points, used for leveling up.
            # - `items`: usable supplies such as health or mana potions.
            # - `score`: adds to the game score.
            # - `reputation`: adds town reputation.
            # - `unlock_special`: makes the SPECIAL battle button available.
            # - `story_items`: permanent keepsakes shown in Inventory.
            # - `equipment`: weapons, armor, or charms from `game_data/equipment.py`.
            "exp": 260,
            "items": {"health": 1, "mana": 1},
            "score": 8,
            "reputation": 1,
            "unlock_special": True,
            "story_items": {"lion_sage_medallion": 1},
            "equipment": ["lion_sage_charm"],
            # This keeps the Sage's training from immediately throwing the
            # player into a dragon ambush before they can choose the Ghost Face
            # path or review the new SPECIAL attack.
            "calm_boss_pressure": True,
            "message": "Lion Sage blessing: {exp} EXP, SPECIAL awakened, medallion received.",
        },
    },
    "forest_apothecary_mooncap": {
        "trigger": "talk_npc",
        "area": (1, 0),
        "speaker": "Wren",
        "title": "Mooncap Antidote",
        "portrait": "forest_apothecary",
        "color": (130, 230, 150),
        "lines": (
            "Wren: Step softly. Mooncaps bruise if you look proud while picking them.",
            "Wren: I came here for medicine, not hero songs. Fear leaves toxins in the hands.",
            "Wren: If the white mask corners you, breathe out first. Panic makes every wound deeper.",
            "Wren: Take this vial. It is not a miracle, but it reminds the body how to keep fighting.",
        ),
        "repeat_lines": (
            "Wren: Mooncaps grow back when the forest feels trusted.",
            "Wren: If your hands shake after battle, warm them before gripping steel again.",
        ),
        "reward": {
            "exp": 55,
            "score": 4,
            "items": {"health": 1},
            "story_items": {"mooncap_vial": 1},
            "message": "Wren shares a Mooncap Vial and {exp} EXP.",
        },
    },
    "plains_ranger_waymarks": {
        "trigger": "talk_npc",
        "area": (1, 1),
        "speaker": "Elian",
        "title": "Waymarks In Tall Grass",
        "portrait": "plains_ranger",
        "color": (235, 210, 110),
        "lines": (
            "Elian: The plains look empty until you are lost in them.",
            "Elian: I mark safe turns with three stones, risky turns with two, and foolish turns with none.",
            "Elian: Monsters use straight roads. People survive by knowing when to bend.",
            "Elian: Here. Carry one of my waymarks. Drop it when the grass starts repeating itself.",
        ),
        "repeat_lines": (
            "Elian: If the horizon starts lying, stop walking and count your shadows.",
            "Elian: Side roads are not distractions. They are how towns keep breathing.",
        ),
        "reward": {
            "exp": 60,
            "score": 5,
            "items": {"health": 1},
            "story_items": {"ranger_waymark": 1},
            "message": "Elian gives you a ranger waymark and {exp} EXP.",
        },
    },
    "star_cartographer_chart": {
        "trigger": "talk_npc",
        "area": (0, 0),
        "speaker": "Ivo",
        "title": "Stars Under Stone",
        "portrait": "star_cartographer",
        "color": (160, 185, 255),
        "lines": (
            "Ivo: Everyone looks up for stars. Mountains teach you to find them in cracks of ice.",
            "Ivo: This chart is not for the dragon. It is for anyone walking home after dark.",
            "Ivo: Mark one star you trust. When fear moves the horizon, that mark stays honest.",
            "Ivo: Keep this torn corner. It has saved better navigators than me from worse weather.",
        ),
        "repeat_lines": (
            "Ivo: Maps do not remove danger. They make danger less dramatic.",
            "Ivo: If you reach a peak, look back. The path behind you is also a teacher.",
        ),
        "reward": {
            "exp": 70,
            "score": 6,
            "items": {"mana": 1},
            "story_items": {"star_chart_corner": 1},
            "message": "Ivo marks your map with a Star Chart Corner and {exp} EXP.",
        },
    },
    "lantern_guard_echo": {
        "trigger": "talk_npc",
        "area": (2, 2),
        "speaker": "Kael",
        "title": "The Echo Lantern",
        "portrait": "lantern_guard",
        "color": (255, 190, 95),
        "lines": (
            "Kael: Cave echoes are thieves. They steal your voice and sell it back as doubt.",
            "Kael: I guard lanterns for miners, children, and anyone too stubborn to admit the dark is winning.",
            "Kael: If your light goes out, do not run. Running teaches the cave your rhythm.",
            "Kael: Take this lantern glass. It catches one good spark and remembers it longer than fear does.",
        ),
        "repeat_lines": (
            "Kael: Walk slow in caves. The ground is allowed to be older than your plans.",
            "Kael: A lantern is a promise you carry with your hand.",
        ),
        "reward": {
            "exp": 80,
            "score": 7,
            "items": {"mana": 1},
            "story_items": {"echo_lantern_glass": 1},
            "message": "Kael gives you Echo Lantern Glass and {exp} EXP.",
        },
    },
}


# ============================================================================
# PERMANENT STORY / SIDE-STORY KEEPSAKES
# ============================================================================
# These are not potions and are not gear. They are permanent souvenirs from
# quests or side stories. The player sees them in the Inventory trophy panel.
#
# Field guide:
# - `label`: player-facing item name.
# - `kind`: short category shown before the item in Inventory.
# - `description`: one-line reminder of where the keepsake came from.
STORY_REWARD_ITEMS = {
    "lion_sage_medallion": {
        "label": "Lion Sage Medallion",
        "kind": "trophy",
        "description": "A healer's sigil proving the Guardian Sage awakened your special technique.",
    },
    "mooncap_vial": {
        "label": "Mooncap Vial",
        "kind": "side",
        "description": "Wren's forest medicine, brewed for steady hands after fear or poison.",
    },
    "ranger_waymark": {
        "label": "Ranger Waymark",
        "kind": "side",
        "description": "Elian's trail stone, used to mark a safe return through tall grass.",
    },
    "star_chart_corner": {
        "label": "Star Chart Corner",
        "kind": "side",
        "description": "A torn mountain chart from Ivo, marked with one trustworthy star.",
    },
    "echo_lantern_glass": {
        "label": "Echo Lantern Glass",
        "kind": "side",
        "description": "A warm cave-lantern shard from Kael that keeps one good spark.",
    },
    "ghost_face_mask_shard": {
        "label": "Ghost Face Mask Shard",
        "kind": "trophy",
        "description": "A cracked white-mask fragment from your first victory in the northern pines.",
    },
    "inn_recovery_mark": {
        "label": "Inn Recovery Mark",
        "kind": "town",
        "description": "Proof the Warm Hearth Inn is ready as the town's safe recovery point.",
    },
    "potion_shop_stamp": {
        "label": "Potion Shop Stamp",
        "kind": "town",
        "description": "A stamped pouch tag showing the Potion Shop restocked your combat supplies.",
    },
    "forge_due_bill": {
        "label": "Blacksmith Due Bill",
        "kind": "town",
        "description": "Borin's note promising level-gated forge work as your class grows stronger.",
    },
    "library_lore_page": {
        "label": "Library Lore Page",
        "kind": "town",
        "description": "A copied dragon-pattern note from the Library for the pause-menu Log.",
    },
    "town_hall_writ": {
        "label": "Town Hall Writ",
        "kind": "town",
        "description": "Captain Marcus' signed town-defense report and permission to carry the town seal.",
    },
    "herbal_cottage_bundle": {
        "label": "Herbal Cottage Bundle",
        "kind": "town",
        "description": "A tied bundle of recovery herbs from Toma's cottage.",
    },
    "market_stew_token": {
        "label": "Market Stew Token",
        "kind": "town",
        "description": "A stamped token from Meri proving the Market Stall is feeding the road crews.",
    },
}


# ============================================================================
# SPECIAL STORY ENEMY REWARDS
# ============================================================================
# Special map enemies can return after being defeated, but the first win should
# feel more important than later farming. `first` means the reward for defeating
# that enemy type for the first time. `repeat` means the smaller reward for later
# defeats of the same enemy type.
STORY_ENEMY_REWARDS = {
    "ghost_face": {
        "first": {
            "exp": 135,
            "score": 35,
            "items": {"mana": 1},
            "story_items": {"ghost_face_mask_shard": 1},
            "equipment": ["mask_shard_edge"],
            "message": "Ghost Face first clear: {exp} EXP, {score} score, Mask Shard claimed.",
        },
        "repeat": {
            "exp": 40,
            "score": 10,
            "items": {"health": 1},
            "message": "Ghost Face fades again: {exp} EXP, {score} score, small supply drop.",
        },
    },
}


def get_story_dialogue(dialogue_key):
    """Return one story dialogue record by key.

    Missing keys return None so callers can fail safely instead of crashing.
    """
    return STORY_AREA_DIALOGUES.get(dialogue_key)


def get_story_dialogues_for_area(area_x, area_y):
    """Return all area-triggered story dialogues for one world tile."""
    return [
        (key, dialogue)
        for key, dialogue in STORY_AREA_DIALOGUES.items()
        if tuple(dialogue.get("area", ())) == (area_x, area_y)
    ]


def get_story_npcs_for_area(area_x, area_y):
    """Return friendly story NPC records for one world tile."""
    return [
        (key, npc)
        for key, npc in STORY_NPCS.items()
        if tuple(npc.get("area", ())) == (area_x, area_y)
    ]


def get_story_reward_item(item_key):
    """Return display data for one trophy or story inventory item."""
    return STORY_REWARD_ITEMS.get(item_key)


def get_story_enemy_reward(enemy_type, repeat=False):
    """Return first-clear or repeat reward data for a special story enemy."""
    rewards = STORY_ENEMY_REWARDS.get(enemy_type)
    if not rewards:
        return None
    return rewards["repeat" if repeat else "first"]
