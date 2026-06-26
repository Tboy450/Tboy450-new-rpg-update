"""Story dialogue and pause-menu drawing helpers.

Beginner note:
    This module only draws overlays. It does not decide *when* a dialogue
    starts, *which* pause-menu command should run, or *how* the story advances.
    `main.py` still owns that gameplay state.

Why this exists:
    The `Game` class in `main.py` was carrying more and more UI drawing code.
    Moving reusable overlay rendering here trims some of that bulk without
    changing the actual game rules.
"""

import pygame


def _draw_dim_overlay(screen, screen_width, screen_height, alpha):
    """Darken the full screen behind an overlay panel."""
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    screen.blit(overlay, (0, 0))


def draw_story_dialogue_overlay(
    screen,
    dialogue,
    line_text,
    line_index,
    total_lines,
    *,
    font_small,
    font_tiny,
    screen_width,
    screen_height,
    ui_bg,
    text_color,
    android_mode,
    get_story_sprite_path,
    load_sprite_by_height,
    wrap_text_to_width,
):
    """Draw the active story dialogue box with portrait, title, and prompt.

    Beginner note:
        `dialogue` is already selected by `main.py`. This helper only draws the
        current line and the page count. It does not advance the story.
    """
    accent = dialogue.get("color", text_color)

    _draw_dim_overlay(screen, screen_width, screen_height, 135)

    panel = pygame.Rect(80, 430, 840, 210)
    pygame.draw.rect(screen, ui_bg, panel, border_radius=10)
    pygame.draw.rect(screen, accent, panel, 3, border_radius=10)

    portrait_box = pygame.Rect(panel.x + 24, panel.y + 24, 150, 150)
    pygame.draw.rect(screen, (12, 12, 24), portrait_box, border_radius=8)
    pygame.draw.rect(screen, accent, portrait_box, 2, border_radius=8)

    # Portraits use short data keys such as "lion_sage". The asset helper turns
    # that readable key into a real PNG path.
    sprite_path = get_story_sprite_path(dialogue.get("portrait"))
    portrait = load_sprite_by_height(sprite_path, 142) if sprite_path else None
    if portrait:
        portrait_rect = portrait.get_rect(center=portrait_box.center)
        screen.blit(portrait, portrait_rect)

    title = font_small.render(dialogue.get("title", "Story"), True, accent)
    speaker = font_tiny.render(dialogue.get("speaker", ""), True, (255, 245, 180))
    screen.blit(title, (panel.x + 196, panel.y + 24))
    screen.blit(speaker, (panel.x + 198, panel.y + 55))

    text_x = panel.x + 196
    text_y = panel.y + 88
    for wrapped_line in wrap_text_to_width(line_text, font_small, panel.right - text_x - 28):
        rendered = font_small.render(wrapped_line, True, (235, 235, 225))
        screen.blit(rendered, (text_x, text_y))
        text_y += 31

    # Show "current/total" so players know whether NEXT advances one more line
    # or closes the current conversation.
    step_text = f"{line_index + 1}/{total_lines}"
    if android_mode:
        prompt_label = f"NEXT button or ENTER/SPACE   {step_text}"
    else:
        prompt_label = f"ENTER/SPACE: continue   {step_text}"
    prompt = font_tiny.render(prompt_label, True, (200, 200, 210))
    screen.blit(prompt, (panel.right - prompt.get_width() - 24, panel.bottom - 32))


def draw_pause_menu_overlay(
    screen,
    buttons,
    *,
    font_large,
    font_tiny,
    screen_width,
    screen_height,
    ui_bg,
    android_mode,
):
    """Draw the shared pause menu and any already-built button objects.

    Beginner note:
        `main.py` builds the button list and decides what each button does.
        This helper only draws the panel and calls `button.draw(screen)`.
    """
    _draw_dim_overlay(screen, screen_width, screen_height, 170)

    # The menu now includes Inventory in addition to Journal/Map/Save/Load.
    # A taller panel keeps seven buttons inside the border on Android.
    panel = pygame.Rect(screen_width // 2 - 220, 70, 440, 590)
    pygame.draw.rect(screen, ui_bg, panel, border_radius=14)
    pygame.draw.rect(screen, (255, 215, 0), panel, 3, border_radius=14)

    title = font_large.render("PAUSE MENU", True, (255, 215, 0))
    screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 22))

    if android_mode:
        subtitle_text = "Android touch menu: no hardware keyboard required."
    else:
        subtitle_text = "Use arrows + Enter, or click the buttons below."
    subtitle = font_tiny.render(subtitle_text, True, (210, 210, 220))
    screen.blit(subtitle, (panel.centerx - subtitle.get_width() // 2, panel.y + 66))

    for button in buttons:
        button.draw(screen)
