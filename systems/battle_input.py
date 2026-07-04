"""Battle input routing helpers.

Beginner note:
    `BattleScreen` still owns combat state, but this module owns the repeated
    keyboard/touch routing. That keeps the large battle class from growing every
    time Android buttons or battle menu behavior changes.

    Plain-language terms:
    - Event: one input moment, such as pressing a key or tapping the screen.
    - Route: decide which part of the battle should receive that input.
    - Cooldown: a short wait after an action so animations/log text can play.
    - Game-space point: the tap position after it is converted to the game's
      fixed 1000x700 coordinate system.

    The helper functions accept a `battle` object instead of importing
    `BattleScreen` from `main.py`. That avoids circular imports:

    - `main.py` imports this file.
    - This file calls methods on whatever battle object it receives.
"""


def get_touch_positions(event, display_to_game_pos):
    """Return every possible game-space point for a click/tap event.

    Android builds can report either real fullscreen pixels or the game's
    virtual 1000x700 coordinates. Checking both makes touch buttons more
    forgiving without changing desktop mouse behavior.
    """
    raw_pos = getattr(event, "pos", None)
    if raw_pos is None:
        return []
    mapped_pos = display_to_game_pos(raw_pos)
    positions = [mapped_pos]
    if raw_pos != mapped_pos:
        positions.append(raw_pos)
    return positions


def play_game_sound(game, sound_name):
    """Play one optional sound effect from the Game object."""
    sound = getattr(game, sound_name, None) if game else None
    if sound:
        sound.play()


def _is_confirm_key(pygame_module, event):
    """Return True when a keyboard event means "choose/continue"."""
    return event.type == pygame_module.KEYDOWN and event.key in (
        pygame_module.K_RETURN,
        pygame_module.K_SPACE,
    )


def _is_mouse_down(pygame_module, event):
    """Return True when the input event is a mouse click or screen tap."""
    return event.type == pygame_module.MOUSEBUTTONDOWN


def _continue_if_needed(battle, event, pygame_module):
    """Handle summary/log pauses before normal battle menu input.

    Beginner note:
        Some battle messages should stay on screen until the player taps NEXT or
        presses ENTER. This helper checks those pause screens first so a tap
        cannot accidentally continue the message and select ATTACK at the same
        time.
    """
    if battle.battle_ended and battle.show_summary:
        if _is_confirm_key(pygame_module, event) or _is_mouse_down(pygame_module, event):
            battle.waiting_for_continue = False
            battle.show_summary = False
        return True

    if battle.waiting_for_continue:
        if _is_confirm_key(pygame_module, event) or _is_mouse_down(pygame_module, event):
            battle.waiting_for_continue = False
        return True

    return False


def handle_battle_input(battle, event, game, pygame_module, display_to_game_pos):
    """Route one keyboard/touch event into the active battle menu.

    Beginner step order:
        1. Let NEXT/summary screens consume input before attacks can happen.
        2. Ignore attacks when it is not the player's turn.
        3. Handle keyboard navigation and confirmation.
        4. Handle touch taps, including Android's raw/scaled coordinate issue.

    Returns:
        True when the event was handled by battle code.
        False when the event was ignored.
    """
    if _continue_if_needed(battle, event, pygame_module):
        return True

    if battle.state != "player_turn" or battle.battle_ended or battle.action_cooldown > 0:
        return False

    # Keyboard path for desktop and Chromebooks. The same battle object is used
    # on Android, but Android usually reaches the mouse/touch path below.
    if event.type == pygame_module.KEYDOWN:
        if event.key in (pygame_module.K_TAB, pygame_module.K_h):
            battle.toggle_combat_buttons()
            play_game_sound(game, "SFX_CLICK")
            return True

        if not battle.combat_buttons_visible:
            # Commands are intentionally hidden. Swallow arrow/confirm input so
            # hidden commands cannot be triggered by accident.
            return True

        option_count = len(battle.buttons)
        if event.key in (pygame_module.K_RIGHT, pygame_module.K_d, pygame_module.K_DOWN, pygame_module.K_s):
            battle.selected_option = (battle.selected_option + 1) % option_count
            play_game_sound(game, "SFX_ARROW")
            return True
        if event.key in (pygame_module.K_LEFT, pygame_module.K_a, pygame_module.K_UP, pygame_module.K_w):
            battle.selected_option = (battle.selected_option - 1) % option_count
            play_game_sound(game, "SFX_ARROW")
            return True
        if event.key in (pygame_module.K_RETURN, pygame_module.K_SPACE):
            play_game_sound(game, "SFX_ENTER")
            battle.handle_action(game)
            return True

    # Touch/mouse path. Android taps can arrive in real screen pixels or in the
    # game's internal 1000x700 pixels, so get_touch_positions() returns both.
    if event.type == pygame_module.MOUSEBUTTONDOWN:
        touch_positions = get_touch_positions(event, display_to_game_pos)

        # Check the small toggle before the command row, so one tap cannot both
        # reveal/hide buttons and trigger an attack.
        for mouse_pos in touch_positions:
            if battle.combat_toggle_button.rect.inflate(24, 24).collidepoint(mouse_pos):
                battle.toggle_combat_buttons()
                play_game_sound(game, "SFX_CLICK")
                return True

        if not battle.combat_buttons_visible:
            # Phones should always have an easy recovery path. Tapping the lower
            # command lane reveals battle buttons even if the small ACTIONS
            # toggle was missed.
            for mouse_pos in touch_positions:
                if mouse_pos[1] >= 490:
                    battle.show_combat_buttons()
                    play_game_sound(game, "SFX_CLICK")
                    return True
            return True

        for mouse_pos in touch_positions:
            for index, button in enumerate(battle.buttons):
                if button.rect.inflate(18, 18).collidepoint(mouse_pos):
                    battle.selected_option = index
                    play_game_sound(game, "SFX_ENTER")
                    battle.handle_action(game)
                    return True

    return False
