"""Input action mapping shared by keyboard and touch controls.

Beginner note:
    Pygame gives the game raw key constants such as `pygame.K_UP`. This module
    translates those keys into simple action names such as `move_up`.

Why this helps:
    `main.py` can check for actions instead of duplicating keyboard and Android
    button logic in multiple places.

BEGINNER CODE LABEL: Input flow map
    1. Desktop keyboard input starts as a raw Pygame key.
    2. `action_for_key(...)` turns that key into one shared action string.
    3. Android touch buttons usually start as action strings already.
    4. `key_for_action(...)` can turn a touch action back into a synthetic
       keyboard key when older code paths still expect a KEYDOWN event.
"""

import pygame

# BEGINNER CODE LABEL: Shared action vocabulary.
# These strings are the bridge between desktop keys, Android touch buttons, and
# gameplay code in `main.py`. Using constants avoids misspelling raw strings in
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

# BEGINNER CODE LABEL: Keyboard -> action.
# Keys on the left are raw Pygame constants. Values on the right are the shared
# action strings that the rest of the game understands.
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

# BEGINNER CODE LABEL: Older Android button names -> keyboard key.
#     These are the older fixed-button names. The newer Android touch system
#     in `systems/android_controls.py` now works mostly with action strings
#     directly, but this mapping is still kept for compatibility and for any
#     code path that still wants to synthesize raw pygame key events.
ANDROID_BUTTON_KEYS = {
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "enter": pygame.K_RETURN,
    "space": pygame.K_SPACE,
}

# BEGINNER CODE LABEL: Action -> preferred keyboard key.
# Touch buttons can use this to post a synthetic KEYDOWN event so the rest of
# the game can reuse its keyboard logic.
#     This table goes in the opposite direction from KEY_ACTIONS. KEY_ACTIONS
#     turns a real key into an action; ACTION_PRIMARY_KEYS turns an action back
#     into the one keyboard key we prefer to imitate.
ACTION_PRIMARY_KEYS = {
    MOVE_UP: pygame.K_UP,
    MOVE_DOWN: pygame.K_DOWN,
    MOVE_LEFT: pygame.K_LEFT,
    MOVE_RIGHT: pygame.K_RIGHT,
    CONFIRM: pygame.K_RETURN,
    INTERACT: pygame.K_SPACE,
    CANCEL: pygame.K_ESCAPE,
    MAP: pygame.K_m,
    JOURNAL: pygame.K_j,
    SAVE: pygame.K_F5,
    LOAD: pygame.K_F9,
}

# BEGINNER CODE LABEL: Action -> grid movement.
# Movement actions can be reused by menus, Android controls, and gameplay
# because they all agree that moving up changes y by -1 grid step.
MOVE_DELTAS = {
    MOVE_UP: (0, -1),
    MOVE_DOWN: (0, 1),
    MOVE_LEFT: (-1, 0),
    MOVE_RIGHT: (1, 0),
}

def action_for_key(key):
    """Return the gameplay action for a pygame key constant.

    BEGINNER CODE LABEL:
        This is the normal desktop-keyboard entry point into the action system.

    Returns None when the key is not mapped to gameplay.
    """
    return KEY_ACTIONS.get(key)


def key_for_android_button(name):
    """Return the pygame key used by a virtual Android button.

    BEGINNER CODE LABEL:
        This supports older Android button names that still imitate keyboard
        keys instead of sending action strings directly.

    Returns None when the virtual button name is unknown.
    """
    return ANDROID_BUTTON_KEYS.get(name)


def key_for_action(action):
    """Return the preferred pygame key constant for an action string.

    BEGINNER CODE LABEL:
        Android touch commands call this when they need to reuse keyboard-based
        code in `main.py` without duplicating the gameplay branch.
    """
    return ACTION_PRIMARY_KEYS.get(action)
