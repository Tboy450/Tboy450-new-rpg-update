"""Split a green-screen enemy sheet into transparent future enemy sprites.

Beginner note:
    This script reuses the PNG and green-screen helpers from
    `process_uploaded_npc_sheet.py`. The input sheet is expected to have three
    enemies arranged left-to-right:

    - plague knight
    - crystal bat
    - ember drake hatchling
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import argparse
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from process_uploaded_npc_sheet import read_png_rgba, remove_connected_green, write_png_rgba


RGBA = tuple[int, int, int, int]


def find_components(pixels: list[list[RGBA]]) -> list[list[tuple[int, int]]]:
    """Return connected visible pixel groups from an RGBA image."""
    height = len(pixels)
    width = len(pixels[0])
    seen = [[False for _ in range(width)] for _ in range(height)]
    components: list[list[tuple[int, int]]] = []

    for start_y in range(height):
        for start_x in range(width):
            if seen[start_y][start_x] or pixels[start_y][start_x][3] == 0:
                continue

            queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
            seen[start_y][start_x] = True
            component = []
            while queue:
                x, y = queue.popleft()
                component.append((x, y))
                for ny in range(y - 1, y + 2):
                    for nx in range(x - 1, x + 2):
                        if (
                            0 <= nx < width
                            and 0 <= ny < height
                            and not seen[ny][nx]
                            and pixels[ny][nx][3] > 0
                        ):
                            seen[ny][nx] = True
                            queue.append((nx, ny))

            components.append(component)

    return components


def crop_components(
    pixels: list[list[RGBA]],
    components: list[list[tuple[int, int]]],
    padding: int = 12,
    border: int = 12,
) -> list[list[RGBA]]:
    """Build a cropped transparent sprite from selected components."""
    if not components:
        raise ValueError("No components selected")

    selected = {point for component in components for point in component}
    min_x = max(0, min(x for x, _ in selected) - padding)
    max_x = min(len(pixels[0]) - 1, max(x for x, _ in selected) + padding)
    min_y = max(0, min(y for _, y in selected) - padding)
    max_y = min(len(pixels) - 1, max(y for _, y in selected) + padding)

    cropped: list[list[RGBA]] = []
    for y in range(min_y, max_y + 1):
        row: list[RGBA] = []
        for x in range(min_x, max_x + 1):
            row.append(pixels[y][x] if (x, y) in selected else (0, 0, 0, 0))
        cropped.append(row)

    # BEGINNER NOTE: Some source art starts very close to the sheet edge. A
    # guaranteed transparent border prevents the final sprite from looking
    # clipped even when the original sheet did not leave enough padding.
    transparent = (0, 0, 0, 0)
    width = len(cropped[0])
    output: list[list[RGBA]] = [[transparent for _ in range(width + border * 2)] for _ in range(border)]
    for row in cropped:
        output.append([transparent for _ in range(border)] + row + [transparent for _ in range(border)])
    output.extend([[transparent for _ in range(width + border * 2)] for _ in range(border)])
    return output


def split_enemy_sheet(source: Path, output_dir: Path) -> None:
    _, _, pixels = read_png_rgba(source)
    cleaned, full_bbox = remove_connected_green(pixels, padding=0)
    components = [component for component in find_components(cleaned) if len(component) >= 18]

    grouped = {
        "plague_knight.png": [],
        "crystal_bat.png": [],
        "ember_drake_hatchling.png": [],
    }
    for component in components:
        min_x = min(x for x, _ in component)
        max_x = max(x for x, _ in component)
        original_center_x = full_bbox[0] + (min_x + max_x) / 2

        # BEGINNER NOTE: These thresholds match the uploaded sheet layout:
        # plague knight on the left, crystal bat in the center, ember drake on
        # the right. Grouping connected components after background removal
        # avoids clipping wide wings or loose floating rocks.
        if original_center_x < 560:
            grouped["plague_knight.png"].append(component)
        elif original_center_x < 1040:
            grouped["crystal_bat.png"].append(component)
        else:
            grouped["ember_drake_hatchling.png"].append(component)

    for filename, selected_components in grouped.items():
        sprite = crop_components(cleaned, selected_components, padding=12)
        output_path = output_dir / filename
        write_png_rgba(output_path, sprite)
        print(f"wrote {output_path} components={len(selected_components)} size={len(sprite[0])}x{len(sprite)}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets/processed/future_assets/enemies"),
    )
    args = parser.parse_args()
    split_enemy_sheet(args.source, args.output_dir)


if __name__ == "__main__":
    main()
