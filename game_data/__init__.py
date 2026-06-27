"""Shared game data exports for Dragon's Lair RPG.

Beginner note:
    `main.py` imports from `game_data` instead of importing each small data file
    directly. This file is the compatibility doorway for the data layer.

    If data moves between modules later, we can update this file and keep most
    of `main.py` unchanged. That makes the project safer to refactor.
"""

# Playable character starting data.
from .characters import CHARACTER_CLASS_STATS

# Enemy spawn pools, generated names, and dragon palette data.
from .enemies import AREA_ENEMY_TYPES, DRAGON_BOSS_COLORS, ENEMY_NAME_POOLS

# Weapons, armor, accessories, and starting gear.
from .equipment import (
    BLACKSMITH_GEAR_REWARDS,
    DEFAULT_EQUIPMENT_BY_CLASS,
    EQUIPMENT_ITEMS,
    EQUIPMENT_SLOT_LABELS,
    EQUIPMENT_STAT_LABELS,
    EQUIPMENT_STAT_ORDER,
    RARITY_COLORS,
    format_equipment_delta,
    format_equipment_bonus,
    get_available_blacksmith_rewards,
    get_default_equipment,
    get_equipment_bonuses,
    get_equipment_item,
    get_equipment_power,
    get_equipment_rarity_color,
    get_equipment_slot_label,
    get_next_blacksmith_unlock,
    iter_equipment_for_slot,
)

# Town building room layouts.
from .interiors import TOWN_INTERIORS

# Reusable combat, pickup, and elemental tuning.
from .mechanics import (
    BATTLE_RULES,
    ELEMENT_PROFILES,
    ITEM_PROFILES,
    ITEM_SPAWN_TABLE,
    get_element_profile,
)

# Town NPCs and service dialogue.
from .npcs import (
    TOWN_GUARD_TEMPLATE,
    TOWN_SERVICES,
    create_town_guard,
    get_town_service_dialogue,
)

# Boss and main quest progression.
from .progression import (
    FINAL_BOSS_LEVEL,
    BOSS_PROGRESSION,
    get_boss_profile,
    get_progression_status,
)

# Lightweight town errands and rewards.
from .quests import TOWN_ERRANDS, get_town_errand, get_town_errand_count

# Main story NPCs and one-shot area dialogue.
from .story import (
    OPENING_STORY_LINES,
    STORY_AREA_DIALOGUES,
    STORY_ENEMY_REWARDS,
    STORY_NPCS,
    STORY_REWARD_ITEMS,
    TOWN_GUARD_STORY_LINES,
    get_story_dialogue,
    get_story_dialogues_for_area,
    get_story_enemy_reward,
    get_story_npcs_for_area,
    get_story_reward_item,
)

# Outdoor town layout data.
from .town import (
    TOWN_BOUNDARIES,
    TOWN_BUILDINGS,
    TOWN_DECORATIONS,
    TOWN_SMOKE_SOURCES,
    clone_town_layout,
)

# Outdoor town population and resident errands.
from .town_population import (
    TOWN_RESIDENTS,
    TOWN_RESIDENT_ERRANDS,
    get_next_town_resident_errand_status,
    get_town_resident,
    get_town_resident_errand_count,
    get_town_resident_quest,
    is_town_resident_quest_available,
    iter_town_residents,
)

# World map layout, area visuals, particles, and environmental effects.
from .world import (
    AREA_DESCRIPTIONS,
    AREA_MECHANICS,
    AREA_PARTICLE_PROFILES,
    AREA_VISUALS,
    WORLD_LAYOUT,
)

# `__all__` lists the names that are intentionally public from this package.
__all__ = [
    "AREA_DESCRIPTIONS",
    "AREA_ENEMY_TYPES",
    "AREA_MECHANICS",
    "AREA_PARTICLE_PROFILES",
    "AREA_VISUALS",
    "BATTLE_RULES",
    "BOSS_PROGRESSION",
    "BLACKSMITH_GEAR_REWARDS",
    "CHARACTER_CLASS_STATS",
    "DRAGON_BOSS_COLORS",
    "ELEMENT_PROFILES",
    "ENEMY_NAME_POOLS",
    "DEFAULT_EQUIPMENT_BY_CLASS",
    "EQUIPMENT_ITEMS",
    "EQUIPMENT_SLOT_LABELS",
    "EQUIPMENT_STAT_LABELS",
    "EQUIPMENT_STAT_ORDER",
    "FINAL_BOSS_LEVEL",
    "ITEM_PROFILES",
    "ITEM_SPAWN_TABLE",
    "OPENING_STORY_LINES",
    "RARITY_COLORS",
    "STORY_AREA_DIALOGUES",
    "STORY_ENEMY_REWARDS",
    "STORY_NPCS",
    "STORY_REWARD_ITEMS",
    "TOWN_GUARD_TEMPLATE",
    "TOWN_GUARD_STORY_LINES",
    "TOWN_INTERIORS",
    "TOWN_ERRANDS",
    "TOWN_BOUNDARIES",
    "TOWN_BUILDINGS",
    "TOWN_DECORATIONS",
    "TOWN_RESIDENTS",
    "TOWN_RESIDENT_ERRANDS",
    "TOWN_SERVICES",
    "TOWN_SMOKE_SOURCES",
    "WORLD_LAYOUT",
    "clone_town_layout",
    "create_town_guard",
    "format_equipment_bonus",
    "format_equipment_delta",
    "get_story_dialogue",
    "get_story_dialogues_for_area",
    "get_story_enemy_reward",
    "get_story_npcs_for_area",
    "get_story_reward_item",
    "get_town_service_dialogue",
    "get_boss_profile",
    "get_element_profile",
    "get_available_blacksmith_rewards",
    "get_default_equipment",
    "get_equipment_bonuses",
    "get_equipment_item",
    "get_equipment_power",
    "get_equipment_rarity_color",
    "get_equipment_slot_label",
    "get_next_blacksmith_unlock",
    "get_progression_status",
    "get_town_errand",
    "get_town_errand_count",
    "get_next_town_resident_errand_status",
    "get_town_resident",
    "get_town_resident_errand_count",
    "get_town_resident_quest",
    "is_town_resident_quest_available",
    "iter_equipment_for_slot",
    "iter_town_residents",
]
