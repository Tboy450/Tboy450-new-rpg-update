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

from .equipment import get_equipment_item
from .mechanics import ITEM_PROFILES
from .story import get_story_reward_item

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


def _append_reward_part(parts, label, amount=None):
    """Append one short reward phrase if it has useful text.

    Beginner note:
        Reward previews need to be compact because they are shown inside small
        phone-sized panels. This helper keeps the repeated "add if present"
        code readable.
    """
    if not label:
        return
    if amount is None:
        parts.append(str(label))
    else:
        parts.append(f"{label} x{amount}")


def format_town_reward_preview(reward, player_type=None, max_parts=5):
    """Return a compact preview string for a town or resident reward.

    Args:
        reward: reward dictionary from `TOWN_ERRANDS` or resident quests.
        player_type: optional class name used for class-specific gear previews.
        max_parts: maximum number of reward chunks to show before "+more".

    Beginner note:
        This does not grant anything. It only turns reward data into a readable
        line for the Log, interior service menu, or future quest boards.
    """
    if not reward:
        return "Reward: none listed"

    parts = []
    if reward.get("exp"):
        _append_reward_part(parts, f"{reward['exp']} EXP")
    if reward.get("score"):
        _append_reward_part(parts, f"{reward['score']} score")
    if reward.get("reputation"):
        _append_reward_part(parts, f"+{reward['reputation']} town rep")

    for item_type, amount in reward.get("items", {}).items():
        profile = ITEM_PROFILES.get(item_type, {})
        label = profile.get("label", item_type.replace("_", " ").title())
        _append_reward_part(parts, label, amount)

    equipment_keys = list(reward.get("equipment", ()))
    class_rewards = reward.get("equipment_by_class", {})
    if player_type:
        equipment_keys.extend(class_rewards.get(player_type, ()))
    else:
        for keys in class_rewards.values():
            equipment_keys.extend(keys)
    for equipment_key in equipment_keys:
        profile = get_equipment_item(equipment_key) or {}
        _append_reward_part(parts, profile.get("label", equipment_key.replace("_", " ").title()))

    for item_key, amount in reward.get("story_items", {}).items():
        profile = get_story_reward_item(item_key) or {}
        label = profile.get("label", item_key.replace("_", " ").title())
        _append_reward_part(parts, label, amount)

    if not parts:
        return "Reward: none listed"
    visible_parts = parts[:max_parts]
    if len(parts) > max_parts:
        visible_parts.append(f"+{len(parts) - max_parts} more")
    return "Reward: " + ", ".join(visible_parts)
