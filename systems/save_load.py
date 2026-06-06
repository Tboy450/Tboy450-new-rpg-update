"""JSON save/load helpers for the active game state.

Beginner note:
    Live game objects contain Python classes, sets, and other values that JSON
    cannot write directly. This module converts the important values into plain
    dictionaries, lists, strings, numbers, and booleans.

Save/load split:
    `build_save_data` reads the active `Game` object and creates JSON-safe data.
    `save_game_state` writes that data to disk.
    `load_game_state` reads JSON from disk and checks the save version.
    `Game.load_saved_game` in `main.py` applies loaded values back to objects.
"""

import json
import os
from pathlib import Path

# Increase this if the save file format changes in a way old saves cannot load.
SAVE_VERSION = 1

# Environment override lets testers choose a custom save path without editing code.
DEFAULT_SAVE_PATH = Path(
    os.environ.get("DRAGONS_LAIR_SAVE", Path.home() / ".dragons_lair_rpg_save.json")
)

def _claim_to_list(claim):
    """Convert a town service claim tuple into a JSON-safe list."""
    if isinstance(claim, (list, tuple)) and len(claim) == 2:
        return [str(claim[0]), int(claim[1])]
    return None

def _pair_to_list(pair):
    """Convert a two-value identifier into a JSON-safe string pair list."""
    if isinstance(pair, (list, tuple)) and len(pair) == 2:
        return [str(pair[0]), str(pair[1])]
    return None

def build_save_data(game):
    """Build a JSON-safe snapshot from a Game instance.

    This function should include every piece of game progress that must survive
    closing and reopening the game.
    """
    if not game.player:
        raise ValueError("No active character to save.")

    # Only store visited area coordinates, not the full WorldArea objects.
    visited = []
    for (area_x, area_y), area in game.world_map.areas.items():
        if getattr(area, "visited", False):
            visited.append([area_x, area_y])

    # Sets and tuples are converted into lists because JSON has no set type.
    claims = []
    for claim in game.player.town_service_claims:
        claim_record = _claim_to_list(claim)
        if claim_record:
            claims.append(claim_record)

    # Interior inspect details are saved so one-time rewards stay one-time.
    inspected_details = []
    for detail in getattr(game, "inspected_town_details", set()):
        detail_record = _pair_to_list(detail)
        if detail_record:
            inspected_details.append(detail_record)

    return {
        "version": SAVE_VERSION,
        "score": game.score,
        "game_time": game.game_time,
        "boss_defeated": game.boss_defeated,
        "player": {
            "type": game.player.type,
            "level": game.player.level,
            "exp": game.player.exp,
            "exp_to_level": game.player.exp_to_level,
            "max_health": game.player.max_health,
            "health": game.player.health,
            "max_mana": game.player.max_mana,
            "mana": game.player.mana,
            "strength": game.player.strength,
            "defense": game.player.defense,
            "speed": game.player.speed,
            "x": game.player.x,
            "y": game.player.y,
            "kills": game.player.kills,
            "items_collected": game.player.items_collected,
            "inventory": dict(game.player.inventory),
            "last_boss_level": game.player.last_boss_level,
            "boss_cooldown": game.player.boss_cooldown,
            "town_service_claims": claims,
        },
        "world": {
            "current_area": [game.world_map.current_area_x, game.world_map.current_area_y],
            "visited_areas": visited,
        },
        "town": {
            "reputation": getattr(game, "town_reputation", 0),
            "completed_errands": sorted(getattr(game, "completed_town_errands", set())),
            "inspected_details": sorted(inspected_details),
        },
    }

def save_game_state(game, path=DEFAULT_SAVE_PATH):
    """Write game state to disk and return the save path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_save_data(game)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path

def load_game_state(path=DEFAULT_SAVE_PATH):
    """Load a saved JSON record from disk.

    This returns raw data. `main.py` decides how to apply it to live objects.
    """
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != SAVE_VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')}")
    return data
