"""Enemy naming, area spawn, and boss palette data.

Beginner note:
    This file does not contain enemy behavior. It contains labels and lookup
    tables that `Enemy` and `Dragon` in `main.py` use when creating enemies.

Key ideas:
    Enemy element keys such as `fiery`, `shadow`, and `ice` must match keys in
    `ELEMENT_PROFILES` from `game_data/mechanics.py`.
"""

# Random regular enemy names are chosen from these pools by element type.
ENEMY_NAME_POOLS = {
    "fiery": [
        "Fire Imp",
        "Lava Sprite",
        "Magma Beast",
        "Inferno Hound",
        "Blaze Fiend",
    ],
    "shadow": [
        "Dark Shade",
        "Night Phantom",
        "Void Walker",
        "Gloom Stalker",
        "Shadow Fiend",
    ],

    # BEGINNER NOTE: Ghost Face is intentionally kept out of AREA_ENEMY_TYPES
    # below, so it does not appear as a random forest/cave enemy. It is placed
    # as a special map enemy by spawn_story_enemies() in main.py.
    "ghost_face": [
        "Ghost Face",
    ],
    "ice": [
        "Frost Sprite",
        "Ice Golem",
        "Blizzard Elemental",
        "Frozen Wraith",
        "Chill Specter",
    ],
}

# Boss dragon drawing uses these color pairs as primary/secondary palettes.
DRAGON_BOSS_COLORS = [
    ((255, 69, 0), (255, 140, 0)),
    ((0, 191, 255), (0, 255, 255)),
    ((50, 205, 50), (124, 252, 0)),
    ((148, 0, 211), (255, 0, 255)),
    ((255, 215, 0), (255, 255, 0)),
    ((255, 20, 147), (255, 105, 180)),
    ((255, 255, 255), (200, 200, 200)),
    ((255, 99, 71), (255, 160, 122)),
    ((70, 130, 180), (176, 224, 230)),
    ((139, 69, 19), (222, 184, 135)),
]

# Area names here should match `WORLD_LAYOUT` and `AREA_VISUALS` in `world.py`.
# A town has no random enemies because it is the safe hub.
AREA_ENEMY_TYPES = {
    "forest": ["shadow", "ice"],
    "desert": ["fiery"],
    "mountain": ["fiery", "ice"],
    "swamp": ["shadow", "ice"],
    "plains": ["fiery", "shadow"],
    "volcano": ["fiery"],
    "ice": ["ice"],
    "town": [],
    "castle": ["shadow", "fiery"],
    "cave": ["shadow", "ice"],
}
