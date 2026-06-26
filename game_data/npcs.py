"""NPC data used by cutscenes and town interactions.

Beginner note:
    This file stores NPC facts and dialogue. It does not draw NPCs. Drawing and
    input handling still happen in `main.py`.

Common fields:
    name: building or service name shown to the player.
    npc: character name used for dialogue.
    prompt: interaction hint shown near the building.
    dialogue: lines rotated when the player talks to the NPC.
"""

# Template copied when the town guard is created. The copy prevents one game's
# animation/dialogue timers from mutating this shared default record.
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

# Cutscene lines for the guard at the town entrance.
TOWN_GUARD_DIALOGUE = (
    "Halt! Welcome to our fair town, traveler.",
    "I am Captain Marcus, keeper of the peace.",
    "You may enter freely, but mind our laws.",
    "If you need assistance, seek me out.",
    "Safe travels, adventurer!",
)

# Keys here must match outdoor building `type` values in `town.py`.
TOWN_SERVICES = {
    "inn": {
        "name": "Warm Hearth Inn",
        "npc": "Innkeeper Mara",
        "prompt": "SPACE/ENTER: enter the inn",
        "dialogue": (
            "Innkeeper Mara: Keep your boots by the hearth and your sword within reach.",
            "Innkeeper Mara: Monsters have grown bolder since the dragons began circling.",
            "Innkeeper Mara: Rest before a boss hunt; pride does not refill mana.",
        ),
    },
    "shop": {
        "name": "Potion Shop",
        "npc": "Peddler Nix",
        "prompt": "SPACE/ENTER: enter the potion shop",
        "dialogue": (
            "Peddler Nix: Red corks heal wounds, blue corks wake the spellwork.",
            "Peddler Nix: I only sell what fits in a battle pouch. No barrels.",
            "Peddler Nix: Bring back dragon scales someday and I will name a shelf after you.",
        ),
    },
    "blacksmith": {
        "name": "Ironroot Forge",
        "npc": "Borin the Smith",
        "prompt": "SPACE/ENTER: enter the forge",
        "dialogue": (
            "Borin the Smith: I can forge better sets as your level rises.",
            "Borin the Smith: I hand you the gear; you decide what to equip from Inventory.",
            "Borin the Smith: Dragon hide hates clean strikes and loves hesitation.",
        ),
    },
    "library": {
        "name": "Starwell Library",
        "npc": "Archivist Luma",
        "prompt": "SPACE/ENTER: enter the library",
        "dialogue": (
            "Archivist Luma: The old maps mark lairs by weather, not by roads.",
            "Archivist Luma: Each dragon repeats a pattern once wounded. Watch the phase shift.",
            "Archivist Luma: Study before you hunt; experience is cheaper than resurrection.",
        ),
    },
    "town_hall": {
        "name": "Dragonwatch Hall",
        "npc": "Captain Marcus",
        "prompt": "SPACE/ENTER: enter town hall",
        "dialogue": (
            "Captain Marcus: The board tracks sightings, but your level decides when they strike.",
            "Captain Marcus: If the town is quiet, train outside the walls and come back prepared.",
            "Captain Marcus: Malakor waits beyond the lesser dragons. Do not rush that gate.",
        ),
    },
    "house": {
        "name": "Mossroof Cottage",
        "npc": "Toma the Gardener",
        "prompt": "SPACE/ENTER: knock on the cottage",
        "dialogue": (
            "Toma the Gardener: The safest paths are not always the cleanest ones.",
            "Toma the Gardener: I leave herbs near the gate when the roads get bad.",
            "Toma the Gardener: Dragons hate prepared villages more than brave heroes.",
        ),
    },
    "stall": {
        "name": "Food Stall",
        "npc": "Meri the Cook",
        "prompt": "SPACE/ENTER: visit the food stall",
        "dialogue": (
            "Meri the Cook: Hot stew before cold steel. That is my rule.",
            "Meri the Cook: Adventurers fight better when they stop skipping meals.",
            "Meri the Cook: If you hear wings, get under stone before you look up.",
        ),
    },
}

def create_town_guard():
    """Return a fresh town guard NPC record.

    `dict(...)` and `list(...)` make mutable copies for the active game.
    """
    guard = dict(TOWN_GUARD_TEMPLATE)
    guard["dialogue"] = list(TOWN_GUARD_DIALOGUE)
    return guard

def get_town_service_dialogue(service_type):
    """Return rotating NPC dialogue for a town service.

    Missing service keys return an empty tuple, which lets callers fail safely.
    """
    service = TOWN_SERVICES.get(service_type, {})
    return service.get("dialogue", ())
