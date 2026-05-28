"""Town errands and lightweight quest reward data."""

TOWN_ERRANDS = {
    "inn": {
        "title": "Warm Beds Ready",
        "summary": "Check the inn and make sure the recovery room is ready.",
        "reward": {"score": 5, "exp": 12, "reputation": 1},
    },
    "shop": {
        "title": "Potion Pouch Stocked",
        "summary": "Visit Mooncap Market and restock the travel pouch.",
        "reward": {"score": 5, "exp": 10, "reputation": 1, "items": {"health": 1}},
    },
    "blacksmith": {
        "title": "Edge And Buckler",
        "summary": "Let Borin inspect your gear before another hunt.",
        "reward": {"score": 8, "exp": 14, "reputation": 1},
    },
    "library": {
        "title": "Dragon Lore Filed",
        "summary": "Study Luma's notes and copy the latest dragon pattern.",
        "reward": {"score": 8, "exp": 16, "reputation": 1, "items": {"mana": 1}},
    },
    "town_hall": {
        "title": "Board Checked",
        "summary": "Report to Captain Marcus and review the current boss threat.",
        "reward": {"score": 10, "exp": 18, "reputation": 2},
    },
    "house": {
        "title": "Cottage Herbs Sorted",
        "summary": "Help Toma check the household herb bundles.",
        "reward": {"score": 6, "exp": 12, "reputation": 1},
    },
    "stall": {
        "title": "Road Stew Shared",
        "summary": "Visit Meri's stall and keep travelers fed.",
        "reward": {"score": 6, "exp": 12, "reputation": 1},
    },
}

def get_town_errand(service_type):
    """Return the town errand tied to a service type."""
    return TOWN_ERRANDS.get(service_type)

def get_town_errand_count():
    """Return the number of available town errands."""
    return len(TOWN_ERRANDS)

