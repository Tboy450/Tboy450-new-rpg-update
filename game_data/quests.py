"""Town errands and lightweight quest reward data.

Beginner note:
    Town errands are one-time tasks tied to town services. Completing one gives
    small rewards and town reputation.

Reward fields:
    score: points added to the total score.
    exp: experience added to the player.
    reputation: town reputation added to the town tracker.
    items: optional inventory items, keyed by item name.
"""

# Keys should match `TOWN_SERVICES`, `TOWN_INTERIORS`, and building types.
TOWN_ERRANDS = {
    "inn": {
        "title": "Inn Recovery Route",
        "summary": "Confirm the Warm Hearth Inn is ready for healing, rumors, and safe recovery.",
        "reward": {"score": 6, "exp": 18, "reputation": 1, "items": {"health": 1}, "story_items": {"inn_recovery_mark": 1}},
    },
    "shop": {
        "title": "Potion Shop Stock",
        "summary": "Restock both health and mana supplies at the Potion Shop.",
        "reward": {"score": 6, "exp": 16, "reputation": 1, "items": {"health": 1, "mana": 1}, "story_items": {"potion_shop_stamp": 1}},
    },
    "blacksmith": {
        "title": "Blacksmith Gear Check",
        "summary": "Let Borin inspect your class gear and unlock the forge route.",
        "reward": {"score": 10, "exp": 22, "reputation": 1, "story_items": {"forge_due_bill": 1}},
    },
    "library": {
        "title": "Library Lore Filed",
        "summary": "Study Luma's notes and copy the latest dragon pattern into the Log.",
        "reward": {"score": 9, "exp": 24, "reputation": 1, "items": {"mana": 1}, "story_items": {"library_lore_page": 1}},
    },
    "town_hall": {
        "title": "Town Hall Report",
        "summary": "Report to Captain Marcus and review the current dragon threat.",
        "reward": {"score": 12, "exp": 28, "reputation": 2, "equipment": ("guardian_seal",), "story_items": {"town_hall_writ": 1}},
    },
    "house": {
        "title": "Herbal Cottage Stores",
        "summary": "Help Toma sort the recovery herbs before the next monster raid.",
        "reward": {"score": 7, "exp": 16, "reputation": 1, "items": {"health": 1}, "story_items": {"herbal_cottage_bundle": 1}},
    },
    "stall": {
        "title": "Market Stall Supplies",
        "summary": "Visit Meri's stall and keep travelers fed for the next hunt.",
        "reward": {"score": 7, "exp": 16, "reputation": 1, "items": {"health": 1}, "story_items": {"market_stew_token": 1}},
    },
}

def get_town_errand(service_type):
    """Return the town errand tied to a service type.

    Missing services return None, which means there is no errand to complete.
    """
    return TOWN_ERRANDS.get(service_type)

def get_town_errand_count():
    """Return the number of available town errands for journal progress text."""
    return len(TOWN_ERRANDS)
