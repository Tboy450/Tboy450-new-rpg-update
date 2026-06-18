"""Imported art paths, sprite loading, and animation-frame helpers.

Beginner note:
    `main.py` is already large, so imported asset plumbing lives here.
    Gameplay still decides *when* to draw things. This module only answers:

    - Where are the active PNG frame folders?
    - How do we load and cache a sprite?
    - How do we draw a reusable imported character/enemy sprite?

    To add another imported visual later, add its processed asset path here,
    then call one of the loader helpers from the gameplay code.
"""

from pathlib import Path

import pygame

# Repository root. This file is systems/assets.py, so parents[1] is the project.
BASE_DIR = Path(__file__).resolve().parents[1]

# BEGINNER NOTE: Imported art uses project-root based absolute paths.
# That keeps paths stable on desktop, GitHub Actions, and inside the Android APK.
GHOST_FACE_SPRITE_PATH = str(BASE_DIR / "assets" / "processed" / "enemies" / "ghost_face.png")
LION_SAGE_SPRITE_PATH = str(BASE_DIR / "assets" / "processed" / "npcs" / "lion_sage.png")
TOWN_GUARD_SPRITE_PATH = str(BASE_DIR / "assets" / "processed" / "npcs" / "town_guard.png")
TITLE_DRAGON_SPRITE_PATH = str(BASE_DIR / "assets" / "processed" / "ui" / "title_dragon.png")
FLAME_TORNADO_FRAME_DIR = str(BASE_DIR / "assets" / "processed" / "effects" / "flame_tornado")
FIRE_BLAST_FRAME_DIR = str(BASE_DIR / "assets" / "processed" / "effects" / "fire_blast")
MAGE_MAGIC_FIREBALL_FRAME_DIR = str(BASE_DIR / "assets" / "processed" / "effects" / "mage_magic_fireball")

# BEGINNER NOTE: Active imported hero sprites.
# The keys must match playable class names exactly: "Warrior", "Mage", "Rogue".
CHARACTER_SPRITE_PATHS = {
    "Warrior": str(BASE_DIR / "assets" / "processed" / "characters" / "warrior.png"),
    "Mage": str(BASE_DIR / "assets" / "processed" / "characters" / "mage.png"),
    "Rogue": str(BASE_DIR / "assets" / "processed" / "characters" / "rogue.png"),
}

# BEGINNER NOTE: Story portraits and friendly map NPCs use short keys.
# `game_data/story.py` stores "lion_sage" instead of a full file path, then
# main.py asks this module for the actual PNG. Add future story sprites here.
STORY_SPRITE_PATHS = {
    "ghost_face": GHOST_FACE_SPRITE_PATH,
    "lion_sage": LION_SAGE_SPRITE_PATH,
}

# BEGINNER NOTE: These caches prevent Pygame from reloading and resizing PNGs
# every frame. Loading images is slow; drawing already-loaded surfaces is fast.
SPRITE_CACHE = {}
ANIMATION_FRAME_CACHE = {}


def load_scaled_sprite(path, size):
    """Load a square sprite once and cache the resized surface."""
    cache_key = (path, int(size), int(size))
    if cache_key in SPRITE_CACHE:
        return SPRITE_CACHE[cache_key]

    try:
        sprite = pygame.image.load(path).convert_alpha()
        sprite = pygame.transform.smoothscale(sprite, (int(size), int(size)))
    except Exception as exc:
        print(f"[WARN] Could not load sprite {path}: {exc}")
        sprite = None

    SPRITE_CACHE[cache_key] = sprite
    return sprite


def get_story_sprite_path(sprite_key):
    """Return the PNG path for a story portrait or friendly map NPC."""
    return STORY_SPRITE_PATHS.get(sprite_key)


def load_sprite_by_height(path, target_height):
    """Load a PNG once and resize it by height.

    Beginner note:
        Character art comes from tall imported PNGs instead of Python shapes.
        The world and battle screens need different sizes, so this helper keeps
        the sprite's original width/height ratio while resizing only by height.
    """
    cache_key = (path, "height", int(target_height))
    if cache_key in SPRITE_CACHE:
        return SPRITE_CACHE[cache_key]

    try:
        sprite = pygame.image.load(path).convert_alpha()
        scale = int(target_height) / max(1, sprite.get_height())
        target_width = max(1, int(sprite.get_width() * scale))

        # Pixel-art sprites stay sharper with nearest-neighbor scaling.
        # smoothscale is useful for photos, but it softens retro sprite pixels.
        sprite = pygame.transform.scale(sprite, (target_width, int(target_height)))
    except Exception as exc:
        print(f"[WARN] Could not load sprite {path}: {exc}")
        sprite = None

    SPRITE_CACHE[cache_key] = sprite
    return sprite


def load_animation_frames(directory, target_height=None):
    """Load numbered PNG frames from a processed animation folder.

    Beginner note:
        Fire Tornado, Fire Blast, and Mage Magic are stored as:
        frame_00.png, frame_01.png, frame_02.png, ...

        This helper loads every PNG in a folder, sorts by filename, optionally
        resizes each frame to a shared height, and caches the result.
    """
    cache_key = (directory, target_height)
    if cache_key in ANIMATION_FRAME_CACHE:
        return ANIMATION_FRAME_CACHE[cache_key]

    frames = []
    try:
        frame_paths = [
            path
            for path in sorted(Path(directory).iterdir())
            if path.suffix.lower() == ".png"
        ]
        for path in frame_paths:
            frame = pygame.image.load(str(path)).convert_alpha()
            if target_height:
                scale = target_height / max(1, frame.get_height())
                width = max(1, int(frame.get_width() * scale))
                frame = pygame.transform.smoothscale(frame, (width, target_height))
            frames.append(frame)
    except Exception as exc:
        print(f"[WARN] Could not load animation frames from {directory}: {exc}")
        frames = []

    ANIMATION_FRAME_CACHE[cache_key] = frames
    return frames


def draw_enemy_sprite(surface, enemy, x, y, size):
    """Draw an enemy's imported square sprite when it has one."""
    sprite_path = getattr(enemy, "sprite_path", None)
    if not sprite_path:
        return False

    sprite = load_scaled_sprite(sprite_path, int(size))
    if not sprite:
        return False

    surface.blit(sprite, (int(x), int(y)))
    return True


def draw_character_sprite(surface, char_type, anchor_x, foot_y, target_height, hit_timer=0):
    """Draw one imported player class sprite.

    Beginner note:
        `anchor_x` is the middle of the character.
        `foot_y` is where the feet touch the ground.
        That makes a tall battle sprite and a small world-map sprite line up
        the same way even though their sizes are different.

        This returns True when a PNG was drawn. If a file is missing or broken,
        `Character.draw()` in main.py falls back to older Python-drawn art.
    """
    sprite_path = CHARACTER_SPRITE_PATHS.get(char_type)
    if not sprite_path:
        return False

    sprite = load_sprite_by_height(sprite_path, target_height)
    if not sprite:
        return False

    shadow_width = max(34, int(sprite.get_width() * 0.55))
    shadow_height = max(7, int(target_height * 0.075))
    shadow_rect = (
        int(anchor_x - shadow_width / 2),
        int(foot_y - shadow_height / 2),
        shadow_width,
        shadow_height,
    )
    pygame.draw.ellipse(surface, (0, 0, 0), shadow_rect)

    draw_sprite = sprite
    if hit_timer > 0:
        # Red flash while the player is being hit. Copying protects the cached
        # original sprite from being permanently tinted.
        draw_sprite = sprite.copy()
        draw_sprite.fill((255, 70, 70, 60), special_flags=pygame.BLEND_RGBA_ADD)

    draw_x = int(anchor_x - draw_sprite.get_width() / 2)
    draw_y = int(foot_y - draw_sprite.get_height())
    surface.blit(draw_sprite, (draw_x, draw_y))
    return True
