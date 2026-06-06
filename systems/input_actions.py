"""Input action mapping shared by keyboard and touch controls.

Beginner note:
    Pygame gives the game raw key constants such as `pygame.K_UP`. This module
    translates those keys into simple action names such as `move_up`.

Why this helps:
    `main.py` can check for actions instead of duplicating keyboard and Android
    button logic in multiple places.
"""

import pygame

# Action name constants. Using constants avoids misspelling raw strings in
# different files.
MOVE_UP = "move_up"
MOVE_DOWN = "move_down"
MOVE_LEFT = "move_left"
MOVE_RIGHT = "move_right"
CONFIRM = "confirm"
INTERACT = "interact"
CANCEL = "cancel"
MAP = "map"
JOURNAL = "journal"
SAVE = "save"
LOAD = "load"

# Keyboard controls. Keys on the left map to action strings on the right.
KEY_ACTIONS = {
    pygame.K_UP: MOVE_UP,
    pygame.K_w: MOVE_UP,
    pygame.K_DOWN: MOVE_DOWN,
    pygame.K_s: MOVE_DOWN,
    pygame.K_LEFT: MOVE_LEFT,
    pygame.K_a: MOVE_LEFT,
    pygame.K_RIGHT: MOVE_RIGHT,
    pygame.K_d: MOVE_RIGHT,
    pygame.K_RETURN: CONFIRM,
    pygame.K_SPACE: INTERACT,
    pygame.K_ESCAPE: CANCEL,
    pygame.K_m: MAP,
    pygame.K_j: JOURNAL,
    pygame.K_F5: SAVE,
    pygame.K_F9: LOAD,
}

# Virtual Android button names map to the pygame key they should imitate.
ANDROID_BUTTON_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "enter": pygame.K_RETURN,
    "space": pygame.K_SPACE,
}

# Grid movement offsets. For example, moving up changes y by -1 grid step.
MOVE_DELTAS = {
    MOVE_UP: (0, -1),
    MOVE_DOWN: (0, 1),
    MOVE_LEFT: (-1, 0),
    MOVE_RIGHT: (1, 0),
}

def action_for_key(key):
    """Return the gameplay action for a pygame key constant.

    Returns None when the key is not mapped to gameplay.
    """
    return KEY_ACTIONS.get(key)

def key_for_android_button(name):
    """Return the pygame key used by a virtual Android button.

    Returns None when the virtual button name is unknown.
    """
    return ANDROID_BUTTON_KEYS.get(name)
