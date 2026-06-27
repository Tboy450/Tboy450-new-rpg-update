"""Outdoor town residents and resident errand data.

Beginner note:
    Building service NPCs live in `npcs.py` because they belong to shops,
    inns, and rooms. This file is for people walking or standing outside in
    town. They make the town feel populated and can give small one-time errands.

Common resident fields:
    name: character name shown in prompts and messages.
    role: short job label.
    local_position: town-screen pixel position, not world-map position.
    color/accent_color: simple drawing colors for the resident sprite.
    lines: normal rotating dialogue before the errand is complete.
    completed_lines: dialogue after the one-time errand is complete.
    quest_key: optional key into TOWN_RESIDENT_ERRANDS.
"""

TOWN_RESIDENTS = {
    "gate_recruit": {
        "name": "Jessa",
        "role": "Gate Recruit",
        "local_position": (382, 322),
        "color": (92, 126, 174),
        "accent_color": (255, 232, 150),
        "prompt": "OK: talk to Jessa",
        "quest_key": "gate_recruit_watch",
        "lines": (
            "Jessa: Captain Marcus says a good patrol starts with watching the road, not swinging first.",
            "Jessa: If you check the gate route with me, I can spare a field potion.",
        ),
        "completed_lines": (
            "Jessa: Gate route is clear for now. I will keep the bell rope close.",
            "Jessa: If wings pass over the wall, I am sending everyone toward the Lion Sage.",
        ),
    },
    "market_runner": {
        "name": "Nella",
        "role": "Market Runner",
        "local_position": (310, 495),
        "color": (110, 86, 178),
        "accent_color": (120, 230, 255),
        "prompt": "OK: talk to Nella",
        "quest_key": "market_runner_supply",
        "lines": (
            "Nella: I carry messages between the market and the inn when the roads get loud.",
            "Nella: Help the town a little and I can show you a charm made for quick feet.",
        ),
        "completed_lines": (
            "Nella: That charm should make dodging and escaping feel less hopeless.",
            "Nella: The market crowd moves fast, but dragon shadows move faster.",
        ),
    },
    "forge_apprentice": {
        "name": "Pip",
        "role": "Forge Apprentice",
        "local_position": (268, 606),
        "color": (158, 92, 52),
        "accent_color": (255, 124, 64),
        "prompt": "OK: talk to Pip",
        "quest_key": "forge_apprentice_coal",
        "lines": (
            "Pip: Borin lets me carry coal, sweep scale dust, and almost touch the good hammer.",
            "Pip: If you finish the forge errand, I can pull a class-fit piece from the ready rack.",
        ),
        "completed_lines": (
            "Pip: That ready-rack piece is yours. Try it in Inventory before the next hunt.",
            "Pip: When Borin says 'almost done,' that means two hours or two sparks from disaster.",
        ),
    },
    "field_medic": {
        "name": "Vale",
        "role": "Field Medic",
        "local_position": (704, 484),
        "color": (48, 142, 132),
        "accent_color": (170, 255, 220),
        "prompt": "OK: talk to Vale",
        "quest_key": "field_medic_kit",
        "lines": (
            "Vale: A good healer checks straps, boots, breath, then bravery. Usually in that order.",
            "Vale: Bring the town together and I will trust you with a guardian seal.",
        ),
        "completed_lines": (
            "Vale: Keep that seal close. It will not make you fearless, but it will help you stand.",
            "Vale: Medicine and armor are the same promise in different shapes.",
        ),
    },
    "map_keeper": {
        "name": "Orrin",
        "role": "Map Keeper",
        "local_position": (650, 594),
        "color": (74, 96, 156),
        "accent_color": (190, 210, 255),
        "prompt": "OK: talk to Orrin",
        "quest_key": "map_keeper_notes",
        "lines": (
            "Orrin: Roads change after monster raids. Maps are arguments with mud.",
            "Orrin: Visit Luma's library, then I can mark a safer route through the plains.",
        ),
        "completed_lines": (
            "Orrin: Your route is marked. The safer road is rarely the shorter one.",
            "Orrin: I have three maps of the same hill and none of them agree.",
        ),
    },
}

TOWN_RESIDENT_ERRANDS = {
    "gate_recruit_watch": {
        "title": "Gate Watch Practice",
        "summary": "Help Jessa check the gate route after Captain Marcus' warning.",
        "reward": {"score": 6, "exp": 18, "reputation": 1, "items": {"health": 1}, "equipment": ("gate_watch_badge",)},
        "complete_message": "{name}: Gate route checked. Take this field potion and my spare badge. ({reward})",
    },
    "market_runner_supply": {
        "title": "Fast Feet Favor",
        "summary": "Earn enough trust for Nella to share a speed charm from the market.",
        "min_reputation": 1,
        "reward": {"score": 8, "exp": 22, "reputation": 1, "equipment": ("swift_charm",)},
        "locked_message": "{name}: Help one town errand first. I do not hand charms to strangers.",
        "complete_message": "{name}: You move like someone who listens. Take this Swift Charm. ({reward})",
    },
    "forge_apprentice_coal": {
        "title": "Ready Rack Gear",
        "summary": "Finish the forge errand so Pip can hand over class-fit practice gear.",
        "requires_completed_errands": ("blacksmith",),
        "reward": {
            "score": 8,
            "exp": 24,
            "reputation": 1,
            "equipment_by_class": {
                "Warrior": ("iron_sword",),
                "Mage": ("arcane_staff",),
                "Rogue": ("ranger_cloak",),
            },
        },
        "locked_message": "{name}: Borin has to approve the forge errand before I can open the ready rack.",
        "complete_message": "{name}: Ready-rack gear cleared by Borin. Try it from Inventory. ({reward})",
    },
    "field_medic_kit": {
        "title": "Medic's Trust",
        "summary": "Show Vale the town is recovering before she gives out a defensive seal.",
        "min_reputation": 3,
        "requires_completed_errands": ("inn", "house"),
        "reward": {"score": 12, "exp": 30, "reputation": 1, "items": {"mana": 1}, "equipment": ("medic_triage_band",)},
        "locked_message": "{name}: Check the inn and cottage first. Healing starts where people sleep.",
        "complete_message": "{name}: You have done real care work. Wear this triage band. ({reward})",
    },
    "map_keeper_notes": {
        "title": "Safer Route Notes",
        "summary": "Study at the library, then help Orrin update the plains route notes.",
        "requires_completed_errands": ("library",),
        "reward": {"score": 9, "exp": 26, "reputation": 1, "items": {"mana": 1}, "equipment": ("cartographer_compass",)},
        "locked_message": "{name}: Bring me a library note first. A route without records is just a guess.",
        "complete_message": "{name}: Route notes updated. Carry this compass when the plains look wrong. ({reward})",
    },
}


def iter_town_residents():
    """Yield resident key/profile pairs in stable drawing order."""
    return TOWN_RESIDENTS.items()


def get_town_resident(resident_key):
    """Return one outdoor town resident profile."""
    return TOWN_RESIDENTS.get(resident_key)


def get_town_resident_quest(resident):
    """Return the one-time errand attached to a resident profile."""
    if not resident:
        return None
    quest_key = resident.get("quest_key")
    return TOWN_RESIDENT_ERRANDS.get(quest_key)


def is_town_resident_quest_available(quest, reputation, completed_errands):
    """Return whether a resident errand can complete right now.

    The second return value is a short reason for beginner-facing messages.
    """
    if not quest:
        return False, "No errand."
    min_reputation = int(quest.get("min_reputation", 0))
    if reputation < min_reputation:
        return False, f"Need town rep {min_reputation}."
    missing = [
        key
        for key in quest.get("requires_completed_errands", ())
        if key not in completed_errands
    ]
    if missing:
        return False, "Finish nearby town errands first."
    return True, "Ready."


def get_next_town_resident_errand_status(reputation, completed_errands, completed_resident_errands):
    """Return the next unfinished resident errand and whether it is ready.

    Beginner note:
        The Log needs a short "what should I do next?" line for town residents.
        This helper keeps that decision beside the resident data and reuses the
        same lock rules as talking to the resident in `main.py`.
    """
    completed_errands = set(completed_errands or ())
    completed_resident_errands = set(completed_resident_errands or ())

    for resident_key, resident in TOWN_RESIDENTS.items():
        quest_key = resident.get("quest_key")
        if not quest_key or quest_key in completed_resident_errands:
            continue
        quest = TOWN_RESIDENT_ERRANDS.get(quest_key)
        if not quest:
            continue

        available, reason = is_town_resident_quest_available(
            quest,
            reputation,
            completed_errands,
        )
        return {
            "resident_key": resident_key,
            "resident": resident["name"],
            "role": resident["role"],
            "quest_key": quest_key,
            "title": quest["title"],
            "summary": quest.get("summary", ""),
            "status": "READY" if available else reason,
            "available": available,
        }

    return None


def get_town_resident_errand_count():
    """Return the number of outdoor resident errands."""
    return len(TOWN_RESIDENT_ERRANDS)
