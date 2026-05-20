"""Shared game data for Dragon's Lair RPG."""

from .characters import CHARACTER_CLASS_STATS
from .enemies import DRAGON_BOSS_COLORS, ENEMY_NAME_POOLS
from .mechanics import (
    BATTLE_RULES,
    ELEMENT_PROFILES,
    ITEM_PROFILES,
    ITEM_SPAWN_TABLE,
    get_element_profile,
)
from .npcs import TOWN_GUARD_TEMPLATE, create_town_guard
from .world import (
    AREA_DESCRIPTIONS,
    AREA_ENEMY_TYPES,
    AREA_PARTICLE_PROFILES,
    WORLD_LAYOUT,
)
