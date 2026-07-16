"""World layout, area descriptions, visuals, and environmental mechanics.

Beginner note:
    This file describes the 3x3 overworld and area-wide effects. It does not
    contain player movement code; `WorldMap` and `WorldArea` in `main.py` read
    these tables.

Common fields:
    background_color: RGB color used to fill the area background.
    grid_color: RGB color used for grid/path lines.
    style: name of the draw-only scenic layer for an area.
    overlay_color/bands/wisps: optional draw-only atmosphere layer controls.
    count: how many particles to spawn at once.
    x_range/y_range: optional local-area spawn bounds for particles.
    interval: frames between environmental mechanic ticks.
    health/mana: amount restored or drained by an area effect.
"""

# 3 rows by 3 columns. Row index is y, column index is x.
WORLD_LAYOUT = (
    ("mountain", "forest", "desert"),
    ("swamp", "plains", "volcano"),
    ("ice", "town", "cave"),
)

# Short labels shown on the map and journal.
AREA_DESCRIPTIONS = {
    "forest": "Dense woodland",
    "mountain": "Rocky peaks",
    "desert": "Harsh wasteland",
    "swamp": "Misty wetlands",
    "plains": "Open grasslands",
    "volcano": "Fiery depths",
    "ice": "Frozen wastes",
    "castle": "Ancient fortress",
    "cave": "Dark caverns",
    "town": "Safe haven",
}

# Color profiles for each area type. Area names should match `WORLD_LAYOUT`.
AREA_VISUALS = {
    "forest": {
        "background_color": (20, 40, 20),
        "grid_color": (40, 60, 40),
    },
    "desert": {
        "background_color": (80, 70, 40),
        "grid_color": (100, 90, 60),
    },
    "mountain": {
        "background_color": (50, 50, 60),
        "grid_color": (70, 70, 80),
    },
    "swamp": {
        "background_color": (25, 35, 25),
        "grid_color": (45, 55, 45),
    },
    "volcano": {
        "background_color": (60, 25, 25),
        "grid_color": (80, 45, 45),
    },
    "ice": {
        "background_color": (35, 45, 65),
        "grid_color": (55, 65, 85),
    },
    "castle": {
        "background_color": (45, 35, 45),
        "grid_color": (65, 55, 65),
    },
    "cave": {
        "background_color": (15, 15, 25),
        "grid_color": (35, 35, 45),
    },
    "plains": {
        "background_color": (58, 92, 46),
        "grid_color": (84, 126, 62),
    },
    "town": {
        "background_color": (80, 120, 60),
        "grid_color": (100, 140, 80),
    },
}

# BEGINNER CODE LABEL: draw-only scenic layer tuning.
# These values give each overworld area a stronger visual identity. The drawing
# code in `WorldArea.draw_scenic_layer` reads this table, but these shapes do
# not add collision, quests, buttons, or new playable spaces.
AREA_SCENIC_PROFILES = {
    "forest": {
        "style": "forest",
        "primary": (34, 82, 38),
        "secondary": (58, 124, 56),
        "accent": (132, 190, 88),
    },
    "desert": {
        "style": "dunes",
        "primary": (128, 102, 58),
        "secondary": (178, 146, 82),
        "accent": (232, 198, 118),
    },
    "mountain": {
        "style": "ridges",
        "primary": (72, 76, 92),
        "secondary": (108, 112, 132),
        "accent": (190, 196, 218),
    },
    "swamp": {
        "style": "wetlands",
        "primary": (34, 68, 42),
        "secondary": (58, 96, 66),
        "accent": (126, 166, 112),
    },
    "plains": {
        "style": "grassland",
        "primary": (72, 132, 52),
        "secondary": (116, 172, 72),
        "accent": (204, 226, 108),
    },
    "volcano": {
        "style": "lava_cracks",
        "primary": (92, 34, 28),
        "secondary": (150, 56, 34),
        "accent": (255, 146, 48),
    },
    "ice": {
        "style": "ice_shards",
        "primary": (72, 106, 142),
        "secondary": (118, 166, 206),
        "accent": (218, 244, 255),
    },
    "castle": {
        "style": "runes",
        "primary": (72, 60, 82),
        "secondary": (110, 92, 128),
        "accent": (238, 210, 112),
    },
    "cave": {
        "style": "crystals",
        "primary": (34, 34, 54),
        "secondary": (70, 70, 104),
        "accent": (154, 176, 238),
    },
}

# BEGINNER CODE LABEL: draw-only atmosphere overlay tuning.
# These values add region mood with transparent haze. They do not create
# collision, hide UI, change enemies, or alter Android packaging. Keep alpha
# values low so the player, items, and landmarks stay readable.
AREA_ATMOSPHERE_PROFILES = {
    "mountain": {
        "overlay_color": (160, 170, 210, 16),
        "band_color": (210, 218, 238),
        "bands": ((128, 70, 20), (252, 86, 16), (382, 58, 12)),
        "wisps": 4,
        "wisp_alpha": 18,
    },
    "swamp": {
        "overlay_color": (118, 158, 126, 24),
        "band_color": (172, 210, 162),
        "bands": ((278, 64, 22), (388, 76, 20), (515, 92, 16)),
        "wisps": 7,
        "wisp_alpha": 22,
    },
    "volcano": {
        "overlay_color": (150, 58, 34, 14),
        "band_color": (255, 142, 54),
        "bands": ((360, 50, 16), (490, 62, 14), (610, 78, 12)),
        "wisps": 5,
        "wisp_alpha": 14,
    },
    "ice": {
        "overlay_color": (184, 220, 255, 20),
        "band_color": (226, 246, 255),
        "bands": ((112, 58, 18), (198, 70, 16), (552, 82, 14)),
        "wisps": 5,
        "wisp_alpha": 16,
    },
    "cave": {
        "overlay_color": (72, 82, 128, 20),
        "band_color": (146, 164, 236),
        "bands": ((322, 62, 12), (512, 82, 10)),
        "wisps": 4,
        "wisp_alpha": 12,
    },
}

# BEGINNER CODE LABEL: overworld music mood by area.
# MusicSystem generates a few short procedural loops and uses this table to
# choose which loop matches the current area. It does not load external audio or
# touch Android packaging.
AREA_MUSIC_PROFILES = {
    "forest": "green",
    "plains": "green",
    "mountain": "highlands",
    "ice": "highlands",
    "desert": "sun",
    "volcano": "sun",
    "swamp": "shadow",
    "cave": "shadow",
    "castle": "shadow",
}

# Optional ambient particles for areas. Missing area keys simply have no custom
# particle profile.
AREA_PARTICLE_PROFILES = {
    "volcano": [
        {
            "count": 5,
            "color": (255, 100, 0),
            "velocity_x": (-0.5, 0.5),
            "velocity_y": (-2, -0.5),
            "size": 6,
            "lifetime": 40,
            "y_range": (240, 660),
        },
        {
            "count": 2,
            "color": (90, 70, 70),
            "velocity_x": (-0.2, 0.2),
            "velocity_y": (-0.7, -0.2),
            "size": 3,
            "lifetime": 55,
            "y_range": (260, 680),
        },
    ],
    "ice": [
        {
            "count": 4,
            "color": (200, 220, 255),
            "velocity_x": (-0.3, 0.3),
            "velocity_y": (0.5, 1.5),
            "size": 4,
            "lifetime": 50,
            "y_range": (0, 360),
        },
        {
            "count": 2,
            "color": (230, 245, 255),
            "velocity_x": (-0.1, 0.1),
            "velocity_y": (-0.1, 0.1),
            "size": 2,
            "lifetime": 45,
            "y_range": (260, 660),
        },
    ],
    "swamp": [
        {
            "count": 3,
            "color": (150, 180, 150),
            "velocity_x": (-0.2, 0.2),
            "velocity_y": (-0.2, 0.2),
            "size": 5,
            "lifetime": 60,
            "y_range": (260, 660),
        },
        {
            "count": 2,
            "color": (92, 136, 96),
            "velocity_x": (-0.1, 0.1),
            "velocity_y": (-0.6, -0.2),
            "size": 4,
            "lifetime": 70,
            "y_range": (360, 680),
        },
    ],
    "forest": [
        {
            "count": 4,
            "color": (100, 150, 50),
            "velocity_x": (-0.3, 0.3),
            "velocity_y": (-0.5, -0.1),
            "size": 5,
            "lifetime": 45,
            "y_range": (180, 620),
        },
        {
            "count": 2,
            "color": (190, 220, 120),
            "velocity_x": (-0.2, 0.2),
            "velocity_y": (-0.15, 0.15),
            "size": 2,
            "lifetime": 55,
            "y_range": (200, 520),
        },
    ],
    "desert": [
        {
            "count": 6,
            "color": (200, 180, 120),
            "velocity_x": (-1, 1),
            "velocity_y": (-0.5, 0.5),
            "size": 4,
            "lifetime": 35,
            "y_range": (300, 680),
        },
    ],
    "mountain": [
        {
            "count": 3,
            "color": (180, 180, 200),
            "velocity_x": (-0.8, 0.8),
            "velocity_y": (-0.3, 0.3),
            "size": 4,
            "lifetime": 40,
            "y_range": (120, 520),
        },
    ],
    "plains": [
        {
            "count": 4,
            "color": (180, 220, 110),
            "velocity_x": (-0.5, 0.5),
            "velocity_y": (-0.4, -0.1),
            "size": 5,
            "lifetime": 55,
            "y_range": (250, 650),
        },
        {
            "count": 2,
            "color": (235, 228, 118),
            "velocity_x": (-0.15, 0.15),
            "velocity_y": (-0.2, 0.05),
            "size": 2,
            "lifetime": 60,
            "y_range": (230, 540),
        },
    ],
    "castle": [
        {
            "count": 3,
            "color": (255, 215, 0),
            "velocity_x": (-0.2, 0.2),
            "velocity_y": (-0.2, 0.2),
            "size": 4,
            "lifetime": 50,
            "y_range": (180, 520),
        },
    ],
    "cave": [
        {
            "count": 2,
            "color": (100, 100, 120),
            "velocity_x": (-0.1, 0.1),
            "velocity_y": (-0.1, 0.1),
            "size": 3,
            "lifetime": 70,
            "y_range": (220, 650),
        },
        {
            "count": 2,
            "color": (150, 160, 230),
            "velocity_x": (-0.05, 0.05),
            "velocity_y": (-0.05, 0.05),
            "size": 2,
            "lifetime": 65,
            "y_range": (300, 640),
        },
    ],
}

# Environmental effects applied while the player spends time in an area.
# Positive health/mana restores resources; negative values drain resources.
AREA_MECHANICS = {
    "forest": {
        "label": "Verdant Cover",
        "color": (120, 210, 90),
        "interval": 420,
        "health": 1,
        "message": "Forest herbs restore {health} HP.",
    },
    "mountain": {
        "label": "Thin Air",
        "color": (180, 180, 220),
        "interval": 420,
        "mana": -1,
        "message": "Thin air drains {mana} MP.",
    },
    "desert": {
        "label": "Sunbaked",
        "color": (230, 190, 100),
        "interval": 360,
        "health": -1,
        "message": "Desert heat costs {health} HP.",
    },
    "swamp": {
        "label": "Miasma",
        "color": (140, 190, 140),
        "interval": 360,
        "health": -1,
        "mana": -1,
        "message": "Swamp miasma saps {health} HP and {mana} MP.",
    },
    "plains": {
        "label": "Open Air",
        "color": (180, 230, 120),
        "interval": 420,
        "mana": 1,
        "message": "Open plains air restores {mana} MP.",
    },
    "volcano": {
        "label": "Scorching Heat",
        "color": (255, 120, 50),
        "interval": 300,
        "health": -2,
        "message": "Scorching heat burns {health} HP.",
    },
    "ice": {
        "label": "Biting Cold",
        "color": (170, 230, 255),
        "interval": 360,
        "health": -1,
        "message": "Biting cold costs {health} HP.",
    },
    "cave": {
        "label": "Echo Focus",
        "color": (170, 170, 210),
        "interval": 420,
        "mana": 1,
        "message": "Echoing crystals restore {mana} MP.",
    },
    "town": {
        "label": "Safe Rest",
        "color": (140, 240, 140),
        "interval": 240,
        "health": 2,
        "mana": 2,
        "message": "Town safety restores {health} HP and {mana} MP.",
    },
}
