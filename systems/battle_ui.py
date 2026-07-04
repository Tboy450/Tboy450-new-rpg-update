"""Reusable battle-screen UI drawing helpers.

Beginner note:
    The battle screen still draws characters, projectiles, and particles inside
    `main.py` because those visuals depend on many live objects. This module
    owns smaller reusable panels: gear status, battle log, action buttons, and
    result summary.

    Plain-language terms:
    - Panel: a boxed UI area, such as the top battle message box.
    - Surface: a pygame drawing layer. Drawing to a surface changes pixels.
    - Rendered text: text that pygame has turned into an image.
    - Fitted text: text scaled down just enough to stay inside its box.
"""

import pygame

from game_data import get_equipment_item, get_equipment_rarity_color
from systems.assets import get_equipment_icon_path, load_scaled_sprite


def set_button_text(button, text, font, text_color):
    """Change a Button label and rebuild its cached rendered text.

    Beginner note:
        A `Button` stores both the words and the already-drawn text image.
        Changing only `button.text` would not update what appears on screen.
    """
    if button.text == text:
        return
    button.text = text
    button.text_surf = font.render(text, True, text_color)
    button.text_rect = button.text_surf.get_rect(center=button.rect.center)


def draw_battle_gear_strip(
    surface,
    player,
    rect,
    render_fitted_text,
    font_tiny,
    bg_color,
):
    """Draw the player's equipped weapon and effective battle stats.

    Beginner note:
        "Effective" stats include gear bonuses. For example, if base strength is
        8 and a sword gives +3, effective strength is 11.
    """
    weapon_profile = get_equipment_item(player.equipment.get("weapon"))
    weapon_label = weapon_profile.get("label", "Unarmed") if weapon_profile else "Unarmed"
    rarity_color = (
        get_equipment_rarity_color(weapon_profile.get("rarity", "common"))
        if weapon_profile else (210, 210, 225)
    )

    pygame.draw.rect(surface, bg_color, rect, border_radius=5)
    pygame.draw.rect(surface, rarity_color, rect, 2, border_radius=5)

    icon_path = get_equipment_icon_path(weapon_profile.get("icon")) if weapon_profile else None
    icon = load_scaled_sprite(icon_path, 22) if icon_path else None
    if icon:
        surface.blit(icon, (rect.x + 6, rect.y + 4))
    else:
        pygame.draw.circle(surface, rarity_color, (rect.x + 18, rect.centery), 7)

    text_x = rect.x + 34
    gear_text = render_fitted_text(
        (
            f"{weapon_label} | STR {player.effective_strength()} "
            f"DEF {player.effective_defense()} SPD {player.effective_speed()}"
        ),
        (232, 236, 245),
        rect.right - text_x - 8,
        (font_tiny,),
    )
    surface.blit(gear_text, (text_x, rect.y + 8))


def draw_battle_log_panel(
    surface,
    battle_log,
    waiting_for_continue,
    continue_button,
    font_small,
    text_color,
    bg_color,
    border_color,
    log_lines_per_page,
):
    """Draw the top battle log panel and optional NEXT prompt.

    Beginner note:
        The log only shows the newest few lines. Older messages stay in
        `battle_log`, but this panel keeps combat readable on a phone screen.
    """
    panel = pygame.Rect(100, 50, 800, 100)
    pygame.draw.rect(surface, bg_color, panel, border_radius=8)
    pygame.draw.rect(surface, border_color, panel, 3, border_radius=8)

    start_idx = max(0, len(battle_log) - log_lines_per_page)
    end_idx = min(len(battle_log), start_idx + log_lines_per_page)
    for index, log in enumerate(battle_log[start_idx:end_idx]):
        log_text = font_small.render(log, True, text_color)
        if log_text.get_width() > 760:
            scale = 760 / max(1, log_text.get_width())
            log_text = pygame.transform.smoothscale(
                log_text,
                (760, max(16, int(log_text.get_height() * scale))),
            )
        surface.blit(log_text, (120, 70 + index * 30))

    if waiting_for_continue:
        continue_text = font_small.render("(Tap NEXT or press ENTER...)", True, (255, 215, 0))
        surface.blit(continue_text, (120, 70 + log_lines_per_page * 30))
        continue_button.selected = True
        continue_button.draw(surface)


def draw_battle_action_buttons(
    surface,
    battle,
    font_tiny,
    text_color,
    special_cost,
):
    """Draw the visible battle command buttons and their small hint labels.

    Beginner note:
        This helper does not decide what a button does. It only draws whatever
        `BattleScreen.buttons` currently points at: either ATTACK/MAGIC/ITEM
        commands or the Health/Mana/BACK item row.
    """
    if battle.state != "player_turn" or battle.waiting_for_continue or battle.battle_ended:
        return

    # The toggle is always drawn on the player's turn. This gives Android users
    # a small fixed target to reveal commands if the larger row is hidden.
    battle.update_combat_toggle_button_label()
    battle.combat_toggle_button.selected = False
    battle.combat_toggle_button.draw(surface)

    if not battle.combat_buttons_visible:
        return

    # `battle.buttons` can mean either the normal action row or the item row.
    # `battle.menu_mode` below tells us which hint text belongs under it.
    for index, button in enumerate(battle.buttons):
        button.selected = index == battle.selected_option
        button.draw(surface)

    if getattr(battle, "menu_mode", "actions") == "items":
        # Item mode shows Health/Mana/BACK buttons, so it gets one direct hint
        # instead of the normal potion count, MP cost, and escape chance hints.
        item_hint = font_tiny.render("Choose a potion or BACK", True, (220, 220, 180))
        surface.blit(item_hint, (battle.buttons[0].rect.x, battle.buttons[0].rect.bottom + 12))
        return

    bag_text = font_tiny.render(
        f"HP x{battle.player.get_inventory_count('health')}  MP x{battle.player.get_inventory_count('mana')}",
        True,
        (220, 220, 180),
    )
    bag_rect = bag_text.get_rect(center=(battle.buttons[2].rect.centerx, battle.buttons[2].rect.bottom + 14))
    surface.blit(bag_text, bag_rect)

    if battle.special_button_index is not None:
        special_text = font_tiny.render(f"MP {special_cost}", True, (255, 190, 90))
        special_rect = special_text.get_rect(
            center=(battle.buttons[battle.special_button_index].rect.centerx,
                    battle.buttons[battle.special_button_index].rect.bottom + 14)
        )
        surface.blit(special_text, special_rect)

    escape_text = font_tiny.render(f"ESC {int(battle.get_escape_chance() * 100)}%", True, (220, 220, 180))
    escape_rect = escape_text.get_rect(
        center=(battle.buttons[battle.run_button_index].rect.centerx,
                battle.buttons[battle.run_button_index].rect.bottom + 14)
    )
    surface.blit(escape_text, escape_rect)


def draw_battle_summary(
    surface,
    result,
    player,
    continue_button,
    font_large,
    text_color,
    screen_width,
    screen_height,
):
    """Draw the dark victory/defeat/escape overlay after a battle ends.

    Beginner note:
        Rewards are not applied here. This is only the visual "battle finished"
        layer that asks the player to continue.
    """
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    if result == "win":
        summary = [
            "VICTORY!",
            "Rewards apply after continue.",
            f"KILLS: {player.kills}",
            "Tap NEXT or press ENTER...",
        ]
    elif result == "lose":
        summary = [
            "DEFEAT...",
            "Tap NEXT or press ENTER...",
        ]
    else:
        summary = [
            "You Escaped!",
            "Tap NEXT or press ENTER...",
        ]

    for index, line in enumerate(summary):
        text = font_large.render(line, True, text_color)
        surface.blit(text, (screen_width // 2 - text.get_width() // 2, 250 + index * 60))

    continue_button.selected = True
    continue_button.draw(surface)
