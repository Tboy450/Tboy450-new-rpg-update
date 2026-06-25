"""Split a green-screen NPC sheet into transparent future NPC sprites.

Beginner note:
    This script is for imported art that already has a bright green background.
    It does three things:

    1. Reads a PNG sprite sheet.
    2. Splits it into left/right halves.
    3. Removes only the connected green background, then crops each sprite.

Why "connected" background matters:
    Some fantasy art may contain small green details, jewels, bottles, or glow
    effects. If we deleted every green pixel, those details could disappear.
    Instead, this script flood-fills green pixels that touch the outside edge.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import argparse
import struct
import zlib


RGBA = tuple[int, int, int, int]


def paeth_predictor(a: int, b: int, c: int) -> int:
    """PNG filter helper used by filter type 4."""
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def read_png_rgba(path: Path) -> tuple[int, int, list[list[RGBA]]]:
    """Read a non-interlaced 8-bit RGB/RGBA PNG into RGBA pixels."""
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError(f"{path} is not a PNG file")

    pos = 8
    width = height = color_type = None
    idat = b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height, bit_depth, color_type, compression, filt, interlace = struct.unpack(
                ">IIBBBBB",
                chunk,
            )
            if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
                raise ValueError("Only non-interlaced 8-bit RGB/RGBA PNGs are supported")
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break

    if width is None or height is None or color_type is None:
        raise ValueError("PNG missing IHDR")

    channels = 4 if color_type == 6 else 3
    row_bytes = width * channels
    raw = zlib.decompress(idat)
    rows: list[bytes] = []
    prior = bytearray(row_bytes)
    offset = 0

    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        scanline = bytearray(raw[offset:offset + row_bytes])
        offset += row_bytes

        for i in range(row_bytes):
            left = scanline[i - channels] if i >= channels else 0
            up = prior[i]
            up_left = prior[i - channels] if i >= channels else 0

            if filter_type == 0:
                value = scanline[i]
            elif filter_type == 1:
                value = (scanline[i] + left) & 0xFF
            elif filter_type == 2:
                value = (scanline[i] + up) & 0xFF
            elif filter_type == 3:
                value = (scanline[i] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                value = (scanline[i] + paeth_predictor(left, up, up_left)) & 0xFF
            else:
                raise ValueError(f"Unsupported PNG filter type {filter_type}")
            scanline[i] = value

        rows.append(bytes(scanline))
        prior = scanline

    pixels: list[list[RGBA]] = []
    for row in rows:
        out_row: list[RGBA] = []
        for x in range(width):
            i = x * channels
            if channels == 4:
                out_row.append((row[i], row[i + 1], row[i + 2], row[i + 3]))
            else:
                out_row.append((row[i], row[i + 1], row[i + 2], 255))
        pixels.append(out_row)

    return width, height, pixels


def write_png_rgba(path: Path, pixels: list[list[RGBA]]) -> None:
    """Write RGBA pixels as a simple non-interlaced PNG."""
    path.parent.mkdir(parents=True, exist_ok=True)
    height = len(pixels)
    width = len(pixels[0]) if height else 0
    raw_rows = [b"\x00" + b"".join(bytes(pixel) for pixel in row) for row in pixels]
    raw = b"".join(raw_rows)

    def chunk(tag: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + tag
            + payload
            + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def is_background_green(pixel: RGBA, key: tuple[int, int, int]) -> bool:
    """Return True when a pixel is close to the green-screen color."""
    r, g, b, _ = pixel
    key_r, key_g, key_b = key
    distance = abs(r - key_r) + abs(g - key_g) + abs(b - key_b)
    return (
        g > 115
        and g > r + 45
        and g > b + 45
        and distance < 150
    )


def is_strong_chroma_green(pixel: RGBA, key: tuple[int, int, int]) -> bool:
    """Return True for obvious pure green-screen islands.

    Beginner note:
        The flood fill removes green connected to the outside edge. Some sheets
        have trapped green holes between a character, a prop, and a sign. This
        stricter check removes those pure background holes without deleting
        darker intentional green details such as potions or magical glow.
    """
    r, g, b, _ = pixel
    key_r, key_g, key_b = key
    distance = abs(r - key_r) + abs(g - key_g) + abs(b - key_b)
    return (
        g > 150
        and g > r + 75
        and g > b + 75
        and distance < 125
    )


def estimate_key_color(pixels: list[list[RGBA]]) -> tuple[int, int, int]:
    """Estimate the green-screen color from the four image corners."""
    height = len(pixels)
    width = len(pixels[0])
    samples = []
    for x, y in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        r, g, b, _ = pixels[y][x]
        samples.append((r, g, b))
    return tuple(sum(sample[i] for sample in samples) // len(samples) for i in range(3))


def remove_connected_green(
    pixels: list[list[RGBA]],
    padding: int = 10,
) -> tuple[list[list[RGBA]], tuple[int, int, int, int]]:
    """Remove green connected to image edges and crop to the remaining sprite."""
    height = len(pixels)
    width = len(pixels[0])
    key = estimate_key_color(pixels)
    background = [[False for _ in range(width)] for _ in range(height)]
    queue: deque[tuple[int, int]] = deque()

    def add_if_bg(x: int, y: int) -> None:
        if not background[y][x] and is_background_green(pixels[y][x], key):
            background[y][x] = True
            queue.append((x, y))

    for x in range(width):
        add_if_bg(x, 0)
        add_if_bg(x, height - 1)
    for y in range(height):
        add_if_bg(0, y)
        add_if_bg(width - 1, y)

    while queue:
        x, y = queue.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < width and 0 <= ny < height:
                add_if_bg(nx, ny)

    output = []
    min_x, min_y = width, height
    max_x, max_y = -1, -1
    for y, row in enumerate(pixels):
        out_row = []
        for x, (r, g, b, a) in enumerate(row):
            if background[y][x] or is_strong_chroma_green((r, g, b, a), key):
                out_row.append((0, 0, 0, 0))
            else:
                # Despill only obvious green fringe pixels next to the removed
                # background. This keeps intentional darker green details.
                if g > max(r, b) + 35:
                    neighbors = (
                        (x - 1, y),
                        (x + 1, y),
                        (x, y - 1),
                        (x, y + 1),
                    )
                    if any(0 <= nx < width and 0 <= ny < height and background[ny][nx] for nx, ny in neighbors):
                        g = min(g, max(r, b) + 24)
                out_row.append((r, g, b, a))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
        output.append(out_row)

    if max_x < min_x or max_y < min_y:
        raise ValueError("No sprite pixels remained after background removal")

    min_x = max(0, min_x - padding)
    min_y = max(0, min_y - padding)
    max_x = min(width - 1, max_x + padding)
    max_y = min(height - 1, max_y + padding)
    cropped = [row[min_x:max_x + 1] for row in output[min_y:max_y + 1]]
    return cropped, (min_x, min_y, max_x + 1, max_y + 1)


def split_sheet(source: Path, output_dir: Path) -> None:
    width, height, pixels = read_png_rgba(source)
    midpoint = width // 2
    jobs = (
        ("ember_blacksmith.png", 0, midpoint),
        ("tavern_innkeeper.png", midpoint, width),
    )
    for filename, left, right in jobs:
        half = [row[left:right] for row in pixels]
        sprite, bbox = remove_connected_green(half)
        output_path = output_dir / filename
        write_png_rgba(output_path, sprite)
        print(f"wrote {output_path} crop={bbox} size={len(sprite[0])}x{len(sprite)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets/processed/future_assets/npcs"),
    )
    args = parser.parse_args()
    split_sheet(args.source, args.output_dir)


if __name__ == "__main__":
    main()
