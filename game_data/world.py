"""World layout and spawn configuration."""

WORLD_LAYOUT = (
    ("mountain", "forest", "desert"),
    ("swamp", "beach", "volcano"),
    ("ice", "town", "cave"),
)

AREA_ENEMY_TYPES = {
    "forest": ["shadow", "ice"],
    "desert": ["fiery"],
    "mountain": ["fiery", "ice"],
    "swamp": ["shadow", "ice"],
    "volcano": ["fiery"],
    "ice": ["ice"],
    "town": [],
    "castle": ["shadow", "fiery"],
    "cave": ["shadow", "ice"],
}

