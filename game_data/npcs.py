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

def create_town_guard():
    """Return a fresh town guard NPC record."""
    guard = dict(TOWN_GUARD_TEMPLATE)
    guard["dialogue"] = list(TOWN_GUARD_DIALOGUE)
    return guard

