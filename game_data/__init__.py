"""Shared game data for Dragon's Lair RPG."""

from .characters import CHARACTER_CLASS_STATS
from .enemies import AREA_ENEMY_TYPES, DRAGON_BOSS_COLORS, ENEMY_NAME_POOLS
from .interiors import TOWN_INTERIORS
from .mechanics import (
    BATTLE_RULES,
    ELEMENT_PROFILES,
    ITEM_PROFILES,
    ITEM_SPAWN_TABLE,
    get_element_profile,
)
from .npcs import (
    TOWN_GUARD_TEMPLATE,
    TOWN_SERVICES,
    create_town_guard,
    get_town_service_dialogue,
)
from .progression import (
    FINAL_BOSS_LEVEL,
    BOSS_PROGRESSION,
    get_boss_profile,
    get_progression_status,
)
from .world import (
    AREA_DESCRIPTIONS,
    AREA_MECHANICS,
    AREA_PARTICLE_PROFILES,
    WORLD_LAYOUT,
)

__all__ = [
    "AREA_DESCRIPTIONS",
    "AREA_ENEMY_TYPES",
    "AREA_MECHANICS",
    "AREA_PARTICLE_PROFILES",
    "BATTLE_RULES",
    "BOSS_PROGRESSION",
    "CHARACTER_CLASS_STATS",
    "DRAGON_BOSS_COLORS",
    "ELEMENT_PROFILES",
    "ENEMY_NAME_POOLS",
    "FINAL_BOSS_LEVEL",
    "ITEM_PROFILES",
    "ITEM_SPAWN_TABLE",
    "TOWN_GUARD_TEMPLATE",
    "TOWN_INTERIORS",
    "TOWN_SERVICES",
    "WORLD_LAYOUT",
    "create_town_guard",
    "get_town_service_dialogue",
    "get_boss_profile",
    "get_element_profile",
    "get_progression_status",
]
