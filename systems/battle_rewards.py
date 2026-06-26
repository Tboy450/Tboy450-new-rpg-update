"""Battle reward helpers.

Beginner note:
    Reward math is gameplay logic, so it belongs in `systems/` instead of being
    buried in the game loop. These helpers return plain dictionaries because
    `Game` still owns applying EXP, score, potions, and story state.
"""


def get_regular_enemy_reward(enemy):
    """Return scaled EXP/score for a normal non-story enemy.

    The old battle reward was a flat 25 EXP / 10 score. That made stronger
    monsters feel the same as weak ones. This formula uses enemy health,
    strength, and speed so tougher fights pay better without needing every
    random enemy to have its own reward table.
    """
    max_health = int(getattr(enemy, "max_health", getattr(enemy, "health", 25)))
    strength = int(getattr(enemy, "strength", 6))
    speed = int(getattr(enemy, "speed", 3))
    exp = max(30, 18 + max_health // 5 + strength * 2 + speed)
    score = max(10, 6 + strength + speed)
    return {
        "exp": exp,
        "score": score,
        "message": f"Battle reward: {exp} EXP, {score} score.",
    }


def get_boss_reward(enemy):
    """Return boss rewards with a safe fallback if older boss fields are absent."""
    # `getattr(object, "field", fallback)` means:
    # "use object.field if it exists; otherwise use this default value."
    # That keeps older or experimental boss classes from crashing the reward
    # screen when they do not define every newer reward field.
    boss_level = int(getattr(enemy, "boss_level", 1))
    exp = int(getattr(enemy, "exp_reward", 105 + boss_level * 35))
    score = int(getattr(enemy, "score_reward", 40 + boss_level * 15))
    return {
        "exp": exp,
        "score": score,
        "message": f"Boss reward: {exp} EXP, {score} score, potions restocked.",
    }
