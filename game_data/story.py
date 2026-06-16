"""Story intro, map NPCs, and one-shot area dialogue.

Beginner note:
    This module is intentionally data-only. It answers questions like:

    - Which story NPCs should appear on the world map?
    - Which dialogue should start when the player enters a special area?
    - What extra town-guard lines should foreshadow those characters?

    The drawing, input handling, and reward code still live in `main.py`.
    Keeping the text here makes future story edits safer because a beginner can
    change dialogue without hunting through the whole game loop.
"""

# Opening cutscene text is still drawn by `OpeningCutscene` in main.py. These
# lines are imported there so the stronger story setup is easy to tune later.
OPENING_STORY_LINES = (
    "MALAKOR'S SHADOW DID NOT RISE ALONE.",
    "A WHITE MASK BEGAN WALKING THE NORTHERN PINES.",
    "THE TOWN KNIGHT GUARDS THE LAST ROAD.",
    "THE LION SAGE HOLDS THE FIRST TRUE QUEST.",
)

# These lines are appended to the town guard's first conversation. The guard is
# still created from `game_data/npcs.py`; this simply lets the town intro point
# toward the new story characters without mixing town-service data and main
# quest data in the same file.
TOWN_GUARD_STORY_LINES = (
    "The dragon is not only a beast. Malakor is a test the world keeps failing.",
    "Do not chase his fire first. A white mask stalks the northern pines.",
    "Seek the Lion Sage in the western marsh. He knows how fear and healing both begin.",
    "Earn his blessing, then choose which threat you are ready to face.",
)

# Friendly story NPCs placed on the 3x3 world map. Positions are local to the
# area tile. `local_position` is the NPC's foot-center point, not its top-left
# corner, so tall sprites stand naturally on the ground.
STORY_NPCS = {
    "lion_sage": {
        "name": "Lion Sage",
        "title": "Guardian Healer",
        "area": (0, 1),  # west-middle tile, currently the swamp biome
        # BEGINNER NOTE: Keep the Lion Sage near the east side of the swamp so
        # players arriving from town see him quickly instead of wandering.
        "local_position": (760, 390),
        "sprite_key": "lion_sage",
        "sprite_height": 176,
        "aura_color": (80, 220, 170),
        "prompt": "ENTER: seek Lion Sage guidance",
        "dialogue_key": "lion_sage_swamp",
    },
}

# One-shot area conversations. `trigger` currently supports "enter_area".
# The same record can also be reused when the player manually talks to a map
# NPC; in that case `repeat_lines` are shown after the first full conversation.
STORY_AREA_DIALOGUES = {
    "ghost_face_forest": {
        "trigger": "enter_area",
        "area": (1, 0),  # top-center forest tile
        "speaker": "Ghost Face",
        "title": "The Mask In The Pines",
        "portrait": "ghost_face",
        "color": (255, 105, 180),
        "lines": (
            "The trees stop moving. Even the wind seems to hold its breath.",
            "A white mask turns toward you from the center of the forest.",
            "Ghost Face: You brought a heartbeat into my woods. I can hear it.",
            "Ghost Face: The lion sent you with courage. I wonder how loud it breaks.",
        ),
        "repeat_lines": (
            "Ghost Face: The mask is still waiting.",
            "Ghost Face: Courage is only useful after it starts shaking.",
        ),
    },
    "lion_sage_swamp": {
        "trigger": "enter_area",
        "area": (0, 1),  # west-middle swamp tile
        "speaker": "Lion Sage",
        "title": "The Guardian Healer",
        "portrait": "lion_sage",
        "color": (80, 220, 170),
        "lines": (
            "The swamp mist curls into colored ribbons before your eyes.",
            "Lion Sage: Strength without care becomes another kind of wound.",
            "Lion Sage: Your first quest is the mask in the northern pines. Ghost Face feeds on panic.",
            "Lion Sage: Your second quest is the dragon path. Defeat the lesser drakes, grow, then face Malakor.",
            "Lion Sage: Black endures. Crimson protects life. Blue stays calm. Teal listens. Green recovers. Purple studies.",
            "Lion Sage: I awaken your special technique. Use it when ordinary courage is not enough.",
        ),
        "repeat_lines": (
            "Lion Sage: Return when your courage feels tired. Healing is not weakness.",
            "Lion Sage: Study the enemy, then protect what still has a chance to grow.",
        ),
        "reward": {
            "health": 35,
            "mana": 30,
            "items": {"health": 1, "mana": 1},
            "score": 8,
            "reputation": 1,
            "unlock_special": True,
            "message": "Lion Sage blessing: HP +{health}, MP +{mana}, potions stocked.",
        },
    },
}


def get_story_dialogue(dialogue_key):
    """Return one story dialogue record by key.

    Missing keys return None so callers can fail safely instead of crashing.
    """
    return STORY_AREA_DIALOGUES.get(dialogue_key)


def get_story_dialogues_for_area(area_x, area_y):
    """Return all area-triggered story dialogues for one world tile."""
    return [
        (key, dialogue)
        for key, dialogue in STORY_AREA_DIALOGUES.items()
        if tuple(dialogue.get("area", ())) == (area_x, area_y)
    ]


def get_story_npcs_for_area(area_x, area_y):
    """Return friendly story NPC records for one world tile."""
    return [
        (key, npc)
        for key, npc in STORY_NPCS.items()
        if tuple(npc.get("area", ())) == (area_x, area_y)
    ]
