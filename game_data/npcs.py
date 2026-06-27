"""NPC data used by cutscenes and town interactions.

Beginner note:
    This file stores NPC facts and dialogue. It does not draw NPCs. Drawing and
    input handling still happen in `main.py`.

Common fields:
    name: building or service name shown to the player.
    npc: character name used for dialogue.
    prompt: interaction hint shown near the building.
    map_label: short label painted on the outdoor doorway marker.
    role: short service role, such as Recovery or Gear.
    purpose: one sentence explaining why the player should visit.
    first_reward: one sentence describing the first errand reward.
    repeat_use: one sentence describing what this building still does later.
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
        "map_label": "INN",
        "role": "Recovery",
        "purpose": "Full HP/MP rest plus a once-per-level careful-rest bonus.",
        "first_reward": "First errand: EXP, town reputation, a potion, and an inn keepsake.",
        "repeat_use": "Return before bosses or after hard fights to refill HP and MP.",
        "dialogue": (
            "Innkeeper Mara: Rest here before you chase masks, dragons, or bad ideas.",
            "Innkeeper Mara: The Log in your pause menu keeps the town errands straight.",
            "Innkeeper Mara: A careful rest can teach more than a reckless victory.",
        ),
    },
    "shop": {
        "name": "Potion Shop",
        "npc": "Peddler Nix",
        "prompt": "SPACE/ENTER: enter the potion shop",
        "map_label": "POTION",
        "role": "Supplies",
        "purpose": "Restocks health potions and mana tonics for battle.",
        "first_reward": "First errand: EXP, reputation, both potion types, and a shop stamp.",
        "repeat_use": "Return whenever your pouch is low before hunting.",
        "dialogue": (
            "Peddler Nix: Red corks heal wounds. Blue corks wake spellwork. Carry both.",
            "Peddler Nix: Ghost Face punishes empty mana pouches faster than bad aim.",
            "Peddler Nix: Check the Log from the menu if you forget which shop errand is open.",
        ),
    },
    "blacksmith": {
        "name": "Blacksmith",
        "npc": "Borin the Smith",
        "prompt": "SPACE/ENTER: enter the forge",
        "map_label": "FORGE",
        "role": "Gear",
        "purpose": "Creates level-gated weapons, armor, and charms for each class.",
        "first_reward": "First errand: EXP, reputation, and a forge due bill keepsake.",
        "repeat_use": "Return after leveling to unlock more equipment patterns.",
        "dialogue": (
            "Borin the Smith: I forge patterns as your level rises; Inventory decides what you wear.",
            "Borin the Smith: Warrior, Mage, and Rogue gear all sit on different hooks.",
            "Borin the Smith: If the next dragon is too hard, train, return, and check the forge.",
        ),
    },
    "library": {
        "name": "Library",
        "npc": "Archivist Luma",
        "prompt": "SPACE/ENTER: enter the library",
        "map_label": "LORE",
        "role": "Knowledge",
        "purpose": "Explains dragon phases and grants level-based lore insight.",
        "first_reward": "First errand: EXP, reputation, mana, and a copied lore page.",
        "repeat_use": "Return after leveling for another study bonus.",
        "dialogue": (
            "Archivist Luma: The Library turns monster rumors into usable instructions.",
            "Archivist Luma: Wounded dragons change phases. The Log names your current threat.",
            "Archivist Luma: Study before you hunt; experience is cheaper than resurrection.",
        ),
    },
    "town_hall": {
        "name": "Town Hall",
        "npc": "Captain Marcus",
        "prompt": "SPACE/ENTER: enter town hall",
        "map_label": "HALL",
        "role": "Main Quest",
        "purpose": "Reports the current dragon threat and points you toward the next objective.",
        "first_reward": "First errand: bigger EXP, reputation, Guardian Seal gear, and a writ.",
        "repeat_use": "Return when you are unsure which dragon or story target is next.",
        "dialogue": (
            "Captain Marcus: Town Hall keeps the dragon threat clear; your Log keeps it portable.",
            "Captain Marcus: If the next objective feels locked, train outside the walls and return.",
            "Captain Marcus: Malakor waits beyond the lesser dragons. Do not rush that gate.",
        ),
    },
    "house": {
        "name": "Herbal Cottage",
        "npc": "Toma the Gardener",
        "prompt": "SPACE/ENTER: knock on the cottage",
        "map_label": "HERBS",
        "role": "Care",
        "purpose": "Gives a small level-based recovery meal and local warnings.",
        "first_reward": "First errand: EXP, reputation, health potion, and an herb bundle.",
        "repeat_use": "Return after leveling for another cottage meal.",
        "dialogue": (
            "Toma the Gardener: The Herbal Cottage handles small wounds before they become big ones.",
            "Toma the Gardener: I leave herbs near the gate when the roads get bad.",
            "Toma the Gardener: Dragons hate prepared villages more than brave heroes.",
        ),
    },
    "stall": {
        "name": "Market Stall",
        "npc": "Meri the Cook",
        "prompt": "SPACE/ENTER: visit the food stall",
        "map_label": "MARKET",
        "role": "Food",
        "purpose": "Provides repeatable light HP/MP recovery through travel stew.",
        "first_reward": "First errand: EXP, reputation, health potion, and a stew token.",
        "repeat_use": "Return between random fights for a small recovery top-up.",
        "dialogue": (
            "Meri the Cook: Hot stew before cold steel. That is the Market Stall rule.",
            "Meri the Cook: Food is not fancy magic, but it keeps heroes upright.",
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
