"""World layout, area descriptions, visuals, and environmental mechanics.

Beginner note:
    This file describes the 3x3 overworld and area-wide effects. It does not
    contain player movement code; `WorldMap` and `WorldArea` in `main.py` read
    these tables.

Common fields:
    background_color: RGB color used to fill the area background.
    grid_color: RGB color used for grid/path lines.
    count: how many particles to spawn at once.
    interval: frames between environmental mechanic ticks.
    health/mana: amount restored or drained by an area effect.
"""

# 3 rows by 3 columns. Row index is y, column index is x.
WORLD_LAYOUT = (
    ("mountain", "forest", "desert"),
    ("swamp", "beach", "volcano"),
    ("ice", "town", "cave"),
)

# Short labels shown on the map and journal.
AREA_DESCRIPTIONS = {
    "forest": "Dense woodland",
    "mountain": "Rocky peaks",
    "desert": "Harsh wasteland",
    "swamp": "Misty wetlands",
    "beach": "Sandy shores",
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
    "beach": {
        "background_color": (75, 65, 45),
        "grid_color": (95, 85, 65),
    },
    "town": {
        "background_color": (80, 120, 60),
        "grid_color": (100, 140, 80),
    },
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
        },
    ],
    "beach": [
        {
            "count": 4,
            "color": (220, 240, 255),
            "velocity_x": (-0.4, 0.4),
            "velocity_y": (-0.2, 0.2),
            "size": 5,
            "lifetime": 55,
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
    "beach": {
        "label": "Sea Breeze",
        "color": (180, 230, 255),
        "interval": 420,
        "mana": 1,
        "message": "Sea breeze restores {mana} MP.",
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
