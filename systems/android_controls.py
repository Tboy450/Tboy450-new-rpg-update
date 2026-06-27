"""State-aware Android touch controls for Dragon's Lair RPG.

Beginner note:
    `main.py` still owns the gameplay rules. This helper module only answers
    three UI questions:

    1. Which touch buttons should exist right now?
    2. Where should those buttons sit on the screen?
    3. How should those buttons be drawn and hit-tested?

Why this exists:
    The original Android controls were hardcoded inside `main.py` as one fixed
    layout. That caused the buttons to overlap story text boxes, journal panels,
    and other overlays. By moving the layout math here, the game can switch to
    a different touch layout for dialogue, map, journal, and normal movement.
"""

import pygame

from .input_actions import CANCEL, CONFIRM, INTERACT, MAP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT, MOVE_UP


def _make_button(name, rect, label, action, fill, border, kind="text", alpha=210):
    """Build one touch-button record.

    The returned dictionary is intentionally plain and beginner-friendly so
    `main.py` can inspect the values without needing a custom class.
    """
    return {
        "name": name,
        "rect": rect,
        "label": label,
        "action": action,
        "fill": fill,
        "border": border,
        "kind": kind,
        "alpha": alpha,
    }


def _current_area(game):
    """Safely read the current overworld area if the game has a world map."""
    if not getattr(game, "world_map", None):
        return None
    try:
        return game.world_map.get_current_area()
    except Exception:
        return None


def _guard_cutscene_active(game):
    """Return True when the town-guard cutscene is waiting for player input."""
    area = _current_area(game)
    return bool(
        area
        and getattr(area, "cutscene_active", False)
        and getattr(area, "cutscene_phase", 0) < 2
        and getattr(area, "guard", None)
    )


def _menu_button(screen_width):
    """Small top-right button used to open the shared pause/touch menu."""
    return _make_button(
        "pause_menu",
        pygame.Rect(screen_width - 128, 22, 106, 44),
        "MENU",
        "toggle_pause_menu",
        (28, 38, 60),
        (255, 215, 0),
    )


def build_android_touch_buttons(game, screen_width, screen_height):
    """Return the touch buttons that should be active for the current game UI.

    The layout changes by context:

    - Normal overworld/interior play: d-pad + USE/OK + MENU
    - Story dialogue or guard cutscene: NEXT + MENU
    - Log/Journal overlay: CLOSE button only
    - Inventory: slot/selection/equip/unequip/close buttons
    - World map: CLOSE MAP button only
    - Pause menu: pause-menu buttons are drawn by `main.py`, so this helper
      returns an empty list
    """
    if getattr(game, "show_pause_menu", False):
        return []

    state = getattr(game, "state", "")
    if state not in {"overworld", "interior"}:
        return []

    buttons = []
    buttons.append(_menu_button(screen_width))

    if getattr(game, "show_world_map", False):
        buttons.append(
            _make_button(
                "close_map",
                pygame.Rect(screen_width - 170, 82, 148, 48),
                "CLOSE MAP",
                MAP,
                (24, 48, 74),
                (140, 220, 255),
            )
        )
        return buttons

    if getattr(game, "show_journal", False):
        buttons.append(
            _make_button(
                "close_journal",
                pygame.Rect(screen_width - 180, 82, 158, 48),
                "CLOSE LOG",
                CONFIRM,
                (34, 54, 74),
                (200, 220, 255),
            )
        )
        return buttons

    if getattr(game, "show_inventory", False):
        base_y = screen_height - 54
        buttons.extend(
            [
                _make_button(
                    "inventory_slot_left",
                    pygame.Rect(28, base_y, 88, 42),
                    "SLOT <",
                    MOVE_LEFT,
                    (42, 50, 76),
                    (180, 220, 255),
                ),
                _make_button(
                    "inventory_slot_right",
                    pygame.Rect(126, base_y, 88, 42),
                    "SLOT >",
                    MOVE_RIGHT,
                    (42, 50, 76),
                    (180, 220, 255),
                ),
                _make_button(
                    "inventory_up",
                    pygame.Rect(514, base_y, 62, 42),
                    "",
                    MOVE_UP,
                    (44, 52, 72),
                    (210, 220, 235),
                    kind="arrow_up",
                ),
                _make_button(
                    "inventory_down",
                    pygame.Rect(584, base_y, 62, 42),
                    "",
                    MOVE_DOWN,
                    (44, 52, 72),
                    (210, 220, 235),
                    kind="arrow_down",
                ),
                _make_button(
                    "inventory_equip",
                    pygame.Rect(654, base_y, 92, 42),
                    "EQUIP",
                    CONFIRM,
                    (42, 70, 48),
                    (120, 220, 160),
                ),
                _make_button(
                    "inventory_unequip",
                    pygame.Rect(754, base_y, 104, 42),
                    "UNEQUIP",
                    INTERACT,
                    (76, 50, 42),
                    (255, 170, 120),
                ),
                _make_button(
                    "close_inventory",
                    pygame.Rect(866, base_y, 106, 42),
                    "CLOSE",
                    CANCEL,
                    (42, 50, 76),
                    (255, 215, 0),
                ),
            ]
        )
        return buttons

    if getattr(game, "active_story_dialogue", None) or _guard_cutscene_active(game):
        buttons.append(
            _make_button(
                "advance_dialogue",
                pygame.Rect(screen_width - 174, 352, 152, 54),
                "NEXT",
                CONFIRM,
                (88, 58, 18),
                (255, 215, 0),
            )
        )
        return buttons

    # Normal exploration controls. The interior uses a larger bottom clearance
    # because its service text panel sits near the bottom center of the screen.
    dpad_size = 56 if state == "overworld" else 52
    action_w = 104
    action_h = 50
    bottom_margin = 20 if state == "overworld" else 118
    left_margin = 22
    right_margin = 22

    top_y = screen_height - bottom_margin - 3 * dpad_size
    mid_y = screen_height - bottom_margin - 2 * dpad_size
    bottom_y = screen_height - bottom_margin - dpad_size

    buttons.extend(
        [
            _make_button(
                "up",
                pygame.Rect(left_margin + dpad_size, top_y, dpad_size, dpad_size),
                "",
                MOVE_UP,
                (44, 52, 72),
                (210, 220, 235),
                kind="arrow_up",
            ),
            _make_button(
                "down",
                pygame.Rect(left_margin + dpad_size, bottom_y, dpad_size, dpad_size),
                "",
                MOVE_DOWN,
                (44, 52, 72),
                (210, 220, 235),
                kind="arrow_down",
            ),
            _make_button(
                "left",
                pygame.Rect(left_margin, mid_y, dpad_size, dpad_size),
                "",
                MOVE_LEFT,
                (44, 52, 72),
                (210, 220, 235),
                kind="arrow_left",
            ),
            _make_button(
                "right",
                pygame.Rect(left_margin + 2 * dpad_size, mid_y, dpad_size, dpad_size),
                "",
                MOVE_RIGHT,
                (44, 52, 72),
                (210, 220, 235),
                kind="arrow_right",
            ),
        ]
    )

    action_x = screen_width - right_margin - action_w
    buttons.extend(
        [
            _make_button(
                "confirm",
                pygame.Rect(action_x, mid_y + 2, action_w, action_h),
                "OK",
                CONFIRM,
                (124, 92, 28),
                (255, 215, 0),
            ),
            _make_button(
                "interact",
                pygame.Rect(action_x, bottom_y - 2, action_w, action_h),
                "USE",
                INTERACT,
                (24, 104, 118),
                (110, 255, 255),
            ),
        ]
    )
    return buttons


def find_android_touch_button(buttons, pos, extra_padding=8):
    """Return the touched button dictionary, or None if nothing was hit.

    Beginner note:
        `extra_padding` makes taps slightly forgiving. Keep it small because
        stacked phone buttons can overlap mechanically if the invisible hitbox
        grows too far beyond the visible rectangle.
    """
    for button in reversed(buttons):
        if button["rect"].inflate(extra_padding, extra_padding).collidepoint(pos):
            return button
    return None


def find_android_touch_button_at_positions(buttons, positions, extra_padding=8):
    """Return the first touch button found from one or more coordinate guesses.

    Beginner note:
        Android launchers are not always consistent about mouse/touch
        coordinates. Some report the real phone display position; others report
        the game's 1000x700 virtual screen position. `main.py` sends both
        guesses here so the visual button and the clickable hitbox stay lined
        up on more devices.
    """
    checked_positions = []
    for pos in positions:
        if pos is None or pos in checked_positions:
            continue
        checked_positions.append(pos)
        touched_button = find_android_touch_button(buttons, pos, extra_padding)
        if touched_button:
            return touched_button
    return None


def draw_android_touch_buttons(surface, buttons, font_small, font_tiny):
    """Draw the active Android touch buttons.

    `font_small` is used for primary labels like MENU or USE.
    `font_tiny` is kept available in case future buttons need a subtitle.
    """
    for button in buttons:
        rect = button["rect"]
        fill = button["fill"]
        border = button["border"]
        alpha = button.get("alpha", 210)

        button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(button_surface, (*fill, alpha), button_surface.get_rect(), border_radius=14)
        surface.blit(button_surface, rect.topleft)
        pygame.draw.rect(surface, border, rect, 2, border_radius=14)

        kind = button.get("kind", "text")
        if kind.startswith("arrow_"):
            if kind == "arrow_up":
                points = [
                    (rect.centerx, rect.top + 14),
                    (rect.left + 14, rect.bottom - 16),
                    (rect.right - 14, rect.bottom - 16),
                ]
            elif kind == "arrow_down":
                points = [
                    (rect.centerx, rect.bottom - 14),
                    (rect.left + 14, rect.top + 16),
                    (rect.right - 14, rect.top + 16),
                ]
            elif kind == "arrow_left":
                points = [
                    (rect.left + 14, rect.centery),
                    (rect.right - 16, rect.top + 14),
                    (rect.right - 16, rect.bottom - 14),
                ]
            else:
                points = [
                    (rect.right - 14, rect.centery),
                    (rect.left + 16, rect.top + 14),
                    (rect.left + 16, rect.bottom - 14),
                ]
            pygame.draw.polygon(surface, (235, 238, 244), points)
            continue

        label_text = button["label"]
        label_font = font_small if len(label_text) <= 7 else font_tiny
        label = label_font.render(label_text, True, (245, 245, 240))
        surface.blit(label, label.get_rect(center=rect.center))
