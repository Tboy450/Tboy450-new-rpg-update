"""Room layout data for town building interiors.

Beginner note:
    These records describe what appears after the player enters a town building.
    Outdoor building positions live in `game_data/town.py`; indoor room contents
    live here.

Common fields:
    title/subtitle: text shown in the interior UI.
    wall_color/floor_color/trim_color/accent_color: RGB colors used by drawing.
    service_prompt: help text shown for the building's main action.
    flavor: rotating descriptive lines.
    npc_position: where the room NPC is drawn.
    props: furniture and decorative objects. Each prop has a kind and rect.
    props[].sprite: optional active PNG drawn instead of the Python shape.
    props[].sprite_preserve_aspect: optional bool. False stretches the sprite
        exactly into the prop rectangle.
    inspect_points: invisible/marked rectangles that give one-time flavor rewards.
"""

# Keys such as `inn`, `shop`, and `town_hall` must match building `type` values
# in `game_data/town.py` and service keys in `game_data/npcs.py`.
TOWN_INTERIORS = {
    "inn": {
        "title": "Warm Hearth Inn",
        "subtitle": "A safe room for wounds, stories, and full recovery.",
        "wall_color": (92, 56, 42),
        "floor_color": (128, 82, 54),
        "trim_color": (58, 34, 24),
        "accent_color": (255, 184, 94),
        "service_prompt": "SPACE: rest and recover",
        "flavor": (
            "The hearth keeps the room bright even after monster raids.",
            "Resting here restores both health and mana.",
        ),
        "npc_position": (720, 350),
        "props": (
            {"kind": "rug", "rect": (330, 430, 330, 80), "color": (166, 70, 54)},
            {"kind": "bed", "rect": (150, 335, 170, 80), "color": (210, 168, 122)},
            {"kind": "bed", "rect": (160, 455, 150, 72), "color": (190, 144, 104)},
            {"kind": "table", "rect": (438, 342, 118, 78), "color": (112, 66, 38)},
            {"kind": "counter", "rect": (670, 410, 190, 58), "color": (118, 66, 34)},
            {"kind": "hearth", "rect": (445, 235, 105, 82), "color": (78, 48, 38)},
            {"kind": "barrel", "rect": (330, 350, 42, 58), "color": (112, 72, 42)},
            {"kind": "plant", "rect": (825, 285, 44, 72), "color": (86, 146, 72)},
        ),
        "inspect_points": (
            {"label": "guest ledger", "rect": (430, 330, 150, 95), "message": "The guest ledger lists monster hunters, merchants, and one suspicious chicken."},
            {"label": "hearth", "rect": (430, 220, 135, 110), "message": "The hearth is banked with fragrant cedar and healing herbs."},
        ),
    },
    "shop": {
        "title": "Mooncap Market",
        "subtitle": "Potion bottles, travel rations, and odd glowing jars.",
        "wall_color": (62, 58, 98),
        "floor_color": (96, 76, 118),
        "trim_color": (38, 34, 64),
        "accent_color": (110, 220, 255),
        "service_prompt": "SPACE: restock potions",
        "flavor": (
            "Shelves are sorted by color, not by safety.",
            "The market refills combat-ready health and mana potions.",
        ),
        "npc_position": (720, 350),
        "props": (
            {"kind": "rug", "rect": (325, 430, 350, 78), "color": (52, 124, 154)},
            {
                "kind": "shelf",
                "rect": (135, 245, 150, 210),
                "color": (74, 50, 92),
                # BEGINNER NOTE: The shop is the first interior to test
                # imported scenery sprites. Keeping `kind` as "shelf" means the
                # same collision behavior still applies.
                "sprite": "town_shop/potion_shelf.png",
                "sprite_anchor": "bottom",
            },
            {"kind": "shelf", "rect": (300, 245, 132, 170), "color": (68, 48, 86)},
            {
                "kind": "counter",
                "rect": (650, 410, 215, 62),
                "color": (76, 54, 94),
                "sprite": "town_shop/shop_counter.png",
                "sprite_preserve_aspect": False,
            },
            {"kind": "crystal", "rect": (500, 315, 75, 98), "color": (110, 220, 255)},
            {"kind": "crate", "rect": (575, 450, 70, 55), "color": (118, 72, 48)},
            {"kind": "cauldron", "rect": (448, 420, 62, 54), "color": (64, 44, 72)},
            {
                "kind": "desk",
                "rect": (696, 286, 112, 64),
                "color": (86, 60, 98),
                "sprite": "town_shop/scroll_desk.png",
            },
        ),
        "inspect_points": (
            {"label": "odd jars", "rect": (130, 235, 310, 220), "message": "The jars glow in colors that do not have proper names."},
            {"label": "sample cauldron", "rect": (430, 400, 92, 85), "message": "A sweet potion vapor restores confidence, if not health."},
        ),
    },
    "blacksmith": {
        "title": "Ironroot Forge",
        "subtitle": "A compact forge for tuning weapons between dragon hunts.",
        "wall_color": (70, 58, 50),
        "floor_color": (94, 78, 64),
        "trim_color": (38, 30, 26),
        "accent_color": (255, 108, 58),
        "service_prompt": "SPACE: forge level gear",
        "flavor": (
            "Heat ripples over anvils, racks, and unfinished blades.",
            "The forge grants level-gated weapons, armor, and charms.",
        ),
        "npc_position": (735, 360),
        "props": (
            {"kind": "rug", "rect": (338, 442, 300, 70), "color": (118, 58, 44)},
            {"kind": "forge", "rect": (135, 275, 190, 170), "color": (82, 70, 62)},
            {"kind": "anvil", "rect": (405, 385, 125, 78), "color": (84, 88, 92)},
            {"kind": "counter", "rect": (660, 425, 205, 58), "color": (92, 62, 42)},
            {"kind": "rack", "rect": (545, 252, 150, 150), "color": (92, 68, 52)},
            {"kind": "crate", "rect": (330, 470, 72, 48), "color": (104, 68, 40)},
            {"kind": "barrel", "rect": (350, 285, 48, 62), "color": (86, 58, 40)},
            {"kind": "lamp", "rect": (615, 395, 34, 78), "color": (255, 108, 58)},
        ),
        "inspect_points": (
            {"label": "tool rack", "rect": (530, 240, 180, 175), "message": "Every tool is polished except the hammer Borin actually uses."},
            {"label": "forge", "rect": (120, 260, 220, 200), "message": "The forge heat bends the air like dragon breath."},
        ),
    },
    "library": {
        "title": "Starwell Library",
        "subtitle": "Maps, monster notes, and half-finished spell diagrams.",
        "wall_color": (50, 58, 84),
        "floor_color": (72, 86, 110),
        "trim_color": (30, 36, 56),
        "accent_color": (178, 205, 255),
        "service_prompt": "SPACE: study dragon lore",
        "flavor": (
            "Blue lamps hum beside stacks of field reports.",
            "Studying grants level-based experience insight.",
        ),
        "npc_position": (720, 350),
        "props": (
            {"kind": "rug", "rect": (320, 430, 355, 82), "color": (58, 80, 134)},
            {"kind": "bookcase", "rect": (125, 235, 160, 250), "color": (52, 42, 74)},
            {"kind": "bookcase", "rect": (300, 235, 145, 205), "color": (48, 38, 68)},
            {"kind": "desk", "rect": (480, 392, 130, 82), "color": (70, 52, 74)},
            {"kind": "counter", "rect": (660, 410, 205, 60), "color": (52, 44, 74)},
            {"kind": "crystal", "rect": (510, 270, 64, 90), "color": (178, 205, 255)},
            {"kind": "stool", "rect": (450, 470, 48, 42), "color": (78, 58, 82)},
            {"kind": "chest", "rect": (590, 305, 64, 44), "color": (78, 68, 96)},
        ),
        "inspect_points": (
            {"label": "dragon notes", "rect": (470, 380, 155, 105), "message": "The notes say bosses change tactics when wounded. Underlined twice."},
            {"label": "star crystal", "rect": (500, 255, 84, 120), "message": "The crystal hums with a map of places you have not visited yet."},
        ),
    },
    "town_hall": {
        "title": "Dragonwatch Hall",
        "subtitle": "The command room tracks boss sightings and town defense.",
        "wall_color": (86, 74, 66),
        "floor_color": (112, 96, 78),
        "trim_color": (48, 38, 32),
        "accent_color": (255, 215, 92),
        "service_prompt": "SPACE: ask about boss progression",
        "flavor": (
            "Pins and red thread mark dragon routes across the valley.",
            "Captain Marcus explains when the next boss can appear.",
        ),
        "npc_position": (720, 350),
        "props": (
            {"kind": "rug", "rect": (305, 430, 395, 86), "color": (130, 54, 50)},
            {"kind": "banner", "rect": (150, 235, 70, 170), "color": (150, 42, 38)},
            {"kind": "banner", "rect": (780, 235, 70, 170), "color": (150, 42, 38)},
            {"kind": "map", "rect": (330, 230, 235, 140), "color": (178, 146, 98)},
            {"kind": "desk", "rect": (405, 392, 190, 86), "color": (88, 56, 36)},
            {"kind": "notice", "rect": (625, 245, 120, 155), "color": (138, 104, 74)},
            {"kind": "chest", "rect": (255, 390, 76, 52), "color": (112, 72, 48)},
            {"kind": "lamp", "rect": (600, 398, 35, 76), "color": (255, 215, 92)},
        ),
        "inspect_points": (
            {"label": "dragon map", "rect": (320, 220, 255, 160), "message": "Red thread marks each dragon sighting. Several routes point back to town."},
            {"label": "notice board", "rect": (615, 235, 140, 175), "message": "The notices request guards, healers, and anyone who owns a larger bell."},
        ),
    },
    "house": {
        "title": "Mossroof Cottage",
        "subtitle": "A quiet home with drying herbs and practical local gossip.",
        "wall_color": (72, 78, 56),
        "floor_color": (100, 84, 58),
        "trim_color": (44, 48, 34),
        "accent_color": (154, 220, 118),
        "service_prompt": "SPACE: accept a small meal",
        "flavor": (
            "Bundles of herbs hang from the rafters.",
            "This cottage offers small comforts and careful warnings.",
        ),
        "npc_position": (715, 355),
        "props": (
            {"kind": "rug", "rect": (330, 430, 330, 80), "color": (82, 128, 72)},
            {"kind": "bed", "rect": (145, 360, 160, 78), "color": (156, 124, 86)},
            {"kind": "table", "rect": (410, 350, 135, 82), "color": (96, 68, 42)},
            {"kind": "counter", "rect": (660, 415, 200, 58), "color": (88, 64, 38)},
            {"kind": "plant", "rect": (570, 285, 48, 82), "color": (94, 158, 74)},
            {"kind": "barrel", "rect": (320, 455, 44, 58), "color": (108, 78, 48)},
            {"kind": "chest", "rect": (210, 455, 76, 48), "color": (108, 82, 48)},
        ),
        "inspect_points": (
            {"label": "herb rack", "rect": (540, 260, 105, 130), "message": "The herb bundles are sorted for burns, chills, and bad decisions."},
            {"label": "family chest", "rect": (198, 440, 100, 76), "message": "A carved chest holds blankets, seed packets, and old guard badges."},
        ),
    },
    "stall": {
        "title": "Sunstripe Stall",
        "subtitle": "A bright food counter wedged between roads and rumors.",
        "wall_color": (86, 62, 42),
        "floor_color": (126, 92, 58),
        "trim_color": (58, 38, 24),
        "accent_color": (255, 198, 88),
        "service_prompt": "SPACE: eat travel stew",
        "flavor": (
            "Steam curls over baskets of bread and glazed root vegetables.",
            "The stall gives quick boosts before another hunt.",
        ),
        "npc_position": (720, 350),
        "props": (
            {"kind": "rug", "rect": (300, 438, 390, 72), "color": (160, 84, 48)},
            {"kind": "counter", "rect": (625, 392, 240, 72), "color": (112, 70, 38)},
            {"kind": "crate", "rect": (185, 390, 92, 70), "color": (116, 78, 44)},
            {"kind": "barrel", "rect": (300, 390, 48, 66), "color": (104, 68, 38)},
            {"kind": "table", "rect": (405, 360, 145, 78), "color": (104, 64, 34)},
            {"kind": "cauldron", "rect": (535, 380, 70, 58), "color": (64, 48, 36)},
            {"kind": "sign", "rect": (670, 270, 120, 52), "color": (255, 198, 88)},
        ),
        "inspect_points": (
            {"label": "stew pot", "rect": (520, 365, 100, 86), "message": "The stew smells like pepper, onion, and suspiciously heroic timing."},
            {"label": "price sign", "rect": (655, 258, 150, 75), "message": "The sign reads: heroes eat first, dragons pay double."},
        ),
    },
}
