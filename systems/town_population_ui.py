"""Drawing helpers for outdoor town residents.

Beginner note:
    Resident facts and quest rewards live in `game_data/town_population.py`.
    This module only draws them. Keeping drawing here prevents `main.py` from
    becoming even larger every time we add a new townsperson.
"""

import math

import pygame


def _shade_color(color, amount):
    """Lighten or darken an RGB color by a signed amount."""
    return tuple(max(0, min(255, channel + amount)) for channel in color)


def draw_town_residents(
    surface,
    residents,
    nearby_key,
    completed_errands,
    game_time,
    font_tiny,
    ui_bg,
):
    """Draw all outdoor town residents and the nearby talk prompt.

    `residents` is an iterable of `(resident_key, resident_profile)` pairs.
    Coordinates are local town-screen pixels. The town screen itself is already
    drawn in local coordinates, so this helper does not need camera math.

    Beginner note:
        `nearby_key` is the one resident the player can currently talk to.
        `completed_errands` changes quest marker color after that resident's
        errand is finished.
    """
    completed_errands = set(completed_errands or ())
    for index, (resident_key, resident) in enumerate(residents):
        x, y = resident["local_position"]
        bob = math.sin(game_time * 0.08 + index * 1.7) * 2
        body_color = resident.get("color", (120, 120, 160))
        accent = resident.get("accent_color", (255, 230, 150))
        # Completed controls marker color. Nearby controls the larger talk
        # prompt. Keeping these separate lets a completed resident still be
        # talkable without pretending they have a new quest.
        completed = resident.get("quest_key") in completed_errands
        nearby = resident_key == nearby_key

        foot_y = int(y + bob)
        pygame.draw.ellipse(surface, (18, 16, 18), (x - 18, foot_y + 34, 42, 13))
        pygame.draw.rect(surface, _shade_color(body_color, -28), (x - 13, foot_y + 2, 26, 38), border_radius=7)
        pygame.draw.rect(surface, body_color, (x - 12, foot_y, 24, 38), border_radius=7)
        pygame.draw.rect(surface, accent, (x - 11, foot_y + 9, 22, 6), border_radius=3)
        pygame.draw.circle(surface, (224, 176, 130), (x, foot_y - 9), 13)
        pygame.draw.circle(surface, _shade_color(body_color, -45), (x, foot_y - 14), 14, 4)
        pygame.draw.circle(surface, (24, 24, 30), (x - 4, foot_y - 10), 2)
        pygame.draw.circle(surface, (24, 24, 30), (x + 4, foot_y - 10), 2)

        # Green means this resident's errand is done; gold means there may be
        # something new or unfinished.
        marker_color = (120, 230, 150) if completed else (255, 215, 92)
        if nearby:
            pygame.draw.circle(surface, marker_color, (x, foot_y - 44), 11)
            pygame.draw.circle(surface, ui_bg, (x, foot_y - 44), 5)
        else:
            pygame.draw.circle(surface, marker_color, (x, foot_y - 40), 5)

        name_text = font_tiny.render(resident["name"], True, accent if nearby else (220, 220, 210))
        surface.blit(name_text, (x - name_text.get_width() // 2, foot_y + 50))

        if nearby:
            prompt = font_tiny.render(resident.get("prompt", "OK: talk"), True, (255, 245, 180))
            panel_w = prompt.get_width() + 24
            panel = pygame.Rect(int(x - panel_w / 2), foot_y + 72, panel_w, 28)
            pygame.draw.rect(surface, ui_bg, panel, border_radius=6)
            pygame.draw.rect(surface, marker_color, panel, 2, border_radius=6)
            surface.blit(prompt, (panel.x + 12, panel.y + 6))
