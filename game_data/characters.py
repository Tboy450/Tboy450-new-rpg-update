"""Player character class stats.

Beginner note:
    Each key in `CHARACTER_CLASS_STATS` is a class name shown to the player.
    Each value is a dictionary of starting stats copied into `Character` in
    `main.py`.

Field meanings:
    max_health: highest HP the character can have.
    max_mana: highest MP the character can have.
    strength: improves physical attack damage.
    defense: reduces incoming damage.
    speed: improves dodge, escape, and some battle timing.
    role: short class identity text shown in the Log and battle start.
    battle_style: one sentence explaining how this class now plays.
    basic_attack: the name used for the ATTACK command in battle messages.
    magic_attack: the name used for the MAGIC command in battle messages.
"""

# Add a new playable class here first, then add a matching select button in
# `Game.__init__` and character select drawing/input in `main.py`.
CHARACTER_CLASS_STATS = {
    "Warrior": {
        "max_health": 120,
        "max_mana": 50,
        "strength": 15,
        "defense": 10,
        "speed": 7,
        "role": "Frontline Guard",
        "battle_style": "Hits hard, then braces to reduce the next enemy hit.",
        "basic_attack": "Guard Break",
        "magic_attack": "Rune Spark",
    },
    "Mage": {
        "max_health": 80,
        "max_mana": 120,
        "strength": 8,
        "defense": 6,
        "speed": 8,
        "role": "Arcane Burst",
        "battle_style": "Builds MP with Firebolt and spends it on stronger spell damage.",
        "basic_attack": "Firebolt",
        "magic_attack": "Fireball",
    },
    "Rogue": {
        "max_health": 100,
        "max_mana": 70,
        "strength": 12,
        "defense": 8,
        "speed": 12,
        "role": "Quick Striker",
        "battle_style": "Uses speed for dodge, escape, and possible second hits.",
        "basic_attack": "Twin Throw",
        "magic_attack": "Smoke Flash",
    },
}


def get_character_class_profile(char_type):
    """Return class stats and beginner-facing identity text.

    Beginner note:
        This helper keeps battle and Log code from reaching directly into
        `CHARACTER_CLASS_STATS`. If an unknown class name appears, Rogue is the
        fallback because it already was the safe default in `Character`.
    """
    return CHARACTER_CLASS_STATS.get(char_type, CHARACTER_CLASS_STATS["Rogue"])
