"""Input action mapping shared by keyboard and touch controls."""

import pygame

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

ANDROID_BUTTON_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "enter": pygame.K_RETURN,
    "space": pygame.K_SPACE,
}

MOVE_DELTAS = {
    MOVE_UP: (0, -1),
    MOVE_DOWN: (0, 1),
    MOVE_LEFT: (-1, 0),
    MOVE_RIGHT: (1, 0),
}

def action_for_key(key):
    """Return the gameplay action for a pygame key constant."""
    return KEY_ACTIONS.get(key)

def key_for_android_button(name):
    """Return the pygame key used by a virtual Android button."""
    return ANDROID_BUTTON_KEYS.get(name)

