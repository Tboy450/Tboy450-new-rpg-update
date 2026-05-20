"""NPC data used by cutscenes and town interactions."""

TOWN_GUARD_TEMPLATE = {
    "x": 300,
    "y": 270,
    "width": 40,
    "height": 60,
    "color": (100, 150, 200),
    "animation_offset": 0,
    "animation_timer": 0,
    "current_dialogue": 0,
    "dialogue_timer": 0,
    "visible": True,
}

TOWN_GUARD_DIALOGUE = (
    "Halt! Welcome to our fair town, traveler.",
    "I am Captain Marcus, keeper of the peace.",
    "You may enter freely, but mind our laws.",
    "If you need assistance, seek me out.",
    "Safe travels, adventurer!",
)

TOWN_SERVICES = {
    "inn": {
        "name": "Warm Hearth Inn",
        "npc": "Innkeeper Mara",
        "prompt": "SPACE: rest at the inn",
    },
    "shop": {
        "name": "Mooncap Market",
        "npc": "Peddler Nix",
        "prompt": "SPACE: restock potions",
    },
    "blacksmith": {
        "name": "Ironroot Forge",
        "npc": "Borin the Smith",
        "prompt": "SPACE: train gear",
    },
    "library": {
        "name": "Starwell Library",
        "npc": "Archivist Luma",
        "prompt": "SPACE: study lore",
    },
    "town_hall": {
        "name": "Dragonwatch Hall",
        "npc": "Captain Marcus",
        "prompt": "SPACE: ask about bosses",
    },
}

def create_town_guard():
    """Return a fresh town guard NPC record."""
    guard = dict(TOWN_GUARD_TEMPLATE)
    guard["dialogue"] = list(TOWN_GUARD_DIALOGUE)
    return guard
