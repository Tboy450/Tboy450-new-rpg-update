"""Equipment item data for weapons, armor, and accessories.

Beginner note:
    Equipment is separate from consumable inventory.

    - Consumables such as health potions live in `mechanics.py`.
    - Story trophies such as the Lion Sage Medallion live in `story.py`.
    - Wearable gear lives here.

    Each equipment record has a slot and small stat bonuses. `main.py` reads
    these records when calculating battle damage and when drawing Inventory.
"""

EQUIPMENT_ITEMS = {
    "warrior_training_sword": {
        "label": "Training Sword",
        "slot": "weapon",
        "bonuses": {"strength": 1},
        "description": "A plain blade kept sharp enough for early dragon drills.",
    },
    "mage_training_staff": {
        "label": "Apprentice Staff",
        "slot": "weapon",
        "bonuses": {"strength": 1},
        "description": "A simple focus staff that steadies beginner spellwork.",
    },
    "rogue_training_daggers": {
        "label": "Practice Daggers",
        "slot": "weapon",
        "bonuses": {"strength": 1, "speed": 1},
        "description": "Balanced practice blades made for quick hands.",
    },
    "warrior_starter_mail": {
        "label": "Starter Mail",
        "slot": "armor",
        "bonuses": {"defense": 1},
        "description": "Plain armor issued to warriors leaving town.",
    },
    "mage_starter_robe": {
        "label": "Threaded Robe",
        "slot": "armor",
        "bonuses": {"defense": 1},
        "description": "A travel robe stitched with light protective thread.",
    },
    "rogue_starter_leathers": {
        "label": "Scout Leathers",
        "slot": "armor",
        "bonuses": {"defense": 1, "speed": 1},
        "description": "Quiet leathers that protect without slowing movement.",
    },
    "lion_sage_charm": {
        "label": "Lion Sage Charm",
        "slot": "accessory",
        "bonuses": {"defense": 2},
        "description": "A healer's charm that steadies the wearer under pressure.",
    },
    "mask_shard_edge": {
        "label": "Mask-Shard Edge",
        "slot": "weapon",
        "bonuses": {"strength": 3, "speed": 1},
        "description": "A weapon reinforced with a cracked fragment from Ghost Face's mask.",
    },
}


DEFAULT_EQUIPMENT_BY_CLASS = {
    "Warrior": {
        "weapon": "warrior_training_sword",
        "armor": "warrior_starter_mail",
        "accessory": None,
    },
    "Mage": {
        "weapon": "mage_training_staff",
        "armor": "mage_starter_robe",
        "accessory": None,
    },
    "Rogue": {
        "weapon": "rogue_training_daggers",
        "armor": "rogue_starter_leathers",
        "accessory": None,
    },
}


def get_equipment_item(item_key):
    """Return one equipment record by key, or None if the key is unknown."""
    return EQUIPMENT_ITEMS.get(item_key)


def get_default_equipment(char_type):
    """Return a fresh equipment slot dictionary for one character class."""
    defaults = DEFAULT_EQUIPMENT_BY_CLASS.get(char_type, DEFAULT_EQUIPMENT_BY_CLASS["Rogue"])
    return dict(defaults)


def format_equipment_bonus(bonuses):
    """Return a short player-facing stat bonus string.

    Example:
        {"strength": 3, "speed": 1} becomes "STR +3, SPD +1".
    """
    labels = {
        "strength": "STR",
        "defense": "DEF",
        "speed": "SPD",
    }
    parts = []
    for stat_key in ("strength", "defense", "speed"):
        amount = int(bonuses.get(stat_key, 0))
        if amount:
            parts.append(f"{labels[stat_key]} +{amount}")
    return ", ".join(parts) if parts else "No stat bonus"
