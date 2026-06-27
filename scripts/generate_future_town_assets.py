"""Generate unused future town scenery sprites.

This script creates transparent PNG files for the future asset library. The
game does not load these images yet; they are a labeled shelf of sprites that
can be moved into active gameplay later.

Beginner note:

- A "sprite" is a small image that the game can draw on the screen.
- These sprites use transparent backgrounds, so only the object appears.
- The helper functions below draw simple pixel-art shapes with rectangles,
  lines, circles, and polygons.
- No extra Python package is required. The PNG writer uses the standard library
  so the script can run on a clean Python install.
"""

from __future__ import annotations

from pathlib import Path
import math
import struct
import zlib


ROOT = Path(__file__).resolve().parents[1]
OUTDOOR_DIR = ROOT / "assets" / "processed" / "future_assets" / "scenery" / "outdoor"
INDOOR_DIR = ROOT / "assets" / "processed" / "future_assets" / "scenery" / "indoor"


TRANSPARENT = (0, 0, 0, 0)
INK = (24, 18, 24, 255)
INK_SOFT = (45, 35, 44, 255)
WOOD_DARK = (78, 46, 24, 255)
WOOD = (126, 79, 38, 255)
WOOD_LIGHT = (176, 119, 56, 255)
STONE_DARK = (70, 68, 72, 255)
STONE = (118, 114, 116, 255)
STONE_LIGHT = (178, 174, 166, 255)
GOLD = (229, 171, 60, 255)
GOLD_LIGHT = (255, 219, 116, 255)
RED = (160, 42, 38, 255)
CRIMSON = (105, 24, 40, 255)
TEAL = (52, 177, 167, 255)
TEAL_LIGHT = (131, 235, 223, 255)
BLUE = (40, 71, 132, 255)
PURPLE = (112, 62, 157, 255)
GREEN = (78, 138, 70, 255)
SAGE = (132, 166, 105, 255)
PARCHMENT = (218, 191, 134, 255)
PARCHMENT_DARK = (154, 118, 72, 255)
FIRE_ORANGE = (255, 117, 28, 255)
FIRE_YELLOW = (255, 224, 88, 255)
SHADOW = (0, 0, 0, 85)


class Canvas:
    """Tiny RGBA drawing surface for crisp pixel-art sprites."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.pixels = [[TRANSPARENT for _ in range(width)] for _ in range(height)]

    def set_pixel(self, x: int, y: int, color: tuple[int, int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = color

    def rect(self, x: int, y: int, width: int, height: int, color: tuple[int, int, int, int]) -> None:
        for yy in range(y, y + height):
            for xx in range(x, x + width):
                self.set_pixel(xx, yy, color)

    def outline_rect(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        fill: tuple[int, int, int, int],
        outline: tuple[int, int, int, int] = INK,
        border: int = 3,
    ) -> None:
        self.rect(x, y, width, height, outline)
        self.rect(x + border, y + border, width - border * 2, height - border * 2, fill)

    def line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: tuple[int, int, int, int],
        width: int = 1,
    ) -> None:
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        x = x1
        y = y1
        while True:
            radius = max(0, width // 2)
            for yy in range(y - radius, y + radius + 1):
                for xx in range(x - radius, x + radius + 1):
                    self.set_pixel(xx, yy, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def polygon(self, points: list[tuple[int, int]], color: tuple[int, int, int, int]) -> None:
        if not points:
            return
        min_y = max(0, min(y for _, y in points))
        max_y = min(self.height - 1, max(y for _, y in points))
        for y in range(min_y, max_y + 1):
            nodes: list[int] = []
            j = len(points) - 1
            for i, (xi, yi) in enumerate(points):
                xj, yj = points[j]
                if (yi < y <= yj) or (yj < y <= yi):
                    nodes.append(int(xi + (y - yi) / (yj - yi) * (xj - xi)))
                j = i
            nodes.sort()
            for a, b in zip(nodes[0::2], nodes[1::2]):
                for x in range(a, b + 1):
                    self.set_pixel(x, y, color)

    def circle(self, cx: int, cy: int, radius: int, color: tuple[int, int, int, int]) -> None:
        r2 = radius * radius
        for y in range(cy - radius, cy + radius + 1):
            for x in range(cx - radius, cx + radius + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    self.set_pixel(x, y, color)

    def ellipse(
        self,
        cx: int,
        cy: int,
        rx: int,
        ry: int,
        color: tuple[int, int, int, int],
    ) -> None:
        if rx <= 0 or ry <= 0:
            return
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) ** 2) / (rx * rx) + ((y - cy) ** 2) / (ry * ry) <= 1:
                    self.set_pixel(x, y, color)

    def save_png(self, path: Path) -> None:
        """Write this canvas as a simple RGBA PNG file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        raw_rows = []
        for row in self.pixels:
            raw_rows.append(b"\x00" + b"".join(bytes(pixel) for pixel in row))
        raw = b"".join(raw_rows)

        def chunk(tag: bytes, data: bytes) -> bytes:
            return (
                struct.pack(">I", len(data))
                + tag
                + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            )

        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 6, 0, 0, 0))
        png += chunk(b"IDAT", zlib.compress(raw, 9))
        png += chunk(b"IEND", b"")
        path.write_bytes(png)


def draw_shadow(c: Canvas, x: int, y: int, width: int, height: int) -> None:
    """Soft base shadow so a prop reads as sitting on the ground."""
    c.ellipse(x + width // 2, y + height // 2, width // 2, height // 2, SHADOW)


def draw_roof(c: Canvas, points: list[tuple[int, int]], fill: tuple[int, int, int, int]) -> None:
    c.polygon(points, INK)
    inset = [(x, y + 4 if y < max(py for _, py in points) else y - 2) for x, y in points]
    c.polygon(inset, fill)


def draw_plank_wall(c: Canvas, x: int, y: int, width: int, height: int) -> None:
    c.outline_rect(x, y, width, height, WOOD, INK, 4)
    for xx in range(x + 12, x + width - 8, 16):
        c.line(xx, y + 5, xx, y + height - 5, WOOD_DARK, 2)
    for yy in range(y + 12, y + height - 8, 18):
        c.line(x + 5, yy, x + width - 6, yy, WOOD_LIGHT, 1)


def draw_window(c: Canvas, x: int, y: int, width: int = 16, height: int = 14) -> None:
    c.outline_rect(x, y, width, height, BLUE, INK, 2)
    c.rect(x + 3, y + 3, width - 6, 3, TEAL_LIGHT)
    c.line(x + width // 2, y + 2, x + width // 2, y + height - 3, INK_SOFT, 1)


def draw_door(c: Canvas, x: int, y: int, width: int = 18, height: int = 28) -> None:
    c.outline_rect(x, y, width, height, WOOD_DARK, INK, 2)
    c.rect(x + 3, y + 3, width - 6, 4, WOOD_LIGHT)
    c.circle(x + width - 5, y + height // 2, 2, GOLD_LIGHT)


def add_sparkles(c: Canvas, points: list[tuple[int, int]], color: tuple[int, int, int, int] = GOLD_LIGHT) -> None:
    for x, y in points:
        c.line(x - 2, y, x + 2, y, color, 1)
        c.line(x, y - 2, x, y + 2, color, 1)


def asset_tavern_front() -> Canvas:
    c = Canvas(112, 96)
    draw_shadow(c, 18, 82, 76, 9)
    draw_plank_wall(c, 18, 40, 76, 43)
    draw_roof(c, [(12, 42), (56, 14), (100, 42)], CRIMSON)
    draw_window(c, 27, 50)
    draw_window(c, 69, 50)
    draw_door(c, 47, 55, 18, 28)
    c.outline_rect(34, 31, 44, 13, PARCHMENT, INK, 2)
    c.rect(43, 34, 26, 3, GOLD)
    c.circle(56, 38, 3, FIRE_ORANGE)
    add_sparkles(c, [(80, 27), (28, 33)])
    return c


def asset_shop_front() -> Canvas:
    c = Canvas(112, 96)
    draw_shadow(c, 14, 82, 84, 9)
    draw_plank_wall(c, 20, 38, 72, 45)
    draw_roof(c, [(15, 39), (56, 16), (97, 39)], BLUE)
    c.outline_rect(22, 39, 68, 12, PARCHMENT, INK, 2)
    c.rect(28, 43, 14, 4, RED)
    c.rect(48, 43, 14, 4, TEAL)
    c.rect(68, 43, 14, 4, GOLD)
    draw_window(c, 30, 56, 16, 13)
    draw_window(c, 66, 56, 16, 13)
    draw_door(c, 48, 55, 16, 28)
    return c


def asset_town_hall_front() -> Canvas:
    c = Canvas(128, 96)
    draw_shadow(c, 20, 85, 88, 9)
    c.outline_rect(24, 32, 80, 52, STONE, INK, 4)
    draw_roof(c, [(16, 34), (64, 10), (112, 34)], STONE_DARK)
    c.rect(33, 44, 12, 38, STONE_LIGHT)
    c.rect(58, 44, 12, 38, STONE_LIGHT)
    c.rect(83, 44, 12, 38, STONE_LIGHT)
    draw_door(c, 54, 57, 20, 27)
    c.outline_rect(46, 29, 36, 13, PARCHMENT, INK, 2)
    c.circle(64, 35, 4, GOLD_LIGHT)
    c.line(64, 18, 64, 9, INK, 2)
    c.polygon([(64, 9), (82, 14), (64, 19)], RED)
    return c


def asset_healer_clinic_front() -> Canvas:
    c = Canvas(112, 96)
    draw_shadow(c, 18, 82, 76, 9)
    c.outline_rect(22, 38, 68, 45, STONE_LIGHT, INK, 4)
    draw_roof(c, [(16, 40), (56, 13), (96, 40)], SAGE)
    draw_door(c, 48, 56, 17, 27)
    draw_window(c, 29, 54, 15, 14)
    draw_window(c, 70, 54, 15, 14)
    c.outline_rect(46, 28, 22, 18, PARCHMENT, INK, 2)
    c.rect(55, 31, 4, 12, TEAL)
    c.rect(50, 35, 14, 4, TEAL)
    add_sparkles(c, [(75, 23), (36, 24)], TEAL_LIGHT)
    return c


def asset_blacksmith_stall() -> Canvas:
    c = Canvas(112, 80)
    draw_shadow(c, 16, 68, 78, 8)
    c.rect(21, 24, 6, 43, WOOD_DARK)
    c.rect(84, 24, 6, 43, WOOD_DARK)
    draw_roof(c, [(15, 28), (56, 10), (97, 28), (89, 38), (23, 38)], CRIMSON)
    c.outline_rect(28, 43, 55, 22, WOOD, INK, 3)
    c.outline_rect(37, 34, 16, 12, STONE_DARK, INK, 2)
    c.circle(45, 40, 5, FIRE_ORANGE)
    c.circle(45, 39, 3, FIRE_YELLOW)
    c.line(60, 39, 79, 33, STONE_LIGHT, 3)
    c.line(64, 37, 73, 31, INK, 1)
    c.rect(57, 50, 18, 5, STONE)
    return c


def asset_market_canopy() -> Canvas:
    c = Canvas(112, 72)
    draw_shadow(c, 16, 62, 78, 7)
    c.rect(19, 22, 5, 40, WOOD_DARK)
    c.rect(88, 22, 5, 40, WOOD_DARK)
    c.polygon([(13, 24), (56, 8), (99, 24), (92, 34), (20, 34)], INK)
    for i, color in enumerate([RED, PARCHMENT, TEAL, PARCHMENT, RED]):
        c.polygon([(19 + i * 15, 25), (30 + i * 13, 18), (34 + i * 15, 25), (33 + i * 15, 33), (18 + i * 15, 33)], color)
    c.outline_rect(27, 43, 58, 18, WOOD, INK, 3)
    c.circle(40, 40, 5, GOLD)
    c.circle(57, 39, 5, GREEN)
    c.circle(72, 40, 5, FIRE_ORANGE)
    return c


def asset_stone_well() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 9, 55, 46, 6)
    c.rect(16, 27, 32, 26, INK)
    for y, color in [(30, STONE_LIGHT), (38, STONE), (46, STONE_DARK)]:
        c.rect(19, y, 26, 6, color)
        c.line(31, y, 31, y + 5, INK_SOFT, 1)
    c.ellipse(32, 27, 18, 7, INK)
    c.ellipse(32, 27, 14, 4, BLUE)
    c.line(14, 27, 21, 9, WOOD_DARK, 3)
    c.line(50, 27, 43, 9, WOOD_DARK, 3)
    c.line(21, 9, 43, 9, WOOD_DARK, 3)
    c.rect(29, 12, 6, 8, WOOD)
    c.circle(32, 16, 4, STONE)
    return c


def asset_notice_board() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 12, 56, 40, 5)
    c.rect(29, 34, 6, 23, WOOD_DARK)
    c.outline_rect(11, 15, 42, 29, WOOD, INK, 3)
    for x, y, w, h in [(17, 21, 12, 8), (32, 20, 13, 9), (20, 32, 24, 6)]:
        c.outline_rect(x, y, w, h, PARCHMENT, PARCHMENT_DARK, 1)
    c.circle(18, 22, 1, RED)
    c.circle(35, 21, 1, TEAL)
    c.rect(14, 13, 36, 5, WOOD_LIGHT)
    return c


def asset_lamp_post() -> Canvas:
    c = Canvas(64, 96)
    draw_shadow(c, 20, 86, 24, 5)
    c.rect(30, 35, 5, 51, INK)
    c.rect(31, 36, 3, 49, WOOD_DARK)
    c.line(32, 35, 44, 28, INK, 3)
    c.line(20, 32, 32, 35, INK, 3)
    c.outline_rect(20, 19, 18, 18, FIRE_YELLOW, INK, 3)
    c.rect(24, 23, 10, 9, FIRE_ORANGE)
    c.outline_rect(42, 17, 16, 18, FIRE_YELLOW, INK, 3)
    c.rect(46, 21, 8, 9, FIRE_ORANGE)
    c.rect(24, 84, 17, 5, STONE)
    return c


def asset_flower_planter() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 12, 52, 40, 5)
    c.outline_rect(13, 36, 38, 15, WOOD, INK, 3)
    c.rect(18, 33, 28, 6, SAGE)
    for x, y, color in [(19, 31, RED), (27, 28, TEAL), (35, 30, GOLD), (43, 29, PURPLE)]:
        c.line(x, y + 4, x, 38, GREEN, 1)
        c.circle(x, y, 4, color)
        c.circle(x + 1, y - 1, 2, PARCHMENT)
    return c


def asset_crate_stack() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 11, 55, 42, 5)
    for x, y in [(10, 33), (31, 34), (20, 16)]:
        c.outline_rect(x, y, 24, 22, WOOD, INK, 3)
        c.line(x + 4, y + 4, x + 19, y + 17, WOOD_LIGHT, 2)
        c.line(x + 19, y + 4, x + 4, y + 17, WOOD_DARK, 2)
    return c


def asset_barrel_stack() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 10, 55, 44, 5)
    for cx, cy in [(22, 40), (42, 40), (32, 23)]:
        c.ellipse(cx, cy, 12, 17, INK)
        c.ellipse(cx, cy, 9, 14, WOOD)
        c.line(cx - 8, cy - 8, cx + 8, cy - 8, WOOD_LIGHT, 2)
        c.line(cx - 9, cy + 8, cx + 9, cy + 8, WOOD_DARK, 2)
        c.rect(cx - 2, cy - 14, 4, 28, WOOD_DARK)
    return c


def asset_cobblestone_patch() -> Canvas:
    c = Canvas(96, 64)
    c.ellipse(48, 43, 40, 16, SHADOW)
    stones = [
        (13, 27, 20, 11),
        (36, 25, 19, 12),
        (58, 27, 24, 11),
        (20, 40, 23, 12),
        (46, 40, 19, 10),
        (68, 39, 17, 11),
    ]
    for i, (x, y, w, h) in enumerate(stones):
        c.outline_rect(x, y, w, h, STONE_LIGHT if i % 2 else STONE, INK_SOFT, 2)
    return c


def asset_lion_fountain() -> Canvas:
    c = Canvas(96, 96)
    draw_shadow(c, 16, 83, 64, 8)
    c.ellipse(48, 74, 35, 12, INK)
    c.ellipse(48, 72, 31, 9, STONE)
    c.ellipse(48, 68, 24, 7, BLUE)
    c.rect(37, 39, 22, 31, STONE_DARK)
    c.circle(48, 33, 18, GOLD)
    c.circle(48, 34, 12, STONE_LIGHT)
    c.circle(42, 32, 2, INK)
    c.circle(54, 32, 2, INK)
    c.rect(45, 38, 6, 4, INK)
    c.line(48, 42, 48, 61, TEAL_LIGHT, 3)
    c.line(39, 52, 31, 65, TEAL_LIGHT, 2)
    c.line(57, 52, 65, 65, TEAL_LIGHT, 2)
    return c


def asset_bookshelf_full() -> Canvas:
    c = Canvas(64, 96)
    draw_shadow(c, 10, 86, 44, 5)
    c.outline_rect(11, 12, 42, 73, WOOD_DARK, INK, 3)
    for y in [26, 45, 64]:
        c.rect(15, y, 34, 3, WOOD_LIGHT)
    book_colors = [RED, BLUE, TEAL, GOLD, PURPLE, PARCHMENT]
    for row, y in enumerate([17, 31, 50, 69]):
        x = 16
        for i in range(5):
            w = 4 + (i + row) % 4
            h = 8 + (i * 2 + row) % 6
            c.rect(x, y + (12 - h), w, h, book_colors[(i + row) % len(book_colors)])
            c.line(x, y + (12 - h), x, y + 11, INK_SOFT, 1)
            x += w + 2
    return c


def asset_potion_shelf() -> Canvas:
    c = Canvas(64, 96)
    draw_shadow(c, 10, 86, 44, 5)
    c.outline_rect(12, 14, 40, 70, WOOD, INK, 3)
    for y in [33, 53, 72]:
        c.rect(16, y, 32, 3, WOOD_DARK)
    for x, y, color in [(20, 25, TEAL), (33, 24, PURPLE), (43, 25, FIRE_ORANGE), (23, 45, RED), (38, 44, BLUE), (28, 64, SAGE), (42, 64, GOLD)]:
        c.outline_rect(x, y, 7, 9, color, INK_SOFT, 1)
        c.rect(x + 2, y - 3, 3, 3, PARCHMENT)
        c.set_pixel(x + 2, y + 2, TEAL_LIGHT)
    add_sparkles(c, [(51, 20), (16, 66)], TEAL_LIGHT)
    return c


def asset_tavern_bar_counter() -> Canvas:
    c = Canvas(128, 64)
    draw_shadow(c, 18, 55, 92, 5)
    c.outline_rect(16, 27, 96, 27, WOOD_DARK, INK, 3)
    c.rect(21, 32, 86, 5, WOOD_LIGHT)
    for x in [34, 58, 82]:
        c.line(x, 32, x, 51, INK_SOFT, 2)
    c.outline_rect(29, 17, 13, 12, GOLD, INK, 2)
    c.outline_rect(50, 15, 11, 14, RED, INK, 2)
    c.outline_rect(70, 17, 12, 12, TEAL, INK, 2)
    c.rect(93, 19, 8, 9, PARCHMENT)
    c.rect(95, 16, 4, 4, FIRE_YELLOW)
    return c


def asset_shop_counter() -> Canvas:
    c = Canvas(112, 64)
    draw_shadow(c, 17, 55, 78, 5)
    c.outline_rect(18, 30, 76, 24, WOOD, INK, 3)
    c.rect(23, 35, 66, 5, WOOD_LIGHT)
    c.outline_rect(30, 19, 16, 12, PARCHMENT, INK, 2)
    c.circle(58, 24, 7, GOLD)
    c.circle(74, 24, 7, TEAL)
    c.line(58, 18, 58, 30, INK_SOFT, 1)
    c.line(74, 18, 74, 30, INK_SOFT, 1)
    c.rect(82, 20, 8, 9, CRIMSON)
    return c


def asset_scroll_desk() -> Canvas:
    c = Canvas(96, 64)
    draw_shadow(c, 16, 55, 64, 5)
    c.outline_rect(18, 29, 60, 21, WOOD_DARK, INK, 3)
    c.polygon([(15, 29), (81, 29), (72, 18), (24, 18)], INK)
    c.polygon([(21, 27), (75, 27), (69, 21), (27, 21)], WOOD_LIGHT)
    c.outline_rect(32, 18, 31, 13, PARCHMENT, PARCHMENT_DARK, 1)
    c.line(36, 23, 56, 23, INK_SOFT, 1)
    c.line(36, 27, 52, 27, INK_SOFT, 1)
    c.line(66, 16, 75, 10, INK, 2)
    c.line(67, 16, 76, 22, FIRE_ORANGE, 2)
    return c


def asset_town_hall_dais() -> Canvas:
    c = Canvas(128, 64)
    draw_shadow(c, 18, 55, 92, 5)
    c.outline_rect(16, 34, 96, 19, STONE_DARK, INK, 3)
    c.outline_rect(28, 24, 72, 15, STONE, INK, 3)
    c.outline_rect(45, 14, 38, 14, WOOD_DARK, INK, 2)
    c.circle(64, 21, 5, GOLD_LIGHT)
    c.line(64, 11, 64, 5, INK, 2)
    c.polygon([(64, 5), (78, 10), (64, 14)], RED)
    c.rect(22, 39, 84, 4, STONE_LIGHT)
    return c


def asset_round_tavern_table() -> Canvas:
    c = Canvas(64, 64)
    draw_shadow(c, 12, 53, 40, 6)
    c.rect(29, 35, 6, 18, WOOD_DARK)
    c.ellipse(32, 31, 23, 13, INK)
    c.ellipse(32, 29, 20, 10, WOOD)
    c.line(15, 29, 49, 29, WOOD_LIGHT, 2)
    c.circle(23, 26, 4, GOLD)
    c.outline_rect(37, 22, 7, 10, TEAL, INK_SOFT, 1)
    return c


def asset_inn_bed() -> Canvas:
    c = Canvas(96, 64)
    draw_shadow(c, 12, 55, 72, 5)
    c.outline_rect(14, 26, 68, 24, WOOD_DARK, INK, 3)
    c.outline_rect(20, 20, 22, 17, PARCHMENT, INK, 2)
    c.outline_rect(41, 23, 37, 20, BLUE, INK, 2)
    c.rect(45, 27, 29, 6, TEAL)
    c.rect(14, 21, 6, 32, WOOD_LIGHT)
    c.rect(78, 21, 6, 32, WOOD_LIGHT)
    return c


def asset_weapon_rack() -> Canvas:
    c = Canvas(96, 64)
    draw_shadow(c, 15, 55, 66, 5)
    c.rect(18, 23, 60, 5, WOOD_DARK)
    c.rect(18, 45, 60, 5, WOOD_DARK)
    c.rect(24, 18, 5, 37, WOOD)
    c.rect(68, 18, 5, 37, WOOD)
    c.line(40, 16, 40, 52, STONE_LIGHT, 3)
    c.polygon([(40, 8), (35, 18), (45, 18)], STONE_LIGHT)
    c.line(54, 18, 66, 50, GOLD, 3)
    c.line(49, 27, 59, 24, INK, 2)
    c.line(31, 35, 56, 35, STONE_LIGHT, 3)
    c.polygon([(60, 35), (53, 30), (53, 40)], STONE_LIGHT)
    return c


def asset_armor_stand() -> Canvas:
    c = Canvas(64, 96)
    draw_shadow(c, 13, 86, 38, 5)
    c.rect(30, 18, 4, 64, WOOD_DARK)
    c.rect(19, 82, 26, 5, WOOD_DARK)
    c.circle(32, 19, 9, STONE_LIGHT)
    c.rect(23, 29, 18, 22, STONE)
    c.rect(18, 32, 7, 18, STONE_LIGHT)
    c.rect(40, 32, 7, 18, STONE_LIGHT)
    c.polygon([(23, 52), (41, 52), (37, 72), (27, 72)], STONE_DARK)
    c.line(32, 30, 32, 70, INK_SOFT, 1)
    c.rect(25, 35, 14, 4, TEAL)
    return c


def asset_hearth_fireplace() -> Canvas:
    c = Canvas(96, 96)
    draw_shadow(c, 16, 84, 64, 7)
    c.outline_rect(18, 32, 60, 48, STONE_DARK, INK, 4)
    c.rect(26, 40, 44, 32, INK)
    c.rect(22, 26, 52, 9, STONE_LIGHT)
    c.rect(38, 17, 20, 14, STONE)
    c.rect(41, 10, 14, 10, STONE_DARK)
    c.line(34, 70, 63, 55, WOOD, 4)
    c.line(62, 70, 35, 54, WOOD_DARK, 4)
    c.circle(48, 59, 14, FIRE_ORANGE)
    c.circle(49, 56, 8, FIRE_YELLOW)
    c.polygon([(48, 42), (39, 61), (56, 61)], FIRE_YELLOW)
    add_sparkles(c, [(69, 43), (27, 46), (65, 66)], FIRE_YELLOW)
    return c


def asset_medical_ribbon_rug() -> Canvas:
    c = Canvas(96, 64)
    c.ellipse(48, 36, 40, 18, CRIMSON)
    c.ellipse(48, 36, 34, 14, RED)
    c.rect(28, 31, 40, 10, PARCHMENT)
    c.rect(43, 20, 10, 31, PARCHMENT)
    c.rect(31, 34, 34, 4, TEAL)
    c.rect(46, 23, 4, 25, TEAL)
    c.line(14, 35, 26, 35, GOLD, 2)
    c.line(70, 35, 82, 35, GOLD, 2)
    return c


ASSETS = {
    OUTDOOR_DIR / "tavern_front.png": asset_tavern_front,
    OUTDOOR_DIR / "shop_front.png": asset_shop_front,
    OUTDOOR_DIR / "town_hall_front.png": asset_town_hall_front,
    OUTDOOR_DIR / "healer_clinic_front.png": asset_healer_clinic_front,
    OUTDOOR_DIR / "blacksmith_stall.png": asset_blacksmith_stall,
    OUTDOOR_DIR / "market_canopy.png": asset_market_canopy,
    OUTDOOR_DIR / "stone_well.png": asset_stone_well,
    OUTDOOR_DIR / "notice_board.png": asset_notice_board,
    OUTDOOR_DIR / "lamp_post.png": asset_lamp_post,
    OUTDOOR_DIR / "flower_planter.png": asset_flower_planter,
    OUTDOOR_DIR / "crate_stack.png": asset_crate_stack,
    OUTDOOR_DIR / "barrel_stack.png": asset_barrel_stack,
    OUTDOOR_DIR / "cobblestone_patch.png": asset_cobblestone_patch,
    OUTDOOR_DIR / "lion_fountain.png": asset_lion_fountain,
    INDOOR_DIR / "bookshelf_full.png": asset_bookshelf_full,
    INDOOR_DIR / "potion_shelf.png": asset_potion_shelf,
    INDOOR_DIR / "tavern_bar_counter.png": asset_tavern_bar_counter,
    INDOOR_DIR / "shop_counter.png": asset_shop_counter,
    INDOOR_DIR / "scroll_desk.png": asset_scroll_desk,
    INDOOR_DIR / "town_hall_dais.png": asset_town_hall_dais,
    INDOOR_DIR / "round_tavern_table.png": asset_round_tavern_table,
    INDOOR_DIR / "inn_bed.png": asset_inn_bed,
    INDOOR_DIR / "weapon_rack.png": asset_weapon_rack,
    INDOOR_DIR / "armor_stand.png": asset_armor_stand,
    INDOOR_DIR / "hearth_fireplace.png": asset_hearth_fireplace,
    INDOOR_DIR / "medical_ribbon_rug.png": asset_medical_ribbon_rug,
}


def main() -> None:
    for path, make_canvas in ASSETS.items():
        make_canvas().save_png(path)
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
