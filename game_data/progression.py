"""Boss and quest progression data."""

FINAL_BOSS_LEVEL = 10

BOSS_PROGRESSION = {
    2: {
        "name": "Ashwing Drake",
        "title": "First Dragon Sign",
        "hint": "A young drake tests hunters beyond the safety of town.",
        "area_hint": "wild areas",
    },
    3: {
        "name": "Frostbite Wyrm",
        "title": "Cold Trail",
        "hint": "Ice marks and broken pine branches point toward a stronger wyrm.",
        "area_hint": "ice, mountain, or forest",
    },
    4: {
        "name": "Cindermaw Drake",
        "title": "Scorched Crossing",
        "hint": "Fresh ash means a fire-breather has begun hunting travelers.",
        "area_hint": "volcano, desert, or mountain",
    },
    5: {
        "name": "Nightcoil Dragon",
        "title": "Shadow Flight",
        "hint": "A shadow dragon circles the roads after sunset.",
        "area_hint": "swamp, cave, or forest",
    },
    6: {
        "name": "Stormscale Drake",
        "title": "Broken Skies",
        "hint": "Thunder rolls over the lair roads when this drake is near.",
        "area_hint": "mountain or beach",
    },
    7: {
        "name": "Graveflame Dragon",
        "title": "Deadfire Omen",
        "hint": "Old battlefields glow when Graveflame wakes.",
        "area_hint": "cave, swamp, or volcano",
    },
    8: {
        "name": "Starfall Wyrm",
        "title": "Falling Star",
        "hint": "A comet-bright wyrm hunts heroes carrying too much fame.",
        "area_hint": "any wild area",
    },
    9: {
        "name": "Dreadhorn Ancient",
        "title": "Last Gate",
        "hint": "Only one ancient guardian stands between you and Malakor.",
        "area_hint": "any wild area",
    },
    FINAL_BOSS_LEVEL: {
        "name": "Malakor, the Dragon",
        "title": "Final Hunt",
        "hint": "The elder dragon waits for a hero strong enough to end the siege.",
        "area_hint": "any wild area",
    },
}


def get_boss_profile(level):
    """Return boss naming and hint data for a level."""
    if level >= FINAL_BOSS_LEVEL:
        return BOSS_PROGRESSION[FINAL_BOSS_LEVEL]
    return BOSS_PROGRESSION.get(
        level,
        {
            "name": f"Dragon Boss Lv.{level}",
            "title": "Uncharted Hunt",
            "hint": "A roaming dragon has marked this level of power.",
            "area_hint": "any wild area",
        },
    )


def get_next_boss_level(player_level, last_boss_level):
    """Return the level of the next boss-relevant objective."""
    if player_level >= FINAL_BOSS_LEVEL and last_boss_level < FINAL_BOSS_LEVEL:
        return FINAL_BOSS_LEVEL
    if player_level > 1 and player_level > last_boss_level:
        return min(player_level, FINAL_BOSS_LEVEL)
    return min(FINAL_BOSS_LEVEL, max(2, player_level + 1))


def get_progression_status(player_level, last_boss_level, boss_cooldown, final_boss_defeated):
    """Build player-facing quest status text for HUDs and town hall."""
    if final_boss_defeated:
        return {
            "state": "complete",
            "color": (255, 230, 110),
            "title": "Dragon Siege Broken",
            "short": "QUEST COMPLETE: Malakor defeated",
            "lines": (
                "Malakor has fallen.",
                "The town can rebuild without dragonfire overhead.",
                "Optional: keep hunting to perfect your build.",
            ),
        }

    next_level = get_next_boss_level(player_level, last_boss_level)
    profile = get_boss_profile(next_level)
    boss_ready = player_level > 1 and player_level > last_boss_level and not boss_cooldown

    if boss_cooldown:
        return {
            "state": "recovering",
            "color": (180, 210, 255),
            "title": "Recover And Train",
            "short": "QUEST: gain a level to clear boss pressure",
            "lines": (
                "The last dragon clash left the trail unstable.",
                "Gain another level before forcing the next boss encounter.",
                f"Next known threat: {profile['name']} at level {next_level}.",
            ),
        }

    if boss_ready:
        return {
            "state": "ready",
            "color": (255, 150, 80),
            "title": profile["title"],
            "short": f"QUEST: {profile['name']} is hunting you",
            "lines": (
                f"Target: {profile['name']}",
                profile["hint"],
                f"Leave town and enter {profile['area_hint']} to trigger the fight.",
            ),
        }

    return {
        "state": "training",
        "color": (150, 230, 150),
        "title": "Build Strength",
        "short": f"QUEST: train for {profile['name']} at level {next_level}",
        "lines": (
            f"Next target: {profile['name']}",
            f"Reach level {next_level} by fighting monsters and collecting supplies.",
            "Use town services between hunts to prepare safely.",
        ),
    }
