"""World layout and spawn configuration."""

WORLD_LAYOUT = (
    ("mountain", "forest", "desert"),
    ("swamp", "beach", "volcano"),
    ("ice", "town", "cave"),
)

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

AREA_ENEMY_TYPES = {
    "forest": ["shadow", "ice"],
    "desert": ["fiery"],
    "mountain": ["fiery", "ice"],
    "swamp": ["shadow", "ice"],
    "volcano": ["fiery"],
    "ice": ["ice"],
    "town": [],
    "castle": ["shadow", "fiery"],
    "cave": ["shadow", "ice"],
}
