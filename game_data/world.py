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
