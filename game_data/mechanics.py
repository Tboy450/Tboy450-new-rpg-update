"""Shared mechanics data for combat, pickups, and matching visuals."""

ELEMENT_PROFILES = {
    "fiery": {
        "label": "Flame",
        "primary_color": (220, 80, 0),
        "secondary_color": (255, 150, 0),
        "accent_color": (255, 255, 0),
        "particle_colors": [(255, 100, 0), (255, 150, 0), (255, 200, 50)],
        "status": {
            "kind": "burn",
            "chance": 0.45,
            "damage": 3,
            "message": "Scorching flames burn you for {amount} damage!",
        },
    },
    "shadow": {
        "label": "Shadow",
        "primary_color": (35, 35, 70),
        "secondary_color": (70, 70, 120),
        "accent_color": (0, 255, 255),
        "particle_colors": [(40, 40, 80), (70, 70, 120), (100, 100, 150)],
        "status": {
            "kind": "drain",
            "chance": 0.4,
            "amount": 6,
            "message": "Shadow energy drains {amount} MP!",
        },
    },
    "ice": {
        "label": "Frost",
        "primary_color": (150, 220, 255),
        "secondary_color": (220, 240, 255),
        "accent_color": (0, 100, 200),
        "particle_colors": [(100, 200, 255), (150, 220, 255), (200, 240, 255)],
        "status": {
            "kind": "chill",
            "chance": 0.45,
            "turns": 1,
            "damage_multiplier": 0.75,
            "message": "Frost slows your next strike!",
        },
    },
    "neutral": {
        "label": "Neutral",
        "primary_color": (160, 160, 160),
        "secondary_color": (210, 210, 210),
        "accent_color": (255, 255, 255),
        "particle_colors": [(160, 160, 160), (210, 210, 210), (255, 255, 255)],
        "status": None,
    },
}

ITEM_PROFILES = {
    "health": {
        "label": "Health",
        "color": (255, 105, 180),
        "effect": "restore_health",
        "amount": 30,
        "message": "Restored {amount} HP!",
    },
    "mana": {
        "label": "Mana",
        "color": (0, 255, 255),
        "effect": "restore_mana",
        "amount": 40,
        "message": "Restored {amount} MP!",
    },
    "might": {
        "label": "Might",
        "color": (255, 215, 0),
        "effect": "raise_strength",
        "amount": 1,
        "message": "Strength increased by {amount}!",
    },
    "ward": {
        "label": "Ward",
        "color": (120, 220, 170),
        "effect": "raise_defense",
        "amount": 1,
        "message": "Defense increased by {amount}!",
    },
}

ITEM_SPAWN_TABLE = (
    "health",
    "health",
    "mana",
    "mana",
    "might",
    "ward",
)

def get_element_profile(element_type):
    """Return a visual/mechanical profile for an enemy element."""
    return ELEMENT_PROFILES.get(element_type, ELEMENT_PROFILES["neutral"])

