"""JSON save/load helpers for the active game state."""

import json
import os
from pathlib import Path

SAVE_VERSION = 1
DEFAULT_SAVE_PATH = Path(
    os.environ.get("DRAGONS_LAIR_SAVE", Path.home() / ".dragons_lair_rpg_save.json")
)

def _claim_to_list(claim):
    if isinstance(claim, (list, tuple)) and len(claim) == 2:
        return [str(claim[0]), int(claim[1])]
    return None

def build_save_data(game):
    """Build a JSON-safe snapshot from a Game instance."""
    if not game.player:
        raise ValueError("No active character to save.")

    visited = []
    for (area_x, area_y), area in game.world_map.areas.items():
        if getattr(area, "visited", False):
            visited.append([area_x, area_y])

    claims = []
    for claim in game.player.town_service_claims:
        claim_record = _claim_to_list(claim)
        if claim_record:
            claims.append(claim_record)

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
    }

def save_game_state(game, path=DEFAULT_SAVE_PATH):
    """Write game state to disk and return the save path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_save_data(game)
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    return path

def load_game_state(path=DEFAULT_SAVE_PATH):
    """Load a saved JSON record from disk."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != SAVE_VERSION:
        raise ValueError(f"Unsupported save version: {data.get('version')}")
    return data

