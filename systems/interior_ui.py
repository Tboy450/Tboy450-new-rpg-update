"""Reusable drawing helpers for town building interiors.

Beginner note:
    Interior gameplay still lives in `main.py`: movement, collision, services,
    inspecting objects, and entering/leaving rooms.

    This module only draws repeated UI pieces:

    - imported/fallback service NPCs
    - service note cards for every building
    - the clickable service menu opened inside a building
    - the bottom room message and prompt panel

    Pulling these helpers out keeps `main.py` from growing every time a town
    room gets better visuals.
"""

import pygame

from systems.assets import draw_sprite_in_rect, get_town_service_npc_sprite_path
from systems.town_services import get_service_hint_lines, get_service_overview_lines


def _shade_color(color, amount):
    """Lighten or darken an RGB color by a signed amount."""
    return tuple(max(0, min(255, value + amount)) for value in color)


def draw_interior_npc(surface, room, service, font_tiny, ui_bg):
    """Draw a service NPC with imported art when available.

    Beginner note:
        The Inn and Blacksmith have PNG sprites now. Other rooms use the simple
        Python-drawn fallback below until imported art exists for them too.
    """
    service_type = service["type"] if service else None
    npc_name = service["npc"] if service else "Townsperson"
    accent_color = room["accent_color"]

    npc_sprite_path = get_town_service_npc_sprite_path(service_type)
    npc_sprite_rect = room.get("npc_sprite_rect")
    if npc_sprite_path and npc_sprite_rect:
        sprite_rect = pygame.Rect(npc_sprite_rect)
        if draw_sprite_in_rect(
            surface,
            npc_sprite_path,
            sprite_rect,
            room.get("npc_sprite_preserve_aspect", True),
            room.get("npc_sprite_anchor", "bottom"),
        ):
            name_text = font_tiny.render(npc_name, True, accent_color)
            name_rect = name_text.get_rect(center=(sprite_rect.centerx, min(sprite_rect.bottom + 15, 592)))
            name_panel = name_rect.inflate(18, 8)
            pygame.draw.rect(surface, ui_bg, name_panel, border_radius=5)
            pygame.draw.rect(surface, accent_color, name_panel, 1, border_radius=5)
            surface.blit(name_text, name_rect)
            return

    npc_x, npc_y = room["npc_position"]
    pygame.draw.ellipse(surface, (20, 18, 18), (npc_x - 22, npc_y + 42, 54, 16))
    pygame.draw.rect(surface, _shade_color(accent_color, -35), (npc_x - 18, npc_y + 8, 36, 48), border_radius=8)
    pygame.draw.circle(surface, (224, 174, 126), (npc_x, npc_y), 18)
    pygame.draw.circle(surface, _shade_color(accent_color, 25), (npc_x - 6, npc_y - 5), 4)
    pygame.draw.circle(surface, _shade_color(accent_color, 25), (npc_x + 6, npc_y - 5), 4)
    npc_text = font_tiny.render(npc_name, True, accent_color)
    surface.blit(npc_text, (npc_x - npc_text.get_width() // 2, npc_y + 68))


def draw_interior_service_card(
    surface,
    room,
    service,
    player,
    font_tiny,
    ui_bg,
    render_fitted_text,
    wrap_text_to_width=None,
):
    """Draw a compact wall note for the active building service.

    Beginner note:
        The card combines static service purpose text with live state text such
        as whether a once-per-level bonus is ready. That gives beginner coders
        one obvious place to adjust the room card without digging through the
        main game loop.
    """
    if not service or not player:
        return

    service_type = service["type"]
    overview_lines = get_service_overview_lines(service_type)
    hint_lines = get_service_hint_lines(service_type, player)
    if not overview_lines and not hint_lines:
        return

    accent_color = room["accent_color"]
    panel = pygame.Rect(82, 104, 330, 152)
    pygame.draw.rect(surface, (18, 18, 26), panel, border_radius=7)
    pygame.draw.rect(surface, accent_color, panel, 2, border_radius=7)

    title = font_tiny.render("SERVICE CARD", True, accent_color)
    surface.blit(title, (panel.x + 12, panel.y + 9))

    line_y = panel.y + 31
    card_lines = []
    if overview_lines:
        card_lines.append(overview_lines[0])
    if len(overview_lines) > 1:
        if wrap_text_to_width:
            card_lines.extend(wrap_text_to_width(overview_lines[1], font_tiny, panel.width - 24)[:2])
        else:
            card_lines.append(overview_lines[1])
    if len(overview_lines) > 2:
        card_lines.append(overview_lines[2])
    card_lines.extend(hint_lines[:2])

    for index, line in enumerate(card_lines[:6]):
        color = accent_color if index == 0 else (222, 222, 214)
        text = render_fitted_text(line, color, panel.width - 24, (font_tiny,))
        surface.blit(text, (panel.x + 12, line_y))
        line_y += 18


def draw_interior_service_menu(
    surface,
    room,
    service,
    buttons,
    selected_index,
    reward_preview,
    font_large,
    font_small,
    font_tiny,
    ui_bg,
    screen_width,
    screen_height,
    wrap_text_to_width,
    render_fitted_text,
):
    """Draw the clickable service menu shown inside town buildings.

    Beginner note:
        The service menu is intentionally drawn here, not in `main.py`, because
        this is visual layout. `main.py` still decides what each button does.
        The `buttons` list contains normal Button objects from the main game.
    """
    if not room or not service:
        return

    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 158))
    surface.blit(overlay, (0, 0))

    accent_color = room["accent_color"]
    panel = pygame.Rect(screen_width // 2 - 235, 122, 470, 424)
    pygame.draw.rect(surface, ui_bg, panel, border_radius=10)
    pygame.draw.rect(surface, accent_color, panel, 3, border_radius=10)

    title = render_fitted_text(service["name"].upper(), accent_color, panel.width - 44, (font_large, font_small))
    surface.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 24))

    npc_line = render_fitted_text(f"{service['npc']} - {service.get('role', 'Town Service')}", (230, 230, 220), panel.width - 44, (font_small, font_tiny))
    surface.blit(npc_line, (panel.centerx - npc_line.get_width() // 2, panel.y + 73))

    overview = get_service_overview_lines(service["type"])
    body_lines = []
    if len(overview) > 1:
        body_lines.extend(wrap_text_to_width(overview[1], font_tiny, panel.width - 48)[:2])
    if reward_preview:
        body_lines.extend(wrap_text_to_width(reward_preview, font_tiny, panel.width - 48)[:2])

    line_y = panel.y + 106
    for index, line in enumerate(body_lines[:4]):
        color = (245, 235, 180) if index >= 2 else (220, 225, 220)
        text = render_fitted_text(line, color, panel.width - 48, (font_tiny,))
        surface.blit(text, (panel.x + 24, line_y))
        line_y += 22

    hint_panel = pygame.Rect(panel.x + 24, panel.bottom - 52, panel.width - 48, 28)
    pygame.draw.rect(surface, (18, 18, 28), hint_panel, border_radius=5)
    pygame.draw.rect(surface, accent_color, hint_panel, 1, border_radius=5)
    hint = render_fitted_text("Select an action. LOG opens from this menu; BACK closes it.", (210, 215, 225), hint_panel.width - 18, (font_tiny,))
    surface.blit(hint, (hint_panel.x + 9, hint_panel.y + 7))

    for index, button in enumerate(buttons):
        button.selected = index == selected_index
        button.draw(surface)


def draw_interior_message_panel(
    surface,
    room,
    message,
    message_color,
    nearby_inspect,
    player_near_npc,
    android_mode,
    font_tiny,
    ui_bg,
    screen_height,
    wrap_text_to_width,
    render_fitted_text,
):
    """Draw the bottom room dialogue/prompt panel.

    Beginner note:
        `message` is already chosen by `main.py`. This helper only wraps and
        draws it, then prints the correct Android or keyboard prompt.
    """
    accent_color = room["accent_color"]
    message_panel = pygame.Rect(145, screen_height - 84, 710, 56)
    pygame.draw.rect(surface, ui_bg, message_panel, border_radius=8)
    pygame.draw.rect(surface, accent_color, message_panel, 2, border_radius=8)

    message_lines = wrap_text_to_width(message, font_tiny, message_panel.width - 34)
    line_y = message_panel.y + 7
    for line in message_lines[:2]:
        message_text = font_tiny.render(line, True, message_color)
        surface.blit(message_text, (message_panel.centerx - message_text.get_width() // 2, line_y))
        line_y += 19

    # Keep the left service action and right navigation hint in separate lanes.
    # That prevents long Android prompts from drawing over the service text.
    prompt_width = 315
    exit_width = 330
    prompt_text = render_fitted_text(room["service_prompt"], accent_color, prompt_width, (font_tiny,))
    if android_mode:
        if player_near_npc:
            exit_label = "OK: talk   MENU: log/save/load   exit mat: leave"
        elif nearby_inspect:
            exit_label = f"OK: inspect {nearby_inspect['label']}"
        else:
            exit_label = "OK or exit mat: leave to town"
    else:
        if player_near_npc:
            exit_label = "ENTER: talk   ESC/exit mat: leave"
        elif nearby_inspect:
            exit_label = f"ENTER: inspect {nearby_inspect['label']}"
        else:
            exit_label = "ENTER/ESC: exit to town"

    exit_text = render_fitted_text(exit_label, (200, 200, 210), exit_width, (font_tiny,))
    surface.blit(prompt_text, (message_panel.x + 22, message_panel.y + 34))
    surface.blit(exit_text, (message_panel.right - exit_text.get_width() - 22, message_panel.y + 34))
