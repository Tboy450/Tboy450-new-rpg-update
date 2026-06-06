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
    },
    "Mage": {
        "max_health": 80,
        "max_mana": 120,
        "strength": 8,
        "defense": 6,
        "speed": 8,
    },
    "Rogue": {
        "max_health": 100,
        "max_mana": 70,
        "strength": 12,
        "defense": 8,
        "speed": 12,
    },
}
