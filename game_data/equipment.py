"""Equipment item data for weapons, armor, and accessories.

Beginner note:
    Equipment is separate from consumable inventory.

    - Consumables such as health potions live in `mechanics.py`.
    - Story trophies such as the Lion Sage Medallion live in `story.py`.
    - Wearable gear lives here.

    Each equipment record has:

    - slot: weapon, armor, or accessory
    - tier: rough progression order; larger means stronger/later
    - rarity: common, uncommon, rare, epic, or legendary
    - icon: PNG filename inside assets/processed/equipment/
    - bonuses: small STR/DEF/SPD changes used by battle math
"""

EQUIPMENT_SLOT_LABELS = {
    "weapon": "Weapon",
    "armor": "Armor",
    "accessory": "Charm",
}

RARITY_COLORS = {
    "common": (215, 215, 215),
    "uncommon": (120, 220, 140),
    "rare": (110, 180, 255),
    "epic": (205, 130, 255),
    "legendary": (255, 205, 90),
}

EQUIPMENT_ITEMS = {
    "warrior_training_sword": {
        "label": "Training Sword",
        "slot": "weapon",
        "tier": 1,
        "rarity": "common",
        "icon": "warrior_training_sword.png",
        "bonuses": {"strength": 1},
        "description": "A plain blade kept sharp enough for early dragon drills.",
    },
    "mage_training_staff": {
        "label": "Apprentice Staff",
        "slot": "weapon",
        "tier": 1,
        "rarity": "common",
        "icon": "mage_training_staff.png",
        "bonuses": {"strength": 1},
        "description": "A simple focus staff that steadies beginner spellwork.",
    },
    "rogue_training_daggers": {
        "label": "Practice Daggers",
        "slot": "weapon",
        "tier": 1,
        "rarity": "common",
        "icon": "rogue_training_daggers.png",
        "bonuses": {"strength": 1, "speed": 1},
        "description": "Balanced practice blades made for quick hands.",
    },
    "iron_sword": {
        "label": "Iron Sword",
        "slot": "weapon",
        "tier": 2,
        "rarity": "common",
        "icon": "iron_sword.png",
        "bonuses": {"strength": 2},
        "description": "A reliable step above the town training blade.",
    },
    "steel_sword": {
        "label": "Steel Sword",
        "slot": "weapon",
        "tier": 3,
        "rarity": "uncommon",
        "icon": "steel_sword.png",
        "bonuses": {"strength": 4},
        "description": "A sharper sword suited for mid-game dragon patrols.",
    },
    "ember_blade": {
        "label": "Ember Blade",
        "slot": "weapon",
        "tier": 4,
        "rarity": "rare",
        "icon": "ember_blade.png",
        "bonuses": {"strength": 5, "speed": 1},
        "description": "A heated blade that leaves orange light across its cuts.",
    },
    "storm_pike": {
        "label": "Storm Pike",
        "slot": "weapon",
        "tier": 5,
        "rarity": "rare",
        "icon": "storm_pike.png",
        "bonuses": {"strength": 4, "speed": 2},
        "description": "A lightning-tuned polearm planned for storm dragon rewards.",
    },
    "arcane_staff": {
        "label": "Arcane Staff",
        "slot": "weapon",
        "tier": 3,
        "rarity": "uncommon",
        "icon": "arcane_staff.png",
        "bonuses": {"strength": 3, "defense": 1},
        "description": "A better casting focus that also helps hold ground.",
    },
    "starfall_staff": {
        "label": "Starfall Staff",
        "slot": "weapon",
        "tier": 6,
        "rarity": "epic",
        "icon": "starfall_staff.png",
        "bonuses": {"strength": 6, "speed": 2},
        "description": "A late-game staff meant for comet and star dragon rewards.",
    },
    "shadow_daggers": {
        "label": "Shadow Daggers",
        "slot": "weapon",
        "tier": 4,
        "rarity": "rare",
        "icon": "shadow_daggers.png",
        "bonuses": {"strength": 3, "speed": 3},
        "description": "Twin dark blades built for fast repeat strikes.",
    },
    "dragonfang_greatsword": {
        "label": "Dragonfang Greatsword",
        "slot": "weapon",
        "tier": 7,
        "rarity": "legendary",
        "icon": "dragonfang_greatsword.png",
        "bonuses": {"strength": 8, "defense": 2},
        "description": "A future legendary weapon forged from an ancient dragon fang.",
    },
    "warrior_starter_mail": {
        "label": "Starter Mail",
        "slot": "armor",
        "tier": 1,
        "rarity": "common",
        "icon": "warrior_starter_mail.png",
        "bonuses": {"defense": 1},
        "description": "Plain armor issued to warriors leaving town.",
    },
    "mage_starter_robe": {
        "label": "Threaded Robe",
        "slot": "armor",
        "tier": 1,
        "rarity": "common",
        "icon": "mage_starter_robe.png",
        "bonuses": {"defense": 1},
        "description": "A travel robe stitched with light protective thread.",
    },
    "rogue_starter_leathers": {
        "label": "Scout Leathers",
        "slot": "armor",
        "tier": 1,
        "rarity": "common",
        "icon": "rogue_starter_leathers.png",
        "bonuses": {"defense": 1, "speed": 1},
        "description": "Quiet leathers that protect without slowing movement.",
    },
    "iron_mail": {
        "label": "Iron Mail",
        "slot": "armor",
        "tier": 2,
        "rarity": "common",
        "icon": "iron_mail.png",
        "bonuses": {"defense": 3},
        "description": "Simple linked armor for early monster hunts.",
    },
    "ranger_cloak": {
        "label": "Ranger Cloak",
        "slot": "armor",
        "tier": 3,
        "rarity": "uncommon",
        "icon": "ranger_cloak.png",
        "bonuses": {"defense": 2, "speed": 2},
        "description": "Light travel armor for fast movement across plains and forest.",
    },
    "battle_plate": {
        "label": "Battle Plate",
        "slot": "armor",
        "tier": 4,
        "rarity": "rare",
        "icon": "battle_plate.png",
        "bonuses": {"defense": 5, "strength": 1},
        "description": "Heavy protective armor planned for stronger town blacksmith rewards.",
    },
    "sage_mantle": {
        "label": "Sage Mantle",
        "slot": "armor",
        "tier": 5,
        "rarity": "rare",
        "icon": "sage_mantle.png",
        "bonuses": {"defense": 4, "speed": 1},
        "description": "A medical-green mantle suited to healing and survival quests.",
    },
    "shadow_cloak": {
        "label": "Shadow Cloak",
        "slot": "armor",
        "tier": 5,
        "rarity": "epic",
        "icon": "shadow_cloak.png",
        "bonuses": {"defense": 3, "speed": 4},
        "description": "A quick cloak planned for stealth or Ghost Face follow-up rewards.",
    },
    "dragon_scale_plate": {
        "label": "Dragon Scale Plate",
        "slot": "armor",
        "tier": 7,
        "rarity": "legendary",
        "icon": "dragon_scale_plate.png",
        "bonuses": {"defense": 8, "strength": 2},
        "description": "A future endgame armor set made from defeated dragon scales.",
    },
    "lion_sage_charm": {
        "label": "Lion Sage Charm",
        "slot": "accessory",
        "tier": 2,
        "rarity": "rare",
        "icon": "lion_sage_charm.png",
        "bonuses": {"defense": 2},
        "description": "A healer's charm that steadies the wearer under pressure.",
    },
    "mask_shard_edge": {
        "label": "Mask-Shard Edge",
        "slot": "weapon",
        "tier": 3,
        "rarity": "rare",
        "icon": "mask_shard_edge.png",
        "bonuses": {"strength": 3, "speed": 1},
        "description": "A weapon reinforced with a cracked fragment from Ghost Face's mask.",
    },
    "swift_charm": {
        "label": "Swift Charm",
        "slot": "accessory",
        "tier": 3,
        "rarity": "uncommon",
        "icon": "swift_charm.png",
        "bonuses": {"speed": 3},
        "description": "A movement charm for players who want better dodge and escape odds.",
    },
    "guardian_seal": {
        "label": "Guardian Seal",
        "slot": "accessory",
        "tier": 4,
        "rarity": "rare",
        "icon": "guardian_seal.png",
        "bonuses": {"defense": 4},
        "description": "A defensive seal for surviving bosses and stronger story enemies.",
    },
    "drakefang_trophy": {
        "label": "Drakefang Trophy",
        "slot": "accessory",
        "tier": 5,
        "rarity": "epic",
        "icon": "drakefang_trophy.png",
        "bonuses": {"strength": 2, "defense": 2},
        "description": "A planned boss trophy that turns victory into battle power.",
    },
    "ancient_lion_crown": {
        "label": "Ancient Lion Crown",
        "slot": "accessory",
        "tier": 7,
        "rarity": "legendary",
        "icon": "ancient_lion_crown.png",
        "bonuses": {"strength": 3, "defense": 4, "speed": 1},
        "description": "A future legendary relic tied to the Lion Sage questline.",
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


def get_equipment_slot_label(slot):
    """Return a player-facing label for one equipment slot."""
    return EQUIPMENT_SLOT_LABELS.get(slot, slot.title())


def get_equipment_rarity_color(rarity):
    """Return the RGB color used for one rarity name."""
    return RARITY_COLORS.get(rarity, RARITY_COLORS["common"])


def iter_equipment_for_slot(slot):
    """Yield equipment records for one slot in progression order."""
    matches = [
        (item_key, profile)
        for item_key, profile in EQUIPMENT_ITEMS.items()
        if profile.get("slot") == slot
    ]
    matches.sort(key=lambda item: (item[1].get("tier", 0), item[1].get("label", item[0])))
    return matches


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
            sign = "+" if amount > 0 else ""
            parts.append(f"{labels[stat_key]} {sign}{amount}")
    return ", ".join(parts) if parts else "No stat bonus"
