"""Reusable town-service mechanics for building interiors.

Beginner note:
    `main.py` still decides when a player presses OK/USE inside a building.
    This module owns what the Inn and Blacksmith *do* once activated.

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


INN_REST_CLAIM_PREFIX = "inn_rest_level"
INN_REST_EXP_BASE = 6
INN_REST_EXP_PER_LEVEL = 4


def _join_parts(parts):
    """Return a readable comma-separated list without empty pieces."""
    return ", ".join(part for part in parts if part)


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
    forge_rewards = get_available_blacksmith_rewards(
        player.type,
        player.level,
        player.owned_equipment,
        limit=limit,
    )
    if forge_rewards:
        forged_parts = []
        for equipment_key in forge_rewards:
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
    """Return short wall-card lines for important service rooms."""
    if service_type == "inn":
        claim_key = (INN_REST_CLAIM_PREFIX, player.level)
        bonus_status = "claimed" if claim_key in player.town_service_claims else "ready"
        return (
            "Restores HP and MP",
            f"Level {player.level} rest bonus: {bonus_status}",
            "Bonus includes EXP and supplies",
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

    return ()
