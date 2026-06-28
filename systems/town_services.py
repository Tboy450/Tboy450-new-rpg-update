"""Reusable town-service mechanics for building interiors.

Beginner note:
    `main.py` still decides when a player presses OK/USE inside a building.
    This module owns what town services *do* once activated and how their
    shared labels are described by UI helpers.

    Keeping service effects here makes it easier to grow town mechanics later
    without turning `Game.apply_town_service()` into a huge pile of special
    cases. A future inn mini-game can plug into this same area.
"""

from game_data.equipment import (
    get_available_blacksmith_rewards,
    get_equipment_item,
    get_equipment_slot_label,
    get_next_blacksmith_unlock,
)
from game_data.npcs import TOWN_SERVICES


INN_REST_CLAIM_PREFIX = "inn_rest_level"
INN_REST_EXP_BASE = 6
INN_REST_EXP_PER_LEVEL = 4

# Short button labels for the active service command inside each building.
# Beginner note:
#     The same interior menu can serve every building because this table names
#     the first button by service type. Add a new key here when a new town
#     building gets a custom action.
SERVICE_ACTION_LABELS = {
    "inn": "REST",
    "shop": "RESTOCK",
    "blacksmith": "FORGE",
    "library": "STUDY",
    "town_hall": "REPORT",
    "house": "MEAL",
    "stall": "STEW",
}


def _join_parts(parts):
    """Return a readable comma-separated list without empty pieces."""
    return ", ".join(part for part in parts if part)


def get_service_profile(service_type):
    """Return one town service record, or an empty record if missing.

    Beginner note:
        Town service facts live in `game_data/npcs.py`. This wrapper keeps UI
        files from reaching into that table directly every time they need a
        label, purpose, or reward hint.
    """
    return TOWN_SERVICES.get(service_type, {})


def get_service_map_label(service_type):
    """Return the short all-caps label used on outdoor doorway markers."""
    service = get_service_profile(service_type)
    return service.get("map_label") or service.get("name", service_type).split()[0].upper()


def get_service_completion_label(service_type, completed_town_errands):
    """Return OPEN or DONE for a building's one-time errand state."""
    return "DONE" if service_type in completed_town_errands else "OPEN"


def get_service_action_label(service_type):
    """Return the service-menu verb for one town building."""
    return SERVICE_ACTION_LABELS.get(service_type, "USE")


def get_service_overview_lines(service_type):
    """Return role/purpose/reward text shared by Log and interior service cards."""
    service = get_service_profile(service_type)
    if not service:
        return ()
    return (
        f"Role: {service.get('role', 'Town Service')}",
        service.get("purpose", "Town service."),
        service.get("first_reward", "First visit grants a small errand reward."),
        service.get("repeat_use", "Return later for more help."),
    )


def apply_inn_rest_service(player, npc_name):
    """Restore HP/MP and grant a small once-per-level rest bonus.

    Beginner note:
        Full healing can happen every time. The extra EXP/supply bonus happens
        once per player level and is saved through `player.town_service_claims`.
        That gives the inn a small progression purpose without making it a
        repeatable infinite reward.
    """
    restored_health = max(0, player.max_health - player.health)
    restored_mana = max(0, player.max_mana - player.mana)
    player.health = player.max_health
    player.mana = player.max_mana

    if restored_health or restored_mana:
        message = f"{npc_name}: Restored {restored_health} HP and {restored_mana} MP."
    else:
        message = f"{npc_name}: You already look rested."

    # This tuple is saved in `player.town_service_claims`. Using the level in
    # the key means the Inn can give one bonus at level 2, another at level 3,
    # and so on, while still allowing normal HP/MP rest every visit.
    claim_key = (INN_REST_CLAIM_PREFIX, player.level)
    if claim_key in player.town_service_claims:
        return f"{message} Rest bonus for level {player.level} is already claimed."

    player.town_service_claims.add(claim_key)
    exp_gain = INN_REST_EXP_BASE + player.level * INN_REST_EXP_PER_LEVEL
    player.gain_exp(exp_gain)

    supply_parts = [f"{exp_gain} EXP"]
    health_added = player.add_inventory_item("health", 1)
    mana_added = player.add_inventory_item("mana", 1 if player.level >= 2 else 0)
    if health_added:
        supply_parts.append(f"health potion x{health_added}")
    if mana_added:
        supply_parts.append(f"mana tonic x{mana_added}")

    return f"{message} First careful rest this level: {_join_parts(supply_parts)}."


def apply_blacksmith_forge_service(player, npc_name, limit=3):
    """Grant level-gated forge gear and return one readable result message."""
    # The equipment table decides which patterns are unlocked for the player's
    # class and level. This service only grants the next missing items.
    forge_rewards = get_available_blacksmith_rewards(
        player.type,
        player.level,
        player.owned_equipment,
        limit=limit,
    )
    if forge_rewards:
        forged_parts = []
        for equipment_key in forge_rewards:
            # Do not auto-equip forge rewards. Sending them to Inventory keeps
            # player choice clear and avoids replacing a favorite rare item.
            if not player.add_equipment_item(equipment_key, auto_equip=False):
                continue
            profile = get_equipment_item(equipment_key) or {}
            slot_label = get_equipment_slot_label(profile.get("slot", "gear"))
            rarity = profile.get("rarity", "common").title()
            forged_parts.append(f"{profile.get('label', equipment_key)} [{slot_label}, {rarity}]")

        if forged_parts:
            return (
                f"{npc_name}: Forged {_join_parts(forged_parts)}. "
                "Open Inventory to equip what fits your build."
            )
        return f"{npc_name}: I could not finish that forge order."

    next_unlock = get_next_blacksmith_unlock(player.level)
    if next_unlock:
        levels_needed = max(1, int(next_unlock["level"]) - int(player.level))
        return (
            f"{npc_name}: No new patterns yet. {next_unlock['label']} unlocks at "
            f"level {next_unlock['level']} ({levels_needed} level"
            f"{'' if levels_needed == 1 else 's'} away)."
        )

    return f"{npc_name}: You own every forge pattern I can make right now."


def get_service_hint_lines(service_type, player):
    """Return short wall-card lines for important service rooms.

    Beginner note:
        These lines describe the live state of the service, such as whether a
        once-per-level bonus is ready. Static purpose text comes from
        `get_service_overview_lines()` above.
    """
    if service_type == "inn":
        claim_key = (INN_REST_CLAIM_PREFIX, player.level)
        bonus_status = "claimed" if claim_key in player.town_service_claims else "ready"
        return (
            "Restores HP and MP",
            f"Level {player.level} rest bonus: {bonus_status}",
            "Bonus includes EXP and supplies",
        )

    if service_type == "shop":
        return (
            f"Health potions: {player.get_inventory_count('health')}",
            f"Mana tonics: {player.get_inventory_count('mana')}",
            "Restocks both pouch types",
        )

    if service_type == "blacksmith":
        available = get_available_blacksmith_rewards(
            player.type,
            player.level,
            player.owned_equipment,
            limit=3,
        )
        if available:
            return (
                f"Forge-ready patterns: {len(available)}",
                "Rewards go to Inventory",
                "Equip or unequip gear from the menu",
            )
        next_unlock = get_next_blacksmith_unlock(player.level)
        if next_unlock:
            return (
                "No new patterns yet",
                f"Next: {next_unlock['label']}",
                f"Unlock level: {next_unlock['level']}",
            )
        return (
            "All forge patterns owned",
            "Inventory controls loadout",
            "Later bosses can add rare patterns",
        )

    if service_type == "library":
        claim_key = ("library", player.level)
        status = "studied" if claim_key in player.town_service_claims else "ready"
        return (
            "Dragon phase notes",
            f"Level {player.level} lore insight: {status}",
            "Use Log for objective review",
        )

    if service_type == "town_hall":
        return (
            "Dragon status command",
            "Town errands feed the Log",
            "Seal reward on first report",
        )

    if service_type == "house":
        claim_key = ("house", player.level)
        status = "claimed" if claim_key in player.town_service_claims else "ready"
        return (
            "Herbs and light recovery",
            f"Level {player.level} cottage meal: {status}",
            "Good before short hunts",
        )

    if service_type == "stall":
        return (
            "Quick travel stew",
            "Repeatable small recovery",
            "Good between random fights",
        )

    return ()
