"""Town overworld layout data.

Beginner note:
    This file describes the outside town map only. The rooms inside buildings
    are described in `game_data/interiors.py`.

Common fields:
    type: key used by services, interiors, errands, drawing, and collision.
    x/y: top-left pixel position on the town screen.
    width/height: size in pixels.
    color: RGB fill color used by the drawing code.
    style: drawing style hint used by `WorldArea.draw_town` in `main.py`.
    collision: whether the player should be blocked by the object.
    entry_depth: how far the player can overlap the top/bottom for visual depth.
    door_width: width of the entrance interaction zone.
"""

# Walls, gate, and towers near the top edge of the town screen.
TOWN_BOUNDARIES = (
    {"type": "gate", "x": 450, "y": 200, "width": 100, "height": 60},
    {"type": "wall", "x": 0, "y": 200, "width": 450, "height": 20},
    {"type": "wall", "x": 550, "y": 200, "width": 450, "height": 20},
    {"type": "tower", "x": 400, "y": 180, "width": 40, "height": 80},
    {"type": "tower", "x": 560, "y": 180, "width": 40, "height": 80},
)

# Outdoor buildings and structures. The `type` values must match the keys used
# by `TOWN_INTERIORS`, `TOWN_SERVICES`, and optional `TOWN_ERRANDS`.
TOWN_BUILDINGS = (
    {
        "type": "town_hall",
        "x": 400,
        "y": 380,
        "width": 200,
        "height": 140,
        "color": (200, 180, 160),
        "style": "grand",
        "collision": True,
        "entry_depth": 42,
        "door_width": 96,
    },
    {
        "type": "shop",
        "x": 60,
        "y": 430,
        "width": 140,
        "height": 90,
        "color": (180, 160, 200),
        "style": "magical",
        "collision": True,
        "entry_depth": 30,
        "door_width": 72,
    },
    {
        "type": "inn",
        "x": 800,
        "y": 430,
        "width": 140,
        "height": 90,
        "color": (200, 160, 140),
        "style": "cozy",
        "collision": True,
        "entry_depth": 30,
        "door_width": 72,
    },
    {
        "type": "blacksmith",
        "x": 100,
        "y": 570,
        "width": 120,
        "height": 80,
        "color": (140, 120, 100),
        "style": "industrial",
        "collision": True,
        "entry_depth": 24,
        "door_width": 68,
    },
    {
        "type": "library",
        "x": 780,
        "y": 570,
        "width": 120,
        "height": 80,
        "color": (160, 180, 200),
        "style": "mystical",
        "collision": True,
        "entry_depth": 24,
        "door_width": 64,
    },
    {
        "type": "house",
        "x": 750,
        "y": 340,
        "width": 70,
        "height": 60,
        "color": (150, 130, 110),
        "style": "cottage",
        "collision": True,
        "entry_depth": 18,
        "door_width": 46,
    },
    {
        "type": "stall",
        "x": 450,
        "y": 530,
        "width": 100,
        "height": 50,
        "color": (170, 150, 130),
        "style": "market",
        "collision": True,
        "entry_depth": 16,
        "door_width": 88,
    },
)

# Decorative records are visual only and do not block player movement.
TOWN_DECORATIONS = (
    {"type": "lamp", "x": 150, "y": 300, "width": 20, "height": 60},
    {"type": "lamp", "x": 850, "y": 300, "width": 20, "height": 60},
    {"type": "lamp", "x": 150, "y": 650, "width": 20, "height": 60},
    {"type": "lamp", "x": 850, "y": 650, "width": 20, "height": 60},
    {"type": "tree", "x": 50, "y": 250, "width": 30, "height": 50},
    {"type": "tree", "x": 920, "y": 250, "width": 30, "height": 50},
    {"type": "tree", "x": 50, "y": 700, "width": 30, "height": 50},
    {"type": "tree", "x": 920, "y": 700, "width": 30, "height": 50},
    {"type": "flowers", "x": 200, "y": 270, "width": 40, "height": 20},
    {"type": "flowers", "x": 760, "y": 270, "width": 40, "height": 20},
    {"type": "flowers", "x": 200, "y": 730, "width": 40, "height": 20},
    {"type": "flowers", "x": 760, "y": 730, "width": 40, "height": 20},
    # Beach is town scenery, not a 3x3 map area. These sand patches give the
    # town a shoreline feel without creating a separate "beach" region.
    {"type": "sand_patch", "x": 275, "y": 620, "width": 155, "height": 52},
    {"type": "sand_patch", "x": 585, "y": 622, "width": 145, "height": 48},
)

# Chimney/smoke emitters. These are read by the town particle generator.
TOWN_SMOKE_SOURCES = (
    {"x": 150, "y": 430},
    {"x": 850, "y": 430},
    {"x": 180, "y": 570},
    {"x": 820, "y": 570},
)


def clone_town_layout():
    """Return mutable copies of town layout records used by WorldArea.

    The source constants above are tuples so they stay stable. `WorldArea` gets
    copies because runtime code may safely attach or adjust per-area values.
    """
    return {
        "boundaries": [dict(item) for item in TOWN_BOUNDARIES],
        "buildings": [dict(item) for item in TOWN_BUILDINGS],
        "decorations": [dict(item) for item in TOWN_DECORATIONS],
        "smoke_sources": [dict(item) for item in TOWN_SMOKE_SOURCES],
    }
