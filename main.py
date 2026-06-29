"""
DRAGON'S LAIR RPG - A Retro-Style Adventure Game
================================================

This is a complete RPG game built with Pygame featuring:
- 3x3 world map with different area types (forest, desert, mountain, swamp, volcano, town)
- Turn-based combat system with multiple character classes
- Procedurally generated chiptune music
- Particle effects and visual effects
- Opening cutscene and story elements
- Boss battles and progression system

GAME STRUCTURE:
- Game States: start_menu → opening_cutscene → character_select → overworld → interior → battle → game_over
- World System: 3x3 grid of areas, each with unique visuals and enemies
- Combat System: Turn-based with attack, magic, special, item, and run options
- Audio System: Procedurally generated music that changes based on game state

MAIN CLASSES:
- Game: Main game controller and state manager
- WorldMap: Manages the 3x3 world grid and area transitions
- WorldArea: Individual areas with terrain, buildings, and enemies
- Character: Player character with stats and abilities
- Enemy: Various enemy types including bosses
- BattleScreen: Turn-based combat interface
- MusicSystem: Procedural chiptune music generation
- ParticleSystem: Visual effects and particles
- OpeningCutscene: Story introduction sequence

CONTROLS:
- Arrow Keys/WASD: Movement in overworld
- Enter/Space: Confirm actions
- Escape: Shared pause/menu overlay in active gameplay
- M: Toggle world map view
- J: Toggle quest log
- F5/F9: Save/load game
- Android: Uses on-screen touch buttons plus the same pause/menu overlay

BEGINNER ORIENTATION:
- `main.py` is still the active game controller and renderer.
- `game_data/` stores facts, numbers, colors, dialogue, layouts, and tuning.
- `systems/` stores reusable helper logic such as input mapping and save/load.
- `archive/` is reference material only and is not part of the active game.
- Start with `docs/beginner_code_map.md` if you need a safer editing path.
"""

import os
if os.name == "nt":
    os.environ.setdefault("SDL_AUDIODRIVER", "wasapi")
import pygame
import sys
import random
import math
import threading
from pygame import gfxdraw
import tempfile
import wave
import io

# Active game data is imported through `game_data/__init__.py`. That file keeps
# this import list stable even if data gets moved between smaller modules later.
from game_data import (
    AREA_DESCRIPTIONS,
    AREA_ENEMY_TYPES,
    AREA_MECHANICS,
    AREA_PARTICLE_PROFILES,
    AREA_VISUALS,
    BATTLE_RULES,
    FINAL_BOSS_LEVEL,
    CHARACTER_CLASS_STATS,
    DRAGON_BOSS_COLORS,
    ENEMY_NAME_POOLS,
    format_equipment_bonus,
    format_equipment_delta,
    format_town_reward_preview,
    get_character_class_profile,
    get_default_equipment,
    get_equipment_item,
    get_equipment_power,
    get_equipment_rarity_color,
    get_equipment_slot_label,
    get_next_boss_level,
    ITEM_PROFILES,
    ITEM_SPAWN_TABLE,
    iter_equipment_for_slot,
    OPENING_STORY_LINES,
    STORY_NPCS,
    TOWN_ERRANDS,
    TOWN_INTERIORS,
    TOWN_GUARD_STORY_LINES,
    TOWN_SERVICES,
    WORLD_LAYOUT,
    clone_town_layout,
    create_town_guard,
    get_boss_profile,
    get_element_profile,
    get_progression_status,
    get_story_dialogue,
    get_story_dialogues_for_area,
    get_story_enemy_reward,
    get_story_npcs_for_area,
    get_story_reward_item,
    get_town_errand,
    get_town_errand_count,
    get_next_town_resident_errand_status,
    get_town_resident_errand_count,
    get_town_resident_quest,
    get_town_service_dialogue,
    is_town_resident_quest_available,
    iter_town_residents,
)

# Runtime helpers split out of `main.py`. These are logic helpers, not pure
# data tables, so they live in `systems/` instead of `game_data/`.
from systems.input_actions import (
    CANCEL,
    CONFIRM,
    INTERACT,
    JOURNAL,
    LOAD,
    MAP,
    MOVE_DOWN,
    MOVE_DELTAS,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    SAVE,
    action_for_key,
    key_for_action,
)
from systems.android_controls import (
    build_android_touch_buttons,
    draw_android_touch_buttons,
    find_android_touch_button_at_positions,
)
from systems.android_update import (
    fetch_latest_android_numeric_version,
    open_android_update_download,
)
from systems.battle_input import handle_battle_input
from systems.battle_rewards import get_boss_reward, get_regular_enemy_reward
from systems.battle_ui import (
    draw_battle_action_buttons,
    draw_battle_gear_strip,
    draw_battle_log_panel,
    draw_battle_summary,
    set_button_text,
)
from systems.assets import (
    FIRE_BLAST_FRAME_DIR,
    FLAME_TORNADO_FRAME_DIR,
    GHOST_FACE_SPRITE_PATH,
    MAGE_MAGIC_FIREBALL_FRAME_DIR,
    TITLE_DRAGON_SPRITE_PATH,
    TOWN_GUARD_SPRITE_PATH,
    draw_character_sprite,
    draw_enemy_sprite,
    draw_sprite_in_rect,
    get_equipment_icon_path,
    get_scenery_asset_path,
    get_story_sprite_path,
    load_animation_frames,
    load_scaled_sprite,
    load_sprite_by_height,
    load_tinted_sprite_by_height,
)
from systems.interior_ui import (
    draw_interior_message_panel,
    draw_interior_npc,
    draw_interior_service_card,
    draw_interior_service_menu as draw_interior_service_menu_overlay,
)
from systems.save_load import DEFAULT_SAVE_PATH, load_game_state, save_game_state
from systems.story_ui import draw_pause_menu_overlay, draw_story_dialogue_overlay
from systems.town_population_ui import draw_town_residents
from systems.town_services import (
    apply_blacksmith_forge_service,
    apply_inn_rest_service,
    get_service_action_label,
    get_service_completion_label,
    get_service_hint_lines,
    get_service_map_label,
    get_service_overview_lines,
)

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.font.init()


def initialize_audio():
    """Try to initialize pygame audio with driver fallbacks.

    Beginner note:
        Different platforms expose different SDL audio drivers. This helper
        tries the best known options, then lets the game continue silently if
        no driver works.
    """
    if pygame.mixer.get_init():
        pygame.mixer.music.set_volume(0.8)
        return True

    preferred_drivers = []
    if os.name == "nt":
        preferred_drivers.extend(("wasapi", "directsound", "winmm"))
    preferred_drivers.append(None)

    original_driver = os.environ.get("SDL_AUDIODRIVER")
    if original_driver:
        preferred_drivers.insert(0, original_driver)

    tried = set()
    for driver in preferred_drivers:
        if driver in tried:
            continue
        tried.add(driver)
        if driver:
            os.environ["SDL_AUDIODRIVER"] = driver
        else:
            os.environ.pop("SDL_AUDIODRIVER", None)

        try:
            pygame.mixer.quit()
            pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.music.set_volume(0.8)
            print(f"Audio initialized with SDL driver: {driver or 'default'}")
            return True
        except pygame.error as exc:
            print(f"[WARN] Audio driver {driver or 'default'} failed: {exc}")

    return False


AUDIO_AVAILABLE = initialize_audio()
if not AUDIO_AVAILABLE:
    print("[WARN] Audio disabled: no working SDL audio driver found.")

SAMPLE_RATE = 44100
MAX_AUDIO_SAMPLE = 32767


def clamp(value, minimum, maximum):
    """Return value limited to the inclusive range minimum..maximum."""
    return max(minimum, min(maximum, value))


def append_stereo_sample(buffer, value):
    """Append one signed 16-bit stereo sample to a PCM byte buffer."""
    sample = int(clamp(value, -1.0, 1.0) * MAX_AUDIO_SAMPLE)
    sample_bytes = sample.to_bytes(2, "little", signed=True)
    buffer.extend(sample_bytes)
    buffer.extend(sample_bytes)


def pcm_to_wav_bytes(pcm_bytes, sample_rate=SAMPLE_RATE):
    """Wrap raw stereo 16-bit PCM bytes in a WAV container for pygame.music."""
    memfile = io.BytesIO()
    with wave.open(memfile, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return memfile.getvalue()


def sound_from_pcm(pcm_bytes):
    """Build a pygame Sound directly from stereo 16-bit PCM bytes."""
    return pygame.mixer.Sound(buffer=pcm_bytes)


def wrap_text_to_width(text, font_obj, max_width):
    """Split text into lines that fit inside a pixel width.

    Beginner note:
        Pygame does not wrap text for us. This helper measures words with the
        chosen font, builds one line at a time, and starts a new line before a
        sentence would spill outside the dialogue panel.
    """
    lines = []
    current_line = ""
    for word in str(text).split():
        test_line = f"{current_line} {word}".strip()
        if current_line and font_obj.size(test_line)[0] > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)
    return lines or [""]

# ============================================================================
# GAME CONSTANTS AND CONFIGURATION
# ============================================================================

# Display and Performance Settings
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
PLAYER_SIZE = 50
ENEMY_SIZE = 40
ITEM_SIZE = 30
FPS = 60

# BEGINNER NOTE: Android updates need two version values.
# - APP_VERSION is the friendly text shown in the game.
# - APP_NUMERIC_VERSION must go UP every time we publish an APK. Android uses
#   this number to decide whether a downloaded APK is allowed to update the app.
#   If Android says "App not installed" after an update, check that this number
#   and `android.numeric_version` in buildozer.spec were both increased.
APP_VERSION = "0.1.32"
APP_NUMERIC_VERSION = 33

# BEGINNER NOTE: Special attack tuning lives here first.
# Fire Tornado is the default special. Mage renames it to Fire Blast and adds a
# second imported impact animation when the tornado reaches the enemy.
# To rename the default attack, change SPECIAL_ATTACK_NAME.
# To make it cheaper or more expensive, change SPECIAL_ATTACK_MANA_COST.
# To make the animation wait longer before the enemy acts, change duration.
SPECIAL_ATTACK_NAME = "Fire Tornado"
MAGE_SPECIAL_ATTACK_NAME = "Fire Blast"
SPECIAL_ATTACK_MANA_COST = 35
SPECIAL_ATTACK_DURATION = 58

# Visual Design - Retro 80s Color Palette
# =======================================
# Core UI Colors
BACKGROUND = (10, 10, 30)        # Dark blue background
UI_BG = (20, 15, 40)             # UI panel background
UI_BORDER = (255, 105, 180)      # Hot pink borders
TEXT_COLOR = (0, 255, 255)       # Cyan text
GRID_COLOR = (50, 50, 80)        # Grid lines

# Character and Entity Colors
PLAYER_COLOR = (0, 255, 0)       # Green player
ENEMY_COLOR = (255, 0, 0)        # Red enemies
DRAGON_COLOR = (255, 69, 0)      # Red-orange dragons
ITEM_COLOR = (255, 215, 0)       # Gold items

# Status Bar Colors
HEALTH_COLOR = (255, 105, 180)   # Hot pink health
MANA_COLOR = (0, 255, 255)       # Cyan mana
EXP_COLOR = (255, 255, 0)        # Yellow experience

# Special Effect Color Palettes
# =============================
# Fire effect gradient (orange to yellow)
FIRE_COLORS = [(255, 100, 0), (255, 150, 0), (255, 200, 50)]
# Ice effect gradient (light blue to white)
ICE_COLORS = [(100, 200, 255), (150, 220, 255), (200, 240, 255)]
# Shadow effect gradient (dark blue to purple)
SHADOW_COLORS = [(40, 40, 80), (70, 70, 120), (100, 100, 150)]
# Magic effect gradient (purple to pink)
MAGIC_COLORS = [(150, 0, 255), (200, 50, 255), (255, 100, 255)]

# ============================================================================
# PYGAME INITIALIZATION AND SETUP
# ============================================================================

def is_android_runtime():
    """Detect Android before the main display is created."""
    return (
        sys.platform.startswith("android") or
        "ANDROID_ARGUMENT" in os.environ
    )


def is_touch_ui_runtime():
    """Return True when touch controls should be visible.

    Beginner note:
        Some Android APK launch paths do not expose the same Python platform
        value every time. Touch controls are required on the phone, so this
        check also looks for Android system paths that desktop Python normally
        will not have.
    """
    if os.environ.get("DRAGONS_LAIR_DISABLE_TOUCH", "").lower() in {"1", "true", "yes"}:
        return False
    if os.environ.get("DRAGONS_LAIR_FORCE_TOUCH", "").lower() in {"1", "true", "yes"}:
        return True
    if is_android_runtime():
        return True
    return os.path.exists("/system/bin/am") and (
        os.path.isdir("/sdcard") or os.path.isdir("/storage/emulated/0")
    )


def create_game_display():
    """Create a virtual game surface and a real display surface.

    Android devices often ignore the requested 1000x700 window size and show it
    as a small corner surface. Rendering to a virtual surface and stretching it
    to the real fullscreen display keeps the game usable on phones.
    """
    if is_android_runtime():
        try:
            real_display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            virtual_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
            return virtual_screen, real_display
        except pygame.error as exc:
            print(f"[WARN] Android fullscreen display setup failed: {exc}")

    real_display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    return real_display, real_display


screen, display_surface = create_game_display()
pygame.display.set_caption("Dragon's Lair RPG")
clock = pygame.time.Clock()


def display_to_game_pos(pos):
    """Map real display coordinates back to the 1000x700 game layout."""
    if display_surface is screen:
        return pos
    display_width, display_height = display_surface.get_size()
    if display_width <= 0 or display_height <= 0:
        return pos
    return (
        int(pos[0] * SCREEN_WIDTH / display_width),
        int(pos[1] * SCREEN_HEIGHT / display_height),
    )


def get_game_mouse_pos():
    """Return the mouse position in the game's 1000x700 coordinate system."""
    return display_to_game_pos(pygame.mouse.get_pos())


def present_frame():
    """Present the virtual game screen on the real display."""
    if display_surface is screen:
        pygame.display.flip()
        return
    try:
        pygame.transform.scale(screen, display_surface.get_size(), display_surface)
    except TypeError:
        scaled = pygame.transform.scale(screen, display_surface.get_size())
        display_surface.blit(scaled, (0, 0))
    pygame.display.flip()


# Font System Setup
# =================
# Try to load custom fonts, fall back to system fonts if not available
try:
    font_large = pygame.font.Font("freesansbold.ttf", 48)      # Main titles
    font_medium = pygame.font.Font("freesansbold.ttf", 32)     # UI headers
    font_small = pygame.font.Font("freesansbold.ttf", 24)      # Regular text
    font_tiny = pygame.font.Font("freesansbold.ttf", 18)       # Small labels
    font_cinematic = pygame.font.Font("freesansbold.ttf", 28)  # Cutscene text
except:
    # Fallback to system fonts if custom fonts not found
    font_large = pygame.font.SysFont("Courier", 48, bold=True)
    font_medium = pygame.font.SysFont("Courier", 32, bold=True)
    font_small = pygame.font.SysFont("Courier", 24, bold=True)
    font_tiny = pygame.font.SysFont("Courier", 18, bold=True)
    font_cinematic = pygame.font.SysFont("Courier", 28, bold=True)


def render_fitted_text(text, color, max_width, preferred_fonts=None):
    """Render text with the largest listed font that fits inside max_width.

    Beginner note:
        Small HUD panels on Android do not have room for full-size labels.
        This helper measures text before drawing it, then falls back to a
        smaller font or trims the ending with "..." before the label can spill
        outside its box.
    """
    text = str(text)
    if max_width <= 0:
        return font_tiny.render("", True, color)

    fonts_to_try = preferred_fonts or (font_small, font_tiny)
    for font_obj in fonts_to_try:
        rendered = font_obj.render(text, True, color)
        if rendered.get_width() <= max_width:
            return rendered

    final_font = fonts_to_try[-1]
    suffix = "..."
    trimmed = text
    while trimmed and final_font.size(trimmed + suffix)[0] > max_width:
        trimmed = trimmed[:-1]
    if trimmed:
        text = trimmed + suffix
    elif final_font.size(suffix)[0] <= max_width:
        text = suffix
    else:
        text = ""
    return final_font.render(text, True, color)

# ============================================================================
# WORLD AND GRID SYSTEM CONFIGURATION
# ============================================================================

# Grid System (for movement and collision detection)
GRID_SIZE = 50                    # Size of each grid square
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE   # Number of grid columns
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE # Number of grid rows
INTERIOR_WALK_BOUNDS = pygame.Rect(120, 300, 760, 280)
INTERIOR_EXIT_ZONE = pygame.Rect(SCREEN_WIDTH // 2 - 80, 548, 160, 40)

# World Map System (3x3 grid of areas)
WORLD_SIZE = 3                    # 3x3 world grid
AREA_WIDTH = SCREEN_WIDTH         # Each area is full screen width
AREA_HEIGHT = SCREEN_HEIGHT       # Each area is full screen height
WORLD_WIDTH = WORLD_SIZE * AREA_WIDTH    # Total world width
WORLD_HEIGHT = WORLD_SIZE * AREA_HEIGHT  # Total world height

# ============================================================================
# WORLD AREA CLASS - Manages individual areas in the 3x3 world grid
# ============================================================================
class WorldArea:
    """
    Represents a single area in the 3x3 world grid.
    Each area has its own terrain type, enemies, items, and visual style.
    
    Area Types: mountain, forest, desert, swamp, plains, volcano, ice, town, cave

    Beginner note:
    - `area_x` and `area_y` are grid coordinates from 0 to 2.
    - `area_type` is a key such as `forest` or `town`.
    - Visual colors come from `game_data/world.py`.
    - Town building records come from `game_data/town.py`.
    """
    def __init__(self, area_x, area_y, area_type="forest"):
        self.area_x = area_x  # Grid position (0-2)
        self.area_y = area_y  # Grid position (0-2)
        self.area_type = area_type
        self.enemies = []
        self.items = []
        self.visited = False
        
        # AREA_VISUALS keeps color tuning out of this class. Unknown area types
        # fall back to forest colors so testing new area names will not crash.
        visual_profile = AREA_VISUALS.get(area_type, AREA_VISUALS["forest"])
        self.background_color = visual_profile["background_color"]
        self.grid_color = visual_profile["grid_color"]

        if area_type == "town":
            # Town-specific buildings and structures
            self.buildings = []
            self.town_boundaries = []
            self.decorations = []
            self._generate_town_layout()
        
        # Area-specific particle effects
        self.particle_timer = 0
        self.particle_interval = 30  # Frames between particle spawns (faster)
        
        # Initialize cutscene attributes for all areas
        self.entrance_cutscene_triggered = False
        self.guard = None
        self.cutscene_active = False
        self.cutscene_timer = 0
        self.cutscene_phase = 0
        
        # Town-specific particle effects
        if area_type == "town":
            self.particle_interval = 15  # More frequent particles for town
            # Create town guard for cutscene
            self._create_town_guard()
    
    def get_world_position(self):
        """Convert area grid position to world pixel position"""
        return (self.area_x * AREA_WIDTH, self.area_y * AREA_HEIGHT)
    
    def is_point_in_area(self, world_x, world_y):
        """Check if a world position is within this area"""
        area_world_x, area_world_y = self.get_world_position()
        return (area_world_x <= world_x < area_world_x + AREA_WIDTH and 
                area_world_y <= world_y < area_world_y + AREA_HEIGHT)
    
    def get_local_position(self, world_x, world_y):
        """Convert world position to local area position"""
        area_world_x, area_world_y = self.get_world_position()
        return (world_x - area_world_x, world_y - area_world_y)
    
    def _generate_town_layout(self):
        """Generate detailed town layout with buildings, boundaries, and decorations.

        The layout data lives in `game_data/town.py`. This method only copies
        that data onto the active `WorldArea` object.
        """
        if self.area_type != "town":
            return

        # Clone data so runtime changes never mutate the shared module constants.
        layout = clone_town_layout()
        self.town_boundaries = layout["boundaries"]
        self.buildings = layout["buildings"]
        self.decorations = layout["decorations"]
        self.smoke_sources = layout["smoke_sources"]
    
    def _draw_scenic_background(self, surface):
        """Draw scenic background with massive fantasy castle and sunset"""
        # Sunset sky gradient
        for y in range(200):
            # Create sunset colors from orange to purple to blue
            if y < 60:
                # Orange to red sunset
                sky_color = (
                    min(255, 200 + y * 2),
                    max(100, 150 - y),
                    max(50, 100 - y * 2)
                )
            elif y < 120:
                # Purple transition
                sky_color = (
                    max(150, 200 - (y - 60) * 2),
                    max(50, 100 - (y - 60) * 2),
                    min(200, 150 + (y - 60) * 2)
                )
            else:
                # Blue night sky
                sky_color = (
                    max(50, 100 - (y - 120) * 2),
                    max(50, 100 - (y - 120) * 2),
                    min(255, 150 + (y - 120) * 2)
                )
            pygame.draw.line(surface, sky_color, (0, y), (1000, y))
        
        # Massive fantasy castle filling half the sky
        castle_base_y = 50
        castle_height = 150
        
        # Main castle structure (orange/purple/blue gradient)
        for i in range(castle_height):
            # Create gradient from orange to purple to blue
            if i < 50:
                # Orange section
                castle_color = (
                    min(255, 200 + i * 2),
                    max(100, 150 - i),
                    max(50, 100 - i * 2)
                )
            elif i < 100:
                # Purple section
                castle_color = (
                    max(150, 200 - (i - 50) * 2),
                    max(50, 100 - (i - 50) * 2),
                    min(200, 150 + (i - 50) * 2)
                )
            else:
                # Blue section
                castle_color = (
                    max(50, 100 - (i - 100) * 2),
                    max(50, 100 - (i - 100) * 2),
                    min(255, 150 + (i - 100) * 2)
                )
            
            # Draw castle base with gradient
            pygame.draw.rect(surface, castle_color, (0, castle_base_y + i, 1000, 1))
        
        # Castle towers and spiral staircases (reduced from 10 to 6)
        tower_positions = [
            (100, castle_base_y), (250, castle_base_y), (400, castle_base_y),
            (600, castle_base_y), (750, castle_base_y), (900, castle_base_y)
        ]
        
        for tower_x, tower_y in tower_positions:
            # Main tower
            tower_width = 40
            tower_height = 120
            
            # Tower base (orange)
            pygame.draw.rect(surface, (255, 150, 50), (tower_x, tower_y + 30, tower_width, tower_height - 30))
            pygame.draw.rect(surface, (200, 100, 30), (tower_x, tower_y + 30, tower_width, tower_height - 30), 2)
            
            # Tower top (purple)
            pygame.draw.rect(surface, (150, 50, 200), (tower_x, tower_y, tower_width, 30))
            pygame.draw.rect(surface, (100, 30, 150), (tower_x, tower_y, tower_width, 30), 2)
            
            # Spiral staircase (blue)
            for step in range(8):
                step_x = tower_x + 5 + (step % 3) * 10
                step_y = tower_y + 35 + step * 10
                pygame.draw.rect(surface, (50, 100, 255), (step_x, step_y, 8, 6))
                pygame.draw.rect(surface, (30, 70, 200), (step_x, step_y, 8, 6), 1)
            
            # Tower windows (glowing)
            for window_y in [tower_y + 15, tower_y + 45, tower_y + 75]:
                pygame.draw.rect(surface, (255, 255, 200), (tower_x + 8, window_y, 12, 15))
                pygame.draw.rect(surface, (255, 255, 100), (tower_x + 8, window_y, 12, 15), 1)
            
            # Tower flags
            flag_x = tower_x + tower_width // 2
            flag_y = tower_y - 10
            pygame.draw.line(surface, (100, 100, 100), (flag_x, flag_y), (flag_x, flag_y + 15), 2)
            flag_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100)]
            flag_color = flag_colors[tower_positions.index((tower_x, tower_y)) % len(flag_colors)]
            pygame.draw.rect(surface, flag_color, (flag_x + 2, flag_y + 2, 12, 8))
            pygame.draw.rect(surface, (255, 255, 255), (flag_x + 2, flag_y + 2, 12, 8), 1)
        
        # Central castle keep (larger structure)
        keep_x = 400
        keep_y = castle_base_y + 20
        keep_width = 200
        keep_height = 100
        
        # Keep base (orange gradient)
        for i in range(keep_height // 2):
            keep_color = (
                min(255, 200 + i * 2),
                max(100, 150 - i),
                max(50, 100 - i * 2)
            )
            pygame.draw.rect(surface, keep_color, (keep_x, keep_y + i, keep_width, 1))
        
        # Keep top (purple gradient)
        for i in range(keep_height // 2):
            keep_color = (
                max(150, 200 - i * 2),
                max(50, 100 - i * 2),
                min(200, 150 + i * 2)
            )
            pygame.draw.rect(surface, keep_color, (keep_x, keep_y + keep_height // 2 + i, keep_width, 1))
        
        # Keep border
        pygame.draw.rect(surface, (100, 50, 150), (keep_x, keep_y, keep_width, keep_height), 3)
        
        # Keep windows
        for window_x in [keep_x + 30, keep_x + 80, keep_x + 130, keep_x + 180]:
            for window_y in [keep_y + 20, keep_y + 50, keep_y + 80]:
                pygame.draw.rect(surface, (255, 255, 200), (window_x, window_y, 20, 25))
                pygame.draw.rect(surface, (255, 255, 100), (window_x, window_y, 20, 25), 1)
        
        # Keep roof (blue)
        roof_points = [(keep_x - 20, keep_y), (keep_x + keep_width // 2, keep_y - 30), (keep_x + keep_width + 20, keep_y)]
        pygame.draw.polygon(surface, (50, 100, 255), roof_points)
        pygame.draw.polygon(surface, (30, 70, 200), roof_points, 2)
        
        # Castle walls connecting towers (updated for 6 towers)
        for i in range(len(tower_positions) - 1):
            wall_x1 = tower_positions[i][0] + 20
            wall_x2 = tower_positions[i + 1][0] + 20
            wall_y = castle_base_y + 140
            wall_height = 20
            
            # Wall gradient
            for j in range(wall_height):
                wall_color = (
                    max(150, 200 - j * 2),
                    max(50, 100 - j * 2),
                    min(200, 150 + j * 2)
                )
                pygame.draw.line(surface, wall_color, (wall_x1, wall_y + j), (wall_x2, wall_y + j))
        
        # Distant mountains (behind castle)
        mountain_points = [
            (0, 200), (200, 160), (400, 180), (600, 150), (800, 170), (1000, 190), (1000, 250), (0, 250)
        ]
        pygame.draw.polygon(surface, (40, 60, 80), mountain_points)
        
        # Mountain details
        for i in range(3):
            peak_x = 200 + i * 300
            peak_y = 160 + (i % 2) * 20
            pygame.draw.circle(surface, (20, 40, 60), (peak_x, peak_y), 20)
        
        # Grass texture overlay (moved much lower)
        for x in range(0, 1000, 20):
            for y in range(250, 700, 15):
                if random.random() < 0.3:
                    grass_color = (60 + random.randint(0, 40), 100 + random.randint(0, 40), 40 + random.randint(0, 20))
                    pygame.draw.circle(surface, grass_color, (x + random.randint(0, 20), y + random.randint(0, 15)), 2)
    
    def _draw_town_paths(self, surface):
        """Draw red dirt paths connecting buildings"""
        # Main path from gate to town center
        path_points = [(500, 260), (500, 350), (500, 400)]
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            pygame.draw.line(surface, (120, 80, 60), (x1, y1), (x2, y2), 8)
        
        # Side paths to buildings (updated for better spacing)
        side_paths = [
            [(500, 400), (200, 475)],  # To shop
            [(500, 400), (870, 475)],  # To inn
            [(500, 400), (160, 610)],  # To blacksmith
            [(500, 400), (840, 610)],  # To library
            [(500, 400), (500, 555)],  # To market stall
            [(500, 400), (785, 370)],  # To house
        ]
        
        for path in side_paths:
            x1, y1 = path[0]
            x2, y2 = path[1]
            pygame.draw.line(surface, (110, 70, 50), (x1, y1), (x2, y2), 6)
        
        # Path texture (dirt spots)
        for path in side_paths + [[(500, 260), (500, 400)]]:
            x1, y1 = path[0]
            x2, y2 = path[1]
            for i in range(0, int(abs(x2-x1) + abs(y2-y1)), 10):
                t = i / max(abs(x2-x1) + abs(y2-y1), 1)
                px = x1 + (x2-x1) * t
                py = y1 + (y2-y1) * t
                if random.random() < 0.4:
                    pygame.draw.circle(surface, (100, 60, 40), (int(px), int(py)), 2)
    
    def draw_town(self, surface):
        """Draw the scenic town with unique building styles and red dirt paths"""
        if self.area_type != "town":
            return
            
        # Draw scenic background first
        self._draw_scenic_background(surface)
        
        # Draw red dirt paths
        self._draw_town_paths(surface)
        
        # Draw town boundaries first (walls and gates) - 3D style
        for boundary in self.town_boundaries:
            if boundary["type"] == "gate":
                # Draw main gate with 3D arch effect
                gate_x, gate_y = boundary["x"], boundary["y"]
                gate_w, gate_h = boundary["width"], boundary["height"]
                
                # Gate base (3D effect with shadow)
                pygame.draw.rect(surface, (60, 40, 20), (gate_x + 3, gate_y + 3, gate_w, gate_h))
                pygame.draw.rect(surface, (80, 60, 40), (gate_x, gate_y, gate_w, gate_h))
                pygame.draw.rect(surface, (40, 20, 10), (gate_x, gate_y, gate_w, gate_h), 3)
                
                # Gate arch (3D effect)
                arch_points = [
                    (gate_x + 10, gate_y), (gate_x + gate_w//2, gate_y - 25), (gate_x + gate_w - 10, gate_y)
                ]
                pygame.draw.polygon(surface, (70, 50, 30), [(p[0] + 2, p[1] + 2) for p in arch_points])
                pygame.draw.polygon(surface, (100, 80, 60), arch_points)
                pygame.draw.polygon(surface, (50, 30, 10), arch_points, 2)
                
                # Gate door (3D effect)
                door_x = gate_x + 20
                door_y = gate_y + 10
                door_w = gate_w - 40
                door_h = gate_h - 20
                pygame.draw.rect(surface, (30, 15, 5), (door_x + 2, door_y + 2, door_w, door_h))
                pygame.draw.rect(surface, (50, 25, 10), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (20, 10, 5), (door_x, door_y, door_w, door_h), 2)
                
            elif boundary["type"] == "wall":
                # Draw wall sections with 3D effect
                wall_x, wall_y = boundary["x"], boundary["y"]
                wall_w, wall_h = boundary["width"], boundary["height"]
                
                # Wall shadow
                pygame.draw.rect(surface, (50, 30, 10), (wall_x + 3, wall_y + 3, wall_w, wall_h))
                # Wall base
                pygame.draw.rect(surface, (70, 50, 30), (wall_x, wall_y, wall_w, wall_h))
                pygame.draw.rect(surface, (50, 30, 10), (wall_x, wall_y, wall_w, wall_h), 2)
                
                # Wall texture (3D bricks)
                for i in range(0, wall_w, 15):
                    for j in range(0, wall_h, 8):
                        brick_x = wall_x + i
                        brick_y = wall_y + j
                        pygame.draw.rect(surface, (60, 40, 20), (brick_x + 1, brick_y + 1, 13, 6))
                        pygame.draw.rect(surface, (80, 60, 40), (brick_x, brick_y, 13, 6), 1)
                    
            elif boundary["type"] == "tower":
                # Draw decorative towers with 3D effect
                tower_x, tower_y = boundary["x"], boundary["y"]
                tower_w, tower_h = boundary["width"], boundary["height"]
                
                # Tower shadow
                pygame.draw.rect(surface, (70, 50, 30), (tower_x + 3, tower_y + 3, tower_w, tower_h))
                # Tower base
                pygame.draw.rect(surface, (90, 70, 50), (tower_x, tower_y, tower_w, tower_h))
                pygame.draw.rect(surface, (70, 50, 30), (tower_x, tower_y, tower_w, tower_h), 2)
                
                # Tower top (3D cone)
                top_points = [
                    (tower_x, tower_y), (tower_x + tower_w//2, tower_y - 15), (tower_x + tower_w, tower_y)
                ]
                pygame.draw.polygon(surface, (80, 60, 40), [(p[0] + 2, p[1] + 2) for p in top_points])
                pygame.draw.polygon(surface, (110, 90, 70), top_points)
                pygame.draw.polygon(surface, (60, 40, 20), top_points, 2)
                
                # Tower windows (3D effect)
                window1 = (tower_x + 5, tower_y + 20, 10, 15)
                window2 = (tower_x + 25, tower_y + 20, 10, 15)
                for wx, wy, ww, wh in [window1, window2]:
                    pygame.draw.rect(surface, (20, 10, 5), (wx + 1, wy + 1, ww, wh))
                    pygame.draw.rect(surface, (40, 20, 10), (wx, wy, ww, wh))
                    pygame.draw.rect(surface, (10, 5, 0), (wx, wy, ww, wh), 1)
        
        # Draw main buildings with 3D pop-up style
        for building in self.buildings:
            color = building["color"]
            x, y, w, h = building["x"], building["y"], building["width"], building["height"]

            # BEGINNER NOTE: Most town buildings are still drawn with Python
            # shapes below. A building can opt into an imported sprite by
            # adding `sprite` and optional `sprite_rect` fields in
            # `game_data/town.py`. If the PNG fails to load, the old drawing
            # code below still runs as a safe fallback.
            drew_building_sprite = False
            sprite_name = building.get("sprite")
            if sprite_name:
                sprite_path = get_scenery_asset_path(sprite_name)
                sprite_rect = pygame.Rect(building.get("sprite_rect", (x, y, w, h)))
                drew_building_sprite = draw_sprite_in_rect(
                    surface,
                    sprite_path,
                    sprite_rect,
                    building.get("sprite_preserve_aspect", True),
                    building.get("sprite_anchor", "bottom"),
                )

            if drew_building_sprite:
                pass
            elif building["type"] == "town_hall":
                # Draw town hall with 3D columns and roof
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 4, y + 4, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Columns
                for i in range(4):
                    col_x = x + 20 + i * 45
                    col_y = y + 10
                    col_w, col_h = 15, h - 20
                    # Column shadow
                    pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (col_x + 2, col_y + 2, col_w, col_h))
                    # Column base
                    pygame.draw.rect(surface, (color[0]-20, color[1]-20, color[2]-20), (col_x, col_y, col_w, col_h))
                    pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (col_x, col_y, col_w, col_h), 1)
                
                # 3D Roof
                roof_points = [(x - 10, y), (x + w//2, y - 35), (x + w + 10, y)]
                pygame.draw.polygon(surface, (color[0]-50, color[1]-50, color[2]-50), [(p[0] + 3, p[1] + 3) for p in roof_points])
                pygame.draw.polygon(surface, (color[0]-30, color[1]-30, color[2]-30), roof_points)
                pygame.draw.polygon(surface, (color[0]-60, color[1]-60, color[2]-60), roof_points, 2)
                
                # 3D Bell tower
                bell_x = x + w//2 - 10
                bell_y = y - 55
                bell_w, bell_h = 20, 30
                pygame.draw.rect(surface, (color[0]-30, color[1]-30, color[2]-30), (bell_x + 2, bell_y + 2, bell_w, bell_h))
                pygame.draw.rect(surface, (color[0]-10, color[1]-10, color[2]-10), (bell_x, bell_y, bell_w, bell_h))
                pygame.draw.rect(surface, (color[0]-50, color[1]-50, color[2]-50), (bell_x, bell_y, bell_w, bell_h), 2)
                
                # 3D Bell
                bell_center_x = x + w//2
                bell_center_y = y - 40
                pygame.draw.circle(surface, (180, 180, 0), (bell_center_x + 1, bell_center_y + 1), 8)
                pygame.draw.circle(surface, (220, 220, 0), (bell_center_x, bell_center_y), 8)
                pygame.draw.circle(surface, (160, 160, 0), (bell_center_x, bell_center_y), 8, 2)
                
            elif building["type"] == "shop":
                # Draw shop with 3D sign and details
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 3, y + 3, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Shop sign
                sign_x = x + w//2 - 15
                sign_y = y - 25
                sign_w, sign_h = 30, 15
                pygame.draw.rect(surface, (120, 80, 40), (sign_x + 2, sign_y + 2, sign_w, sign_h))
                pygame.draw.rect(surface, (150, 100, 50), (sign_x, sign_y, sign_w, sign_h))
                pygame.draw.rect(surface, (100, 50, 0), (sign_x, sign_y, sign_w, sign_h), 2)
                
                # 3D Door
                door_x = x + w//2 - 15
                door_y = y + h - 35
                door_w, door_h = 30, 30
                pygame.draw.rect(surface, (60, 40, 20), (door_x + 2, door_y + 2, door_w, door_h))
                pygame.draw.rect(surface, (80, 60, 40), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (40, 20, 10), (door_x, door_y, door_w, door_h), 2)
                
                # 3D Windows
                for wx, wy in [(x + 10, y + 15), (x + w - 30, y + 15)]:
                    pygame.draw.rect(surface, (80, 120, 200), (wx + 1, wy + 1, 20, 20))
                    pygame.draw.rect(surface, (100, 150, 255), (wx, wy, 20, 20))
                    pygame.draw.rect(surface, (60, 100, 180), (wx, wy, 20, 20), 2)
                
            elif building["type"] == "inn":
                # Draw inn with 3D thatched roof
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 3, y + 3, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Thatched roof
                roof_points = [(x - 5, y), (x + w//2, y - 30), (x + w + 5, y)]
                pygame.draw.polygon(surface, (100, 80, 40), [(p[0] + 2, p[1] + 2) for p in roof_points])
                pygame.draw.polygon(surface, (120, 100, 60), roof_points)
                pygame.draw.polygon(surface, (80, 60, 20), roof_points, 2)
                
                # 3D Door
                door_x = x + w//2 - 15
                door_y = y + h - 35
                door_w, door_h = 30, 30
                pygame.draw.rect(surface, (60, 40, 20), (door_x + 2, door_y + 2, door_w, door_h))
                pygame.draw.rect(surface, (80, 60, 40), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (40, 20, 10), (door_x, door_y, door_w, door_h), 2)
                
                # 3D Windows
                for wx, wy in [(x + 15, y + 15), (x + w - 40, y + 15)]:
                    pygame.draw.rect(surface, (220, 220, 180), (wx + 1, wy + 1, 25, 25))
                    pygame.draw.rect(surface, (255, 255, 200), (wx, wy, 25, 25))
                    pygame.draw.rect(surface, (180, 180, 150), (wx, wy, 25, 25), 2)
                
            elif building["type"] == "blacksmith":
                # Draw blacksmith with 3D chimney and smoke
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 3, y + 3, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Chimney
                chimney_x = x + w - 25
                chimney_y = y - 25
                chimney_w, chimney_h = 15, 20
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (chimney_x + 2, chimney_y + 2, chimney_w, chimney_h))
                pygame.draw.rect(surface, (color[0]-20, color[1]-20, color[2]-20), (chimney_x, chimney_y, chimney_w, chimney_h))
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (chimney_x, chimney_y, chimney_w, chimney_h), 2)
                
                # 3D Smoke effect
                smoke_x = x + w - 17
                smoke_y = y - 30
                pygame.draw.circle(surface, (80, 80, 80), (smoke_x + 1, smoke_y + 1), 5)
                pygame.draw.circle(surface, (100, 100, 100), (smoke_x, smoke_y), 5)
                pygame.draw.circle(surface, (60, 60, 60), (smoke_x, smoke_y), 5, 1)
                
                # 3D Door
                door_x = x + w//2 - 15
                door_y = y + h - 30
                door_w, door_h = 30, 25
                pygame.draw.rect(surface, (40, 20, 10), (door_x + 2, door_y + 2, door_w, door_h))
                pygame.draw.rect(surface, (60, 40, 20), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (20, 10, 5), (door_x, door_y, door_w, door_h), 2)
                
            elif building["type"] == "library":
                # Draw library with 3D columns
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 3, y + 3, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Columns
                for col_x, col_y in [(x + 10, y + 10), (x + w - 18, y + 10)]:
                    col_w, col_h = 8, h - 20
                    pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (col_x + 1, col_y + 1, col_w, col_h))
                    pygame.draw.rect(surface, (color[0]-20, color[1]-20, color[2]-20), (col_x, col_y, col_w, col_h))
                    pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (col_x, col_y, col_w, col_h), 1)
                
                # 3D Door
                door_x = x + w//2 - 12
                door_y = y + h - 30
                door_w, door_h = 24, 25
                pygame.draw.rect(surface, (60, 40, 20), (door_x + 2, door_y + 2, door_w, door_h))
                pygame.draw.rect(surface, (80, 60, 40), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (40, 20, 10), (door_x, door_y, door_w, door_h), 2)
                
                # 3D Windows
                for wx, wy in [(x + 25, y + 15), (x + w - 45, y + 15)]:
                    pygame.draw.rect(surface, (180, 180, 220), (wx + 1, wy + 1, 20, 20))
                    pygame.draw.rect(surface, (200, 200, 255), (wx, wy, 20, 20))
                    pygame.draw.rect(surface, (140, 140, 200), (wx, wy, 20, 20), 2)
                
            elif building["type"] == "house":
                # Draw houses with 3D roofs
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 3, y + 3, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 3)
                
                # 3D Roof
                roof_points = [(x - 3, y), (x + w//2, y - 20), (x + w + 3, y)]
                pygame.draw.polygon(surface, (color[0]-50, color[1]-50, color[2]-50), [(p[0] + 2, p[1] + 2) for p in roof_points])
                pygame.draw.polygon(surface, (color[0]-30, color[1]-30, color[2]-30), roof_points)
                pygame.draw.polygon(surface, (color[0]-70, color[1]-70, color[2]-70), roof_points, 2)
                
                # 3D Door
                door_x = x + w//2 - 8
                door_y = y + h - 25
                door_w, door_h = 16, 20
                pygame.draw.rect(surface, (40, 20, 10), (door_x + 1, door_y + 1, door_w, door_h))
                pygame.draw.rect(surface, (60, 40, 20), (door_x, door_y, door_w, door_h))
                pygame.draw.rect(surface, (20, 10, 5), (door_x, door_y, door_w, door_h), 2)
                
                # 3D Window
                window_x = x + w//2 - 6
                window_y = y + 10
                window_w, window_h = 12, 12
                pygame.draw.rect(surface, (180, 180, 220), (window_x + 1, window_y + 1, window_w, window_h))
                pygame.draw.rect(surface, (200, 200, 255), (window_x, window_y, window_w, window_h))
                pygame.draw.rect(surface, (140, 140, 200), (window_x, window_y, window_w, window_h), 2)
                
            elif building["type"] == "stall":
                # Draw market stalls with 3D effect
                # Building shadow
                pygame.draw.rect(surface, (color[0]-60, color[1]-60, color[2]-60), (x + 2, y + 2, w, h))
                # Building base
                pygame.draw.rect(surface, color, (x, y, w, h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (x, y, w, h), 2)
                
                # 3D Stall roof
                roof_points = [(x - 2, y), (x + w//2, y - 12), (x + w + 2, y)]
                pygame.draw.polygon(surface, (color[0]-30, color[1]-30, color[2]-30), [(p[0] + 1, p[1] + 1) for p in roof_points])
                pygame.draw.polygon(surface, (color[0]-20, color[1]-20, color[2]-20), roof_points)
                pygame.draw.polygon(surface, (color[0]-50, color[1]-50, color[2]-50), roof_points, 1)
                
                # 3D Stall counter
                counter_x = x + 5
                counter_y = y + h - 20
                counter_w, counter_h = w - 10, 10
                pygame.draw.rect(surface, (color[0]-20, color[1]-20, color[2]-20), (counter_x + 1, counter_y + 1, counter_w, counter_h))
                pygame.draw.rect(surface, (color[0]-10, color[1]-10, color[2]-10), (counter_x, counter_y, counter_w, counter_h))
                pygame.draw.rect(surface, (color[0]-40, color[1]-40, color[2]-40), (counter_x, counter_y, counter_w, counter_h), 1)

            if building["type"] in TOWN_SERVICES:
                entry_rect = self.get_building_entry_rect(building, depth=38)
                # BEGINNER NOTE: This is the always-visible doorway mat. It is
                # intentionally separate from the larger active marker drawn by
                # `Game.draw_town_service_marker`, because this one identifies
                # every building even before the player walks close enough.
                pygame.draw.rect(surface, (34, 26, 24), entry_rect.inflate(8, 6), border_radius=7)
                pygame.draw.rect(surface, (104, 66, 36), entry_rect, border_radius=5)
                pygame.draw.rect(surface, (190, 126, 58), entry_rect, 2, border_radius=5)
                label = get_service_map_label(building["type"])
                label_text = render_fitted_text(label, (255, 235, 180), entry_rect.width - 8, (font_tiny,))
                screen_x = entry_rect.centerx - label_text.get_width() // 2
                screen_y = entry_rect.y + entry_rect.height // 2 - label_text.get_height() // 2
                surface.blit(label_text, (screen_x, screen_y))

        # Draw decorative elements with 3D effect
        for decoration in self.decorations:
            x, y, w, h = decoration["x"], decoration["y"], decoration["width"], decoration["height"]
            
            if decoration["type"] == "lamp":
                # Draw 3D street lamps
                # Lamp post shadow
                pygame.draw.rect(surface, (40, 20, 10), (x + w//2 - 2, y + h - 18, 6, 20))
                # Lamp post
                pygame.draw.rect(surface, (60, 40, 20), (x + w//2 - 3, y + h - 20, 6, 20))
                pygame.draw.rect(surface, (40, 20, 10), (x + w//2 - 3, y + h - 20, 6, 20), 1)
                
                # 3D Lamp top
                lamp_x = x + w//2
                lamp_y = y + h - 25
                pygame.draw.circle(surface, (180, 180, 80), (lamp_x + 1, lamp_y + 1), 8)
                pygame.draw.circle(surface, (200, 200, 100), (lamp_x, lamp_y), 8)
                pygame.draw.circle(surface, (160, 160, 60), (lamp_x, lamp_y), 8, 2)
                
                # 3D Light glow
                pygame.draw.circle(surface, (255, 255, 200), (lamp_x, lamp_y), 12, 1)
                
            elif decoration["type"] == "tree":
                # Draw 3D trees
                # Tree trunk shadow
                pygame.draw.rect(surface, (60, 40, 20), (x + w//2 - 2, y + h - 12, 6, 15))
                # Tree trunk
                pygame.draw.rect(surface, (80, 60, 40), (x + w//2 - 3, y + h - 15, 6, 15))
                pygame.draw.rect(surface, (60, 40, 20), (x + w//2 - 3, y + h - 15, 6, 15), 1)
                
                # 3D Tree foliage
                tree_center_x = x + w//2
                tree_center_y = y + h - 20
                pygame.draw.circle(surface, (30, 60, 30), (tree_center_x + 2, tree_center_y + 2), 15)
                pygame.draw.circle(surface, (40, 80, 40), (tree_center_x, tree_center_y), 15)
                pygame.draw.circle(surface, (20, 40, 20), (tree_center_x, tree_center_y), 15, 2)
                
                # 3D Tree details
                for detail_x, detail_y in [(tree_center_x - 8, tree_center_y - 5), (tree_center_x + 8, tree_center_y - 5)]:
                    pygame.draw.circle(surface, (50, 80, 50), (detail_x + 1, detail_y + 1), 8)
                    pygame.draw.circle(surface, (60, 100, 60), (detail_x, detail_y), 8)
                    pygame.draw.circle(surface, (40, 60, 40), (detail_x, detail_y), 8, 1)
                
            elif decoration["type"] == "flowers":
                # Draw 3D flower beds
                # Flower bed shadow
                pygame.draw.rect(surface, (30, 60, 30), (x + 1, y + 1, w, h))
                # Flower bed base
                pygame.draw.rect(surface, (40, 80, 40), (x, y, w, h))
                pygame.draw.rect(surface, (20, 40, 20), (x, y, w, h), 1)
                
                # 3D Flowers
                for i in range(6):
                    flower_x = x + 5 + i * 5
                    flower_y = y + 5 + (i % 2) * 8
                    color_choices = [(255, 100, 100), (255, 200, 100), (200, 100, 255), (100, 200, 255)]
                    flower_color = color_choices[i % len(color_choices)]
                    
                    # Flower shadow
                    pygame.draw.circle(surface, (flower_color[0]-50, flower_color[1]-50, flower_color[2]-50), (flower_x + 1, flower_y + 1), 3)
                    # Flower base
                    pygame.draw.circle(surface, flower_color, (flower_x, flower_y), 3)
                    pygame.draw.circle(surface, (255, 255, 255), (flower_x, flower_y), 1)

            elif decoration["type"] == "sand_patch":
                # BEGINNER NOTE: Sand patches are scenery only.
                # They preserve the old beach flavor inside town without making
                # "beach" a separate overworld map area.
                pygame.draw.ellipse(surface, (98, 82, 50), (x + 3, y + 4, w, h))
                pygame.draw.ellipse(surface, (178, 154, 92), (x, y, w, h))
                pygame.draw.ellipse(surface, (214, 190, 120), (x + 8, y + 6, max(12, w - 16), max(10, h - 12)), 2)
                for grain_index in range(8):
                    grain_x = x + 16 + (grain_index * 17) % max(18, w - 20)
                    grain_y = y + 12 + (grain_index * 11) % max(14, h - 16)
                    pygame.draw.circle(surface, (128, 106, 62), (grain_x, grain_y), 2)
    
    def generate_town_particles(self, particle_system):
        """Generate town-specific particle effects"""
        if self.area_type != "town":
            return
            
        # Generate smoke from chimneys
        for smoke_source in self.smoke_sources:
            if random.random() < 0.3:  # 30% chance each frame
                smoke_x = smoke_source["x"] + random.randint(-5, 5)
                smoke_y = smoke_source["y"] - 10
                velocity = (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5))
                color = (100 + random.randint(0, 50), 100 + random.randint(0, 50), 100 + random.randint(0, 50))
                particle_system.add_particle(smoke_x, smoke_y, color, velocity, random.randint(3, 8), random.randint(30, 60))
        
        # Generate floating leaves
        if random.random() < 0.2:  # 20% chance each frame
            leaf_x = random.randint(50, 950)
            leaf_y = random.randint(220, 320)
            velocity = (random.uniform(-0.2, 0.2), random.uniform(0.1, 0.3))
            color = (100 + random.randint(0, 50), 150 + random.randint(0, 50), 50 + random.randint(0, 30))
            particle_system.add_particle(leaf_x, leaf_y, color, velocity, random.randint(2, 5), random.randint(40, 80))
    
    def is_player_near_building(self, player_x, player_y, building_type=None):
        """Check if player is near a specific building type for interaction"""
        if self.area_type != "town":
            return False, None
            
        # Convert world coordinates to local area coordinates
        area_world_x, area_world_y = self.get_world_position()
        local_x = player_x - area_world_x
        local_y = player_y - area_world_y
        
        # Check distance to buildings
        for building in self.buildings:
            if building_type and building["type"] != building_type:
                continue
                
            building_center_x = building["x"] + building["width"] // 2
            building_center_y = building["y"] + building["height"] // 2
            
            distance = math.sqrt((local_x - building_center_x)**2 + (local_y - building_center_y)**2)
            if distance < 80:  # Interaction range
                return True, building["type"]
        
        return False, None

    def get_building_collision_rect(self, building):
        max_overlap = max(12, building["height"] // 3)
        inset_y = min(building.get("entry_depth", GRID_SIZE), max_overlap)
        usable_height = max(1, building["height"] - inset_y * 2)
        return pygame.Rect(
            building["x"],
            building["y"] + inset_y,
            building["width"],
            usable_height,
        )

    def get_building_entry_rect(self, building, depth=95):
        """Return the doorway/action rectangle for one town building.

        Beginner note:
            This is not the same as building collision. Collision blocks walls.
            This smaller rectangle says where OK/USE can enter the building.
            `door_width` changes the horizontal size; `interaction_depth`
            changes how far down from the door the player can stand.
        """
        door_width = min(building.get("door_width", building["width"]), building["width"] + 40)
        interaction_depth = building.get("interaction_depth", depth)
        return pygame.Rect(
            building["x"] + building["width"] // 2 - door_width // 2,
            building["y"] + building["height"] - 18,
            door_width,
            interaction_depth,
        )

    def check_building_collision(self, player_x, player_y):
        """Block building sides while allowing shallow top/bottom visual overlap."""
        if self.area_type != "town":
            return False
            
        # Convert world coordinates to local area coordinates
        area_world_x, area_world_y = self.get_world_position()
        local_x = player_x - area_world_x
        local_y = player_y - area_world_y
        player_center = (local_x + PLAYER_SIZE // 2, local_y + PLAYER_SIZE // 2)
        
        for building in self.buildings:
            if building.get("collision", False):
                collision_rect = self.get_building_collision_rect(building)
                if collision_rect.collidepoint(player_center):
                    return True
        return False

    def get_nearby_town_service(self, player_x, player_y):
        """Return the town service/building the player can currently use.

        Beginner note:
            The returned dictionary includes `entry_rect` and `service_rect` so
            drawing code and interaction code use the same doorway location.
            That keeps the yellow marker honest: if the marker shows, OK/USE
            should target that same building.
        """
        if self.area_type != "town":
            return None

        area_world_x, area_world_y = self.get_world_position()
        local_x = player_x - area_world_x
        local_y = player_y - area_world_y
        player_rect = pygame.Rect(local_x, local_y, PLAYER_SIZE, PLAYER_SIZE)

        best_service = None
        best_distance = None
        for building in self.buildings:
            service_type = building["type"]
            if service_type not in TOWN_SERVICES:
                continue

            door_rect = self.get_building_entry_rect(building)

            # Keep interaction doorway-focused so side walls still behave like
            # walls. If two inflated doorway zones overlap, this method keeps
            # the closest doorway instead of returning the first building in
            # the layout table.
            service_rect = door_rect.inflate(44, 24)
            if player_rect.colliderect(door_rect) or player_rect.colliderect(service_rect):
                service = dict(TOWN_SERVICES[service_type])
                service["type"] = service_type
                service["entry_rect"] = door_rect
                service["service_rect"] = service_rect
                service["distance"] = math.hypot(player_rect.centerx - door_rect.centerx, player_rect.centery - door_rect.centery)
                if best_distance is None or service["distance"] < best_distance:
                    best_distance = service["distance"]
                    best_service = service

        return best_service

    def _create_town_guard(self):
        """Create the town guard NPC for the entrance cutscene"""
        if self.area_type != "town":
            return
            
        # Create guard at the town entrance (near the gate)
        self.guard = create_town_guard()
        # BEGINNER NOTE: The normal guard greeting lives in game_data/npcs.py.
        # The main-story warning below lives in game_data/story.py so future
        # quest text can be edited without touching town-service dialogue.
        self.guard["dialogue"].extend(TOWN_GUARD_STORY_LINES)
    
    def check_entrance_cutscene(self, player_x, player_y):
        """Check if player should trigger the entrance cutscene"""
        if self.area_type != "town" or self.entrance_cutscene_triggered:
            return False
            
        # Convert world coordinates to local area coordinates
        area_world_x, area_world_y = self.get_world_position()
        local_x = player_x - area_world_x
        local_y = player_y - area_world_y
        
        # Check if player is near the entrance area (adjusted for new gate position)
        if 450 <= local_x <= 550 and 250 <= local_y <= 300:
            self.entrance_cutscene_triggered = True
            self.cutscene_active = True
            self.cutscene_timer = 0
            self.cutscene_phase = 0
            if self.guard:
                self.guard["visible"] = True
                self.guard["current_dialogue"] = 0
            return True
        return False
    
    def update_cutscene(self):
        """Update the entrance cutscene"""
        if not self.cutscene_active or not self.guard:
            return
            
        self.cutscene_timer += 1
        
        # Update guard animation
        self.guard["animation_timer"] += 1
        if self.guard["animation_timer"] >= 10:
            self.guard["animation_timer"] = 0
            self.guard["animation_offset"] = 2 if self.guard["animation_offset"] == 0 else 0
        
        # Cutscene phases
        if self.cutscene_phase == 0:  # Guard approaches
            if self.cutscene_timer > 5:  # Much faster spawn (reduced from 15 to 5)
                self.cutscene_phase = 1
                self.cutscene_timer = 0
                # Reset dialogue to first line
                if self.guard:
                    self.guard["current_dialogue"] = 0
        elif self.cutscene_phase == 1:  # Guard speaks
            # Dialogue progression is now handled by SPACE key input
            # Only auto-advance to phase 2 if player reaches the last dialogue
            return
        elif self.cutscene_phase == 2:  # Cutscene ends
            if self.cutscene_timer > 60:  # 1 second
                self.cutscene_active = False
                # Hide the guard after cutscene
                if self.guard:
                    self.guard["visible"] = False
    
    def draw_cutscene(self, surface):
        """Draw the entrance cutscene"""
        if not self.cutscene_active or not self.guard or self.cutscene_phase >= 2:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((1000, 700), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))
        
        # Draw Dragon Knight Guard
        if not self.guard.get("visible", True):
            return
            
        guard_x = self.guard["x"]
        guard_y = self.guard["y"] + self.guard["animation_offset"]
        guard_w = self.guard["width"]
        guard_h = self.guard["height"]
        
        # Dragon Knight shadow
        pygame.draw.ellipse(surface, (0, 0, 0), (guard_x + 2, guard_y + 62, guard_w - 4, 8))
        
        # Silver armor with detailed shading
        armor_base = (180, 180, 200)  # Silver base
        armor_highlight = (220, 220, 240)  # Bright silver
        armor_shadow = (140, 140, 160)  # Dark silver
        armor_detail = (100, 100, 120)  # Darker detail lines
        
        # Main armor body
        pygame.draw.rect(surface, armor_base, (guard_x + 2, guard_y + 12, guard_w - 4, guard_h - 12))
        # Armor highlight
        pygame.draw.rect(surface, armor_highlight, (guard_x + 4, guard_y + 14, guard_w - 8, 8))
        # Armor shadow
        pygame.draw.rect(surface, armor_shadow, (guard_x + 2, guard_y + 12, 4, guard_h - 12))
        
        # Dragon scale pattern on chest
        for i in range(3):
            for j in range(2):
                scale_x = guard_x + 8 + i * 8
                scale_y = guard_y + 20 + j * 8
                pygame.draw.ellipse(surface, armor_detail, (scale_x, scale_y, 6, 4))
                pygame.draw.ellipse(surface, armor_highlight, (scale_x + 1, scale_y + 1, 4, 2))
        
        # Dragon Knight head with detailed helmet
        head_x = guard_x + guard_w//2 - 10
        head_y = guard_y - 15
        
        # Head shadow
        pygame.draw.circle(surface, (180, 140, 100), (head_x + 10 + 1, head_y + 10 + 1), 10)
        # Head base
        pygame.draw.circle(surface, (240, 200, 150), (head_x + 10, head_y + 10), 10)
        # Head highlight
        pygame.draw.circle(surface, (255, 220, 180), (head_x + 8, head_y + 8), 4)
        # Head outline
        pygame.draw.circle(surface, (200, 150, 100), (head_x + 10, head_y + 10), 10, 1)
        
        # Dragon Knight full helmet with flares
        helmet_color = (160, 160, 180)
        helmet_highlight = (200, 200, 220)
        helmet_shadow = (120, 120, 140)
        helmet_detail = (100, 100, 120)
        
        # Helmet base (full coverage)
        helmet_base_points = [
            (head_x + 2, head_y), (head_x + 18, head_y),  # Top
            (head_x + 20, head_y + 2), (head_x + 20, head_y + 8),  # Right side
            (head_x + 18, head_y + 12), (head_x + 2, head_y + 12),  # Bottom
            (head_x, head_y + 8), (head_x, head_y + 2)  # Left side
        ]
        pygame.draw.polygon(surface, helmet_color, helmet_base_points)
        pygame.draw.polygon(surface, helmet_highlight, [
            (head_x + 4, head_y + 1), (head_x + 16, head_y + 1),
            (head_x + 18, head_y + 3), (head_x + 18, head_y + 7),
            (head_x + 16, head_y + 10), (head_x + 4, head_y + 10),
            (head_x + 2, head_y + 7), (head_x + 2, head_y + 3)
        ])
        pygame.draw.polygon(surface, helmet_shadow, [
            (head_x + 2, head_y), (head_x, head_y + 2), (head_x, head_y + 8),
            (head_x + 2, head_y + 12), (head_x + 4, head_y + 12)
        ])
        
        # Helmet crown with dragon motifs
        crown_points = [
            (head_x + 2, head_y), (head_x + 18, head_y),
            (head_x + 16, head_y - 2), (head_x + 14, head_y - 4),
            (head_x + 12, head_y - 6), (head_x + 8, head_y - 6),
            (head_x + 6, head_y - 4), (head_x + 4, head_y - 2)
        ]
        pygame.draw.polygon(surface, helmet_color, crown_points)
        pygame.draw.polygon(surface, helmet_highlight, [
            (head_x + 4, head_y - 1), (head_x + 16, head_y - 1),
            (head_x + 14, head_y - 3), (head_x + 12, head_y - 5),
            (head_x + 8, head_y - 5), (head_x + 6, head_y - 3)
        ])
        
        # Dragon horns on helmet (larger and more detailed)
        horn_color = (140, 140, 160)
        horn_highlight = (180, 180, 200)
        
        # Left horn (curved)
        left_horn_points = [
            (head_x + 4, head_y), (head_x + 2, head_y - 2), (head_x + 1, head_y - 6),
            (head_x + 2, head_y - 10), (head_x + 4, head_y - 12), (head_x + 6, head_y - 10),
            (head_x + 7, head_y - 6), (head_x + 6, head_y - 2)
        ]
        pygame.draw.polygon(surface, horn_color, left_horn_points)
        pygame.draw.polygon(surface, horn_highlight, [
            (head_x + 4, head_y), (head_x + 3, head_y - 2), (head_x + 2, head_y - 6),
            (head_x + 3, head_y - 10), (head_x + 5, head_y - 10), (head_x + 6, head_y - 6),
            (head_x + 5, head_y - 2)
        ])
        
        # Right horn (curved)
        right_horn_points = [
            (head_x + 12, head_y), (head_x + 14, head_y - 2), (head_x + 15, head_y - 6),
            (head_x + 14, head_y - 10), (head_x + 12, head_y - 12), (head_x + 10, head_y - 10),
            (head_x + 9, head_y - 6), (head_x + 10, head_y - 2)
        ]
        pygame.draw.polygon(surface, horn_color, right_horn_points)
        pygame.draw.polygon(surface, horn_highlight, [
            (head_x + 12, head_y), (head_x + 13, head_y - 2), (head_x + 14, head_y - 6),
            (head_x + 13, head_y - 10), (head_x + 11, head_y - 10), (head_x + 10, head_y - 6),
            (head_x + 11, head_y - 2)
        ])
        
        # Helmet visor (full face coverage with multiple slits)
        visor_points = [
            (head_x + 3, head_y + 3), (head_x + 17, head_y + 3),
            (head_x + 18, head_y + 5), (head_x + 18, head_y + 9),
            (head_x + 17, head_y + 11), (head_x + 3, head_y + 11),
            (head_x + 2, head_y + 9), (head_x + 2, head_y + 5)
        ]
        pygame.draw.polygon(surface, (80, 80, 100), visor_points)
        pygame.draw.polygon(surface, (120, 120, 140), [
            (head_x + 4, head_y + 4), (head_x + 16, head_y + 4),
            (head_x + 17, head_y + 6), (head_x + 17, head_y + 8),
            (head_x + 16, head_y + 10), (head_x + 4, head_y + 10),
            (head_x + 3, head_y + 8), (head_x + 3, head_y + 6)
        ])
        
        # Multiple visor slits for better visibility
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 4, head_y + 4, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 7, head_y + 4, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 10, head_y + 4, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 13, head_y + 4, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 4, head_y + 7, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 7, head_y + 7, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 10, head_y + 7, 2, 2))
        pygame.draw.rect(surface, (40, 40, 60), (head_x + 13, head_y + 7, 2, 2))
        
        # Chin guard (full face and chin coverage)
        chin_guard_points = [
            (head_x + 2, head_y + 11), (head_x + 18, head_y + 11),  # Top
            (head_x + 20, head_y + 13), (head_x + 20, head_y + 18),  # Right side
            (head_x + 18, head_y + 20), (head_x + 2, head_y + 20),   # Bottom
            (head_x, head_y + 18), (head_x, head_y + 13)             # Left side
        ]
        pygame.draw.polygon(surface, helmet_color, chin_guard_points)
        pygame.draw.polygon(surface, helmet_highlight, [
            (head_x + 4, head_y + 12), (head_x + 16, head_y + 12),
            (head_x + 18, head_y + 14), (head_x + 18, head_y + 17),
            (head_x + 16, head_y + 19), (head_x + 4, head_y + 19),
            (head_x + 2, head_y + 17), (head_x + 2, head_y + 14)
        ])
        pygame.draw.polygon(surface, helmet_shadow, [
            (head_x + 2, head_y + 11), (head_x, head_y + 13), (head_x, head_y + 18),
            (head_x + 2, head_y + 20), (head_x + 4, head_y + 20)
        ])
        
        # Chin guard breathing holes
        pygame.draw.circle(surface, (60, 60, 80), (head_x + 6, head_y + 15), 1)
        pygame.draw.circle(surface, (60, 60, 80), (head_x + 14, head_y + 15), 1)
        pygame.draw.circle(surface, (60, 60, 80), (head_x + 6, head_y + 17), 1)
        pygame.draw.circle(surface, (60, 60, 80), (head_x + 14, head_y + 17), 1)
        
        # Helmet flares (larger decorative metal pieces)
        flare_color = (180, 180, 200)
        flare_highlight = (220, 220, 240)
        
        # Left flare (larger)
        left_flare_points = [
            (head_x, head_y + 4), (head_x - 6, head_y + 1), (head_x - 8, head_y + 4),
            (head_x - 6, head_y + 7), (head_x, head_y + 10)
        ]
        pygame.draw.polygon(surface, flare_color, left_flare_points)
        pygame.draw.polygon(surface, flare_highlight, [
            (head_x, head_y + 4), (head_x - 3, head_y + 2), (head_x - 6, head_y + 4),
            (head_x - 3, head_y + 7), (head_x, head_y + 9)
        ])
        
        # Right flare (larger)
        right_flare_points = [
            (head_x + 20, head_y + 4), (head_x + 26, head_y + 1), (head_x + 28, head_y + 4),
            (head_x + 26, head_y + 7), (head_x + 20, head_y + 10)
        ]
        pygame.draw.polygon(surface, flare_color, right_flare_points)
        pygame.draw.polygon(surface, flare_highlight, [
            (head_x + 20, head_y + 4), (head_x + 23, head_y + 2), (head_x + 26, head_y + 4),
            (head_x + 23, head_y + 7), (head_x + 20, head_y + 9)
        ])
        
        # Helmet details (extensive rivets and engravings)
        for i in range(5):
            rivet_x = head_x + 3 + i * 4
            rivet_y = head_y + 2
            pygame.draw.circle(surface, helmet_detail, (rivet_x, rivet_y), 1)
            pygame.draw.circle(surface, helmet_highlight, (rivet_x, rivet_y), 1, 1)
        
        # Additional rivets on sides
        for i in range(3):
            rivet_x = head_x + 2
            rivet_y = head_y + 4 + i * 4
            pygame.draw.circle(surface, helmet_detail, (rivet_x, rivet_y), 1)
            pygame.draw.circle(surface, helmet_highlight, (rivet_x, rivet_y), 1, 1)
            
            rivet_x = head_x + 18
            pygame.draw.circle(surface, helmet_detail, (rivet_x, rivet_y), 1)
            pygame.draw.circle(surface, helmet_highlight, (rivet_x, rivet_y), 1, 1)
        
        # Dragon scale pattern on helmet (more extensive)
        for i in range(3):
            for j in range(3):
                scale_x = head_x + 5 + i * 5
                scale_y = head_y + 5 + j * 3
                pygame.draw.ellipse(surface, helmet_detail, (scale_x, scale_y, 3, 2))
                pygame.draw.ellipse(surface, helmet_highlight, (scale_x + 1, scale_y + 1, 1, 1))
        
        # Eyes (glowing through visor)
        pygame.draw.circle(surface, (255, 255, 0), (head_x + 6, head_y + 6), 2)
        pygame.draw.circle(surface, (255, 255, 0), (head_x + 10, head_y + 6), 2)
        pygame.draw.circle(surface, (255, 255, 255), (head_x + 5, head_y + 5), 1)
        pygame.draw.circle(surface, (255, 255, 255), (head_x + 9, head_y + 5), 1)
        
        # Dragon Knight arms with armor
        arm_color = (160, 160, 180)
        arm_highlight = (200, 200, 220)
        arm_shadow = (120, 120, 140)
        
        # Left arm
        pygame.draw.rect(surface, arm_color, (guard_x + 2, guard_y + 20, 6, 12))
        pygame.draw.rect(surface, arm_highlight, (guard_x + 3, guard_y + 21, 4, 6))
        pygame.draw.rect(surface, arm_shadow, (guard_x + 2, guard_y + 20, 2, 12))
        
        # Right arm
        pygame.draw.rect(surface, arm_color, (guard_x + guard_w - 8, guard_y + 20, 6, 12))
        pygame.draw.rect(surface, arm_highlight, (guard_x + guard_w - 9, guard_y + 21, 4, 6))
        pygame.draw.rect(surface, arm_shadow, (guard_x + guard_w - 8, guard_y + 20, 2, 12))
        
        # Dragon Knight legs with armor
        leg_color = (160, 160, 180)
        leg_highlight = (200, 200, 220)
        leg_shadow = (120, 120, 140)
        
        # Left leg
        pygame.draw.rect(surface, leg_color, (guard_x + 6, guard_y + 32, 8, 12))
        pygame.draw.rect(surface, leg_highlight, (guard_x + 7, guard_y + 33, 6, 6))
        pygame.draw.rect(surface, leg_shadow, (guard_x + 6, guard_y + 32, 2, 12))
        
        # Right leg
        pygame.draw.rect(surface, leg_color, (guard_x + guard_w - 14, guard_y + 32, 8, 12))
        pygame.draw.rect(surface, leg_highlight, (guard_x + guard_w - 15, guard_y + 33, 6, 6))
        pygame.draw.rect(surface, leg_shadow, (guard_x + guard_w - 14, guard_y + 32, 2, 12))
        
        # Dragon Knight shield (detailed)
        shield_x = guard_x - 25
        shield_y = guard_y + 15
        shield_color = (140, 140, 160)
        shield_highlight = (180, 180, 200)
        shield_shadow = (100, 100, 120)
        shield_detail = (80, 80, 100)
        
        # Shield base
        pygame.draw.ellipse(surface, shield_color, (shield_x, shield_y, 20, 30))
        # Shield highlight
        pygame.draw.ellipse(surface, shield_highlight, (shield_x + 2, shield_y + 2, 16, 26))
        # Shield shadow
        pygame.draw.ellipse(surface, shield_shadow, (shield_x, shield_y, 8, 30))
        
        # Shield border
        pygame.draw.ellipse(surface, shield_detail, (shield_x, shield_y, 20, 30), 2)
        
        # Dragon emblem on shield
        dragon_center_x = shield_x + 10
        dragon_center_y = shield_y + 15
        # Dragon head
        pygame.draw.circle(surface, shield_detail, (dragon_center_x, dragon_center_y - 5), 3)
        # Dragon body
        pygame.draw.ellipse(surface, shield_detail, (dragon_center_x - 2, dragon_center_y, 4, 8))
        # Dragon wings
        pygame.draw.polygon(surface, shield_detail, 
                          [(dragon_center_x - 2, dragon_center_y + 2), (dragon_center_x - 6, dragon_center_y - 2), (dragon_center_x - 4, dragon_center_y + 4)])
        pygame.draw.polygon(surface, shield_detail, 
                          [(dragon_center_x + 2, dragon_center_y + 2), (dragon_center_x + 6, dragon_center_y - 2), (dragon_center_x + 4, dragon_center_y + 4)])
        
        # Shield handle
        pygame.draw.rect(surface, (80, 60, 40), (shield_x + 8, shield_y + 12, 4, 6))
        
        # Dragon Knight sword (silver with dragon hilt)
        sword_x = guard_x + guard_w + 5
        sword_y = guard_y + guard_h//2
        
        # Sword handle (dragon-themed)
        handle_color = (120, 80, 40)
        handle_highlight = (160, 120, 80)
        pygame.draw.rect(surface, handle_color, (sword_x, sword_y - 2, 6, 8))
        pygame.draw.rect(surface, handle_highlight, (sword_x + 1, sword_y - 1, 4, 6))
        
        # Dragon hilt detail
        pygame.draw.circle(surface, (100, 60, 20), (sword_x + 3, sword_y + 2), 2)
        pygame.draw.circle(surface, (140, 100, 60), (sword_x + 3, sword_y + 2), 1)
        
        # Sword blade (silver)
        blade_color = (220, 220, 240)
        blade_highlight = (255, 255, 255)
        blade_shadow = (180, 180, 200)
        
        pygame.draw.rect(surface, blade_color, (sword_x + 6, sword_y - 3, 25, 6))
        pygame.draw.rect(surface, blade_highlight, (sword_x + 7, sword_y - 2, 23, 4))
        pygame.draw.rect(surface, blade_shadow, (sword_x + 6, sword_y - 3, 2, 6))
        
        # Sword tip
        pygame.draw.polygon(surface, blade_color, 
                          [(sword_x + 31, sword_y - 3), (sword_x + 35, sword_y), (sword_x + 31, sword_y + 3)])
        pygame.draw.polygon(surface, blade_highlight, 
                          [(sword_x + 31, sword_y - 3), (sword_x + 33, sword_y - 1), (sword_x + 31, sword_y + 1)])
        
        # Sword guard (dragon wings)
        guard_color = (160, 120, 80)
        guard_highlight = (200, 160, 120)
        
        # Left wing of guard
        pygame.draw.polygon(surface, guard_color, 
                          [(sword_x + 4, sword_y - 4), (sword_x, sword_y - 6), (sword_x + 2, sword_y - 2)])
        pygame.draw.polygon(surface, guard_highlight, 
                          [(sword_x + 4, sword_y - 4), (sword_x + 1, sword_y - 5), (sword_x + 3, sword_y - 3)])
        
        # Right wing of guard
        pygame.draw.polygon(surface, guard_color, 
                          [(sword_x + 4, sword_y + 4), (sword_x, sword_y + 6), (sword_x + 2, sword_y + 2)])
        pygame.draw.polygon(surface, guard_highlight, 
                          [(sword_x + 4, sword_y + 4), (sword_x + 1, sword_y + 5), (sword_x + 3, sword_y + 3)])
        
        # BEGINNER NOTE: Imported guard overlay.
        # The large procedural knight above is kept as fallback art. If the PNG
        # exists, we draw it over the old shapes so the town intro matches the
        # newer imported hero/enemy style without deleting the original code.
        imported_guard = load_sprite_by_height(TOWN_GUARD_SPRITE_PATH, 260)
        if imported_guard:
            sprite_x = int(guard_x + guard_w // 2 - imported_guard.get_width() / 2 + 10)
            sprite_y = int(guard_y + guard_h - imported_guard.get_height() + 16)
            shadow_w = max(95, int(imported_guard.get_width() * 0.42))
            shadow_h = max(12, int(imported_guard.get_height() * 0.05))
            pygame.draw.ellipse(
                surface,
                (0, 0, 0),
                (guard_x - 34, sprite_y + imported_guard.get_height() - 14, shadow_w, shadow_h),
            )
            surface.blit(imported_guard, (sprite_x, sprite_y))

        # Draw dialogue box
        if self.cutscene_phase == 1:
            # Safety check to prevent index out of bounds
            dialogue_index = min(self.guard["current_dialogue"], len(self.guard["dialogue"]) - 1)
            dialogue = self.guard["dialogue"][dialogue_index]
            
            # Dialogue box background.
            # BEGINNER NOTE: Keep this compact. Android already has a separate
            # NEXT touch button for town-guard cutscenes, so this box only
            # needs to show the current line clearly.
            box_x = 200
            box_y = 500
            box_w = 600
            box_h = 100
            
            # Box shadow
            pygame.draw.rect(surface, (20, 20, 20), (box_x + 3, box_y + 3, box_w, box_h))
            # Box base
            pygame.draw.rect(surface, (40, 40, 60), (box_x, box_y, box_w, box_h))
            pygame.draw.rect(surface, (80, 80, 120), (box_x, box_y, box_w, box_h), 3)
            
            # BEGINNER NOTE: The guard has longer story dialogue now, so the
            # town intro box wraps text instead of trying to force one long
            # sentence onto a single line.
            wrapped_dialogue = wrap_text_to_width(dialogue, font_small, box_w - 40)
            line_height = 24
            text_y = box_y + 38 + max(0, (3 - len(wrapped_dialogue)) * 6)
            for wrapped_line in wrapped_dialogue:
                text = font_small.render(wrapped_line, True, (255, 255, 255))
                text_rect = text.get_rect(center=(box_x + box_w//2, text_y))
                surface.blit(text, text_rect)
                text_y += line_height
            
            # Dragon Knight name
            name_text = font_tiny.render("Sir Marcus - Dragon Knight", True, (255, 215, 0))
            name_rect = name_text.get_rect(center=(box_x + box_w//2, box_y + 20))
            surface.blit(name_text, name_rect)

        # Draw keyboard prompt. Android still uses the separate NEXT button
        # built in systems/android_controls.py.
        if self.cutscene_phase == 1 and self.cutscene_timer > 60:
            prompt_text = font_tiny.render("ENTER/SPACE to continue", True, (200, 200, 200))
            prompt_rect = prompt_text.get_rect(center=(500, 620))
            surface.blit(prompt_text, prompt_rect)

# ============================================================================
# WORLD MAP CLASS - Manages the 3x3 world grid and camera system
# ============================================================================
class WorldMap:
    """
    Manages the entire 3x3 world grid, camera positioning, and area transitions.
    Handles coordinate conversion between world and screen space.

    Beginner note:
    `WORLD_LAYOUT` from `game_data/world.py` decides which area type appears in
    each grid cell. This class turns those strings into live `WorldArea` objects.
    """
    def __init__(self):
        self.areas = {}
        self.current_area_x = 1  # Start in center area
        self.current_area_y = 1
        self.camera_x = 0
        self.camera_y = 0
        self.area_transition_alpha = 0
        self.transitioning = False
        
        # Initialize all areas from the data table. The tuple key `(x, y)` makes
        # it easy to fetch an area by grid coordinate later.
        for y in range(WORLD_SIZE):
            for x in range(WORLD_SIZE):
                area_type = WORLD_LAYOUT[y][x]
                self.areas[(x, y)] = WorldArea(x, y, area_type)
        
        # Mark starting area as visited
        self.areas[(1, 1)].visited = True
    
    def get_current_area(self):
        return self.areas.get((self.current_area_x, self.current_area_y))
    
    def get_area_at_world_pos(self, world_x, world_y):
        """Get area at world position"""
        area_x = world_x // AREA_WIDTH
        area_y = world_y // AREA_HEIGHT
        return self.areas.get((area_x, area_y))
    
    def update_camera(self, player_world_x, player_world_y):
        """Update camera to follow player - now screen-based"""
        # Calculate which area the player is in
        area_x = player_world_x // AREA_WIDTH
        area_y = player_world_y // AREA_HEIGHT
        
        # Clamp area coordinates to valid range (0-2)
        area_x = max(0, min(2, area_x))
        area_y = max(0, min(2, area_y))
        
        # Set camera to show the current area
        self.camera_x = area_x * AREA_WIDTH
        self.camera_y = area_y * AREA_HEIGHT
    
    def world_to_screen(self, world_x, world_y):
        """Convert world coordinates to screen coordinates"""
        return (world_x - self.camera_x, world_y - self.camera_y)
    
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        return (screen_x + self.camera_x, screen_y + self.camera_y)
    
    def check_area_transition(self, player_world_x, player_world_y):
        """Check if player should transition to a new area"""
        # Clamp player position to world bounds
        player_world_x = max(0, min(WORLD_WIDTH - 1, player_world_x))
        player_world_y = max(0, min(WORLD_HEIGHT - 1, player_world_y))
        
        current_area = self.get_area_at_world_pos(player_world_x, player_world_y)
        if current_area:
            new_area_x, new_area_y = current_area.area_x, current_area.area_y
            if new_area_x != self.current_area_x or new_area_y != self.current_area_y:
                self.current_area_x = new_area_x
                self.current_area_y = new_area_y
                current_area.visited = True
                self.transitioning = True
                self.area_transition_alpha = 255
                return True
        return False
    

    
    def update_transition(self):
        """Update area transition effect"""
        if self.transitioning:
            self.area_transition_alpha = max(0, self.area_transition_alpha - 15)
            if self.area_transition_alpha <= 0:
                self.transitioning = False

# ============================================================================
# PARTICLE SYSTEM CLASSES - Visual effects and particle management
# ============================================================================
class Particle:
    """
    Individual particle for visual effects like explosions, magic, and environmental effects.

    Beginner note:
        A particle is a tiny temporary drawing object. It moves each frame,
        fades as it ages, then deletes itself when its lifetime is over.
    """
    def __init__(self, x, y, color, velocity, size, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        
    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.age += 1
        return self.age >= self.lifetime
        
    def draw(self, surface):
        alpha = 255 * (1 - self.age/self.lifetime)
        color = (*self.color[:3], int(alpha))
        radius = int(self.size * (1 - self.age/self.lifetime))
        if radius > 0:
            # Use regular pygame circle drawing instead of gfxdraw
            pygame.draw.circle(surface, color, (int(self.x), int(self.y)), radius)

class ParticleSystem:
    """
    Manages all particles in the game, including explosions, magic effects, and environmental particles.
    Provides methods for creating various types of particle effects.

    Beginner note:
        Other systems ask this object to create particles. This object owns the
        list and removes old particles after they finish animating.
    """
    def __init__(self):
        self.particles = []
        
    def add_particle(self, x, y, color, velocity, size, lifetime):
        self.particles.append(Particle(x, y, color, velocity, size, lifetime))
        
    def add_explosion(self, x, y, color, count=20, size_range=(2, 5), speed_range=(1, 3), lifetime_range=(20, 40)):
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(*speed_range)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            size = random.uniform(*size_range)
            lifetime = random.randint(*lifetime_range)
            self.add_particle(x, y, color, velocity, size, lifetime)
            
    def add_beam(self, x1, y1, x2, y2, color, width=3, particle_count=10, speed=2):
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx*dx + dy*dy)
        steps = max(1, int(distance / 5))
        
        for i in range(steps):
            px = x1 + (dx * i/steps)
            py = y1 + (dy * i/steps)
            for _ in range(particle_count):
                angle = random.uniform(0, math.pi*2)
                velocity = (math.cos(angle) * 0.2, math.sin(angle) * 0.2)
                self.add_particle(px, py, color, velocity, width, 15)
    
    def update(self):
        self.particles = [p for p in self.particles if not p.update()]
        
    def draw(self, surface, world_map=None):
        for particle in self.particles:
            if world_map:
                # Convert world coordinates to screen coordinates
                screen_x, screen_y = world_map.world_to_screen(particle.x, particle.y)
                # Temporarily set particle position for drawing
                original_x, original_y = particle.x, particle.y
                particle.x, particle.y = screen_x, screen_y
                particle.draw(surface)
                particle.x, particle.y = original_x, original_y
            else:
                particle.draw(surface)

# ============================================================================
# UI COMPONENTS - User interface elements
# ============================================================================
class Button:
    """
    Interactive button for menus and UI elements.
    Handles hover effects and click detection.

    Beginner note:
        This is the desktop/menu button class. Android virtual controls are
        drawn separately in `systems/android_controls.py`, while battle action
        buttons reuse this class inside `BattleScreen`.
    """
    def __init__(self, x, y, width, height, text, color=UI_BORDER, hover_color=(255, 215, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.text_surf = font_medium.render(text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.glow = 0
        self.glow_dir = 1
        self.selected = False
        
    def draw(self, surface):
        if self.glow > 0 or self.selected:
            glow_radius = max(self.glow, 8 if self.selected else 0)
            glow_surf = pygame.Surface((self.rect.width + glow_radius*2, self.rect.height + glow_radius*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.current_color[:3], 50), glow_surf.get_rect(), border_radius=12)
            surface.blit(glow_surf, (self.rect.x - glow_radius, self.rect.y - glow_radius))
        
        pygame.draw.rect(surface, UI_BG, self.rect, border_radius=8)
        
        border_color = (255, 215, 0) if self.selected else self.current_color
        border_width = 4 if self.selected else 3
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=8)
        
        surface.blit(self.text_surf, self.text_rect)
        
    def update(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            self.glow = min(self.glow + 2, 10)
            return True
        else:
            self.current_color = self.color
            self.glow = max(self.glow - 1, 0)
        return False
        
    def is_clicked(self, mouse_pos, mouse_click):
        return self.rect.collidepoint(mouse_pos) and mouse_click

# ============================================================================
# CHARACTER SYSTEM - Player character with stats, abilities, and progression
# ============================================================================
class Character:
    """
    Player character with RPG stats, abilities, and progression system.
    Supports multiple character classes: Warrior, Mage, Rogue

    Beginner note:
        This object stores the hero's live state: health, mana, level,
        inventory, equipment, position, and battle animation timers.
    """
    def __init__(self, char_type="Warrior"):
        self.type = char_type
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100

        stats = CHARACTER_CLASS_STATS.get(char_type, CHARACTER_CLASS_STATS["Rogue"])
        self.max_health = stats["max_health"]
        self.max_mana = stats["max_mana"]
        self.strength = stats["strength"]
        self.defense = stats["defense"]
        self.speed = stats["speed"]
            
        self.health = self.max_health
        self.mana = self.max_mana
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.attack_cooldown = 0
        self.kills = 0
        self.items_collected = 0
        self.inventory = {"health": 2, "mana": 1}
        # Non-consumable story inventory. Potions stay in `inventory`; trophies
        # and quest keepsakes live here so they can be shown without being used
        # up in battle.
        self.story_items = {}
        # Equipped gear is its own small system. `equipment` stores what is
        # currently worn, while `owned_equipment` remembers gear the player has
        # earned. Inventory is where the player can equip and unequip the gear
        # they want to use.
        self.equipment = get_default_equipment(char_type)
        self.owned_equipment = {
            item_key: 1
            for item_key in self.equipment.values()
            if item_key
        }
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        self.last_boss_level = 0  # Track the last boss level encountered
        self.just_leveled_up = False
        self.boss_cooldown = False  # Prevent boss battles during cooldown
        self.town_service_claims = set()
        # BEGINNER NOTE: The player does not start with SPECIAL unlocked.
        # Lion Sage grants this early in the story. BattleScreen checks this
        # flag before allowing the SPECIAL button to spend MP and attack.
        self.special_unlocked = False
        
    def move(self, dx, dy):
        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE
        
        # Check world boundaries (0 to WORLD_WIDTH/HEIGHT)
        if 0 <= new_x < WORLD_WIDTH:
            self.x = new_x
        if 0 <= new_y < WORLD_HEIGHT:
            self.y = new_y
            
    def update_animation(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        
        if self.attack_animation > 0:
            self.attack_animation -= 1
            
        if self.hit_animation > 0:
            self.hit_animation -= 1
            
    def draw(self, surface, sprite_mode="world"):
        offset_x = self.animation_offset
        offset_y = self.animation_offset
        
        if self.attack_animation > 0:
            if self.type == "Warrior":
                offset_x = 5 * math.sin(self.attack_animation * 0.2)
            elif self.type == "Mage":
                offset_y -= 5 * (1 - self.attack_animation / 10)
            else:  # Rogue
                offset_x = -5 * math.sin(self.attack_animation * 0.2)
                
        if self.hit_animation > 0:
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
        
        x = self.x + offset_x
        y = self.y + offset_y

        # BEGINNER NOTE: Imported hero sprite path.
        # This is the normal drawing path now. The Warrior, Mage, and Rogue PNGs
        # live in assets/processed/characters/. World-map sprites are smaller
        # so they fit inside a tile; battle sprites are larger so the imported
        # detail is visible during fights.
        if sprite_mode == "battle":
            sprite_height = 170
            foot_y = y + PLAYER_SIZE + 10
        else:
            sprite_height = 76
            foot_y = y + PLAYER_SIZE + 4

        if draw_character_sprite(
            surface,
            self.type,
            x + PLAYER_SIZE / 2,
            foot_y,
            sprite_height,
            self.hit_animation,
        ):
            return

        # BEGINNER NOTE: Legacy fallback starts here.
        # The large drawing blocks below are the older Python-drawn characters.
        # They are intentionally kept instead of deleted. If an imported PNG is
        # missing, renamed, or broken, the game still draws a playable hero.
        # Future coders can also compare these old procedural shapes against
        # the newer imported art path above.
        
        if self.type == "Warrior":
            # Draw shadow first
            pygame.draw.ellipse(surface, (0, 0, 0), (x + 2, y + 45, PLAYER_SIZE - 4, 8))
            
            # Paladin - Noble and righteous
            # Torso (armored and noble)
            torso_color = (192, 192, 192)  # Silver armor
            torso_highlight = (220, 220, 220)  # Bright silver
            torso_shadow = (160, 160, 160)  # Dark silver
            
            # Main torso (armored)
            torso_points = [
                (x + 6, y + 10), (x + PLAYER_SIZE - 6, y + 10),  # Top
                (x + PLAYER_SIZE - 4, y + 18), (x + PLAYER_SIZE - 2, y + 30),  # Right curve
                (x + PLAYER_SIZE - 4, y + 38), (x + 4, y + 38),  # Bottom
                (x + 2, y + 30), (x + 4, y + 18)  # Left curve
            ]
            pygame.draw.polygon(surface, torso_color, torso_points)
            pygame.draw.polygon(surface, torso_highlight, [
                (x + 8, y + 12), (x + PLAYER_SIZE - 8, y + 12),
                (x + PLAYER_SIZE - 10, y + 20), (x + 10, y + 20)
            ])
            pygame.draw.polygon(surface, torso_shadow, [
                (x + 6, y + 10), (x + 4, y + 18), (x + 2, y + 30),
                (x + 4, y + 38), (x + 6, y + 38)
            ])
            
            # Armor plates and details
            # Chest plate
            pygame.draw.ellipse(surface, (160, 160, 160), (x + 10, y + 14, PLAYER_SIZE - 20, 12))
            pygame.draw.ellipse(surface, (180, 180, 180), (x + 11, y + 15, PLAYER_SIZE - 22, 10))
            # Armor trim
            pygame.draw.ellipse(surface, (139, 69, 19), (x + 8, y + 8, PLAYER_SIZE - 16, 8))
            pygame.draw.ellipse(surface, (160, 82, 45), (x + 10, y + 9, PLAYER_SIZE - 20, 6))
            # Belt
            pygame.draw.ellipse(surface, (139, 69, 19), (x + 6, y + 32, PLAYER_SIZE - 12, 6))
            pygame.draw.ellipse(surface, (160, 82, 45), (x + 8, y + 33, PLAYER_SIZE - 16, 4))
            
            # Head (noble and righteous)
            head_center_x = x + PLAYER_SIZE // 2
            head_center_y = y + 8
            # Head shadow
            pygame.draw.circle(surface, (180, 140, 100), (head_center_x + 1, head_center_y + 1), 10)
            # Head base (noble)
            pygame.draw.ellipse(surface, (240, 200, 150), (head_center_x - 10, head_center_y - 8, 20, 22))
            # Head highlight
            pygame.draw.ellipse(surface, (255, 220, 180), (head_center_x - 8, head_center_y - 6, 16, 18))
            # Head outline
            pygame.draw.ellipse(surface, (200, 150, 100), (head_center_x - 10, head_center_y - 8, 20, 22), 1)
            
            # Noble hair (flowing and well-groomed)
            hair_color = (139, 69, 19)  # Brown
            hair_highlight = (160, 82, 45)
            # Hair base
            pygame.draw.ellipse(surface, hair_color, (head_center_x - 8, head_center_y - 6, 16, 8))
            pygame.draw.ellipse(surface, hair_highlight, (head_center_x - 6, head_center_y - 5, 12, 6))
            # Flowing hair strands
            hair_strands = [
                (head_center_x - 6, head_center_y - 6), (head_center_x - 4, head_center_y - 10),
                (head_center_x - 2, head_center_y - 8), (head_center_x, head_center_y - 12),
                (head_center_x + 2, head_center_y - 10), (head_center_x + 4, head_center_y - 12),
                (head_center_x + 6, head_center_y - 8)
            ]
            for i in range(len(hair_strands) - 1):
                pygame.draw.line(surface, hair_color, hair_strands[i], hair_strands[i+1], 2)
            
            # Noble eyes (determined and righteous)
            pygame.draw.ellipse(surface, (50, 50, 50), (head_center_x - 6, head_center_y - 2, 4, 3))
            pygame.draw.ellipse(surface, (50, 50, 50), (head_center_x + 2, head_center_y - 2, 4, 3))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x - 5, head_center_y - 3, 2, 2))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x + 3, head_center_y - 3, 2, 2))
            pygame.draw.circle(surface, (0, 150, 255), (head_center_x - 4, head_center_y - 1), 1)  # Blue eyes
            pygame.draw.circle(surface, (0, 150, 255), (head_center_x + 4, head_center_y - 1), 1)
            
            # Noble features
            pygame.draw.ellipse(surface, (220, 180, 140), (head_center_x - 1, head_center_y + 1, 2, 3))  # Nose
            
            # Noble beard (well-groomed)
            beard_points = [
                (head_center_x - 4, head_center_y + 4), (head_center_x - 6, head_center_y + 8),
                (head_center_x - 4, head_center_y + 12), (head_center_x, head_center_y + 14),
                (head_center_x + 4, head_center_y + 12), (head_center_x + 6, head_center_y + 8),
                (head_center_x + 4, head_center_y + 4)
            ]
            pygame.draw.polygon(surface, hair_color, beard_points)
            pygame.draw.polygon(surface, hair_highlight, [
                (head_center_x - 2, head_center_y + 6), (head_center_x - 4, head_center_y + 10),
                (head_center_x, head_center_y + 12), (head_center_x + 4, head_center_y + 10),
                (head_center_x + 2, head_center_y + 6)
            ])
            
            # Arms (armored)
            arm_color = (192, 192, 192)  # Silver armor
            arm_highlight = (220, 220, 220)  # Bright silver
            arm_shadow = (160, 160, 160)  # Dark silver
            
            # Left arm (armored)
            left_arm_points = [
                (x + 2, y + 16), (x + 10, y + 16), (x + 12, y + 20), (x + 10, y + 32), (x + 2, y + 32)
            ]
            pygame.draw.polygon(surface, arm_color, left_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + 3, y + 17), (x + 9, y + 17), (x + 10, y + 20), (x + 9, y + 30), (x + 3, y + 30)])
            # Armor details
            pygame.draw.ellipse(surface, (160, 160, 160), (x + 3, y + 20, 8, 6))
            pygame.draw.ellipse(surface, (180, 180, 180), (x + 4, y + 21, 6, 4))
            
            # Right arm (armored)
            right_arm_points = [
                (x + PLAYER_SIZE - 2, y + 16), (x + PLAYER_SIZE - 10, y + 16), 
                (x + PLAYER_SIZE - 12, y + 20), (x + PLAYER_SIZE - 10, y + 32), (x + PLAYER_SIZE - 2, y + 32)
            ]
            pygame.draw.polygon(surface, arm_color, right_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + PLAYER_SIZE - 3, y + 17), (x + PLAYER_SIZE - 9, y + 17), (x + PLAYER_SIZE - 10, y + 20), (x + PLAYER_SIZE - 9, y + 30), (x + PLAYER_SIZE - 3, y + 30)])
            # Armor details
            pygame.draw.ellipse(surface, (160, 160, 160), (x + PLAYER_SIZE - 11, y + 20, 8, 6))
            pygame.draw.ellipse(surface, (180, 180, 180), (x + PLAYER_SIZE - 12, y + 21, 6, 4))
            
            # Holy Sword (noble and righteous)
            sword_offset = 0
            if self.attack_animation > 0:
                sword_offset = -12 * (1 - self.attack_animation / 10)
            
            # Sword handle (ornate)
            pygame.draw.rect(surface, (139, 69, 19), (x + 32 + sword_offset, y + 16, 4, 10))
            pygame.draw.rect(surface, (160, 82, 45), (x + 33 + sword_offset, y + 17, 2, 8))
            # Handle grip
            pygame.draw.rect(surface, (101, 67, 33), (x + 33 + sword_offset, y + 20, 2, 4))
            pygame.draw.rect(surface, (139, 69, 19), (x + 33 + sword_offset, y + 21, 2, 2))
            
            # Sword guard (ornate cross)
            guard_points = [
                (x + 28 + sword_offset, y + 18), (x + 40 + sword_offset, y + 18),
                (x + 39 + sword_offset, y + 20), (x + 29 + sword_offset, y + 20)
            ]
            pygame.draw.polygon(surface, (192, 192, 192), guard_points)
            pygame.draw.polygon(surface, (220, 220, 220), [
                (x + 29 + sword_offset, y + 18), (x + 39 + sword_offset, y + 18),
                (x + 38 + sword_offset, y + 19), (x + 30 + sword_offset, y + 19)
            ])
            # Cross detail
            pygame.draw.rect(surface, (160, 160, 160), (x + 32 + sword_offset, y + 16, 4, 4))
            pygame.draw.rect(surface, (180, 180, 180), (x + 33 + sword_offset, y + 17, 2, 2))
            
            # Sword blade (holy and gleaming)
            blade_points = [
                (x + 30 + sword_offset, y + 12), (x + 34 + sword_offset, y + 12),
                (x + 35 + sword_offset, y + 18), (x + 34 + sword_offset, y + 24),
                (x + 30 + sword_offset, y + 24)
            ]
            pygame.draw.polygon(surface, (220, 220, 240), blade_points)
            pygame.draw.polygon(surface, (180, 180, 200), blade_points, 1)
            # Blade edge
            pygame.draw.line(surface, (255, 255, 255), (x + 30 + sword_offset, y + 12), (x + 34 + sword_offset, y + 12), 2)
            
            # Sword tip (pointed)
            pygame.draw.polygon(surface, (200, 200, 220), [
                (x + 30 + sword_offset, y + 12), (x + 36 + sword_offset, y + 6),
                (x + 32 + sword_offset, y + 12)
            ])
            pygame.draw.polygon(surface, (220, 220, 240), [
                (x + 30 + sword_offset, y + 12), (x + 34 + sword_offset, y + 8),
                (x + 32 + sword_offset, y + 12)
            ])
            
            # Holy glow effect
            glow_points = [
                (x + 32 + sword_offset, y + 8), (x + 34 + sword_offset, y + 8),
                (x + 35 + sword_offset, y + 10), (x + 34 + sword_offset, y + 12),
                (x + 32 + sword_offset, y + 12)
            ]
            pygame.draw.polygon(surface, (255, 255, 200), glow_points)
            pygame.draw.polygon(surface, (255, 255, 255), [
                (x + 32 + sword_offset, y + 9), (x + 34 + sword_offset, y + 9),
                (x + 34 + sword_offset, y + 11), (x + 32 + sword_offset, y + 11)
            ])
            
            # Legs (armored)
            leg_color = (192, 192, 192)  # Silver armor
            leg_highlight = (220, 220, 220)  # Bright silver
            leg_shadow = (160, 160, 160)  # Dark silver
            
            # Left leg (armored)
            left_leg_points = [
                (x + 6, y + 38), (x + 16, y + 38), (x + 17, y + 42), (x + 16, y + 50), (x + 6, y + 50)
            ]
            pygame.draw.polygon(surface, leg_color, left_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + 7, y + 39), (x + 15, y + 39), (x + 16, y + 42), (x + 15, y + 48), (x + 7, y + 48)])
            # Armor details
            pygame.draw.ellipse(surface, (160, 160, 160), (x + 7, y + 44, 10, 6))
            pygame.draw.ellipse(surface, (180, 180, 180), (x + 8, y + 45, 8, 4))
            
            # Right leg (armored)
            right_leg_points = [
                (x + PLAYER_SIZE - 6, y + 38), (x + PLAYER_SIZE - 16, y + 38), 
                (x + PLAYER_SIZE - 17, y + 42), (x + PLAYER_SIZE - 16, y + 50), (x + PLAYER_SIZE - 6, y + 50)
            ]
            pygame.draw.polygon(surface, leg_color, right_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + PLAYER_SIZE - 7, y + 39), (x + PLAYER_SIZE - 15, y + 39), (x + PLAYER_SIZE - 16, y + 42), (x + PLAYER_SIZE - 15, y + 48), (x + PLAYER_SIZE - 7, y + 48)])
            # Armor details
            pygame.draw.ellipse(surface, (160, 160, 160), (x + PLAYER_SIZE - 17, y + 44, 10, 6))
            pygame.draw.ellipse(surface, (180, 180, 180), (x + PLAYER_SIZE - 18, y + 45, 8, 4))
            
        elif self.type == "Mage":
            # Draw shadow first
            pygame.draw.ellipse(surface, (0, 0, 0), (x + 2, y + 50, PLAYER_SIZE - 4, 8))
            
            # Mystical Elementalist - Ethereal and otherworldly
            # Robe (flowing and ethereal)
            robe_color = (75, 0, 130)  # Deep purple
            robe_highlight = (138, 43, 226)  # Bright purple
            robe_shadow = (47, 0, 82)  # Dark purple
            robe_detail = (147, 112, 219)  # Medium purple
            
            # Main robe (flowing and mystical)
            robe_points = [
                (x + 4, y + 16), (x + PLAYER_SIZE - 4, y + 16),  # Top
                (x + PLAYER_SIZE - 2, y + 20), (x + PLAYER_SIZE, y + 28),  # Right curve
                (x + PLAYER_SIZE - 2, y + 36), (x + 2, y + 36),  # Bottom
                (x, y + 28), (x + 2, y + 20)  # Left curve
            ]
            pygame.draw.polygon(surface, robe_color, robe_points)
            pygame.draw.polygon(surface, robe_highlight, [
                (x + 6, y + 18), (x + PLAYER_SIZE - 6, y + 18),
                (x + PLAYER_SIZE - 8, y + 24), (x + 8, y + 24)
            ])
            pygame.draw.polygon(surface, robe_shadow, [
                (x + 4, y + 16), (x + 2, y + 20), (x, y + 28),
                (x + 2, y + 36), (x + 4, y + 36)
            ])
            
            # Mystical symbols and runes
            for i in range(4):
                rune_x = x + 10 + i * 6
                rune_y = y + 22
                # Star symbols
                star_points = [
                    (rune_x, rune_y - 2), (rune_x + 1, rune_y), (rune_x + 2, rune_y - 2),
                    (rune_x, rune_y + 2), (rune_x - 1, rune_y), (rune_x - 2, rune_y + 2)
                ]
                pygame.draw.polygon(surface, robe_detail, star_points)
                pygame.draw.polygon(surface, robe_highlight, [
                    (rune_x, rune_y - 1), (rune_x + 1, rune_y), (rune_x + 1, rune_y - 1),
                    (rune_x, rune_y + 1), (rune_x - 1, rune_y), (rune_x - 1, rune_y + 1)
                ])
            
            # Head (ethereal and mystical)
            head_center_x = x + PLAYER_SIZE // 2
            head_center_y = y + 10
            # Head shadow
            pygame.draw.circle(surface, (180, 140, 100), (head_center_x + 1, head_center_y + 1), 9)
            # Head base (slightly smaller, more ethereal)
            pygame.draw.ellipse(surface, (240, 200, 150), (head_center_x - 8, head_center_y - 6, 16, 18))
            # Head highlight
            pygame.draw.ellipse(surface, (255, 220, 180), (head_center_x - 6, head_center_y - 4, 12, 14))
            # Head outline
            pygame.draw.ellipse(surface, (200, 150, 100), (head_center_x - 8, head_center_y - 6, 16, 18), 1)
            
            # Mystical eyes (glowing)
            pygame.draw.ellipse(surface, (50, 50, 50), (head_center_x - 5, head_center_y - 2, 4, 3))
            pygame.draw.ellipse(surface, (50, 50, 50), (head_center_x + 1, head_center_y - 2, 4, 3))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x - 4, head_center_y - 3, 2, 2))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x + 2, head_center_y - 3, 2, 2))
            pygame.draw.circle(surface, (138, 43, 226), (head_center_x - 3, head_center_y - 1), 1)  # Purple eyes
            pygame.draw.circle(surface, (138, 43, 226), (head_center_x + 3, head_center_y - 1), 1)
            
            # Mystical hood (flowing)
            hood_color = (47, 0, 82)  # Dark purple
            hood_highlight = (75, 0, 130)
            hood_points = [
                (head_center_x - 8, head_center_y - 6), (head_center_x + 8, head_center_y - 6),
                (head_center_x + 10, head_center_y - 8), (head_center_x + 8, head_center_y - 12),
                (head_center_x + 4, head_center_y - 16), (head_center_x, head_center_y - 18),
                (head_center_x - 4, head_center_y - 16), (head_center_x - 8, head_center_y - 12),
                (head_center_x - 10, head_center_y - 8)
            ]
            pygame.draw.polygon(surface, hood_color, hood_points)
            pygame.draw.polygon(surface, hood_highlight, [
                (head_center_x - 6, head_center_y - 8), (head_center_x + 6, head_center_y - 8),
                (head_center_x + 8, head_center_y - 10), (head_center_x + 6, head_center_y - 14),
                (head_center_x + 2, head_center_y - 16), (head_center_x - 2, head_center_y - 16),
                (head_center_x - 6, head_center_y - 14), (head_center_x - 8, head_center_y - 10)
            ])
            
            # Mystical beard (ethereal wisps)
            beard_wisps = [
                (head_center_x - 4, head_center_y + 4), (head_center_x - 6, head_center_y + 8),
                (head_center_x - 4, head_center_y + 12), (head_center_x - 2, head_center_y + 16),
                (head_center_x + 2, head_center_y + 16), (head_center_x + 4, head_center_y + 12),
                (head_center_x + 6, head_center_y + 8), (head_center_x + 4, head_center_y + 4)
            ]
            # Draw individual wisps
            for i in range(len(beard_wisps) - 1):
                pygame.draw.line(surface, (147, 112, 219), beard_wisps[i], beard_wisps[i+1], 2)
            # Beard base
            pygame.draw.ellipse(surface, (138, 43, 226), (head_center_x - 4, head_center_y + 4, 8, 8))
            pygame.draw.ellipse(surface, (147, 112, 219), (head_center_x - 3, head_center_y + 5, 6, 6))
            
            # Arms with flowing sleeves
            hat_offset = 0
            if self.attack_animation > 0:
                hat_offset = -5 * (1 - self.attack_animation / 10)
            
            hat_color = (80, 40, 160)
            hat_highlight = (120, 60, 200)
            hat_shadow = (60, 30, 120)
            hat_detail = (100, 50, 180)
            
            # Hat base (curved)
            hat_base_points = [
                (head_center_x - 12, head_center_y - 5 + hat_offset),
                (head_center_x + 12, head_center_y - 5 + hat_offset),
                (head_center_x + 10, head_center_y - 2 + hat_offset),
                (head_center_x - 10, head_center_y - 2 + hat_offset)
            ]
            pygame.draw.polygon(surface, hat_color, hat_base_points)
            pygame.draw.polygon(surface, hat_highlight, [
                (head_center_x - 10, head_center_y - 4 + hat_offset),
                (head_center_x + 10, head_center_y - 4 + hat_offset),
                (head_center_x + 8, head_center_y - 2 + hat_offset),
                (head_center_x - 8, head_center_y - 2 + hat_offset)
            ])
            
            # Hat point (curved)
            hat_point_points = [
                (head_center_x, head_center_y - 15 + hat_offset),
                (head_center_x - 8, head_center_y - 5 + hat_offset),
                (head_center_x - 6, head_center_y - 8 + hat_offset),
                (head_center_x, head_center_y - 12 + hat_offset),
                (head_center_x + 6, head_center_y - 8 + hat_offset),
                (head_center_x + 8, head_center_y - 5 + hat_offset)
            ]
            pygame.draw.polygon(surface, hat_color, hat_point_points)
            pygame.draw.polygon(surface, hat_highlight, [
                (head_center_x, head_center_y - 15 + hat_offset),
                (head_center_x - 4, head_center_y - 8 + hat_offset),
                (head_center_x, head_center_y - 11 + hat_offset),
                (head_center_x + 4, head_center_y - 8 + hat_offset)
            ])
            
            # Hat details (stars)
            for i in range(3):
                star_x = head_center_x - 8 + i * 8
                star_y = head_center_y - 3 + hat_offset
                pygame.draw.circle(surface, hat_detail, (star_x, star_y), 1)
            
            # Staff with enhanced magical glow
            staff_top_offset = 0
            if self.attack_animation > 0:
                staff_top_offset = -10 * (1 - self.attack_animation / 10)
            
            # Staff shaft (curved)
            staff_points = [
                (x + 12, y + 12), (x + 14, y + 20), (x + 12, y + 28), (x + 10, y + 36), (x + 12, y + PLAYER_SIZE)
            ]
            for i in range(len(staff_points) - 1):
                pygame.draw.line(surface, (120, 80, 40), staff_points[i], staff_points[i + 1], 4)
            
            # Staff orb with enhanced glow effect
            orb_x = x + 12
            orb_y = y + 12 + staff_top_offset
            # Outer glow
            pygame.draw.circle(surface, (80, 80, 255), (orb_x, orb_y), 10)
            # Main orb
            pygame.draw.circle(surface, (100, 100, 255), (orb_x, orb_y), 8)
            pygame.draw.circle(surface, (150, 150, 255), (orb_x, orb_y), 5)
            pygame.draw.circle(surface, (200, 200, 255), (orb_x, orb_y), 2)
            # Orb highlight
            pygame.draw.circle(surface, (255, 255, 255), (orb_x - 2, orb_y - 2), 1)
            
            # Arms with flowing sleeves (mystical)
            arm_color = (75, 0, 130)  # Deep purple
            arm_highlight = (138, 43, 226)  # Bright purple
            arm_shadow = (47, 0, 82)  # Dark purple
            
            # Left arm (flowing sleeves)
            left_arm_points = [
                (x + 2, y + 20), (x + 10, y + 20), (x + 12, y + 24), (x + 10, y + 32), (x + 2, y + 32)
            ]
            pygame.draw.polygon(surface, arm_color, left_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + 3, y + 21), (x + 9, y + 21), (x + 10, y + 24), (x + 9, y + 30), (x + 3, y + 30)])
            # Sleeve details
            pygame.draw.ellipse(surface, robe_detail, (x + 3, y + 24, 8, 6))
            pygame.draw.ellipse(surface, robe_highlight, (x + 4, y + 25, 6, 4))
            
            # Right arm (flowing sleeves)
            right_arm_points = [
                (x + PLAYER_SIZE - 2, y + 20), (x + PLAYER_SIZE - 10, y + 20),
                (x + PLAYER_SIZE - 12, y + 24), (x + PLAYER_SIZE - 10, y + 32), (x + PLAYER_SIZE - 2, y + 32)
            ]
            pygame.draw.polygon(surface, arm_color, right_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + PLAYER_SIZE - 3, y + 21), (x + PLAYER_SIZE - 9, y + 21), (x + PLAYER_SIZE - 10, y + 24), (x + PLAYER_SIZE - 9, y + 30), (x + PLAYER_SIZE - 3, y + 30)])
            # Sleeve details
            pygame.draw.ellipse(surface, robe_detail, (x + PLAYER_SIZE - 11, y + 24, 8, 6))
            pygame.draw.ellipse(surface, robe_highlight, (x + PLAYER_SIZE - 12, y + 25, 6, 4))
            
            # Mystical Staff (ethereal)
            staff_offset = 0
            if self.attack_animation > 0:
                staff_offset = -15 * (1 - self.attack_animation / 10)
            
            # Staff shaft (mystical wood)
            staff_color = (139, 69, 19)  # Brown
            staff_highlight = (160, 82, 45)
            pygame.draw.rect(surface, staff_color, (x + 14 + staff_offset, y + 16, 4, 20))
            pygame.draw.rect(surface, staff_highlight, (x + 15 + staff_offset, y + 17, 2, 18))
            
            # Staff orb (mystical crystal)
            orb_x = x + 16 + staff_offset
            orb_y = y + 12
            # Outer glow
            pygame.draw.circle(surface, (138, 43, 226), (orb_x, orb_y), 8)
            # Main orb
            pygame.draw.circle(surface, (147, 112, 219), (orb_x, orb_y), 6)
            pygame.draw.circle(surface, (186, 85, 211), (orb_x, orb_y), 4)
            pygame.draw.circle(surface, (221, 160, 221), (orb_x, orb_y), 2)
            # Orb highlight
            pygame.draw.circle(surface, (255, 255, 255), (orb_x - 1, orb_y - 1), 1)
            
            # Mystical energy around orb
            for i in range(4):
                angle = i * 90
                energy_x = orb_x + int(6 * math.cos(math.radians(angle)))
                energy_y = orb_y + int(6 * math.sin(math.radians(angle)))
                pygame.draw.circle(surface, (138, 43, 226), (energy_x, energy_y), 2)
                pygame.draw.circle(surface, (147, 112, 219), (energy_x, energy_y), 1)
            
            # Legs with flowing robes
            leg_color = (75, 0, 130)  # Deep purple
            leg_highlight = (138, 43, 226)  # Bright purple
            leg_shadow = (47, 0, 82)  # Dark purple
            
            # Left leg (flowing robe)
            left_leg_points = [
                (x + 6, y + 36), (x + 14, y + 36), (x + 15, y + 40), (x + 14, y + 48), (x + 6, y + 48)
            ]
            pygame.draw.polygon(surface, leg_color, left_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + 7, y + 37), (x + 13, y + 37), (x + 14, y + 40), (x + 13, y + 46), (x + 7, y + 46)])
            # Robe hem details
            pygame.draw.ellipse(surface, robe_detail, (x + 7, y + 44, 8, 6))
            pygame.draw.ellipse(surface, robe_highlight, (x + 8, y + 45, 6, 4))
            
            # Right leg (flowing robe)
            right_leg_points = [
                (x + PLAYER_SIZE - 6, y + 36), (x + PLAYER_SIZE - 14, y + 36),
                (x + PLAYER_SIZE - 15, y + 40), (x + PLAYER_SIZE - 14, y + 48), (x + PLAYER_SIZE - 6, y + 48)
            ]
            pygame.draw.polygon(surface, leg_color, right_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + PLAYER_SIZE - 7, y + 37), (x + PLAYER_SIZE - 13, y + 37), (x + PLAYER_SIZE - 14, y + 40), (x + PLAYER_SIZE - 13, y + 46), (x + PLAYER_SIZE - 7, y + 46)])
            # Robe hem details
            pygame.draw.ellipse(surface, robe_detail, (x + PLAYER_SIZE - 15, y + 44, 8, 6))
            pygame.draw.ellipse(surface, robe_highlight, (x + PLAYER_SIZE - 16, y + 45, 6, 4))
            
        else:  # Rogue
            # Draw shadow first
            pygame.draw.ellipse(surface, (0, 0, 0), (x + 2, y + 50, PLAYER_SIZE - 4, 8))
            
            # Stealthy Assassin - Dark and mysterious
            # Leather armor (dark and sleek)
            armor_color = (40, 40, 40)  # Dark gray
            armor_highlight = (80, 80, 80)  # Light gray
            armor_shadow = (20, 20, 20)  # Very dark gray
            armor_detail = (60, 60, 60)  # Medium gray
            
            # Main armor (sleek and form-fitting)
            armor_points = [
                (x + 4, y + 16), (x + PLAYER_SIZE - 4, y + 16),  # Top
                (x + PLAYER_SIZE - 2, y + 20), (x + PLAYER_SIZE, y + 28),  # Right curve
                (x + PLAYER_SIZE - 2, y + 36), (x + 2, y + 36),  # Bottom
                (x, y + 28), (x + 2, y + 20)  # Left curve
            ]
            pygame.draw.polygon(surface, armor_color, armor_points)
            pygame.draw.polygon(surface, armor_highlight, [
                (x + 6, y + 18), (x + PLAYER_SIZE - 6, y + 18),
                (x + PLAYER_SIZE - 8, y + 24), (x + 8, y + 24)
            ])
            pygame.draw.polygon(surface, armor_shadow, [
                (x + 4, y + 16), (x + 2, y + 20), (x, y + 28),
                (x + 2, y + 36), (x + 4, y + 36)
            ])
            
            # Armor details (straps and buckles)
            for i in range(3):
                strap_x = x + 8 + i * 8
                strap_y = y + 22
                pygame.draw.rect(surface, armor_detail, (strap_x, strap_y, 4, 2))
                pygame.draw.rect(surface, armor_highlight, (strap_x + 1, strap_y + 1, 2, 1))
                # Buckles
                pygame.draw.rect(surface, (139, 69, 19), (strap_x + 1, strap_y - 1, 2, 4))
                pygame.draw.rect(surface, (160, 82, 45), (strap_x + 1, strap_y, 2, 2))
            
            # Leather straps and buckles
            for i in range(2):
                strap_x = x + 10 + i * 12
                strap_y = y + 22
                pygame.draw.rect(surface, armor_detail, (strap_x, strap_y, 8, 2))
                pygame.draw.rect(surface, (60, 60, 60), (strap_x + 2, strap_y, 4, 2))
            
            # Head (hidden and mysterious)
            head_center_x = x + PLAYER_SIZE // 2
            head_center_y = y + 10
            # Head shadow
            pygame.draw.circle(surface, (180, 140, 100), (head_center_x + 1, head_center_y + 1), 8)
            # Head base (smaller, more hidden)
            pygame.draw.ellipse(surface, (240, 200, 150), (head_center_x - 7, head_center_y - 5, 14, 16))
            # Head highlight
            pygame.draw.ellipse(surface, (255, 220, 180), (head_center_x - 5, head_center_y - 3, 10, 12))
            # Head outline
            pygame.draw.ellipse(surface, (200, 150, 100), (head_center_x - 7, head_center_y - 5, 14, 16), 1)
            
            # Dark hood (mysterious)
            hood_color = (20, 20, 20)  # Very dark
            hood_highlight = (40, 40, 40)
            hood_points = [
                (head_center_x - 8, head_center_y - 5), (head_center_x + 8, head_center_y - 5),
                (head_center_x + 10, head_center_y - 7), (head_center_x + 8, head_center_y - 11),
                (head_center_x + 4, head_center_y - 15), (head_center_x, head_center_y - 17),
                (head_center_x - 4, head_center_y - 15), (head_center_x - 8, head_center_y - 11),
                (head_center_x - 10, head_center_y - 7)
            ]
            pygame.draw.polygon(surface, hood_color, hood_points)
            pygame.draw.polygon(surface, hood_highlight, [
                (head_center_x - 6, head_center_y - 7), (head_center_x + 6, head_center_y - 7),
                (head_center_x + 8, head_center_y - 9), (head_center_x + 6, head_center_y - 13),
                (head_center_x + 2, head_center_y - 15), (head_center_x - 2, head_center_y - 15),
                (head_center_x - 6, head_center_y - 13), (head_center_x - 8, head_center_y - 9)
            ])
            
            # Hood stitching (stealth details)
            for i in range(3):
                stitch_x = head_center_x - 5 + i * 5
                stitch_y = head_center_y - 9
                pygame.draw.line(surface, (10, 10, 10), (stitch_x, stitch_y), (stitch_x, stitch_y + 2), 1)
            
            # Eyes (hidden in shadow, mysterious)
            pygame.draw.ellipse(surface, (10, 10, 10), (head_center_x - 4, head_center_y - 2, 5, 3))
            pygame.draw.ellipse(surface, (10, 10, 10), (head_center_x - 1, head_center_y - 2, 5, 3))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x - 3, head_center_y - 3, 2, 2))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x, head_center_y - 3, 2, 2))
            pygame.draw.circle(surface, (0, 255, 0), (head_center_x - 2, head_center_y - 1), 1)  # Green eyes
            pygame.draw.circle(surface, (0, 255, 0), (head_center_x + 1, head_center_y - 1), 1)
            pygame.draw.ellipse(surface, (255, 255, 0), (head_center_x - 1, head_center_y - 2, 4, 3))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x - 2, head_center_y - 3, 2, 2))
            pygame.draw.ellipse(surface, (255, 255, 255), (head_center_x, head_center_y - 3, 2, 2))
            pygame.draw.circle(surface, (0, 0, 0), (head_center_x - 1, head_center_y - 1), 1)
            pygame.draw.circle(surface, (0, 0, 0), (head_center_x + 1, head_center_y - 1), 1)
            
            # Daggers with enhanced detail
            dagger_offset = 0
            if self.attack_animation > 0:
                dagger_offset = -15 * (1 - self.attack_animation / 10)
            
            # Left dagger (curved blade)
            left_dagger_points = [
                (x + 18 + dagger_offset, y + 22), (x + 22 + dagger_offset, y + 18),
                (x + 25 + dagger_offset, y + 20), (x + 26 + dagger_offset, y + 22),
                (x + 25 + dagger_offset, y + 24), (x + 22 + dagger_offset, y + 22)
            ]
            pygame.draw.polygon(surface, (200, 200, 220), left_dagger_points)
            pygame.draw.polygon(surface, (180, 180, 200), left_dagger_points, 1)
            # Dagger handle (wrapped)
            pygame.draw.rect(surface, (120, 80, 40), (x + 20 + dagger_offset, y + 22, 4, 6))
            for i in range(2):
                pygame.draw.line(surface, (100, 60, 20), (x + 20 + dagger_offset, y + 24 + i*2), (x + 24 + dagger_offset, y + 24 + i*2), 1)
            
            # Right dagger (curved blade)
            right_dagger_points = [
                (x + PLAYER_SIZE - 18 - dagger_offset, y + 22), (x + PLAYER_SIZE - 22 - dagger_offset, y + 18),
                (x + PLAYER_SIZE - 25 - dagger_offset, y + 20), (x + PLAYER_SIZE - 26 - dagger_offset, y + 22),
                (x + PLAYER_SIZE - 25 - dagger_offset, y + 24), (x + PLAYER_SIZE - 22 - dagger_offset, y + 22)
            ]
            pygame.draw.polygon(surface, (200, 200, 220), right_dagger_points)
            pygame.draw.polygon(surface, (180, 180, 200), right_dagger_points, 1)
            # Dagger handle (wrapped)
            pygame.draw.rect(surface, (120, 80, 40), (x + PLAYER_SIZE - 24 - dagger_offset, y + 22, 4, 6))
            for i in range(2):
                pygame.draw.line(surface, (100, 60, 20), (x + PLAYER_SIZE - 24 - dagger_offset, y + 24 + i*2), (x + PLAYER_SIZE - 20 - dagger_offset, y + 24 + i*2), 1)
            
            # Arms with organic shape
            arm_color = (100, 0, 0)
            arm_highlight = (140, 0, 0)
            arm_shadow = (80, 0, 0)
            
            # Left arm (curved)
            left_arm_points = [
                (x + 2, y + 25), (x + 8, y + 25), (x + 10, y + 28), (x + 8, y + 35), (x + 2, y + 35)
            ]
            pygame.draw.polygon(surface, arm_color, left_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + 3, y + 26), (x + 7, y + 26), (x + 9, y + 28), (x + 7, y + 33), (x + 3, y + 33)])
            
            # Right arm (curved)
            right_arm_points = [
                (x + PLAYER_SIZE - 2, y + 25), (x + PLAYER_SIZE - 8, y + 25),
                (x + PLAYER_SIZE - 10, y + 28), (x + PLAYER_SIZE - 8, y + 35), (x + PLAYER_SIZE - 2, y + 35)
            ]
            pygame.draw.polygon(surface, arm_color, right_arm_points)
            pygame.draw.polygon(surface, arm_highlight, [(x + PLAYER_SIZE - 3, y + 26), (x + PLAYER_SIZE - 7, y + 26), (x + PLAYER_SIZE - 9, y + 28), (x + PLAYER_SIZE - 7, y + 33), (x + PLAYER_SIZE - 3, y + 33)])
            
            # Legs with organic shape
            leg_color = (80, 0, 0)
            leg_highlight = (120, 0, 0)
            leg_shadow = (60, 0, 0)
            
            # Left leg (curved)
            left_leg_points = [
                (x + 6, y + 35), (x + 14, y + 35), (x + 15, y + 38), (x + 14, y + 45), (x + 6, y + 45)
            ]
            pygame.draw.polygon(surface, leg_color, left_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + 7, y + 36), (x + 13, y + 36), (x + 14, y + 38), (x + 13, y + 43), (x + 7, y + 43)])
            
            # Right leg (curved)
            right_leg_points = [
                (x + PLAYER_SIZE - 14, y + 35), (x + PLAYER_SIZE - 6, y + 35),
                (x + PLAYER_SIZE - 5, y + 38), (x + PLAYER_SIZE - 6, y + 45), (x + PLAYER_SIZE - 14, y + 45)
            ]
            pygame.draw.polygon(surface, leg_color, right_leg_points)
            pygame.draw.polygon(surface, leg_highlight, [(x + PLAYER_SIZE - 13, y + 36), (x + PLAYER_SIZE - 7, y + 36), (x + PLAYER_SIZE - 6, y + 38), (x + PLAYER_SIZE - 7, y + 43), (x + PLAYER_SIZE - 13, y + 43)])
            
            # Belt with buckle
            pygame.draw.rect(surface, (40, 40, 40), (x + 2, y + 35, PLAYER_SIZE - 4, 3))
            # Belt buckle
            buckle_x = x + PLAYER_SIZE // 2 - 3
            buckle_y = y + 35
            pygame.draw.rect(surface, (80, 80, 80), (buckle_x, buckle_y, 6, 3))
            pygame.draw.rect(surface, (120, 120, 120), (buckle_x + 1, buckle_y + 1, 4, 1))
    
    def start_attack_animation(self):
        self.attack_animation = 10
        
    def start_hit_animation(self):
        self.hit_animation = 5

    def get_inventory_count(self, item_type):
        return self.inventory.get(item_type, 0)

    def add_inventory_item(self, item_type, amount=1):
        profile = ITEM_PROFILES.get(item_type)
        if not profile or not profile.get("battle_usable"):
            return 0

        limit = profile.get("inventory_limit", amount)
        current = self.inventory.get(item_type, 0)
        added = min(amount, max(0, limit - current))
        if added:
            self.inventory[item_type] = current + added
        return added

    def use_inventory_item(self, item_type):
        current = self.inventory.get(item_type, 0)
        if current <= 0:
            return False

        self.inventory[item_type] = current - 1
        return True

    def add_story_item(self, item_key, amount=1):
        """Add a trophy or story keepsake to the player's permanent inventory."""
        amount = max(0, int(amount))
        if amount <= 0:
            return 0
        current = self.story_items.get(item_key, 0)
        self.story_items[item_key] = current + amount
        return amount

    def get_story_item_count(self, item_key):
        """Return how many copies of a trophy/story item the player owns."""
        return self.story_items.get(item_key, 0)

    def add_equipment_item(self, item_key, auto_equip=True):
        """Add a weapon, armor, or accessory and optionally equip it.

        Beginner note:
            Story rewards can call this with a key from `game_data/equipment.py`.
            The method validates the key, stores ownership, and equips it in the
            correct slot. This keeps equipment reward logic out of the story
            tables and out of battle math.
        """
        profile = get_equipment_item(item_key)
        if not profile:
            return False

        self.owned_equipment[item_key] = self.owned_equipment.get(item_key, 0) + 1
        if auto_equip:
            self.equipment[profile["slot"]] = item_key
        return True

    def get_owned_equipment_for_slot(self, slot):
        """Return owned gear keys for one slot in progression order."""
        owned_keys = set(self.owned_equipment)
        return [
            item_key
            for item_key, _profile in iter_equipment_for_slot(slot)
            if item_key in owned_keys
        ]

    def equip_owned_item(self, item_key):
        """Equip an owned gear item and return True when it changed a slot."""
        profile = get_equipment_item(item_key)
        if not profile or self.owned_equipment.get(item_key, 0) <= 0:
            return False
        self.equipment[profile["slot"]] = item_key
        return True

    def unequip_slot(self, slot):
        """Remove the gear from one slot if something is equipped there."""
        if slot not in self.equipment or not self.equipment.get(slot):
            return False
        self.equipment[slot] = None
        return True

    def get_equipment_bonus(self, stat_key):
        """Return the combined equipped bonus for one stat."""
        total = 0
        for item_key in self.equipment.values():
            profile = get_equipment_item(item_key)
            if profile:
                total += int(profile.get("bonuses", {}).get(stat_key, 0))
        return total

    def effective_strength(self):
        """Base strength plus equipped weapon/accessory bonuses."""
        return self.strength + self.get_equipment_bonus("strength")

    def effective_defense(self):
        """Base defense plus equipped armor/accessory bonuses."""
        return self.defense + self.get_equipment_bonus("defense")

    def effective_speed(self):
        """Base speed plus equipped gear bonuses."""
        return self.speed + self.get_equipment_bonus("speed")
        
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.effective_defense() // 3)
        self.health -= actual_damage
        self.start_hit_animation()
        return actual_damage
    
    def gain_exp(self, amount):
        self.exp += amount
        while self.exp >= self.exp_to_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.5)
        self.max_health += 20
        self.max_mana += 15
        self.strength += 3
        self.defense += 2
        self.speed += 1
        self.health = self.max_health
        self.mana = self.max_mana
        self.just_leveled_up = True
        self.boss_cooldown = False  # Reset cooldown on level up
    
    def draw_stats(self, surface, x, y, width=240):
        """Draw the compact player HUD used in the upper-left panel.

        Beginner note:
            The old HUD placed HP/MP words to the right of the bars, which
            looked fine on a large desktop window but spilled outside the
            Android panel. This version keeps every label inside the fixed HUD
            width so the panel remains neat on phone screens.
        """
        bar_bg = (18, 18, 30)
        label_color = (245, 245, 245)
        shadow_color = (5, 5, 12)
        width = max(170, int(width))

        def draw_labeled_bar(row_y, label, current_value, max_value, fill_color, height=24):
            """Draw one status row, such as HP, MP, or EXP."""
            outer = pygame.Rect(x, row_y, width, height)
            inner = outer.inflate(-4, -4)
            safe_max = max(1, max_value)
            fill_ratio = clamp(current_value / safe_max, 0.0, 1.0)
            fill_width = int(inner.width * fill_ratio)

            pygame.draw.rect(surface, bar_bg, outer, border_radius=4)
            if fill_width > 0:
                pygame.draw.rect(
                    surface,
                    fill_color,
                    (inner.x, inner.y, fill_width, inner.height),
                    border_radius=3
                )
            pygame.draw.rect(surface, UI_BORDER, outer, 1, border_radius=4)

            text = render_fitted_text(label, label_color, width - 12, (font_tiny,))
            shadow = render_fitted_text(label, shadow_color, width - 12, (font_tiny,))
            text_x = outer.x + 6
            text_y = outer.y + (outer.height - text.get_height()) // 2
            surface.blit(shadow, (text_x + 1, text_y + 1))
            surface.blit(text, (text_x, text_y))

        draw_labeled_bar(y, f"HP {self.health}/{self.max_health}", self.health, self.max_health, HEALTH_COLOR)
        draw_labeled_bar(y + 29, f"MP {self.mana}/{self.max_mana}", self.mana, self.max_mana, MANA_COLOR)
        draw_labeled_bar(y + 58, f"LV {self.level}  EXP {self.exp}/{self.exp_to_level}", self.exp, self.exp_to_level, EXP_COLOR, 20)

        stats_text = render_fitted_text(
            f"STR {self.effective_strength()}  DEF {self.effective_defense()}  SPD {self.effective_speed()}",
            TEXT_COLOR,
            width,
            (font_tiny,)
        )
        surface.blit(stats_text, (x, y + 86))

        bag_text = render_fitted_text(
            f"BAG HPx{self.get_inventory_count('health')}  MPx{self.get_inventory_count('mana')}",
            (220, 220, 180),
            width,
            (font_tiny,)
        )
        surface.blit(bag_text, (x, y + 108))

# ============================================================================
# ENEMY SYSTEM - Various enemy types with AI and combat abilities
# ============================================================================
class Enemy:
    """
    Base enemy class with AI behavior, combat abilities, and progression scaling.
    Different enemy types have unique abilities and visual appearances.

    Beginner note:
        Normal enemies use an element key such as `fiery`, `ice`, or
        `ghost_face`. That key chooses colors, names, status effects, and
        optional imported sprites.
    """
    def __init__(self, player_level):
        self.size = ENEMY_SIZE
        # Enemies will be positioned by the spawn system
        self.x = 0
        self.y = 0
        self.set_type(random.choice(list(ENEMY_NAME_POOLS)))
        
        self.health = random.randint(20, 30) + player_level * 5
        self.max_health = self.health
        self.strength = random.randint(5, 10) + player_level * 2
        self.speed = random.randint(3, 6) + player_level // 2
        self.movement_cooldown = 0
        self.movement_delay = 60
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0

    def set_type(self, enemy_type):
        self.enemy_type = enemy_type
        self.profile = get_element_profile(enemy_type)
        self.color = self.profile["primary_color"]
        self.sprite_path = GHOST_FACE_SPRITE_PATH if enemy_type == "ghost_face" else None
        self.size = 78 if self.sprite_path else ENEMY_SIZE
        names = ENEMY_NAME_POOLS.get(enemy_type, ["Wandering Foe"])
        self.name = random.choice(names)
        
    def update_animation(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        
        if self.attack_animation > 0:
            self.attack_animation -= 1
            
        if self.hit_animation > 0:
            self.hit_animation -= 1
            
    def start_attack_animation(self):
        self.attack_animation = 10
        
    def start_hit_animation(self):
        self.hit_animation = 5
        
    def draw(self, surface):
        offset_x = 0
        offset_y = self.animation_offset
        
        if self.attack_animation > 0:
            offset_x = 5 * math.sin(self.attack_animation * 0.2)
            
        if self.hit_animation > 0:
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
        
        x = self.x + offset_x
        y = self.y + offset_y

        if draw_enemy_sprite(surface, self, x, y, self.size):
            bar_width = max(40, self.size)
            pygame.draw.rect(surface, (20, 20, 30), (x - 5, y - 15, bar_width, 8), border_radius=2)
            health_width = (bar_width - 2) * (self.health / self.max_health)
            pygame.draw.rect(surface, HEALTH_COLOR, (x - 4, y - 14, health_width, 6), border_radius=2)

            name_text = font_tiny.render(self.name, True, TEXT_COLOR)
            name_rect = name_text.get_rect(midtop=(x + self.size//2, y - 30))
            surface.blit(name_text, name_rect)
            return

        profile = get_element_profile(self.enemy_type)
        
        if self.enemy_type == "fiery":
            pygame.draw.ellipse(surface, profile["primary_color"], (x, y, self.size, self.size))
            flame_size = 15
            if self.attack_animation > 0:
                flame_size = 20 * (1 - self.attack_animation / 10)
            for i in range(8):
                angle = i * math.pi / 4
                flame_x = x + self.size//2 + math.cos(angle) * flame_size
                flame_y = y + self.size//2 + math.sin(angle) * flame_size
                pygame.draw.polygon(surface, profile["secondary_color"], 
                                  [(x + self.size//2, y + self.size//2),
                                   (flame_x, flame_y),
                                   (flame_x + math.cos(angle+0.3)*5, flame_y + math.sin(angle+0.3)*5)])
            pygame.draw.circle(surface, profile["accent_color"], (x + 15, y + 15), 4)
            pygame.draw.circle(surface, profile["accent_color"], (x + self.size - 15, y + 15), 4)
            pygame.draw.arc(surface, profile["secondary_color"], (x + 10, y + 20, self.size - 20, 15), 0, math.pi, 2)
            
        elif self.enemy_type == "shadow":
            pygame.draw.ellipse(surface, profile["primary_color"], (x, y, self.size, self.size))
            smoke_count = 6
            if self.attack_animation > 0:
                smoke_count = 12 * (1 - self.attack_animation / 10)
            for i in range(int(smoke_count)):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                pygame.draw.circle(surface, profile["secondary_color"], 
                                 (x + self.size//2 + offset_x, y + self.size//2 + offset_y), 
                                 random.randint(3, 8))
            pygame.draw.circle(surface, profile["accent_color"], (x + 20, y + 20), 5)
            pygame.draw.circle(surface, profile["accent_color"], (x + self.size - 20, y + 20), 5)
            claw_length = 10
            if self.attack_animation > 0:
                claw_length = 15 * (1 - self.attack_animation / 10)
            pygame.draw.line(surface, profile["accent_color"], (x, y + self.size), (x - claw_length, y + self.size + claw_length), 2)
            pygame.draw.line(surface, profile["accent_color"], (x + self.size, y + self.size), (x + self.size + claw_length, y + self.size + claw_length), 2)
            
        else:  # Ice enemy
            pygame.draw.ellipse(surface, profile["primary_color"], (x, y, self.size, self.size))
            shard_length = 20
            if self.attack_animation > 0:
                shard_length = 30 * (1 - self.attack_animation / 10)
            for i in range(8):
                angle = i * math.pi / 4
                shard_x = x + self.size//2 + math.cos(angle) * shard_length
                shard_y = y + self.size//2 + math.sin(angle) * shard_length
                pygame.draw.line(surface, profile["secondary_color"], 
                               (x + self.size//2, y + self.size//2),
                               (shard_x, shard_y), 2)
            pygame.draw.circle(surface, profile["accent_color"], (x + 15, y + 15), 4)
            pygame.draw.circle(surface, profile["accent_color"], (x + self.size - 15, y + 15), 4)
            breath_width = 10
            if self.attack_animation > 0:
                breath_width = 20 * (1 - self.attack_animation / 10)
            pygame.draw.arc(surface, profile["secondary_color"], (x + 10, y + 25, self.size - 20, breath_width), 0, math.pi, 2)
            
        bar_width = 40
        pygame.draw.rect(surface, (20, 20, 30), (x - 5, y - 15, bar_width, 8), border_radius=2)
        health_width = (bar_width - 2) * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (x - 4, y - 14, health_width, 6), border_radius=2)
        
        # Draw enemy name
        name_text = font_tiny.render(self.name, True, TEXT_COLOR)
        name_rect = name_text.get_rect(midtop=(x + self.size//2, y - 30))
        surface.blit(name_text, name_rect)
        
    def update(self, player_x, player_y):
        self.update_animation()
        self.movement_cooldown -= 1
        if self.movement_cooldown <= 0:
            self.movement_cooldown = self.movement_delay
            
            dx, dy = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
            new_x = self.x + dx * GRID_SIZE
            new_y = self.y + dy * GRID_SIZE
            
            # Check world boundaries
            if 0 <= new_x < WORLD_WIDTH:
                self.x = new_x
            if 0 <= new_y < WORLD_HEIGHT:
                self.y = new_y

# ============================================================================
# ITEM SYSTEM - Collectible items and power-ups
# ============================================================================
class Item:
    """
    Collectible items that provide healing, mana restoration, or other benefits.
    Items spawn randomly in the world and can be collected by the player.

    Beginner note:
        This is for overworld pickups, not Inventory gear. Consumable item
        effects come from `game_data/mechanics.py`.
    """
    def __init__(self):
        self.size = ITEM_SIZE
        # Items will be positioned by the spawn system
        self.x = 0
        self.y = 0
        self.type = random.choice(ITEM_SPAWN_TABLE)
        self.profile = ITEM_PROFILES[self.type]
        self.color = self.profile["color"]
        self.pulse = 0
        self.float_offset = 0
        
    def update(self):
        self.pulse += 0.1
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        
    def draw(self, surface):
        pulse_size = int(self.size//2 + math.sin(self.pulse) * 3)
        y_pos = int(self.y + self.float_offset)
        
        pygame.draw.circle(surface, self.color, (self.x + self.size//2, y_pos + self.size//2), pulse_size)
        
        if self.type == "health":
            pygame.draw.rect(surface, (255, 255, 255), (self.x + 10, y_pos + 8, 10, 14), border_radius=2)
        elif self.type == "mana":
            pygame.draw.polygon(surface, (255, 255, 255), 
                              [(self.x + 15, y_pos + 8),
                               (self.x + 8, y_pos + 22),
                               (self.x + 22, y_pos + 22)])
        elif self.type == "might":
            pygame.draw.polygon(surface, (255, 255, 255),
                              [(self.x + 15, y_pos + 6),
                               (self.x + 19, y_pos + 14),
                               (self.x + 27, y_pos + 15),
                               (self.x + 21, y_pos + 20),
                               (self.x + 23, y_pos + 28),
                               (self.x + 15, y_pos + 23),
                               (self.x + 7, y_pos + 28),
                               (self.x + 9, y_pos + 20),
                               (self.x + 3, y_pos + 15),
                               (self.x + 11, y_pos + 14)])
        elif self.type == "ward":
            pygame.draw.polygon(surface, (255, 255, 255),
                              [(self.x + 15, y_pos + 7),
                               (self.x + 24, y_pos + 11),
                               (self.x + 22, y_pos + 22),
                               (self.x + 15, y_pos + 28),
                               (self.x + 8, y_pos + 22),
                               (self.x + 6, y_pos + 11)])

# ============================================================================
# DECORATIVE DRAGON - Animated background element for title screen
# ============================================================================
class Dragon:
    """
    Decorative dragon for the title screen with fire breathing animation.
    This is a visual element, not a combat enemy.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame = 0
        self.fire_frame = 0
        self.fire_active = False
        self.flap_direction = 1
        self.flap_speed = 0.1

    def get_boss_palette(self, boss_level):
        """Return the dragon/body and fire colors for a boss level.

        Beginner note:
            `DRAGON_BOSS_COLORS` is shared with real dragon boss fights. Using it
            here makes the title/opening dragon preview the same progression
            palette the player will later fight.
        """
        color_index = (max(1, int(boss_level)) - 1) % len(DRAGON_BOSS_COLORS)
        return DRAGON_BOSS_COLORS[color_index]

    def draw(self, surface, boss_level=1, target_height=270):
        dragon_color, fire_color = self.get_boss_palette(boss_level)
        imported_dragon = load_tinted_sprite_by_height(
            TITLE_DRAGON_SPRITE_PATH,
            target_height,
            dragon_color,
            tint_alpha=62,
        )
        if imported_dragon:
            # BEGINNER NOTE: Active title dragon.
            # This PNG is the newer imported dragon. The older Python-drawn
            # dragon below is now fallback/archive code only, used if the PNG
            # cannot load on a future device.
            bob = int(math.sin(self.animation_frame * 1.4) * 4)
            draw_x = int(self.x - 72)
            draw_y = int(self.y - 42 + bob)

            shadow = pygame.Surface((imported_dragon.get_width() + 40, 48), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 110), shadow.get_rect())
            surface.blit(shadow, (draw_x + 18, draw_y + imported_dragon.get_height() - 28))

            glow = pygame.Surface(imported_dragon.get_size(), pygame.SRCALPHA)
            glow.blit(imported_dragon, (0, 0))
            glow.set_alpha(38 + int(18 * math.sin(self.animation_frame * 1.7)))
            surface.blit(glow, (draw_x - 2, draw_y + 2))
            surface.blit(imported_dragon, (draw_x, draw_y))

            if self.fire_active:
                # The imported image already has a base flame. This overlay
                # extends and animates it from the dragon mouth instead of
                # drawing the old right-facing procedural fire.
                scale = imported_dragon.get_height() / 960
                mouth_x = draw_x + int(488 * scale)
                mouth_y = draw_y + int(296 * scale)
                flame_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flame_progress = min(1.0, self.fire_frame / 54)
                flame_length = 170 + int(320 * flame_progress)
                flame_r, flame_g, flame_b = fire_color

                for i in range(58):
                    travel = i / 57
                    wave = math.sin(self.fire_frame * 0.42 + i * 0.7)
                    flame_x = int(mouth_x - flame_length * travel - self.fire_frame * 1.25)
                    flame_y = int(mouth_y + 46 * travel + wave * (6 + travel * 18))
                    outer_size = max(5, int(24 - travel * 11 + math.sin(self.fire_frame * 0.25 + i) * 5))
                    alpha = max(0, int(235 * (1 - travel * 0.62)))

                    pygame.draw.circle(
                        flame_overlay,
                        (flame_r, max(40, flame_g // 2), max(0, flame_b // 4), max(35, alpha - 55)),
                        (flame_x, flame_y),
                        outer_size + 9,
                    )
                    pygame.draw.circle(
                        flame_overlay,
                        (flame_r, flame_g, max(24, flame_b), alpha),
                        (flame_x, flame_y),
                        outer_size,
                    )
                    pygame.draw.circle(
                        flame_overlay,
                        (255, 250, 172, min(255, alpha + 20)),
                        (flame_x + 2, flame_y - 1),
                        max(3, outer_size // 2),
                    )

                for spark in range(34):
                    travel = spark / 33
                    spark_x = int(mouth_x - flame_length * travel + random.randint(-16, 8))
                    spark_y = int(mouth_y + 56 * travel + random.randint(-18, 18))
                    pygame.draw.circle(
                        flame_overlay,
                        (255, max(160, flame_g), max(90, flame_b), 165),
                        (spark_x, spark_y),
                        random.randint(2, 5),
                    )

                surface.blit(flame_overlay, (0, 0))

            self.animation_frame += self.flap_speed
            return

        # BEGINNER NOTE: Archived fallback title dragon.
        # Keep this older Python-drawn dragon only as an emergency fallback.
        # The active title screen should use assets/processed/ui/title_dragon.png.
        pygame.draw.ellipse(surface, dragon_color, (self.x, self.y + 30, 180, 70))
        pygame.draw.circle(surface, dragon_color, (self.x + 180, self.y + 50), 35)
        pygame.draw.circle(surface, (255, 255, 255), (self.x + 195, self.y + 45), 10)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 195, self.y + 45), 5)
        pygame.draw.polygon(surface, (200, 100, 50), [
            (self.x + 180, self.y + 25),
            (self.x + 190, self.y + 10),
            (self.x + 195, self.y + 20)
        ])
        pygame.draw.polygon(surface, (200, 100, 50), [
            (self.x + 205, self.y + 25),
            (self.x + 215, self.y + 10),
            (self.x + 210, self.y + 20)
        ])
        
        wing_y_offset = math.sin(self.animation_frame) * 12
        pygame.draw.polygon(surface, (200, 50, 50), [
            (self.x + 40, self.y + 50),
            (self.x, self.y + 15 + wing_y_offset),
            (self.x + 50, self.y + 30)
        ])
        pygame.draw.polygon(surface, (200, 50, 50), [
            (self.x + 40, self.y + 50),
            (self.x, self.y + 85 - wing_y_offset),
            (self.x + 50, self.y + 70)
        ])
        
        pygame.draw.polygon(surface, dragon_color, [
            (self.x, self.y + 50),
            (self.x - 50, self.y + 20),
            (self.x - 50, self.y + 80)
        ])
        
        for i in range(3):
            offset = i * 15
            pygame.draw.polygon(surface, (200, 50, 50), [
                (self.x - 50 + offset, self.y + 50 - offset//2),
                (self.x - 55 + offset, self.y + 40 - offset//2),
                (self.x - 45 + offset, self.y + 40 - offset//2)
            ])
        
        if self.fire_active:
            self.draw_archived_old_fire_animation(surface)
        
        self.animation_frame += self.flap_speed

    def draw_archived_old_fire_animation(self, surface):
        """Draw the old procedural title fire only for fallback dragon mode.

        Beginner note:
            This is archived behavior. The active title screen fire is the
            left-facing imported-dragon overlay near the top of Dragon.draw().
            Keep this method only so the old fallback dragon still works if the
            imported PNG cannot load.
        """
        mouth_x = self.x + 214
        mouth_y = self.y + 42
        flame_progress = min(1.0, self.fire_frame / 30)
        flame_length = 145 + int(210 * flame_progress)
        flame_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        for i in range(28):
            travel = i / 27
            wave = math.sin(self.fire_frame * 0.34 + i * 0.9)
            flame_x = int(mouth_x + flame_length * travel + self.fire_frame * 1.5)
            flame_y = int(mouth_y + wave * (5 + travel * 15))
            outer_size = int(20 - travel * 9 + math.sin(self.fire_frame * 0.2 + i) * 3)
            inner_size = max(4, int(outer_size * 0.52))
            alpha = max(0, int(225 * (1 - travel * 0.62)))

            pygame.draw.circle(
                flame_overlay,
                (255, 70 + int(80 * travel), 0, max(30, alpha - 45)),
                (flame_x, flame_y),
                max(5, outer_size + 5),
            )
            pygame.draw.circle(
                flame_overlay,
                (255, 205, 45, alpha),
                (flame_x, flame_y),
                max(4, outer_size),
            )
            pygame.draw.circle(
                flame_overlay,
                (255, 250, 180, min(255, alpha + 20)),
                (flame_x - 3, flame_y - 2),
                inner_size,
            )

        for spark in range(18):
            travel = spark / 17
            spark_x = int(mouth_x + flame_length * travel + random.randint(-6, 14))
            spark_y = int(mouth_y + math.sin(self.fire_frame * 0.4 + spark) * 18 + random.randint(-10, 10))
            pygame.draw.circle(
                flame_overlay,
                (255, 225, 115, max(35, 150 - spark * 5)),
                (spark_x, spark_y),
                random.randint(2, 5),
            )

        surface.blit(flame_overlay, (0, 0))
        
    def breathe_fire(self):
        self.fire_active = True
        self.fire_frame = 0
        
    def update(self):
        if self.fire_active:
            self.fire_frame += 1
            if self.fire_frame > 54:
                self.fire_active = False

# ============================================================================
# BATTLE SYSTEM - Turn-based combat interface and mechanics
# ============================================================================
class BattleScreen:
    """
    Turn-based combat system with attack, magic, special, item, and run options.
    Handles battle animations, damage calculations, and victory/defeat conditions.

    Beginner note:
        This class still owns combat state and attack math. Reusable drawing,
        input routing, and reward formulas were split into `systems/battle_ui.py`,
        `systems/battle_input.py`, and `systems/battle_rewards.py`.
    """
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = "player_turn"
        self.battle_log = ["Battle started!", "It's your turn!"]

        # BEGINNER NOTE: Battle menu button order matters.
        # Before Lion Sage unlocks the special technique, the SPECIAL button is
        # not present at all. That means RUN shifts left by one slot.
        self.action_buttons = [
            Button(30, 525, 170, 50, "ATTACK"),
            Button(220, 525, 170, 50, "MAGIC"),
            Button(410, 525, 170, 50, "ITEM"),
        ]
        self.special_button_index = None
        if getattr(self.player, "special_unlocked", False):
            self.special_button_index = len(self.action_buttons)
            self.action_buttons.append(Button(600, 525, 170, 50, "SPECIAL"))
            run_x = 790
        else:
            run_x = 600
        self.run_button_index = len(self.action_buttons)
        self.action_buttons.append(Button(run_x, 525, 170, 50, "RUN"))

        # BEGINNER NOTE: The battle item menu is separate from the main action
        # row. Pressing ITEM switches into these buttons so Android players can
        # choose Health or Mana directly instead of the game guessing for them.
        self.item_buttons = [
            Button(110, 525, 210, 50, "HEALTH"),
            Button(340, 525, 210, 50, "MANA"),
            Button(570, 525, 170, 50, "BACK"),
        ]
        self.item_back_button_index = 2
        self.menu_mode = "actions"
        self.buttons = self.action_buttons
        self.selected_option = 0

        # BEGINNER NOTE: Android battle controls are different from the
        # overworld d-pad. Battle choices belong to BattleScreen because this
        # class knows which actions are currently legal. The small toggle stays
        # out of the way and shows/hides the larger action buttons.
        self.combat_buttons_visible = True
        self.combat_toggle_button = Button(
            SCREEN_WIDTH - 172, 166, 150, 46, "HIDE",
            (135, 95, 35), (255, 220, 120)
        )
        self.battle_continue_button = Button(
            SCREEN_WIDTH - 172, 222, 150, 46, "NEXT",
            (45, 92, 80), (150, 255, 220)
        )
        self.update_combat_toggle_button_label()

        self.battle_ended = False
        self.result = None
        self.transition_alpha = 0
        self.transition_state = "in"
        self.transition_speed = 8
        self.show_summary = False
        self.damage_effect_timer = 0
        self.damage_target = None
        self.damage_amount = 0
        self.action_cooldown = 0
        self.action_delay = 30
        self.log_page = 0
        self.log_lines_per_page = 3
        self.waiting_for_continue = False
        self.action_steps = []
        self.particle_system = ParticleSystem()
        self.screen_shake = 0
        self.attack_effect_timer = 0
        self.enemy_attack_fx = []

        # BEGINNER NOTE: Fire Tornado uses this dictionary while it is active.
        # When it is None, no player special effect is being drawn.
        # start_special_animation() creates the dictionary.
        # update() increments its timer.
        # draw_player_special_fx() uses it to draw the moving tornado.
        self.player_special_fx = None
        self.magic_effect = {
            'active': False,
            'x': 0, 'y': 0,
            'radius': 0,
            'max_radius': 50,
            'color': MAGIC_COLORS[0]
        }
        self.is_boss = hasattr(self.enemy, 'enemy_type') and "boss_dragon" in self.enemy.enemy_type
        self.pending_elemental_effect = None
        self.elemental_effect_timer = 0
        self.player_chill_turns = 0
        # BEGINNER NOTE: Warrior's basic ATTACK sets this to 1. The next enemy
        # hit spends it to reduce damage, which makes Warrior feel defensive
        # without adding a separate Guard button.
        self.player_guard_turns = 0
        self.player_condition = None
        self.player_condition_timer = 0
        self.boss_phase_announced = set()
        if self.is_boss:
            self.battle_log = [
                f"{self.enemy.name} descends!",
                getattr(self.enemy, "boss_hint", "A dragon boss blocks your path."),
            ]
        gear_line = self.get_battle_gear_line()
        if gear_line:
            self.battle_log.append(gear_line)
        identity_line = self.get_class_battle_line()
        if identity_line:
            self.battle_log.append(identity_line)

    def update_combat_toggle_button_label(self):
        """Refresh the small battle touch toggle label.

        Beginner note:
            `Button` renders its text once when it is created. When we change
            the label from HIDE to ACTIONS, we also rebuild the rendered text
            surface and re-center it inside the same rectangle.
        """
        label = "HIDE" if self.combat_buttons_visible else "ACTIONS"
        if self.combat_toggle_button.text == label:
            return

        self.combat_toggle_button.text = label
        self.combat_toggle_button.text_surf = font_small.render(label, True, TEXT_COLOR)
        self.combat_toggle_button.text_rect = self.combat_toggle_button.text_surf.get_rect(
            center=self.combat_toggle_button.rect.center
        )

    def toggle_combat_buttons(self):
        """Show or hide the large battle action buttons."""
        self.combat_buttons_visible = not self.combat_buttons_visible
        self.update_combat_toggle_button_label()

    def show_combat_buttons(self):
        """Reveal battle action buttons without toggling them back off."""
        self.combat_buttons_visible = True
        self.update_combat_toggle_button_label()

    def set_battle_menu_mode(self, mode):
        """Switch between the main battle command row and the item row.

        Beginner note:
            `self.buttons` always points at whichever row is currently active.
            The input helper only needs to move through `self.buttons`, so it
            does not care whether the player is choosing ATTACK or HEALTH.
        """
        self.menu_mode = mode
        if mode == "items":
            self.refresh_item_button_labels()
            self.buttons = self.item_buttons
        else:
            self.buttons = self.action_buttons
        self.selected_option = 0

    def refresh_item_button_labels(self):
        """Update battle item button text with current potion counts."""
        set_button_text(
            self.item_buttons[0],
            f"HEALTH x{self.player.get_inventory_count('health')}",
            font_medium,
            TEXT_COLOR,
        )
        set_button_text(
            self.item_buttons[1],
            f"MANA x{self.player.get_inventory_count('mana')}",
            font_medium,
            TEXT_COLOR,
        )

    def get_class_profile(self):
        """Return this hero's class identity record from game_data/characters.py."""
        return get_character_class_profile(self.player.type)

    def get_basic_attack_name(self):
        """Return the name used for this class's ATTACK command."""
        return self.get_class_profile().get("basic_attack", "Attack")

    def get_magic_attack_name(self):
        """Return the name used for this class's MAGIC command."""
        return self.get_class_profile().get("magic_attack", "Fireball")

    def get_class_battle_line(self):
        """Build the short class-style line shown at battle start.

        Beginner note:
            This is only display text. The actual class mechanics are in
            execute_attack(), execute_magic(), and the enemy-turn guard block.
        """
        profile = self.get_class_profile()
        role = profile.get("role")
        style = profile.get("battle_style")
        if role and style:
            return f"{role}: {style}"
        return ""

    def get_special_attack_name(self):
        """Return the class-specific SPECIAL attack name.

        Beginner note:
            The button, battle log, and animation title all call this one helper
            so the Mage can say "Fire Blast" while Warrior/Rogue still say
            "Fire Tornado". Add more class-specific names here later.
        """
        if self.player.type == "Mage":
            return MAGE_SPECIAL_ATTACK_NAME
        return SPECIAL_ATTACK_NAME

    def get_equipped_item_note(self, slot):
        """Return a short battle note for one equipped gear slot."""
        item_key = self.player.equipment.get(slot)
        profile = get_equipment_item(item_key) if item_key else None
        if not profile:
            return ""
        bonus_text = format_equipment_bonus(profile.get("bonuses", {}))
        return f"{profile.get('label', item_key)} ({bonus_text})"

    def get_battle_gear_line(self):
        """Build the non-blocking gear summary shown at battle start."""
        weapon_note = self.get_equipped_item_note("weapon")
        armor_note = self.get_equipped_item_note("armor")
        if weapon_note and armor_note:
            return f"Gear ready: {weapon_note}; {armor_note}."
        if weapon_note:
            return f"Gear ready: {weapon_note}."
        if armor_note:
            return f"Gear ready: {armor_note}."
        return ""

    def get_attack_gear_note(self, mode="attack"):
        """Return a small damage-log suffix explaining equipped gear impact."""
        weapon_note = self.get_equipped_item_note("weapon")
        if not weapon_note:
            return ""
        if mode == "magic":
            return f" Focus: {weapon_note}."
        return f" Weapon: {weapon_note}."
        
    def start_transition(self):
        self.transition_state = "in"
        self.transition_alpha = 0
        
    def add_screen_shake(self, intensity=5, duration=10):
        self.screen_shake = duration
        self.shake_intensity = intensity

    def queue_enemy_attack_fx(self, kind, duration=36):
        """Queue a named enemy attack effect for drawing over multiple frames.

        Beginner note:
            Ghost Face attacks are not one-frame drawings. They need to stay on
            screen for several frames, so we store their type, timer, duration,
            and a random seed here. `update()` advances the timer later.
        """
        self.enemy_attack_fx.append({
            "kind": kind,
            "timer": 0,
            "duration": duration,
            "seed": random.randint(1, 999999),
        })

    def draw_enemy_attack_fx(self, surface):
        """Draw every active enemy attack effect.

        Beginner note:
            `kind` is the string that chooses which drawing function runs.
            To add a new Ghost Face attack later:
            1. Add a new dictionary in choose_ghostface_attack().
            2. Add a matching `elif fx["kind"] == "...":` case here.
            3. Write a draw function that accepts surface/progress/seed.
        """
        for fx in self.enemy_attack_fx:
            progress = fx["timer"] / max(1, fx["duration"])
            if fx["kind"] == "ghostface_stab":
                self.draw_ghostface_stab_fx(surface, progress, fx["seed"])
            elif fx["kind"] == "ghostface_cross_stab":
                self.draw_ghostface_cross_stab_fx(surface, progress, fx["seed"])
            elif fx["kind"] == "ghostface_scream":
                self.draw_ghostface_scream_fx(surface, progress, fx["seed"])

    def draw_player_special_fx(self, surface):
        """Draw the player's active SPECIAL attack.

        Beginner note:
            This is visual-only. Damage and MP cost are handled by
            execute_special_attack(). This method answers: "What should the
            player see while the special attack is happening?"

            The animation has five visual layers:
            1. A charge ring near the player at the beginning.
            2. Glowing trail rings that mark the path across the screen.
            3. The imported PNG tornado frame from assets/processed/effects.
            4. For Mage only, imported Fire Blast frames when the tornado hits.
            5. Extra impact lines when the attack reaches the enemy.
            6. The class-specific attack label that fades in and out.
        """
        fx = self.player_special_fx
        if not fx:
            return

        # progress always stays between 0.0 and 1.0.
        # 0.0 means the animation just started; 1.0 means it is finished.
        frames = fx.get("frames", [])
        impact_frames = fx.get("impact_frames", [])
        special_name = fx.get("name", SPECIAL_ATTACK_NAME)
        is_fire_blast = fx.get("kind") == "fire_blast"
        timer = fx["timer"]
        duration = max(1, fx["duration"])
        progress = min(1.0, timer / duration)

        # travel moves a little faster than progress so the tornado reaches the
        # enemy before the last few frames, leaving time for the impact burst.
        travel = min(1.0, progress * 1.18)

        # ease makes the tornado accelerate smoothly instead of sliding at one
        # flat speed. It starts slower and gets faster near the enemy.
        ease = 1 - (1 - travel) * (1 - travel) * (1 - travel)
        center_x = 165 + (705 - 165) * ease
        center_y = 352 - 38 * math.sin(progress * math.pi) + 12 * math.sin(progress * math.pi * 7)

        # surge grows/shrinks the sprite so the tornado feels alive.
        surge = math.sin(min(1.0, progress * 1.2) * math.pi)

        # Draw everything to a transparent overlay first, then blit it once.
        # This keeps the special effect separate from the battle background.
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        rng = random.Random(fx["seed"] + timer)

        # Startup charge ring. This is only visible during the first 22% of the
        # animation and tells the player the special attack is powering up.
        if progress < 0.22:
            charge_alpha = int(140 * (1 - progress / 0.22))
            pygame.draw.circle(overlay, (255, 120, 25, charge_alpha), (225, 365), int(30 + progress * 190), 5)
            pygame.draw.circle(overlay, (255, 245, 190, charge_alpha), (225, 365), int(16 + progress * 95), 2)

        # Motion trail. Each ring is a slightly older tornado position, so the
        # player can read the attack moving across the screen.
        for i in range(7):
            trail_progress = max(0.0, min(1.0, travel - i * 0.052))
            if trail_progress <= 0:
                continue
            trail_ease = 1 - (1 - trail_progress) * (1 - trail_progress) * (1 - trail_progress)
            tx = 165 + (705 - 165) * trail_ease
            ty = 352 - 38 * math.sin(trail_progress * math.pi) + 12 * math.sin(trail_progress * math.pi * 7)
            alpha = max(0, 118 - i * 17)
            radius = int(30 + surge * 28 + i * 5)
            pygame.draw.circle(overlay, (255, 90, 20, alpha), (int(tx), int(ty)), radius, 3)
            pygame.draw.circle(overlay, (255, 220, 130, max(0, alpha - 28)), (int(tx), int(ty)), max(8, radius // 2), 2)

        if frames and (not is_fire_blast or progress < 0.74):
            # Pick a source PNG frame. `timer // 2` means each imported frame is
            # shown for two game frames, which slows the GIF down slightly.
            frame = frames[(timer // 2) % len(frames)]
            frame_scale = 0.92 + surge * 0.45
            width = max(1, int(frame.get_width() * frame_scale))
            height = max(1, int(frame.get_height() * frame_scale))
            frame = pygame.transform.smoothscale(frame, (width, height))

            # Fade in/out so the tornado does not pop on/off harshly.
            alpha = 255
            if progress < 0.08:
                alpha = int(255 * progress / 0.08)
            elif progress > 0.92:
                alpha = int(255 * (1 - progress) / 0.08)
            if is_fire_blast and progress > 0.55:
                # The Mage's tornado transforms into the Fire Blast impact, so
                # fade the moving tornado as the imported blast frames appear.
                alpha = min(alpha, int(255 * max(0.0, 1 - (progress - 0.55) / 0.19)))
            frame.set_alpha(max(0, min(255, alpha)))

            # Ghost copies behind the main sprite create a fast afterimage.
            for ghost in range(3, 0, -1):
                ghost_frame = frame.copy()
                ghost_frame.set_alpha(max(0, int(42 - ghost * 8)))
                ghost_x = center_x - ghost * 42
                ghost_y = center_y + rng.randint(-8, 8)
                ghost_rect = ghost_frame.get_rect(center=(int(ghost_x), int(ghost_y)))
                overlay.blit(ghost_frame, ghost_rect)

            rect = frame.get_rect(center=(int(center_x), int(center_y)))
            overlay.blit(frame, rect)
        else:
            # Fallback if the PNG frames are missing. This keeps battle playable
            # even if the asset folder is accidentally deleted.
            for ring in range(12):
                angle = progress * math.tau * 5 + ring * math.tau / 12
                radius = 22 + ring * 7
                x = center_x + math.cos(angle) * radius * 0.45
                y = center_y + math.sin(angle) * radius
                pygame.draw.circle(overlay, (255, 120, 25, 210), (int(x), int(y)), 12)

        # Mage-only Fire Blast impact. The cutout frames were processed from
        # assets/source/effects/fire_blast_impact.gif into transparent PNGs.
        if is_fire_blast and impact_frames and progress > 0.52:
            blast_progress = min(1.0, (progress - 0.52) / 0.38)
            # The final source frames fill the whole rectangle, which can look
            # boxy in battle. Stop before the last strip of frames and then
            # fade/crop the blast out procedurally.
            asset_progress = min(0.82, blast_progress) / 0.82
            frame_index = min(len(impact_frames) - 1, int(asset_progress * (len(impact_frames) - 1)))
            blast_frame = impact_frames[frame_index]
            blast_surge = math.sin(blast_progress * math.pi)
            blast_width = max(1, int(blast_frame.get_width() * (0.92 + blast_surge * 0.16)))
            blast_height = max(1, int(blast_frame.get_height() * (0.92 + blast_surge * 0.16)))
            blast_frame = pygame.transform.smoothscale(blast_frame, (blast_width, blast_height))

            blast_alpha = 255
            if blast_progress < 0.14:
                blast_alpha = int(255 * blast_progress / 0.14)
            elif blast_progress > 0.68:
                blast_alpha = int(255 * max(0.0, 1 - (blast_progress - 0.68) / 0.32))
            blast_frame.set_alpha(max(0, min(255, blast_alpha)))

            if blast_progress > 0.54:
                crop_strength = min(1.0, (blast_progress - 0.54) / 0.46)
                crop_x = int(blast_width * 0.12 * crop_strength)
                crop_y = int(blast_height * 0.10 * crop_strength)
                source_rect = pygame.Rect(
                    crop_x,
                    crop_y,
                    max(1, blast_width - crop_x * 2),
                    max(1, blast_height - crop_y * 2),
                )
                cropped_frame = pygame.Surface(source_rect.size, pygame.SRCALPHA)
                cropped_frame.blit(blast_frame, (0, 0), source_rect)
                blast_frame = cropped_frame

            glow_radius = int(52 + blast_surge * 130)
            pygame.draw.circle(overlay, (255, 88, 12, 76), (740, 285), glow_radius)
            pygame.draw.circle(overlay, (255, 235, 140, 54), (740, 285), max(16, glow_radius // 2))

            if blast_progress > 0.62:
                fade_sparks = int(24 * (1 - min(1.0, (blast_progress - 0.62) / 0.38)))
                for _ in range(fade_sparks):
                    angle = rng.uniform(-0.8, 0.8)
                    distance = rng.uniform(42, 210)
                    spark_x = int(735 + math.cos(angle) * distance)
                    spark_y = int(282 + math.sin(angle) * distance + rng.randint(-36, 36))
                    pygame.draw.circle(
                        overlay,
                        rng.choice([(255, 245, 190, 150), (255, 130, 28, 135), (255, 70, 14, 120)]),
                        (spark_x, spark_y),
                        rng.randint(2, 6),
                    )

            # The source blast already sweeps across the frame from left to
            # right, so anchoring it on the enemy side makes it read like the
            # tornado opened into a wide explosion at impact.
            blast_rect = blast_frame.get_rect(center=(735 + rng.randint(-5, 5), 282 + rng.randint(-4, 4)))
            overlay.blit(blast_frame, blast_rect)

        # Impact burst. It starts after 58% progress, when the moving tornado is
        # near the enemy side. These lines sell the hit even before damage text.
        if progress > 0.58:
            impact = min(1.0, (progress - 0.58) / 0.22)
            impact_alpha = max(0, int(220 * (1 - impact)))
            for i in range(16):
                angle = i * math.tau / 16 + progress * 9
                inner = 28 + impact * 22
                outer = 78 + impact * 175 + rng.randint(-10, 18)
                start = (int(730 + math.cos(angle) * inner), int(280 + math.sin(angle) * inner))
                end = (int(730 + math.cos(angle) * outer), int(280 + math.sin(angle) * outer))
                color = rng.choice([(255, 95, 20, impact_alpha), (255, 220, 120, impact_alpha), (255, 255, 245, impact_alpha)])
                pygame.draw.line(overlay, color, start, end, rng.randint(3, 8))

        # Attack title. It is drawn during the middle of the animation so it
        # does not cover the battle menu or result text for too long.
        if 0.18 < progress < 0.78:
            text_alpha = int(220 * math.sin((progress - 0.18) / 0.60 * math.pi))
            title = font_medium.render(special_name.upper(), True, (255, 250, 210))
            shadow = font_medium.render(special_name.upper(), True, (255, 80, 20))
            title.set_alpha(text_alpha)
            shadow.set_alpha(text_alpha)
            overlay.blit(shadow, (382 + rng.randint(-2, 2), 158 + rng.randint(-2, 2)))
            overlay.blit(title, (378, 154))

        surface.blit(overlay, (0, 0))

    def draw_ghostface_stab_fx(self, surface, progress, seed):
        rng = random.Random(seed + int(progress * 20))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        start_x, start_y = 730, 280
        target_x, target_y = 235, 365
        p = min(1.0, progress * 1.45)
        ease = 1 - (1 - p) * (1 - p)
        tip_x = start_x + (target_x - start_x) * ease
        tip_y = start_y + (target_y - start_y) * ease
        angle = math.atan2(target_y - start_y, target_x - start_x)
        forward = (math.cos(angle), math.sin(angle))
        side = (-math.sin(angle), math.cos(angle))
        blade_len = 145
        blade_w = 24
        base_x = tip_x - forward[0] * blade_len
        base_y = tip_y - forward[1] * blade_len
        blade = [
            (tip_x, tip_y),
            (base_x + side[0] * blade_w, base_y + side[1] * blade_w),
            (base_x - side[0] * blade_w, base_y - side[1] * blade_w),
        ]

        for _ in range(10):
            trail_p = rng.uniform(0.08, max(0.2, ease))
            tx = start_x + (target_x - start_x) * trail_p
            ty = start_y + (target_y - start_y) * trail_p
            pygame.draw.line(
                overlay, (255, 255, 255, 65),
                (tx - side[0] * rng.randint(10, 30), ty - side[1] * rng.randint(10, 30)),
                (tx + side[0] * rng.randint(10, 30), ty + side[1] * rng.randint(10, 30)),
                rng.randint(2, 5),
            )

        pygame.draw.polygon(overlay, (230, 235, 255, 235), blade)
        pygame.draw.polygon(overlay, (255, 255, 255, 255), blade, 3)
        handle_center = (base_x - forward[0] * 30, base_y - forward[1] * 30)
        pygame.draw.line(
            overlay, (20, 15, 25, 250),
            (handle_center[0] - side[0] * 30, handle_center[1] - side[1] * 30),
            (handle_center[0] + side[0] * 30, handle_center[1] + side[1] * 30),
            12,
        )

        if progress > 0.45:
            impact = min(1.0, (progress - 0.45) / 0.55)
            radius = int(22 + impact * 115)
            for i in range(20):
                angle_i = (math.pi * 2 * i / 20) - progress * 5
                outer = radius + rng.randint(-10, 18)
                color = rng.choice([(255, 30, 80, 215), (255, 255, 255, 230), (160, 70, 255, 190)])
                pygame.draw.line(
                    overlay, color,
                    (target_x + math.cos(angle_i) * 16, target_y + math.sin(angle_i) * 16),
                    (target_x + math.cos(angle_i) * outer, target_y + math.sin(angle_i) * outer),
                    5,
                )

            text = font_large.render("STAB", True, (255, 255, 255))
            shadow = font_large.render("STAB", True, (255, 30, 80))
            overlay.blit(shadow, (target_x - 54 + rng.randint(-4, 4), target_y - 122 + rng.randint(-4, 4)))
            overlay.blit(text, (target_x - 58, target_y - 126))

        surface.blit(overlay, (0, 0))

    def draw_ghostface_cross_stab_fx(self, surface, progress, seed):
        rng = random.Random(seed + int(progress * 24))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        target_x, target_y = 235, 365
        flash = int(180 * max(0, 1 - progress))
        if flash > 0:
            overlay.fill((255, 255, 255, flash // 5))

        slash_pairs = [
            ((target_x - 130, target_y - 90), (target_x + 115, target_y + 85)),
            ((target_x + 125, target_y - 100), (target_x - 120, target_y + 90)),
            ((target_x - 80, target_y + 105), (target_x + 75, target_y - 120)),
        ]
        for index, (start, end) in enumerate(slash_pairs):
            phase = min(1.0, max(0.0, progress * 1.8 - index * 0.18))
            if phase <= 0:
                continue
            cut_x = start[0] + (end[0] - start[0]) * phase
            cut_y = start[1] + (end[1] - start[1]) * phase
            width = 18 - index * 4
            pygame.draw.line(overlay, (255, 30, 80, 210), start, (cut_x, cut_y), width)
            pygame.draw.line(overlay, (255, 255, 255, 235), start, (cut_x, cut_y), max(3, width // 3))

        if progress > 0.35:
            for _ in range(16):
                angle = rng.uniform(0, math.pi * 2)
                dist = rng.uniform(8, 95)
                px = target_x + math.cos(angle) * dist
                py = target_y + math.sin(angle) * dist
                pygame.draw.circle(overlay, rng.choice([(255, 30, 80, 180), (255, 255, 255, 180)]), (int(px), int(py)), rng.randint(2, 5))
            text = font_medium.render("CROSS STAB", True, (255, 255, 255))
            shadow = font_medium.render("CROSS STAB", True, (255, 30, 80))
            overlay.blit(shadow, (target_x - 100 + rng.randint(-3, 3), target_y - 130 + rng.randint(-3, 3)))
            overlay.blit(text, (target_x - 104, target_y - 134))

        surface.blit(overlay, (0, 0))

    def draw_ghostface_scream_fx(self, surface, progress, seed):
        rng = random.Random(seed + int(progress * 18))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        mask = load_scaled_sprite(GHOST_FACE_SPRITE_PATH, 190)
        if mask:
            mask_copy = mask.copy()
            mask_copy.set_alpha(int(70 + 90 * math.sin(min(1, progress) * math.pi)))
            overlay.blit(mask_copy, (635 + rng.randint(-2, 2), 112 + rng.randint(-2, 2)))

        origin = (725, 275)
        target = (235, 365)
        for ring in range(6):
            ring_progress = (progress * 1.8 - ring * 0.12)
            if ring_progress <= 0:
                continue
            radius = int(40 + ring_progress * 290)
            alpha = max(0, 190 - int(ring_progress * 150))
            pygame.draw.circle(overlay, (245, 245, 255, alpha), origin, radius, 4)
            pygame.draw.circle(overlay, (255, 30, 160, max(0, alpha - 50)), origin, radius + 12, 2)

        for i in range(14):
            phase = min(1.0, max(0.0, progress * 1.4 - i * 0.025))
            x = origin[0] + (target[0] - origin[0]) * phase + rng.randint(-8, 8)
            y = origin[1] + (target[1] - origin[1]) * phase + rng.randint(-8, 8)
            pygame.draw.line(overlay, (255, 255, 255, 95), origin, (x, y), 2)

        if progress > 0.25:
            text = font_large.render("SCREAM", True, (255, 255, 255))
            shadow = font_large.render("SCREAM", True, (160, 70, 255))
            overlay.blit(shadow, (430 + rng.randint(-4, 4), 155 + rng.randint(-4, 4)))
            overlay.blit(text, (424, 150))

        surface.blit(overlay, (0, 0))

    def draw_elemental_enemy(self, surface, enemy_x, enemy_y):
        profile = get_element_profile(self.enemy.enemy_type)
        primary = profile["primary_color"]
        secondary = profile["secondary_color"]
        accent = profile["accent_color"]

        if self.enemy.enemy_type == "fiery":
            pygame.draw.ellipse(surface, primary, (enemy_x, enemy_y, 60, 60))
            for i in range(12):
                angle = i * math.pi / 6
                flame_length = random.randint(10, 20)
                flame_x = enemy_x + 30 + math.cos(angle) * flame_length
                flame_y = enemy_y + 30 + math.sin(angle) * flame_length
                flame_color = random.choice(profile["particle_colors"])
                pygame.draw.line(surface, flame_color,
                               (enemy_x + 30, enemy_y + 30),
                               (flame_x, flame_y), 3)
        elif self.enemy.enemy_type == "shadow":
            pygame.draw.ellipse(surface, primary, (enemy_x, enemy_y, 60, 60))
            for _ in range(10):
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                size = random.randint(5, 15)
                alpha = random.randint(50, 150)
                smoke_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (*secondary, alpha), (size, size), size)
                surface.blit(smoke_surf, (enemy_x + 30 - size + offset_x, enemy_y + 30 - size + offset_y))
        else:
            pygame.draw.ellipse(surface, primary, (enemy_x, enemy_y, 60, 60))
            for i in range(8):
                angle = i * math.pi / 4
                crystal_length = random.randint(10, 20)
                crystal_x = enemy_x + 30 + math.cos(angle) * crystal_length
                crystal_y = enemy_y + 30 + math.sin(angle) * crystal_length
                pygame.draw.line(surface, secondary,
                               (enemy_x + 30, enemy_y + 30),
                               (crystal_x, crystal_y), 3)

        pygame.draw.circle(surface, accent, (enemy_x + 20, enemy_y + 25), 6)
        pygame.draw.circle(surface, accent, (enemy_x + 40, enemy_y + 25), 6)
        
    def draw(self, surface):
        shake_offset_x = 0
        shake_offset_y = 0
        if self.screen_shake > 0:
            shake_offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_offset_y = random.randint(-self.shake_intensity, self.shake_intensity)
            self.screen_shake -= 1
        
        temp_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        temp_surface.fill((20, 10, 40))
        
        # Draw player and enemy avatars
        player_x, player_y = 200 + shake_offset_x, 350 + shake_offset_y
        enemy_x, enemy_y = 700 + shake_offset_x, 250 + shake_offset_y
        
        # Draw player using the same character drawing method as overworld
        # Temporarily set the player's position for battle drawing
        original_x, original_y = self.player.x, self.player.y
        self.player.x, self.player.y = player_x, player_y
        
        # Draw the player directly to the battle surface.
        # BEGINNER NOTE: sprite_mode="battle" tells Character.draw() to use the
        # same imported PNG, but at a larger height than the overworld sprite.
        self.player.draw(temp_surface, sprite_mode="battle")
        
        # Restore original position
        self.player.x, self.player.y = original_x, original_y
        
        # Draw enemy
        if hasattr(self.enemy, 'enemy_type') and "boss_dragon" in self.enemy.enemy_type:
            # Draw the boss using its own draw method, at the correct position
            boss_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            self.enemy.x = enemy_x
            self.enemy.y = enemy_y
            self.enemy.draw(boss_surf)
            temp_surface.blit(boss_surf, (0, 0))
        elif getattr(self.enemy, "sprite_path", None):
            draw_enemy_sprite(temp_surface, self.enemy, enemy_x - 24, enemy_y - 38, 118)
        else:
            self.draw_elemental_enemy(temp_surface, enemy_x, enemy_y)
        
        # Draw character-specific attack effects
        if self.attack_effect_timer > 0:
            if self.player.type == "Warrior":
                # Holy slash effect for Warrior/Paladin
                effect_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                # Multiple holy slashes with different angles and colors
                slash_angles = [0, 15, -15, 30, -30]
                for i, angle in enumerate(slash_angles):
                    # Calculate slash start and end points
                    start_x = player_x + 25
                    start_y = player_y + 15
                    end_x = start_x + math.cos(math.radians(angle)) * 80
                    end_y = start_y + math.sin(math.radians(angle)) * 80
                    
                    # Holy slash colors (gold, white, light blue)
                    slash_colors = [(255, 215, 0, 200), (255, 255, 255, 180), (173, 216, 230, 160)]
                    color = slash_colors[i % len(slash_colors)]
                    
                    # Draw the slash with glow effect
                    for width in range(8, 2, -2):
                        alpha = color[3] - (8 - width) * 20
                        glow_color = (*color[:3], max(0, alpha))
                        pygame.draw.line(effect_surf, glow_color, (start_x, start_y), (end_x, end_y), width)
                
                # Add enemy-side slash effect
                enemy_slash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                
                # Draw impact slashes on enemy
                impact_angles = [0, 20, -20, 40, -40]
                for i, angle in enumerate(impact_angles):
                    # Calculate impact slash points
                    center_x = enemy_x + 30
                    center_y = enemy_y + 30
                    start_x = center_x - math.cos(math.radians(angle)) * 25
                    start_y = center_y - math.sin(math.radians(angle)) * 25
                    end_x = center_x + math.cos(math.radians(angle)) * 25
                    end_y = center_y + math.sin(math.radians(angle)) * 25
                    
                    # Impact slash colors (brighter versions)
                    impact_colors = [(255, 255, 100, 250), (255, 255, 255, 220), (200, 230, 255, 200)]
                    color = impact_colors[i % len(impact_colors)]
                    
                    # Draw impact slash with glow
                    for width in range(10, 3, -2):
                        alpha = color[3] - (10 - width) * 25
                        glow_color = (*color[:3], max(0, alpha))
                        pygame.draw.line(enemy_slash_surf, glow_color, (start_x, start_y), (end_x, end_y), width)
                
                temp_surface.blit(effect_surf, (0, 0))
                temp_surface.blit(enemy_slash_surf, (0, 0))
            
            self.attack_effect_timer -= 1
        
        # Draw magic effect
        if self.magic_effect['active']:
            radius = self.magic_effect['radius']
            max_radius = self.magic_effect['max_radius']
            
            for i in range(3, 0, -1):
                r = radius * (i/3)
                alpha = 150 * (1 - r/max_radius)
                color = (*self.magic_effect['color'][:3], int(alpha))
                pygame.draw.circle(temp_surface, color, 
                                 (self.magic_effect['x'], self.magic_effect['y']), 
                                 int(r), 2)
            
            pygame.draw.circle(temp_surface, self.magic_effect['color'], 
                             (self.magic_effect['x'], self.magic_effect['y']), 8)
        
        # Draw fireball projectile
        if hasattr(self, 'fireball_projectile') and self.fireball_projectile['active'] and not self.fireball_projectile.get('hit', False):
            # Draw fireball with glow effect
            x, y = int(self.fireball_projectile['x']), int(self.fireball_projectile['y'])
            size = self.fireball_projectile['size']
            color = self.fireball_projectile['color']
            imported_frames = self.fireball_projectile.get("frames", [])
            
            # Outer glow
            for i in range(3, 0, -1):
                glow_size = size + i * 3
                glow_alpha = 100 - i * 30
                glow_color = (*color[:3], glow_alpha)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
                temp_surface.blit(glow_surf, (x - glow_size, y - glow_size))

            if imported_frames:
                # BEGINNER NOTE: Imported Mage MAGIC overlay.
                # This does not replace the old fireball. It draws the cutout
                # GIF frame between the old glow above and the old circle below.
                # If assets/processed/effects/mage_magic_fireball/ is missing,
                # imported_frames is empty and the old circles still draw.
                frame_index = (self.fireball_projectile["timer"] // 2) % len(imported_frames)
                fireball_frame = imported_frames[frame_index].copy()
                if self.fireball_projectile["timer"] < 5:
                    fireball_frame.set_alpha(int(255 * self.fireball_projectile["timer"] / 5))

                # The source fireball's bright head is near the right edge of
                # the frame. Place that head on the projectile x/y point while
                # the tail stretches behind it.
                draw_x = int(x - fireball_frame.get_width() * 0.82)
                draw_y = int(y - fireball_frame.get_height() * 0.50)
                temp_surface.blit(fireball_frame, (draw_x, draw_y))
            
            # Main fireball
            pygame.draw.circle(temp_surface, color, (x, y), size)
            pygame.draw.circle(temp_surface, (255, 255, 200), (x, y), size // 2)
        
        # Draw knife projectile
        if hasattr(self, 'knife_projectile') and self.knife_projectile['active'] and not self.knife_projectile.get('hit', False):
            x, y = int(self.knife_projectile['x']), int(self.knife_projectile['y'])
            size = self.knife_projectile['size']
            rotation = self.knife_projectile['rotation']
            color = self.knife_projectile['color']
            
            # Create knife surface for rotation
            knife_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            
            # Draw knife blade (pointed oval) - scaled for larger size
            blade_points = [
                (size, 0),  # Tip
                (size - 4, size // 2),  # Top edge
                (size - 2, size),  # Bottom edge
                (size + 2, size),  # Bottom edge
                (size + 4, size // 2),  # Top edge
            ]
            pygame.draw.polygon(knife_surf, color, blade_points)
            
            # Draw knife handle - scaled for larger size
            handle_rect = pygame.Rect(size - 2, size, 4, size // 2)
            pygame.draw.rect(knife_surf, (139, 69, 19), handle_rect)  # Brown handle
            
            # Add metallic shine to blade
            shine_points = [
                (size, 2),  # Tip shine
                (size - 2, size // 2 - 2),  # Top shine
                (size + 2, size // 2 - 2),  # Top shine
            ]
            pygame.draw.polygon(knife_surf, (200, 200, 200), shine_points)
            
            # Rotate and draw
            rotated_knife = pygame.transform.rotate(knife_surf, rotation)
            knife_rect = rotated_knife.get_rect(center=(x, y))
            temp_surface.blit(rotated_knife, knife_rect)

        self.draw_player_special_fx(temp_surface)
        self.draw_enemy_attack_fx(temp_surface)
        
        # Draw health bars
        player_health_width = 150 * (self.player.health / max(1, self.player.max_health))
        pygame.draw.rect(temp_surface, (30, 30, 50), (180, 410, 160, 20))
        pygame.draw.rect(temp_surface, HEALTH_COLOR, (182, 412, player_health_width, 16))
        player_text = font_small.render(f"{self.player.health}/{self.player.max_health}", True, TEXT_COLOR)
        text_rect = player_text.get_rect(center=(180 + 80, 410 + 10))
        temp_surface.blit(player_text, text_rect)
        player_mana_width = 150 * (self.player.mana / max(1, self.player.max_mana))
        pygame.draw.rect(temp_surface, (30, 30, 50), (180, 435, 160, 16))
        pygame.draw.rect(temp_surface, MANA_COLOR, (182, 437, player_mana_width, 12))
        mana_text = font_tiny.render(f"MP {self.player.mana}/{self.player.max_mana}", True, TEXT_COLOR)
        mana_rect = mana_text.get_rect(center=(180 + 80, 435 + 8))
        temp_surface.blit(mana_text, mana_rect)
        if self.player_condition and self.player_condition_timer > 0:
            condition_text = font_tiny.render(self.player_condition["label"], True, self.player_condition["color"])
            pygame.draw.rect(temp_surface, UI_BG, (180, 458, max(90, condition_text.get_width() + 16), 24), border_radius=4)
            pygame.draw.rect(temp_surface, self.player_condition["color"], (180, 458, max(90, condition_text.get_width() + 16), 24), 2, border_radius=4)
            temp_surface.blit(condition_text, (188, 462))

        # BEGINNER NOTE: The gear/status strip drawing lives in
        # systems/battle_ui.py so future combat HUD work does not keep bloating
        # this already-large battle class.
        draw_battle_gear_strip(
            temp_surface,
            self.player,
            pygame.Rect(180, 486, 318, 30),
            render_fitted_text,
            font_tiny,
            (18, 20, 34),
        )
        # Only draw enemy health bar and name if not a boss dragon
        if not (hasattr(self.enemy, 'enemy_type') and "boss_dragon" in self.enemy.enemy_type):
            enemy_health_width = 150 * (self.enemy.health / max(1, self.enemy.max_health))
            pygame.draw.rect(temp_surface, (30, 30, 50), (680, 310, 160, 20))
            pygame.draw.rect(temp_surface, HEALTH_COLOR, (682, 312, enemy_health_width, 16))
            enemy_text = font_small.render(f"{self.enemy.health}/{self.enemy.max_health}", True, TEXT_COLOR)
            text_rect = enemy_text.get_rect(center=(680 + 80, 310 + 10))
            temp_surface.blit(enemy_text, text_rect)
        # Draw enemy name (not for boss)
        if not (hasattr(self.enemy, 'enemy_type') and "boss_dragon" in self.enemy.enemy_type):
            enemy_name = font_small.render(self.enemy.name, True, (255, 215, 0))
            name_rect = enemy_name.get_rect(midtop=(enemy_x + 30, enemy_y - 25))
            temp_surface.blit(enemy_name, name_rect)

        phase = self.get_boss_phase()
        if phase:
            phase_text = font_small.render(f"PHASE: {phase['name'].upper()}", True, phase["color"])
            phase_rect = phase_text.get_rect(midtop=(enemy_x + 120, enemy_y + 155))
            temp_surface.blit(phase_text, phase_rect)

        if self.is_boss and getattr(self.enemy, "boss_title", None):
            title_text = font_tiny.render(getattr(self.enemy, "boss_title"), True, (255, 225, 150))
            title_rect = title_text.get_rect(midtop=(enemy_x + 120, enemy_y + 182))
            temp_surface.blit(title_text, title_rect)
        
        draw_battle_log_panel(
            temp_surface,
            self.battle_log,
            self.waiting_for_continue,
            self.battle_continue_button,
            font_small,
            TEXT_COLOR,
            UI_BG,
            UI_BORDER,
            self.log_lines_per_page,
        )

        draw_battle_action_buttons(
            temp_surface,
            self,
            font_tiny,
            TEXT_COLOR,
            SPECIAL_ATTACK_MANA_COST,
        )
        
        # Draw damage effect
        if self.damage_effect_timer > 0:
            effect_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            if self.damage_target == "player":
                pygame.draw.rect(effect_surf, (255, 0, 0, 100), (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
            elif self.damage_target == "enemy":
                pygame.draw.rect(effect_surf, (255, 0, 0, 100), (enemy_x, enemy_y, ENEMY_SIZE, ENEMY_SIZE))
            
            damage_text = font_medium.render(f"-{self.damage_amount}", True, (255, 50, 50))
            if self.damage_target == "player":
                temp_surface.blit(damage_text, (player_x + 20, player_y - 30))
            elif self.damage_target == "enemy":
                temp_surface.blit(damage_text, (enemy_x + 20, enemy_y - 30))
                
            temp_surface.blit(effect_surf, (0, 0))
            self.damage_effect_timer -= 1
        
        # Draw particles
        self.particle_system.draw(temp_surface)
        
        # Draw transition overlay if active
        if self.transition_state != "none":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            temp_surface.blit(overlay, (0, 0))
            
        if self.battle_ended and self.show_summary:
            draw_battle_summary(
                temp_surface,
                self.result,
                self.player,
                self.battle_continue_button,
                font_large,
                TEXT_COLOR,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
            )
        
        # Draw the temporary surface to the screen
        surface.blit(temp_surface, (0, 0))

    def update(self):
        if self.battle_ended:
            # Keep drawing the summary until the player presses NEXT/ENTER.
            # Game.run resolves the reward only after show_summary is false.
            return not self.show_summary

        self.player.update_animation()
        self.enemy.update_animation()
        self.particle_system.update()
        if self.player_condition_timer > 0:
            self.player_condition_timer -= 1
            if self.player_condition_timer <= 0:
                self.player_condition = None
        for fx in self.enemy_attack_fx:
            fx["timer"] += 1
        self.enemy_attack_fx = [fx for fx in self.enemy_attack_fx if fx["timer"] <= fx["duration"]]

        if self.player_special_fx:
            # BEGINNER NOTE: This is the SPECIAL attack animation clock.
            # The dictionary is created in start_special_animation().
            # Each call to update() is one game frame, so timer += 1 advances
            # the effect one frame. When timer passes duration, the effect ends.
            self.player_special_fx["timer"] += 1
            timer = self.player_special_fx["timer"]
            duration = max(1, self.player_special_fx["duration"])
            progress = min(1.0, timer / duration)

            # These lines repeat the same movement math used by
            # draw_player_special_fx(), but here we use the position to spawn
            # extra fire particles along the tornado's path.
            travel = min(1.0, progress * 1.18)
            ease = 1 - (1 - travel) * (1 - travel) * (1 - travel)
            center_x = 165 + (705 - 165) * ease
            center_y = 352 - 38 * math.sin(progress * math.pi) + 12 * math.sin(progress * math.pi * 7)
            for _ in range(3):
                angle = random.uniform(0, math.tau)
                dist = random.uniform(10, 58)
                self.particle_system.add_particle(
                    center_x + math.cos(angle) * dist,
                    center_y + math.sin(angle) * dist,
                    random.choice(FIRE_COLORS),
                    (random.uniform(-1.4, 1.4), random.uniform(-1.1, 0.8)),
                    random.randint(3, 7),
                    random.randint(14, 28),
                )
            if timer > duration:
                self.player_special_fx = None
        
        # Update magic effect
        if self.magic_effect['active']:
            self.magic_effect['radius'] += 3
            if self.magic_effect['radius'] > self.magic_effect['max_radius']:
                self.magic_effect['active'] = False
                self.magic_effect['radius'] = 0
        
        # Update fireball projectile
        if hasattr(self, 'fireball_projectile') and self.fireball_projectile['active']:
            # Update timer
            self.fireball_projectile['timer'] += 1
            
            if self.fireball_projectile['timer'] < self.fireball_projectile['max_timer']:
                # Calculate direction to target
                dx = self.fireball_projectile['target_x'] - self.fireball_projectile['x']
                dy = self.fireball_projectile['target_y'] - self.fireball_projectile['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Move fireball towards target
                    self.fireball_projectile['x'] += (dx / distance) * self.fireball_projectile['speed']
                    self.fireball_projectile['y'] += (dy / distance) * self.fireball_projectile['speed']
                
                # Add trail particles
                for _ in range(2):
                    angle = random.uniform(0, math.pi*2)
                    dist = random.uniform(0, 6)
                    px = self.fireball_projectile['x'] + math.cos(angle) * dist
                    py = self.fireball_projectile['y'] + math.sin(angle) * dist
                    self.particle_system.add_particle(
                        px, py, self.fireball_projectile['color'],
                        (random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)),
                        2, 15
                    )
            else:
                # Timer expired - fireball hits target and explodes
                self.particle_system.add_explosion(
                    700 + 30, 250 + 30,  # Enemy center position
                    self.fireball_projectile['color'], count=30, size_range=(3, 8), 
                    speed_range=(2, 6), lifetime_range=(20, 35)
                )
                self.fireball_projectile['active'] = False
                self.fireball_projectile['hit'] = True  # Mark as hit
                # Add a small delay to ensure projectile is removed before next frame
                self.action_cooldown = 2
        
        # Clean up hit projectiles
        if hasattr(self, 'fireball_projectile') and self.fireball_projectile.get('hit', False):
            delattr(self, 'fireball_projectile')
        if hasattr(self, 'knife_projectile') and self.knife_projectile.get('hit', False):
            delattr(self, 'knife_projectile')
        
        # Update knife projectile
        if hasattr(self, 'knife_projectile') and self.knife_projectile['active']:
            # Update timer
            self.knife_projectile['timer'] += 1
            
            if self.knife_projectile['timer'] < self.knife_projectile['max_timer']:
                # Calculate direction to target
                dx = self.knife_projectile['target_x'] - self.knife_projectile['x']
                dy = self.knife_projectile['target_y'] - self.knife_projectile['y']
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    # Move knife towards target
                    self.knife_projectile['x'] += (dx / distance) * self.knife_projectile['speed']
                    self.knife_projectile['y'] += (dy / distance) * self.knife_projectile['speed']
                    self.knife_projectile['rotation'] += 60  # Spin the knife faster (4x speed)
                
                # Add trail particles
                for _ in range(1):
                    angle = random.uniform(0, math.pi*2)
                    dist = random.uniform(0, 4)
                    px = self.knife_projectile['x'] + math.cos(angle) * dist
                    py = self.knife_projectile['y'] + math.sin(angle) * dist
                    self.particle_system.add_particle(
                        px, py, (120, 120, 120),
                        (random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)),
                        1, 10
                    )
            else:
                # Timer expired - knife hits target and explodes
                self.particle_system.add_explosion(
                    700 + 30, 250 + 30,  # Enemy center position
                    (80, 80, 80), count=20, size_range=(2, 6), 
                    speed_range=(1, 4), lifetime_range=(15, 25)
                )
                self.knife_projectile['active'] = False
                self.knife_projectile['hit'] = True  # Mark as hit
                # Add a small delay to ensure projectile is removed before next frame
                self.action_cooldown = 2
        
        if self.transition_state == "in":
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.transition_state = "out"
        elif self.transition_state == "out":
            self.transition_alpha -= self.transition_speed
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_state = "none"
                
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
            return False
        
        # Check for battle end conditions
        if self.enemy.health <= 0:
            self.battle_ended = True
            self.result = "win"
            self.add_log("You defeated the enemy!")
            self.show_summary = True
            return False
        elif self.player.health <= 0:
            self.battle_ended = True
            self.result = "lose"
            self.add_log("You were defeated...")
            self.show_summary = True
            return False
        
        # Update elemental effect
        if self.elemental_effect_timer > 0:
            self.elemental_effect_timer -= 1
            if self.elemental_effect_timer == 0:
                self.pending_elemental_effect = None
        
        # Process current action steps
        if self.action_steps:
            step = self.action_steps.pop(0)
            step()
            return False
            
        # Handle enemy turn if no actions are queued
        if self.state == "enemy_turn" and not self.battle_ended and not self.waiting_for_continue:
            if self.roll_player_dodge():
                speed_bonus = self.player.get_equipment_bonus("speed")
                if speed_bonus:
                    self.add_log(f"You dodge {self.enemy.name}'s attack! Speed gear helped.")
                else:
                    self.add_log(f"You dodge {self.enemy.name}'s attack!")
                self.state = "player_turn"
                self.combat_buttons_visible = True
                self.update_combat_toggle_button_label()
                self.add_log("It's your turn!")
                self.action_cooldown = self.action_delay
                return False

            incoming_strength = self.enemy.strength
            phase = self.get_boss_phase()
            if phase:
                incoming_strength += phase.get("strength_bonus", 0)
                self.add_log(phase["attack_message"])

            # BEGINNER NOTE: Ghost Face has custom attacks.
            # Regular enemies use the generic line below:
            #     "{enemy} attacks for X damage"
            # Ghost Face instead picks one attack data dictionary from
            # choose_ghostface_attack(), then uses that dictionary to adjust
            # damage, choose a visual FX name, shake the screen, and optionally
            # drain player MP.
            ghostface_attack = None
            if getattr(self.enemy, "enemy_type", None) == "ghost_face":
                ghostface_attack = self.choose_ghostface_attack()
                incoming_strength += ghostface_attack["damage_bonus"]
            damage = max(1, incoming_strength - self.player.effective_defense() // 3)
            base_damage_without_gear = max(1, incoming_strength - self.player.defense // 3)
            gear_guard = max(0, base_damage_without_gear - damage)
            guard_block = 0
            if self.player_guard_turns > 0:
                # BEGINNER NOTE: Warrior's Guard Break does not make the player
                # invincible. It shaves off part of the next hit, then expires.
                # `min(damage - 1, ...)` keeps every enemy hit at least 1 damage.
                guard_block = max(
                    0,
                    min(
                        damage - 1,
                        int(damage * 0.34) + max(1, self.player.effective_defense() // 6),
                    ),
                )
                damage = max(1, damage - guard_block)
                self.player_guard_turns = 0
            self.player.health = max(0, self.player.health - damage)
            if ghostface_attack:
                self.add_log(ghostface_attack["message"].format(name=self.enemy.name, damage=damage))
                self.queue_enemy_attack_fx(ghostface_attack["fx"], ghostface_attack["duration"])
                self.add_screen_shake(*ghostface_attack["shake"])
                mana_drain = min(self.player.mana, ghostface_attack.get("mana_drain", 0))
                if mana_drain:
                    self.player.mana -= mana_drain
                    self.add_log(f"The scream drains {mana_drain} MP!")
            else:
                self.add_log(f"{self.enemy.name} attacks for {damage} damage!")
                self.add_screen_shake(3, 5)
            if gear_guard:
                self.add_log(f"Equipped armor blocked {gear_guard} damage.")
            if guard_block:
                self.add_log(f"Guard stance blocked {guard_block} more damage.")
            self.damage_target = "player"
            self.damage_amount = damage
            self.damage_effect_timer = 20
            self.enemy.start_attack_animation()
            self.player.start_hit_animation()
            self.apply_enemy_elemental_effect()
            self.pending_elemental_effect = self.enemy.enemy_type
            self.elemental_effect_timer = 20
            self.state = "player_turn"
            self.combat_buttons_visible = True
            self.update_combat_toggle_button_label()
            self.add_log("It's your turn!")
            self.action_cooldown = self.action_delay
            
        return False
    
    def add_log(self, message):
        self.battle_log.append(message)
        self.waiting_for_continue = True

    def choose_ghostface_attack(self):
        """Return one random Ghost Face attack data record.

        Beginner note:
            Each dictionary below describes one possible Ghost Face move.

            message:
                Battle log text. `{name}` and `{damage}` get filled in later.
            fx:
                Which visual effect to draw. This string must match a case in
                draw_enemy_attack_fx().
            duration:
                How many frames the visual effect stays on screen.
            damage_bonus:
                Extra damage added to Ghost Face's normal enemy damage.
            shake:
                Two numbers passed to add_screen_shake(intensity, duration).
            mana_drain:
                Optional extra MP loss. Only the scream attack uses it now.
        """
        attacks = [
            {
                "message": "{name} lunges in with a stab for {damage} damage!",
                "fx": "ghostface_stab",
                "duration": 38,
                "damage_bonus": 4,
                "shake": (7, 12),
            },
            {
                "message": "{name} vanishes, then cross-stabs for {damage} damage!",
                "fx": "ghostface_cross_stab",
                "duration": 42,
                "damage_bonus": 7,
                "shake": (9, 14),
            },
            {
                "message": "{name}'s mask scream hits for {damage} damage!",
                "fx": "ghostface_scream",
                "duration": 48,
                "damage_bonus": 3,
                "shake": (8, 16),
                "mana_drain": 6,
            },
        ]
        return random.choice(attacks)

    def set_player_condition(self, label, color, duration=90):
        self.player_condition = {"label": label, "color": color}
        self.player_condition_timer = duration

    def apply_enemy_elemental_effect(self):
        profile = get_element_profile(self.enemy.enemy_type)
        status = profile.get("status")
        if not status or random.random() > status["chance"]:
            return

        kind = status["kind"]
        color = profile["accent_color"]
        self.particle_system.add_explosion(
            200 + 25, 350 + 25, random.choice(profile["particle_colors"]),
            count=18, size_range=(2, 5), speed_range=(1, 3), lifetime_range=(15, 30)
        )

        if kind == "burn":
            amount = max(1, status["damage"] + self.enemy.strength // 12)
            self.player.health = max(0, self.player.health - amount)
            self.set_player_condition("BURNING", color)
            self.add_log(status["message"].format(amount=amount))
        elif kind == "drain":
            amount = min(self.player.mana, status["amount"] + self.enemy.strength // 10)
            if amount > 0:
                self.player.mana -= amount
                self.set_player_condition("DRAINED", color)
                self.add_log(status["message"].format(amount=amount))
        elif kind == "chill":
            self.player_chill_turns = max(self.player_chill_turns, status["turns"])
            self.set_player_condition("CHILLED", color)
            self.add_log(status["message"])

    def apply_player_damage_modifiers(self, damage):
        if self.player_chill_turns <= 0:
            return damage

        self.player_chill_turns -= 1
        multiplier = get_element_profile("ice")["status"]["damage_multiplier"]
        reduced_damage = max(1, int(damage * multiplier))
        self.add_log("Chill weakens the strike.")
        return reduced_damage

    def roll_player_damage(self, base_damage):
        damage = self.apply_player_damage_modifiers(base_damage)
        crit_chance = min(
            BATTLE_RULES["max_crit_chance"],
            BATTLE_RULES["base_crit_chance"] + self.player.effective_speed() * BATTLE_RULES["speed_crit_bonus"],
        )
        if random.random() < crit_chance:
            damage = max(1, int(damage * BATTLE_RULES["crit_multiplier"]))
            self.add_log("Critical hit!")
        return damage

    def roll_player_dodge(self):
        speed_edge = max(0, self.player.effective_speed() - self.enemy.speed)
        dodge_chance = min(
            BATTLE_RULES["max_dodge_chance"],
            BATTLE_RULES["base_dodge_chance"] + speed_edge * BATTLE_RULES["speed_dodge_bonus"],
        )
        return random.random() < dodge_chance

    def get_escape_chance(self):
        speed_edge = self.player.effective_speed() - self.enemy.speed
        chance = BATTLE_RULES["base_escape_chance"] + speed_edge * BATTLE_RULES["speed_escape_bonus"]
        return max(
            BATTLE_RULES["min_escape_chance"],
            min(BATTLE_RULES["max_escape_chance"], chance)
        )

    def can_use_battle_item(self, item_type):
        """Return whether a selected battle potion can be used right now."""
        profile = ITEM_PROFILES[item_type]
        if self.player.get_inventory_count(item_type) <= 0:
            return False, f"No {profile['label'].lower()} potions left."
        if profile["effect"] == "restore_health" and self.player.health >= self.player.max_health:
            return False, "HP is already full."
        if profile["effect"] == "restore_mana" and self.player.mana >= self.player.max_mana:
            return False, "MP is already full."
        return True, ""

    def get_boss_phase(self):
        if not self.is_boss or not hasattr(self.enemy, "phase_thresholds"):
            return None

        health_ratio = self.enemy.health / max(1, self.enemy.max_health)
        active_phase = None
        for phase in self.enemy.phase_thresholds:
            if health_ratio <= phase["threshold"]:
                active_phase = phase
        return active_phase

    def check_boss_phase_transition(self):
        phase = self.get_boss_phase()
        if not phase or self.enemy.health <= 0 or phase["name"] in self.boss_phase_announced:
            return

        self.boss_phase_announced.add(phase["name"])
        self.add_log(f"{self.enemy.name} enters {phase['name']} phase!")
        self.add_screen_shake(phase.get("shake", 5), 12)
        self.particle_system.add_explosion(
            700 + 30, 250 + 30, phase["color"],
            count=35, size_range=(3, 8), speed_range=(2, 6), lifetime_range=(20, 35)
        )
    
    def handle_input(self, event, game=None):
        """Delegate battle keyboard/touch routing to systems/battle_input.py."""
        handle_battle_input(self, event, game, pygame, display_to_game_pos)
    
    def handle_action(self, game=None):
        if self.state != "player_turn" or self.battle_ended or self.action_cooldown > 0:
            return

        if self.menu_mode == "items":
            self.handle_item_action(game)
            return

        # BEGINNER NOTE: This method turns the selected button index into an
        # action. The first three slots are always ATTACK, MAGIC, ITEM.
        # SPECIAL only exists after Lion Sage unlocks it. RUN is always the
        # last button and uses self.run_button_index.
        if self.selected_option == 0:  # Attack
            if game and hasattr(game, 'SFX_ATTACK') and game.SFX_ATTACK: game.SFX_ATTACK.play()
            attack_name = self.get_basic_attack_name()
            self.action_steps = [
                lambda attack_name=attack_name: self.add_log(f"You use {attack_name}!"),
                lambda: self.start_attack_animation(),
                lambda: self.execute_attack()
            ]
        elif self.selected_option == 1:  # Magic
            if self.player.mana >= 20:
                if game and hasattr(game, 'SFX_MAGIC') and game.SFX_MAGIC: game.SFX_MAGIC.play()
                magic_name = self.get_magic_attack_name()
                self.action_steps = [
                    lambda magic_name=magic_name: self.add_log(f"You cast {magic_name}!"),
                    lambda: self.start_magic_animation(),
                    lambda: self.execute_magic()
                ]
            else:
                if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
                self.add_log("Not enough mana!")
        elif self.selected_option == 2:  # Item
            if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
            self.set_battle_menu_mode("items")
            self.show_combat_buttons()
            if not self.battle_log or self.battle_log[-1] != "Choose a battle item.":
                self.battle_log.append("Choose a battle item.")
            return
        elif self.special_button_index is not None and self.selected_option == self.special_button_index:
            # The class special is a stronger player move, so it costs MP.
            # The constant at the top of the file is the only number to change
            # if the special should be easier or harder to use.
            special_name = self.get_special_attack_name()
            if self.player.mana >= SPECIAL_ATTACK_MANA_COST:
                if game and hasattr(game, 'SFX_MAGIC') and game.SFX_MAGIC: game.SFX_MAGIC.play()

                # BEGINNER NOTE: action_steps is a tiny queue.
                # update() pops and runs one lambda per frame/cycle. That lets
                # the battle log, animation start, and damage happen in order.
                self.action_steps = [
                    lambda special_name=special_name: self.add_log(f"You summon {special_name}!"),
                    lambda: self.start_special_animation(),
                    lambda: self.execute_special_attack()
                ]
            else:
                if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
                self.add_log(f"Need {SPECIAL_ATTACK_MANA_COST} MP for {special_name}!")
        elif self.selected_option == self.run_button_index:  # Run
            if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
            self.action_steps = [
                lambda: self.add_log("You attempt to escape..."),
                lambda: self.execute_run()
            ]

        if self.action_steps:
            # BEGINNER NOTE: Once a real action has been chosen, hide the big
            # battle buttons until the next player turn. The small ACTIONS
            # toggle remains available when control returns to the player.
            self.combat_buttons_visible = False
            self.update_combat_toggle_button_label()

    def handle_item_action(self, game=None):
        """Run the selected item menu command."""
        item_keys = ("health", "mana")
        if self.selected_option == self.item_back_button_index:
            if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
            self.set_battle_menu_mode("actions")
            return

        item_type = item_keys[self.selected_option]
        can_use, reason = self.can_use_battle_item(item_type)
        if not can_use:
            if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
            self.add_log(reason)
            return

        if game and hasattr(game, 'SFX_ITEM') and game.SFX_ITEM: game.SFX_ITEM.play()
        item_label = ITEM_PROFILES[item_type]["label"].lower()
        self.action_steps = [
            lambda item_label=item_label: self.add_log(f"You used a {item_label} potion!"),
            lambda item_type=item_type: self.execute_item(item_type)
        ]
        self.set_battle_menu_mode("actions")
        self.combat_buttons_visible = False
        self.update_combat_toggle_button_label()
    

    
    def start_attack_animation(self):
        self.player.start_attack_animation()
        self.attack_effect_timer = 20
        
        # Clear any existing projectiles to prevent stacking
        if hasattr(self, 'fireball_projectile'):
            delattr(self, 'fireball_projectile')
        if hasattr(self, 'knife_projectile'):
            delattr(self, 'knife_projectile')
        
        # Character-specific attack animations
        if self.player.type == "Mage":
            # Fireball attack animation
            self.fireball_projectile = {
                'active': True,
                'x': 200 + 25,  # Player center
                'y': 350 + 15,  # Player center
                'target_x': 700 + 30,  # Enemy center
                'target_y': 250 + 30,  # Enemy center
                'speed': 56,  # Slightly faster than knife
                'size': 12,
                'color': random.choice(FIRE_COLORS),
                'trail_particles': [],
                'timer': 0,  # Timer for 0.8 seconds
                'max_timer': 48  # 0.8 seconds at 60 FPS
            }
            
            # Create fireball trail particles
            for _ in range(10):
                angle = random.uniform(0, math.pi*2)
                dist = random.uniform(0, 8)
                px = self.fireball_projectile['x'] + math.cos(angle) * dist
                py = self.fireball_projectile['y'] + math.sin(angle) * dist
                self.particle_system.add_particle(
                    px, py, self.fireball_projectile['color'],
                    (math.cos(angle) * 0.3, math.sin(angle) * 0.3),
                    2, 20
                )
                
        elif self.player.type == "Rogue":
            # Knife throw attack animation
            self.knife_projectile = {
                'active': True,
                'x': 200 + 25,  # Player center
                'y': 350 + 15,  # Player center
                'target_x': 700 + 30,  # Enemy center
                'target_y': 250 + 30,  # Enemy center
                'speed': 48,  # 4 times faster (12 * 4)
                'size': 16,  # 2 times bigger (8 * 2)
                'rotation': 0,
                'color': (100, 100, 100),  # Steel gray
                'trail_particles': [],
                'timer': 0,  # Timer for 0.6 seconds
                'max_timer': 36  # 0.6 seconds at 60 FPS
            }
            
            # Create knife throw particles
            for _ in range(8):
                angle = random.uniform(0, math.pi*2)
                dist = random.uniform(0, 6)
                px = self.knife_projectile['x'] + math.cos(angle) * dist
                py = self.knife_projectile['y'] + math.sin(angle) * dist
                self.particle_system.add_particle(
                    px, py, (150, 150, 150),
                    (math.cos(angle) * 0.4, math.sin(angle) * 0.4),
                    1, 15
                )
                
        else:
            # Warrior/Paladin holy attack animation
            # Create holy energy particles around the player
            for _ in range(12):
                angle = random.uniform(0, math.pi*2)
                dist = random.uniform(0, 15)
                px = 200 + 25 + math.cos(angle) * dist
                py = 350 + 15 + math.sin(angle) * dist
                # Holy particle colors (gold, white, light blue)
                holy_colors = [(255, 215, 0), (255, 255, 255), (173, 216, 230)]
                particle_color = random.choice(holy_colors)
                self.particle_system.add_particle(
                    px, py, 
                    particle_color,
                    (math.cos(angle) * 0.8, math.sin(angle) * 0.8),
                    4, 25
                )
    
    def start_magic_animation(self):
        self.player.start_attack_animation()
        if hasattr(self, 'fireball_projectile'):
            delattr(self, 'fireball_projectile')
        if hasattr(self, 'knife_projectile'):
            delattr(self, 'knife_projectile')

        self.magic_effect = {
            'active': True,
            'x': 700 + 30,  # Enemy center x (where magic hits)
            'y': 250 + 30,  # Enemy center y (where magic hits)
            'radius': 0,
            'max_radius': 100,
            'color': random.choice(MAGIC_COLORS)
        }

        if self.player.type == "Mage":
            # BEGINNER NOTE: Mage normal MAGIC now uses an imported cutout GIF
            # overlay, but the old ring/beam/particle effects below still run.
            # If the PNG frames are missing, `frames` is empty and the old
            # procedural magic graphics still carry the attack.
            frames = load_animation_frames(MAGE_MAGIC_FIREBALL_FRAME_DIR, target_height=82)
            self.fireball_projectile = {
                'active': True,
                'x': 200 + 25,
                'y': 350 + 15,
                'target_x': 700 + 30,
                'target_y': 250 + 30,
                'speed': 54,
                'size': 12,
                'color': random.choice(FIRE_COLORS),
                'trail_particles': [],
                'timer': 0,
                'max_timer': 36,
                'frames': frames,
            }
        
        for _ in range(20):
            angle = random.uniform(0, math.pi*2)
            dist = random.uniform(0, 10)
            px = self.magic_effect['x'] + math.cos(angle) * dist
            py = self.magic_effect['y'] + math.sin(angle) * dist
            self.particle_system.add_particle(
                px, py, self.magic_effect['color'],
                (math.cos(angle) * 0.5, math.sin(angle) * 0.5),
                3, 30
            )

    def start_special_animation(self):
        """Start the class SPECIAL visual effect.

        Beginner note:
            This does NOT apply damage. It only prepares the animation and
            opening particles. The actual hit is handled in
            execute_special_attack() so visuals and battle math stay separate.
        """
        self.player.start_attack_animation()

        # BEGINNER NOTE: Warrior/Rogue use Fire Tornado.
        # Mage starts with the same tornado travel, then adds the imported
        # Fire Blast impact frames when the tornado reaches the enemy.
        special_name = self.get_special_attack_name()
        is_fire_blast = self.player.type == "Mage"

        # The special has its own imported animation, so turn off the normal
        # slash/magic visuals before starting it.
        self.attack_effect_timer = 0
        self.magic_effect["active"] = False

        # Remove old projectiles so a previous fireball/knife cannot overlap
        # the new special if actions happen quickly.
        if hasattr(self, 'fireball_projectile'):
            delattr(self, 'fireball_projectile')
        if hasattr(self, 'knife_projectile'):
            delattr(self, 'knife_projectile')

        # Load the transparent PNG frames that were cut out from the uploaded
        # Fire Tornado GIF. `target_height=220` controls the base on-screen size.
        frames = load_animation_frames(FLAME_TORNADO_FRAME_DIR, target_height=220)
        impact_frames = []
        if is_fire_blast:
            # BEGINNER NOTE: These frames were cut out from the uploaded
            # firestorm GIF. They are only loaded for Mage to keep the regular
            # Fire Tornado effect unchanged for the other classes.
            impact_frames = load_animation_frames(FIRE_BLAST_FRAME_DIR, target_height=320)
        self.player_special_fx = {
            "timer": 0,
            "duration": SPECIAL_ATTACK_DURATION,
            "frames": frames,
            "impact_frames": impact_frames,
            "kind": "fire_blast" if is_fire_blast else "fire_tornado",
            "name": special_name,
            "seed": random.randint(1, 999999),
        }

        # Opening spark burst around the player. This is separate from the
        # imported tornado frames and makes the move feel like it is being cast.
        for _ in range(32):
            angle = random.uniform(0, math.tau)
            dist = random.uniform(8, 45)
            self.particle_system.add_particle(
                225 + math.cos(angle) * dist,
                365 + math.sin(angle) * dist,
                random.choice(FIRE_COLORS),
                (math.cos(angle) * random.uniform(0.5, 1.4), math.sin(angle) * random.uniform(0.4, 1.2)),
                random.randint(3, 7),
                random.randint(18, 34),
            )
        self.add_screen_shake(4, 18)
    
    def execute_attack(self):
        """Apply the class-specific basic ATTACK command.

        Beginner note:
            This is where class identity becomes mechanics:
            - Warrior: heavier hit and one guarded enemy hit.
            - Mage: lighter Firebolt that restores a little MP.
            - Rogue: fast knife throw with a chance for a second strike.
        """
        attack_name = self.get_basic_attack_name()
        base_damage = self.player.effective_strength()
        gear_note = self.get_attack_gear_note("magic" if self.player.type == "Mage" else "attack")
        extra_note = ""

        if self.player.type == "Warrior":
            base_damage += max(1, self.player.effective_defense() // 3)
            self.player_guard_turns = 1
            self.set_player_condition("BRACED", (255, 230, 130), duration=130)
            extra_note = " Braced for the next hit."
        elif self.player.type == "Mage":
            mana_gain = min(self.player.max_mana - self.player.mana, 3 + self.player.level // 2)
            if mana_gain:
                self.player.mana += mana_gain
                extra_note = f" MP +{mana_gain}."

        damage = self.roll_player_damage(base_damage)
        bonus_damage = 0

        if self.player.type == "Rogue":
            # Speed is the Rogue's class stat, so it controls the second-hit
            # chance. The cap stops late-game speed gear from making it certain.
            second_hit_chance = min(0.48, 0.18 + self.player.effective_speed() * 0.018)
            if random.random() < second_hit_chance:
                bonus_base = max(2, self.player.effective_speed() + self.player.effective_strength() // 2)
                bonus_damage = max(1, self.roll_player_damage(bonus_base) // 2)
                extra_note = f" Quick second hit +{bonus_damage}."

        total_damage = damage + bonus_damage
        self.enemy.health = max(0, self.enemy.health - total_damage)

        if self.player.type == "Mage":
            self.add_log(f"{attack_name} dealt {total_damage} damage to {self.enemy.name}!{extra_note}{gear_note}")
        elif self.player.type == "Rogue":
            self.add_log(f"{attack_name} dealt {total_damage} damage to {self.enemy.name}!{extra_note}{gear_note}")
        else:
            self.add_log(f"{attack_name} dealt {total_damage} damage to {self.enemy.name}!{extra_note}{gear_note}")
            profile = get_element_profile(self.enemy.enemy_type)
            self.particle_system.add_explosion(
                700 + 30, 250 + 30, random.choice(profile["particle_colors"]),
                count=28, size_range=(2, 6), speed_range=(1, 4), lifetime_range=(15, 30)
            )

        self.damage_target = "enemy"
        self.damage_amount = total_damage
        self.damage_effect_timer = 20
        self.enemy.start_hit_animation()
        self.add_screen_shake(5, 8)
        self.check_boss_phase_transition()
        
        self.state = "enemy_turn"
        self.action_cooldown = self.action_delay
    
    def execute_magic(self):
        magic_name = self.get_magic_attack_name()
        base_damage = self.player.effective_strength() * 2
        if self.player.type == "Mage":
            # Mage has the highest MP pool, so MAGIC scales partly from max MP.
            # This makes the class feel like a spellcaster before SPECIAL unlocks.
            base_damage += int(self.player.max_mana * 0.12 + self.player.level * 2)
        elif self.player.type == "Warrior":
            base_damage += max(1, self.player.effective_defense() // 4)
        elif self.player.type == "Rogue":
            base_damage += max(1, self.player.effective_speed() // 3)

        damage = self.roll_player_damage(base_damage)
        self.enemy.health = max(0, self.enemy.health - damage)
        self.player.mana -= 20
        self.add_log(f"{magic_name} dealt {damage} damage to {self.enemy.name}!{self.get_attack_gear_note('magic')}")
        self.damage_target = "enemy"
        self.damage_amount = damage
        self.damage_effect_timer = 20
        self.enemy.start_hit_animation()
        self.add_screen_shake(8, 10)
        self.check_boss_phase_transition()
        
        self.particle_system.add_beam(
            200 + 25, 350 + 15,  # Staff top (adjusted for new player position)
            700 + 30, 250 + 30,  # Enemy center (adjusted for new enemy position)
            self.magic_effect['color'], width=5, particle_count=15, speed=3
        )
        
        self.particle_system.add_explosion(
            700 + 30, 250 + 30, self.magic_effect['color'],
            count=40, size_range=(3, 7), speed_range=(1, 5), lifetime_range=(15, 30)
        )
        
        self.state = "enemy_turn"
        self.action_cooldown = 40 if self.player.type == "Mage" else self.action_delay

    def execute_special_attack(self):
        """Apply the class SPECIAL attack's MP cost, damage, and hit feedback.

        Beginner note:
            This is the battle-math half of the special attack.
            To tune Fire Tornado/Fire Blast strength, edit the base_damage
            lines below.
            To tune the animation, edit draw_player_special_fx() and the
            SPECIAL_ATTACK_DURATION constant instead.
        """
        self.player.mana = max(0, self.player.mana - SPECIAL_ATTACK_MANA_COST)
        special_name = self.get_special_attack_name()

        # Damage formula:
        # - strength is the main stat
        # - speed gives a smaller bonus because the tornado crosses the screen
        # - level keeps the special useful as the player grows
        # roll_player_damage() is still used so critical hits and chill effects
        # work the same way they do for regular attacks.
        if self.player.type == "Mage":
            # Mage has low strength but high mana, so Fire Blast uses max_mana
            # as part of its power budget. That keeps the Mage special feeling
            # like a real spell instead of a weak physical attack.
            base_damage = int(self.player.effective_strength() * 2.0 + self.player.max_mana * 0.23 + self.player.level * 4)
        else:
            base_damage = int(self.player.effective_strength() * 2.4 + self.player.effective_speed() * 0.8 + self.player.level * 3)
        damage = self.roll_player_damage(base_damage)
        self.enemy.health = max(0, self.enemy.health - damage)
        gear_note = self.get_attack_gear_note("magic" if self.player.type == "Mage" else "attack")
        if self.player.type == "Mage":
            self.add_log(f"{special_name} erupted on {self.enemy.name} for {damage} damage!{gear_note}")
        else:
            self.add_log(f"{special_name} tore across {self.enemy.name} for {damage} damage!{gear_note}")
        self.damage_target = "enemy"
        self.damage_amount = damage
        self.damage_effect_timer = 34
        self.enemy.start_hit_animation()
        self.add_screen_shake(10, 20)
        self.check_boss_phase_transition()

        self.particle_system.add_beam(
            225, 365,
            730, 280,
            random.choice(FIRE_COLORS),
            width=5,
            particle_count=18,
            speed=4,
        )
        self.particle_system.add_explosion(
            730, 280, random.choice(FIRE_COLORS),
            count=56, size_range=(4, 10), speed_range=(2, 7), lifetime_range=(18, 42)
        )

        # Keep the enemy from immediately taking a turn while Fire Tornado is
        # still crossing the screen. This makes the visual and turn flow line up.
        self.state = "enemy_turn"
        self.action_cooldown = SPECIAL_ATTACK_DURATION
    
    def execute_item(self, item_type):
        profile = ITEM_PROFILES[item_type]
        can_use, reason = self.can_use_battle_item(item_type)
        if not can_use:
            self.add_log(reason)
            return
        if not self.player.use_inventory_item(item_type):
            self.add_log(f"No {profile['label'].lower()} potions left!")
            return

        amount = profile["amount"]
        if profile["effect"] == "restore_health":
            before = self.player.health
            self.player.health = min(self.player.max_health, self.player.health + amount)
            restored = self.player.health - before
        elif profile["effect"] == "restore_mana":
            before = self.player.mana
            self.player.mana = min(self.player.max_mana, self.player.mana + amount)
            restored = self.player.mana - before
        else:
            restored = amount
        self.add_log(profile["message"].format(amount=restored))
        
        for _ in range(20):
            x = random.randint(200, 200 + PLAYER_SIZE)
            y = random.randint(300, 300 + PLAYER_SIZE)
            self.particle_system.add_particle(
                x, y, profile["color"],
                (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)),
                3, 30
            )
        
        self.state = "enemy_turn"
        self.action_cooldown = self.action_delay
    
    def execute_run(self):
        if random.random() < self.get_escape_chance():
            self.add_log("You successfully escaped!")
            self.battle_ended = True
            self.result = "escape"
            self.show_summary = True
        else:
            self.add_log("Escape failed! The enemy attacks!")
            self.state = "enemy_turn"
            self.action_cooldown = self.action_delay

# ============================================================================
# STORY SYSTEM - Opening cutscene and narrative elements
# ============================================================================
class OpeningCutscene:
    """
    Story introduction sequence with multiple scenes and text progression.
    Sets up the game's narrative and world background.

    Beginner note:
        This is only the opening movie-style sequence. Regular story dialogue
        after gameplay starts is handled by `Game.start_story_dialogue` and
        drawn through `systems/story_ui.py`.
    """
    def __init__(self):
        self.state = "intro"
        self.timer = 0
        # BEGINNER NOTE: The opening has three scenes. Each duration is in
        # frames, so 300 frames is about five seconds at 60 FPS.
        self.scene_durations = [300, 360, 600]
        self.scene_duration = self.scene_durations[0]
        self.scene_index = 0
        self.transition_alpha = 0
        self.transition_speed = 5
        self.text_alpha = 0
        self.text_appear_speed = 3
        self.text_disappear_speed = 2
        self.particle_system = ParticleSystem()
        self.transition_state = "none"  # Initialize transition_state
        self.story_page_duration = 160
        self.dragon = Dragon(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2 - 108)

        # BEGINNER NOTE: Precompute stars and mountains once. The old opening
        # used random mountain heights every draw call, which made the scene
        # flicker instead of feeling animated.
        self.stars = [
            (
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.choice((1, 1, 1, 2)),
                random.random() * math.tau,
            )
            for _ in range(120)
        ]
        self.mountains = [
            (i * 100, 150 + random.randint(0, 70), random.choice(((24, 24, 52), (34, 28, 60), (44, 30, 48))))
            for i in range(11)
        ]
        self.story_pages = (
            {
                "title": "The Last Road",
                "lines": (
                    "The kingdom of Pixelonia still has walls, but the roads between them are burning.",
                    "Malakor has returned. The dragon is real, and every village now watches the sky.",
                ),
            },
            {
                "title": "The Mask In The Pines",
                "lines": (
                    "The dragon is not the first test. In the northern forest, Ghost Face hunts courage before it can grow.",
                    "The town knight will send you toward the one guide who understands fear and healing.",
                ),
            },
            {
                "title": "The Guardian Healer",
                "lines": (
                    "Find the Lion Sage in the western marsh. Earn his blessing and your first special technique.",
                    "Then choose your path: break the mask in the pines, or grow strong enough to face Malakor.",
                ),
            },
        )

    def current_scene_duration(self):
        """Return how long the active opening scene should last."""
        index = min(self.scene_index, len(self.scene_durations) - 1)
        return self.scene_durations[index]
        
    def update(self):
        self.timer += 1
        self.particle_system.update()
        self.scene_duration = self.current_scene_duration()
        
        # Update text alpha
        if self.timer < 120:  # First 2 seconds: text appears
            self.text_alpha = min(255, self.text_alpha + self.text_appear_speed)
        elif self.timer > self.scene_duration - 120:  # Last 2 seconds: text disappears
            self.text_alpha = max(0, self.text_alpha - self.text_disappear_speed)
        
        # Scene transitions
        if self.timer >= self.scene_duration:
            self.timer = 0
            self.scene_index += 1
            self.text_alpha = 0
            self.transition_alpha = 0
            self.transition_state = "in"
            
        # Add particles for scene 2
        if self.scene_index == 1 and self.timer % 5 == 0:
            self.particle_system.add_particle(
                random.randint(0, SCREEN_WIDTH),
                -10,
                random.choice(FIRE_COLORS),
                (random.uniform(-0.5, 0.5), random.uniform(1, 3)),
                random.randint(3, 7),
                random.randint(40, 80)
            )
        if self.scene_index == 1:
            self.dragon.update()
            if self.timer % 118 == 16:
                self.dragon.breathe_fire()
        
        # Transition animation
        if self.timer > self.scene_duration - 60:  # Last second of scene
            self.transition_alpha = min(255, self.transition_alpha + self.transition_speed)
        
        # End of cutscene
        if self.scene_index >= 3:
            return "character_select"
            
        return None
    
    def draw(self, screen):
        # Draw scene based on index
        if self.scene_index == 0:
            self.draw_intro_scene(screen)
        elif self.scene_index == 1:
            self.draw_dragon_scene(screen)
        elif self.scene_index == 2:
            self.draw_story_scene(screen)
        
        # Draw transition overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.transition_alpha))
        screen.blit(overlay, (0, 0))
        
        # Draw particles
        self.particle_system.draw(screen)
        
        # Draw skip prompt
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking text
            skip_text = font_tiny.render("Tap / press any key to continue", True, (210, 210, 210))
            screen.blit(skip_text, (SCREEN_WIDTH - skip_text.get_width() - 20, SCREEN_HEIGHT - 34))
    
    def draw_intro_scene(self, screen):
        # Draw starfield background
        screen.fill((5, 8, 24))
        ticks = pygame.time.get_ticks() * 0.001
        for x, y, size, phase in self.stars:
            twinkle = int(35 * (0.5 + 0.5 * math.sin(ticks * 2.0 + phase)))
            color = (170 + twinkle, 175 + twinkle, 225)
            pygame.draw.circle(screen, color, (x, y), size)

        # A soft horizon glow makes the opening feel less empty while keeping
        # the text readable.
        horizon = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for radius in range(260, 40, -35):
            alpha = max(0, 28 - radius // 15)
            pygame.draw.circle(horizon, (160, 35, 30, alpha), (SCREEN_WIDTH // 2, 520), radius)
        screen.blit(horizon, (0, 0))
        
        # Draw title
        title = font_large.render("DRAGON'S LAIR", True, (255, 50, 50))
        title_shadow = font_large.render("DRAGON'S LAIR", True, (150, 0, 0))
        title_x = SCREEN_WIDTH//2 - title.get_width()//2
        for offset in range(10, 1, -2):
            glow = font_large.render("DRAGON'S LAIR", True, (120, 20, 20))
            glow.set_alpha(16)
            screen.blit(glow, (title_x - offset, 100))
            screen.blit(glow, (title_x + offset, 100))
        screen.blit(title_shadow, (title_x + 3, 103))
        screen.blit(title, (title_x, 100))
        
        # Draw subtitle
        subtitle = font_medium.render("A RETRO RPG ADVENTURE", True, TEXT_COLOR)
        subtitle_shadow = font_medium.render("A RETRO RPG ADVENTURE", True, (0, 100, 100))
        screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 162))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
        
        # Draw intro text
        # BEGINNER NOTE: The intro lines live in game_data/story.py now.
        # Edit OPENING_STORY_LINES there if you want to rewrite the opening.
        intro_text = list(OPENING_STORY_LINES)
        
        panel = pygame.Rect(150, 240, 700, 235)
        pygame.draw.rect(screen, (8, 10, 26), panel, border_radius=8)
        pygame.draw.rect(screen, (80, 54, 82), panel, 2, border_radius=8)

        y_pos = panel.y + 28
        for line in intro_text:
            text = font_cinematic.render(line, True, TEXT_COLOR)
            text.set_alpha(self.text_alpha)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 44
    
    def draw_dragon_scene(self, screen):
        # Draw dark background
        screen.fill((10, 5, 20))
        ticks = pygame.time.get_ticks() * 0.001

        # Distant moon and smoke clouds.
        pygame.draw.circle(screen, (92, 82, 110), (770, 120), 54)
        pygame.draw.circle(screen, (10, 5, 20), (748, 108), 50)
        smoke_layer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(16):
            sx = 40 + i * 70
            sy = 150 + math.sin(ticks * 0.8 + i) * 18
            pygame.draw.circle(smoke_layer, (70, 55, 70, 28), (int(sx), int(sy)), 45 + (i % 3) * 12)
        screen.blit(smoke_layer, (0, 0))
        
        # Draw mountains
        for base_x, height, color in self.mountains:
            pygame.draw.polygon(screen, color, [
                (base_x, SCREEN_HEIGHT),
                (base_x + 50, SCREEN_HEIGHT - height),
                (base_x + 100, SCREEN_HEIGHT)
            ])
        
        # BEGINNER NOTE: The opening used to draw a separate old silhouette
        # dragon here. It now uses the same imported title dragon as the main
        # menu, tinted through the real boss progression palette.
        boss_level = min(FINAL_BOSS_LEVEL, 2 + self.timer // 45)
        boss_profile = get_boss_profile(boss_level)
        self.dragon.draw(screen, boss_level=boss_level, target_height=280)
        aspect_label = render_fitted_text(
            f"Dragon aspect: {boss_profile['name']}",
            (255, 225, 150),
            420,
            (font_tiny,),
        )
        aspect_panel = pygame.Rect(SCREEN_WIDTH // 2 - 230, 474, 460, 32)
        pygame.draw.rect(screen, UI_BG, aspect_panel, border_radius=6)
        pygame.draw.rect(screen, DRAGON_BOSS_COLORS[(boss_level - 1) % len(DRAGON_BOSS_COLORS)][1], aspect_panel, 2, border_radius=6)
        screen.blit(aspect_label, (aspect_panel.centerx - aspect_label.get_width() // 2, aspect_panel.y + 8))
        
        # Draw scene text
        scene_text = [
            "THE DRAGON MALAKOR RAVAGED THE LAND,",
            "BURNING VILLAGES AND TERRIFYING THE PEOPLE.",
            "THE KING CALLED FOR HEROES TO RISE UP",
            "AND CHALLENGE THE ANCIENT EVIL."
        ]
        
        y_pos = 86
        for line in scene_text:
            text = font_cinematic.render(line, True, (255, 200, 100))
            text.set_alpha(self.text_alpha)
            shadow = font_cinematic.render(line, True, (35, 15, 10))
            shadow.set_alpha(self.text_alpha)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            screen.blit(shadow, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text, text_rect)
            y_pos += 42
    
    def draw_story_scene(self, screen):
        # Draw parchment background.
        screen.fill((42, 30, 24))
        board = pygame.Rect(72, 56, SCREEN_WIDTH - 144, SCREEN_HEIGHT - 112)
        inner = board.inflate(-74, -88)

        pygame.draw.rect(screen, (76, 45, 28), board.move(8, 10), border_radius=12)
        pygame.draw.rect(screen, (205, 181, 126), board, border_radius=12)
        pygame.draw.rect(screen, (136, 91, 45), board, 5, border_radius=12)
        pygame.draw.rect(screen, (232, 210, 154), inner, border_radius=8)
        pygame.draw.rect(screen, (116, 76, 38), inner, 3, border_radius=8)

        # Decorative scroll rods.
        pygame.draw.rect(screen, (114, 74, 36), (44, 38, SCREEN_WIDTH - 88, 22), border_radius=8)
        pygame.draw.rect(screen, (114, 74, 36), (44, SCREEN_HEIGHT - 60, SCREEN_WIDTH - 88, 22), border_radius=8)
        pygame.draw.circle(screen, (88, 54, 28), (56, 49), 20)
        pygame.draw.circle(screen, (88, 54, 28), (SCREEN_WIDTH - 56, 49), 20)
        pygame.draw.circle(screen, (88, 54, 28), (56, SCREEN_HEIGHT - 49), 20)
        pygame.draw.circle(screen, (88, 54, 28), (SCREEN_WIDTH - 56, SCREEN_HEIGHT - 49), 20)

        # BEGINNER NOTE: The old opening scrolled one long list of text upward.
        # On Android that could pass through the border and leave the screen
        # before the player could read it. These pages are static, clipped to
        # the parchment's inner rectangle, and changed by the timer instead.
        page_index = min(len(self.story_pages) - 1, self.timer // self.story_page_duration)
        page = self.story_pages[page_index]
        page_timer = self.timer - page_index * self.story_page_duration
        fade_in = min(255, page_timer * 10)
        if page_index < len(self.story_pages) - 1 and page_timer > self.story_page_duration - 30:
            fade_out = max(0, (self.story_page_duration - page_timer) * 10)
        else:
            fade_out = 255
        page_alpha = min(self.text_alpha, fade_in, fade_out)

        old_clip = screen.get_clip()
        screen.set_clip(inner.inflate(-28, -22))

        title = font_medium.render(page["title"].upper(), True, (78, 39, 20))
        title.set_alpha(page_alpha)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, inner.y + 58))
        screen.blit(title, title_rect)

        divider_y = inner.y + 100
        divider_color = (130, 82, 40)
        pygame.draw.line(screen, divider_color, (inner.x + 60, divider_y), (inner.right - 60, divider_y), 3)

        y_pos = inner.y + 138
        for paragraph in page["lines"]:
            wrapped_lines = wrap_text_to_width(paragraph, font_small, inner.width - 110)
            for wrapped_line in wrapped_lines:
                text = font_small.render(wrapped_line, True, (55, 35, 22))
                text.set_alpha(page_alpha)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
                screen.blit(text, text_rect)
                y_pos += 34
            y_pos += 18

        screen.set_clip(old_clip)

        # Page dots tell the player the story is progressing without needing a
        # fast scroll.
        dot_y = inner.bottom - 42
        start_x = SCREEN_WIDTH // 2 - (len(self.story_pages) - 1) * 16
        for i in range(len(self.story_pages)):
            color = (90, 52, 24) if i == page_index else (160, 122, 76)
            pygame.draw.circle(screen, color, (start_x + i * 32, dot_y), 7)

        # Draw continue prompt
        if self.timer > 180 and pygame.time.get_ticks() % 1000 < 500:
            prompt = font_small.render("TAP OR PRESS ANY KEY TO CONTINUE", True, (100, 60, 30))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 92))
    
    def skip(self):
        """Advance the opening by one readable stage.

        Beginner note:
            This used to jump straight to character select. On Android, a
            single tap could erase the whole opening. Now each tap advances one
            scene, and the parchment scene advances one page at a time.
        """
        if self.scene_index == 2:
            current_page = min(len(self.story_pages) - 1, self.timer // self.story_page_duration)
            if current_page < len(self.story_pages) - 1:
                self.timer = (current_page + 1) * self.story_page_duration
                self.text_alpha = 255
                self.transition_alpha = 0
                return

        self.scene_index += 1
        self.timer = 0
        self.text_alpha = 0
        self.transition_alpha = 0
        self.transition_state = "in"

# ============================================================================
# PLATFORM DETECTION - Cross-platform compatibility
# ============================================================================
def is_android():
    """
    Detects if the game should use phone/touch-facing UI text.

    This uses the same robust touch-runtime check as the Android control
    overlay, so APK builds do not fall back to keyboard-only prompts.
    """
    return is_touch_ui_runtime()

# ============================================================================
# MAIN GAME CLASS - Central game controller and state manager
# ============================================================================
class Game:
    """
    Main game controller that manages all game states, systems, and user input.
    Handles the complete game loop from start menu to game over.
    
    Game States:
    - start_menu: Title screen with start/quit options
    - opening_cutscene: Story introduction sequence
    - character_select: Choose character class
    - overworld: Main gameplay area with movement and exploration
    - interior: Town building rooms with services and future NPC hooks
    - battle: Turn-based combat system
    - game_over: End game screen

    Beginner note:
    This class is the hub. Most features eventually connect here because this
    object owns the player, world, UI state, battle screen, and save/load calls.
    """
    def __init__(self):
        # Current screen/state. Many update and draw methods branch on this.
        self.state = "start_menu"

        # Core gameplay objects.
        self.player = None
        self.world_map = WorldMap()
        self.enemies = []
        self.items = []
        self.score = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.item_timer = 0

        # Visual/background state used by menus and transitions.
        self.starfield = []
        self.dragon = Dragon(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 120)
        self.fire_timer = 0
        self.battle_screen = None
        self.transition_alpha = 0
        self.transition_state = "none"
        self.transition_speed = 10

        # Movement and effects.
        self.player_moved = False
        self.movement_cooldown = 0
        self.movement_delay = 10
        self.particle_system = ParticleSystem()
        self.opening_cutscene = OpeningCutscene()

        # Progression and UI toggles.
        self.boss_battle_triggered = False
        self.boss_defeated = False
        self.show_world_map = False
        self.show_journal = False
        self.show_inventory = False
        self.inventory_slots = ("weapon", "armor", "accessory")
        self.inventory_slot_index = 0
        self.inventory_item_index = 0
        self.inventory_message = "Select gear with arrows. OK equips. USE unequips."
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.pickup_message = None
        self.pickup_message_timer = 0
        self.area_effect_timer = 0
        self.area_effect_message = None
        self.area_effect_message_timer = 0
        self.town_service_message = None
        self.town_service_message_timer = 0

        # Interior state tracks which town building room the player is inside.
        self.current_interior = None
        self.current_interior_service = None
        self.interior_return_position = None
        self.interior_player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.interior_player_y = 500
        self.npc_dialogue_index = 0
        # BEGINNER NOTE: This is the small button menu shown inside a building.
        # It gives Android players direct buttons for service/talk/log/leave
        # instead of relying on hidden keyboard-only shortcuts.
        self.interior_service_menu_open = False
        self.interior_service_menu_index = 0
        self.interior_service_menu_buttons = []

        # Town progression saved by `systems/save_load.py`.
        self.town_reputation = 0
        self.completed_town_errands = set()
        self.completed_resident_errands = set()
        self.inspected_town_details = set()
        self.town_resident_dialogue_index = {}

        # Story progression outside town services. These sets keep one-shot
        # area conversations and one-time Lion Sage rewards from repeating.
        self.seen_story_dialogues = set()
        self.claimed_story_rewards = set()
        self.story_enemy_defeats = {}
        self.active_story_dialogue_key = None
        self.active_story_dialogue = None
        self.active_story_lines = []
        self.active_story_line_index = 0
        self.active_story_repeat = False
        
        # Initialize starfield
        for _ in range(150):
            self.starfield.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.random() * 2 + 0.5
            ])
        
        # Add flying dragons
        self.flying_dragons = []
        for _ in range(5):
            self.flying_dragons.append({
                'x': random.randint(-200, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(2, 5),
                'flap': random.random() * 2 * math.pi
            })
        
        # UI Elements
        self.start_button = Button(SCREEN_WIDTH//2 - 120, 455, 240, 55, "START QUEST", UI_BORDER)
        self.load_button = Button(SCREEN_WIDTH//2 - 120, 525, 240, 55, "LOAD SAVE", (110, 220, 255))

        # BEGINNER NOTE: The start menu UPDATE APP button.
        # It does not install silently. Android requires the player to approve
        # APK updates. Pressing this button only opens the stable GitHub APK
        # download URL so Android can show its normal installer prompt.
        self.update_button = Button(SCREEN_WIDTH//2 - 120, 555, 240, 55, "UPDATE APP", (255, 190, 80))
        self.quit_button = Button(SCREEN_WIDTH//2 - 120, 595, 240, 55, "QUIT", UI_BORDER)
        self.back_button = Button(20, 20, 100, 40, "BACK")
        self.start_menu_index = 0
        self.character_menu_index = 0
        self.end_menu_index = 0

        # BEGINNER NOTE: These fields control the one-line update message on
        # the title screen. The background thread below fills them in after it
        # checks GitHub. They are intentionally simple booleans/strings so the
        # draw code can read them without doing internet work every frame.
        self.update_available = False
        self.update_check_done = False
        self.update_status = "Checking for app updates..."

        # BEGINNER NOTE: Network checks can freeze the game if they run on the
        # main loop. This thread lets the title screen keep animating while the
        # game asks GitHub whether a newer APK version exists.
        self.update_thread = threading.Thread(target=self.check_for_updates, daemon=True)
        self.update_thread.start()
        
        # Character buttons
        # BEGINNER NOTE: These buttons are still the clickable/touchable class
        # cards. Their text is blank because the draw code renders the imported
        # sprite preview plus a custom label strip on top of each card.
        self.warrior_button = Button(SCREEN_WIDTH//2 - 300, 300, 200, 150, "", (0, 255, 0))
        self.mage_button = Button(SCREEN_WIDTH//2 - 50, 300, 200, 150, "", (0, 200, 255))
        self.rogue_button = Button(SCREEN_WIDTH//2 + 200, 300, 200, 150, "", (255, 100, 0))
        
        # ========================================
        # AUDIO SYSTEM - Procedurally Generated Sound Effects
        # ========================================
        # Generate retro-style sound effects using mathematical waveforms
        def generate_tone(frequency=440, duration_ms=100, volume=0.5, sample_rate=SAMPLE_RATE, waveform='sine'):
            pcm = bytearray()
            sample_count = int(sample_rate * duration_ms / 1000)
            for sample_index in range(sample_count):
                t = sample_index / sample_rate
                phase = frequency * 2 * math.pi * t
                if waveform == 'sine':
                    wave_value = math.sin(phase)
                elif waveform == 'square':
                    wave_value = 1.0 if math.sin(phase) >= 0 else -1.0
                elif waveform == 'sawtooth':
                    wave_value = 2 * (t * frequency - math.floor(t * frequency + 0.5))
                elif waveform == 'noise':
                    wave_value = random.uniform(-1, 1)
                else:
                    wave_value = math.sin(phase)
                append_stereo_sample(pcm, wave_value * volume)
            return sound_from_pcm(bytes(pcm))
        if AUDIO_AVAILABLE and pygame.mixer.get_init():
            try:
                self.SFX_CLICK = generate_tone(frequency=800, duration_ms=60, volume=0.5, waveform='square')
                self.SFX_ATTACK = generate_tone(frequency=200, duration_ms=120, volume=0.5, waveform='square')
                self.SFX_MAGIC = generate_tone(frequency=1200, duration_ms=200, volume=0.5, waveform='sine')
                self.SFX_ITEM = generate_tone(frequency=1000, duration_ms=80, volume=0.5, waveform='sine')
                self.SFX_LEVELUP = generate_tone(frequency=1500, duration_ms=300, volume=0.5, waveform='sine')
                self.SFX_GAMEOVER = generate_tone(frequency=100, duration_ms=400, volume=0.5, waveform='sine')
                self.SFX_VICTORY = generate_tone(frequency=900, duration_ms=500, volume=0.5, waveform='sine')
                self.SFX_ARROW = generate_tone(frequency=600, duration_ms=40, volume=0.4, waveform='square')
                self.SFX_ENTER = generate_tone(frequency=1200, duration_ms=80, volume=0.5, waveform='sine')
            except Exception as e:
                print("[WARNING] Could not generate sound effects:", e)
                self.SFX_CLICK = self.SFX_ATTACK = self.SFX_MAGIC = self.SFX_ITEM = self.SFX_LEVELUP = self.SFX_GAMEOVER = self.SFX_VICTORY = None
                self.SFX_ARROW = self.SFX_ENTER = None
        else:
            self.SFX_CLICK = self.SFX_ATTACK = self.SFX_MAGIC = self.SFX_ITEM = self.SFX_LEVELUP = self.SFX_GAMEOVER = self.SFX_VICTORY = None
            self.SFX_ARROW = self.SFX_ENTER = None
        
        # ========================================
        # MUSIC SYSTEM - Procedural Chiptune Generation
        # ========================================
        # Dynamic music that changes based on game state and area
        self.music = MusicSystem()
        
        # BEGINNER NOTE:
        # `show_pause_menu` is a shared in-game menu for both keyboard and
        # Android players. It exposes Log / Map / Save / Load as clickable
        # buttons so the game no longer depends on a hardware keyboard.
        self.show_pause_menu = False
        self.pause_menu_index = 0
        self.pause_menu_buttons = []
        self.android_touch_enabled = is_touch_ui_runtime()

    def apply_world_item(self, item):
        profile = ITEM_PROFILES.get(item.type, ITEM_PROFILES["health"])
        amount = profile["amount"]
        effect = profile["effect"]
        messages = []

        if effect == "restore_health":
            before = self.player.health
            self.player.health = min(self.player.max_health, self.player.health + amount)
            restored = self.player.health - before
            if restored:
                messages.append(profile["message"].format(amount=restored))
        elif effect == "restore_mana":
            before = self.player.mana
            self.player.mana = min(self.player.max_mana, self.player.mana + amount)
            restored = self.player.mana - before
            if restored:
                messages.append(profile["message"].format(amount=restored))
        elif effect == "raise_strength":
            self.player.strength += amount
            messages.append(profile["message"].format(amount=amount))
        elif effect == "raise_defense":
            self.player.defense += amount
            messages.append(profile["message"].format(amount=amount))

        if profile.get("battle_usable"):
            added = self.player.add_inventory_item(item.type)
            if added:
                messages.append(profile["stored_message"])
            elif not messages:
                messages.append(f"{profile['label']} pouch is full.")

        self.pickup_message = " ".join(messages) if messages else profile["message"].format(amount=amount)
        self.pickup_message_timer = 120
        for _ in range(18):
            x = random.randint(self.player.x, self.player.x + PLAYER_SIZE)
            y = random.randint(self.player.y, self.player.y + PLAYER_SIZE)
            self.particle_system.add_particle(
                x, y, profile["color"],
                (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)),
                3, 30
            )

    def set_town_service_message(self, message):
        self.town_service_message = message
        self.town_service_message_timer = 180

    def set_button(self, button, text, rect=None):
        if rect is not None:
            button.rect = rect
        if button.text != text:
            button.text = text
        button.text_surf = font_medium.render(button.text, True, TEXT_COLOR)
        button.text_rect = button.text_surf.get_rect(center=button.rect.center)

    def reset_menu_buttons(self):
        self.set_button(self.start_button, "START QUEST", pygame.Rect(SCREEN_WIDTH//2 - 120, 395, 240, 50))
        self.set_button(self.load_button, "LOAD SAVE", pygame.Rect(SCREEN_WIDTH//2 - 120, 455, 240, 50))
        self.set_button(self.update_button, "UPDATE APP", pygame.Rect(SCREEN_WIDTH//2 - 120, 515, 240, 50))
        self.set_button(self.quit_button, "QUIT", pygame.Rect(SCREEN_WIDTH//2 - 120, 575, 240, 50))

    def start_menu_buttons(self):
        return [self.start_button, self.load_button, self.update_button, self.quit_button]

    def get_title_dragon_boss_level(self):
        """Return the boss-level palette the title dragon should preview.

        Beginner note:
            Before a save is loaded, the title screen slowly cycles through
            dragon palettes so players can see the progression. After a save is
            loaded, it previews the next boss level from the player's progress.
        """
        if self.player:
            return get_next_boss_level(self.player.level, self.player.last_boss_level)
        return 1 + ((pygame.time.get_ticks() // 1800) % len(DRAGON_BOSS_COLORS))

    def draw_title_dragon_progress_badge(self, screen):
        """Draw a small label for the current title dragon palette."""
        boss_level = self.get_title_dragon_boss_level()
        profile = get_boss_profile(boss_level)
        _, fire_color = DRAGON_BOSS_COLORS[(boss_level - 1) % len(DRAGON_BOSS_COLORS)]
        if self.player:
            label = f"Next dragon: {profile['name']}"
        else:
            label = f"Dragon progression preview: {profile['name']}"
        text = render_fitted_text(label, (255, 235, 170), 315, (font_tiny,))
        panel = pygame.Rect(SCREEN_WIDTH - 370, 204, 350, 30)
        pygame.draw.rect(screen, UI_BG, panel, border_radius=6)
        pygame.draw.rect(screen, fire_color, panel, 2, border_radius=6)
        screen.blit(text, (panel.centerx - text.get_width() // 2, panel.y + 7))

    def set_selected_buttons(self, buttons, selected_index):
        for index, button in enumerate(buttons):
            button.selected = index == selected_index

    def move_menu_selection(self, attr_name, count, direction):
        setattr(self, attr_name, (getattr(self, attr_name) + direction) % count)
        if self.SFX_ARROW:
            self.SFX_ARROW.play()

    def choose_hero(self, hero_type):
        if self.SFX_CLICK:
            self.SFX_CLICK.play()
        self.player = Character(hero_type)
        self.state = "overworld"
        self.start_game()

    def activate_start_menu_selection(self):
        """Run whichever title-screen option is selected.

        Beginner note:
            `start_menu_index` matches the list returned by start_menu_buttons():
            0 START QUEST, 1 LOAD SAVE, 2 UPDATE APP, 3 QUIT.
        """
        if self.SFX_CLICK:
            self.SFX_CLICK.play()
        if self.start_menu_index == 0:
            self.state = "opening_cutscene"
            self.opening_cutscene = OpeningCutscene()
            return True
        if self.start_menu_index == 1:
            self.load_saved_game()
            return True
        if self.start_menu_index == 2:
            self.open_update_link()
            return True
        return False

    def check_for_updates(self):
        """Check GitHub for a newer Android APK version.

        Beginner note:
            The latest number comes from buildozer.spec on the main branch.
            If latest_version is bigger than APP_NUMERIC_VERSION, the title
            screen says a new APK is available. The player still has to press
            UPDATE APP to open the download.
        """
        try:
            latest_version = fetch_latest_android_numeric_version()
        except Exception as exc:
            self.update_status = "Update check unavailable. APK link still works."
            self.update_available = False
            self.update_check_done = True
            print(f"[WARN] Update check failed: {exc}")
            return

        self.update_available = latest_version > APP_NUMERIC_VERSION
        if self.update_available:
            self.update_status = "New Android APK available."
        else:
            self.update_status = f"Android app is current: v{APP_VERSION}."
        self.update_check_done = True

    def open_update_link(self):
        """Open the APK download link from the title screen."""
        opened_target = open_android_update_download()
        if opened_target in ("apk", "compat"):
            self.update_status = "Opened APK download. Tap the downloaded APK to install."
        elif opened_target == "github_app":
            self.update_status = "Opened GitHub app release. Tap the APK asset to download."
        elif opened_target == "release":
            self.update_status = "Opened release page. Tap the APK asset to download."
        else:
            self.update_status = "Could not open update link. Open GitHub release android-latest."

    def activate_character_menu_selection(self):
        if self.character_menu_index == 0:
            self.choose_hero("Warrior")
        elif self.character_menu_index == 1:
            self.choose_hero("Mage")
        elif self.character_menu_index == 2:
            self.choose_hero("Rogue")
        else:
            if self.SFX_CLICK:
                self.SFX_CLICK.play()
            self.state = "start_menu"

    def activate_end_menu_selection(self):
        if self.SFX_CLICK:
            self.SFX_CLICK.play()
        if self.end_menu_index == 0:
            self.state = "character_select"
            self.character_menu_index = 0
        else:
            self.state = "start_menu"

    def build_pause_menu_entries(self):
        """Return the clickable actions shown in the shared pause menu.

        Beginner note:
            Each tuple is `(command_key, label_text)`.
            The command key is the internal action name.
            The label text is what the player sees on the button.
        """
        entries = [
            ("resume", "RESUME"),
            ("journal", "LOG"),
        ]
        if self.state == "overworld":
            entries.append(("map", "WORLD MAP"))
        entries.append(("inventory", "INVENTORY"))
        entries.extend(
            [
                ("save", "SAVE GAME"),
                ("load", "LOAD GAME"),
            ]
        )
        if self.state == "interior":
            entries.append(("leave_interior", "LEAVE BUILDING"))
        entries.append(("main_menu", "MAIN MENU"))
        return entries

    def rebuild_pause_menu_buttons(self):
        """Recreate pause-menu buttons after the available commands change."""
        entries = self.build_pause_menu_entries()
        button_width = 320
        button_height = 52
        gap = 12
        total_height = len(entries) * button_height + max(0, len(entries) - 1) * gap
        start_y = max(186, SCREEN_HEIGHT // 2 - total_height // 2)
        self.pause_menu_buttons = []
        for index, (command, label) in enumerate(entries):
            button = Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + index * (button_height + gap),
                button_width,
                button_height,
                label,
                color=(100, 140, 185),
            )
            button.command = command
            self.pause_menu_buttons.append(button)
        if self.pause_menu_buttons:
            self.pause_menu_index = max(0, min(self.pause_menu_index, len(self.pause_menu_buttons) - 1))
        else:
            self.pause_menu_index = 0

    def close_pause_menu(self, play_sound=True):
        """Hide the shared pause menu overlay."""
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        if play_sound and self.SFX_CLICK:
            self.SFX_CLICK.play()

    def toggle_pause_menu(self):
        """Open or close the shared pause menu during active gameplay."""
        if self.state not in ["overworld", "interior"] or not self.player:
            return
        self.show_pause_menu = not self.show_pause_menu
        if self.show_pause_menu:
            self.show_journal = False
            self.show_inventory = False
            self.show_world_map = False
            self.interior_service_menu_open = False
            self.interior_service_menu_buttons = []
            self.rebuild_pause_menu_buttons()
        else:
            self.pause_menu_buttons = []
        if self.SFX_CLICK:
            self.SFX_CLICK.play()

    def activate_pause_menu_command(self, command):
        """Run one pause-menu command and keep the branching in one place."""
        if command == "resume":
            self.close_pause_menu(play_sound=True)
            return

        if command == "journal":
            self.show_journal = True
            self.show_inventory = False
            self.show_world_map = False
            self.close_pause_menu(play_sound=True)
            return

        if command == "inventory":
            self.show_inventory = True
            self.show_journal = False
            self.show_world_map = False
            self.inventory_slot_index = 0
            self.inventory_item_index = 0
            self.inventory_message = "Select gear with arrows. OK equips. USE unequips."
            self.close_pause_menu(play_sound=True)
            return

        if command == "map":
            self.show_world_map = True
            self.show_journal = False
            self.show_inventory = False
            self.close_pause_menu(play_sound=True)
            return

        if command == "save":
            self.close_pause_menu(play_sound=False)
            self.save_current_game()
            return

        if command == "load":
            self.close_pause_menu(play_sound=False)
            self.load_saved_game()
            return

        if command == "leave_interior":
            self.close_pause_menu(play_sound=False)
            self.exit_town_interior()
            return

        if command == "main_menu":
            self.close_pause_menu(play_sound=False)
            self.show_journal = False
            self.show_inventory = False
            self.show_world_map = False
            self.state = "start_menu"
            if self.SFX_CLICK:
                self.SFX_CLICK.play()
            return

    def activate_pause_menu_selection(self):
        """Run the currently highlighted pause-menu button."""
        if not self.pause_menu_buttons:
            return
        command = getattr(self.pause_menu_buttons[self.pause_menu_index], "command", None)
        if command:
            self.activate_pause_menu_command(command)

    def get_active_inventory_slot(self):
        """Return the currently selected equipment slot in the Inventory screen."""
        return self.inventory_slots[self.inventory_slot_index % len(self.inventory_slots)]

    def get_inventory_slot_items(self):
        """Return owned gear keys for the currently selected slot."""
        if not self.player:
            return []
        return self.player.get_owned_equipment_for_slot(self.get_active_inventory_slot())

    def move_inventory_slot(self, direction):
        """Move left/right between weapon, armor, and charm slots."""
        self.inventory_slot_index = (self.inventory_slot_index + direction) % len(self.inventory_slots)
        self.inventory_item_index = 0
        self.inventory_message = f"Viewing {get_equipment_slot_label(self.get_active_inventory_slot())} gear."
        if self.SFX_ARROW:
            self.SFX_ARROW.play()

    def move_inventory_selection(self, direction):
        """Move up/down through owned gear for the current slot."""
        slot_items = self.get_inventory_slot_items()
        if not slot_items:
            self.inventory_item_index = 0
            self.inventory_message = "No owned gear in this slot yet."
            return
        self.inventory_item_index = (self.inventory_item_index + direction) % len(slot_items)
        if self.SFX_ARROW:
            self.SFX_ARROW.play()

    def equip_inventory_selection(self):
        """Equip the selected owned gear item from the Inventory screen."""
        slot_items = self.get_inventory_slot_items()
        if not self.player or not slot_items:
            self.inventory_message = "No owned gear in this slot yet."
            return False
        self.inventory_item_index = max(0, min(self.inventory_item_index, len(slot_items) - 1))
        item_key = slot_items[self.inventory_item_index]
        profile = get_equipment_item(item_key) or {}
        if self.player.equip_owned_item(item_key):
            self.inventory_message = f"Equipped {profile.get('label', item_key)}."
            if self.SFX_ITEM:
                self.SFX_ITEM.play()
            return True
        self.inventory_message = "That gear is not owned yet."
        return False

    def unequip_inventory_slot(self):
        """Unequip the current slot from the Inventory screen."""
        if not self.player:
            return False
        slot = self.get_active_inventory_slot()
        old_key = self.player.equipment.get(slot)
        old_profile = get_equipment_item(old_key) if old_key else None
        if self.player.unequip_slot(slot):
            label = old_profile.get("label", "gear") if old_profile else "gear"
            self.inventory_message = f"Unequipped {label}."
            if self.SFX_CLICK:
                self.SFX_CLICK.play()
            return True
        self.inventory_message = f"No {get_equipment_slot_label(slot).lower()} equipped."
        return False

    def handle_android_touch_command(self, command):
        """Run a touch button command.

        Touch buttons mostly reuse keyboard actions by posting synthetic key
        events. That keeps one action path in the main game loop.
        """
        if command == "toggle_pause_menu":
            self.toggle_pause_menu()
            return True

        key = key_for_action(command)
        if key is None:
            return False

        fake_event = pygame.event.Event(pygame.KEYDOWN, key=key)
        pygame.event.post(fake_event)
        return True

    def save_current_game(self):
        if not self.player:
            self.set_town_service_message("No active hero to save.")
            return False
        try:
            path = save_game_state(self)
        except Exception as exc:
            self.set_town_service_message(f"Save failed: {exc}")
            return False
        self.set_town_service_message(f"Saved game to {path.name}.")
        if self.SFX_ITEM:
            self.SFX_ITEM.play()
        return True

    def load_saved_game(self):
        try:
            data = load_game_state()
        except FileNotFoundError:
            self.set_town_service_message(f"No save found at {DEFAULT_SAVE_PATH}.")
            return False
        except Exception as exc:
            self.set_town_service_message(f"Load failed: {exc}")
            return False

        player_data = data["player"]
        self.player = Character(player_data.get("type", "Warrior"))
        for field in (
            "level", "exp", "exp_to_level", "max_health", "health",
            "max_mana", "mana", "strength", "defense", "speed",
            "x", "y", "kills", "items_collected", "last_boss_level",
            "boss_cooldown", "special_unlocked",
        ):
            if field in player_data:
                setattr(self.player, field, player_data[field])
        self.player.inventory = dict(player_data.get("inventory", self.player.inventory))
        self.player.story_items = dict(player_data.get("story_items", getattr(self.player, "story_items", {})))
        loaded_equipment = player_data.get("equipment")
        if isinstance(loaded_equipment, dict):
            self.player.equipment.update(
                {
                    str(slot): item_key if item_key else None
                    for slot, item_key in loaded_equipment.items()
                    if slot in {"weapon", "armor", "accessory"}
                }
            )
        loaded_owned_equipment = player_data.get("owned_equipment")
        if isinstance(loaded_owned_equipment, dict):
            self.player.owned_equipment = {
                str(item_key): int(count)
                for item_key, count in loaded_owned_equipment.items()
            }
        self.player.town_service_claims = {
            (claim[0], claim[1])
            for claim in player_data.get("town_service_claims", [])
            if isinstance(claim, list) and len(claim) == 2
        }
        self.player.just_leveled_up = False

        self.score = data.get("score", 0)
        self.game_time = data.get("game_time", 0)
        self.boss_defeated = data.get("boss_defeated", False)
        town_data = data.get("town", {})
        self.town_reputation = town_data.get("reputation", 0)
        self.completed_town_errands = set(town_data.get("completed_errands", []))
        self.completed_resident_errands = set(town_data.get("completed_resident_errands", []))
        self.inspected_town_details = {
            (detail[0], detail[1])
            for detail in town_data.get("inspected_details", [])
            if isinstance(detail, list) and len(detail) == 2
        }
        story_data = data.get("story", {})
        self.seen_story_dialogues = set(story_data.get("seen_dialogues", []))
        self.claimed_story_rewards = set(story_data.get("claimed_rewards", []))
        self.story_enemy_defeats = {
            str(enemy_type): int(count)
            for enemy_type, count in story_data.get("enemy_defeats", {}).items()
        }
        self.active_story_dialogue_key = None
        self.active_story_dialogue = None
        self.active_story_lines = []
        self.active_story_line_index = 0
        self.active_story_repeat = False
        self.boss_battle_triggered = False
        self.battle_screen = None
        self.current_interior = None
        self.current_interior_service = None
        self.interior_return_position = None
        self.show_world_map = False
        self.show_journal = False
        self.show_inventory = False
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.interior_service_menu_open = False
        self.interior_service_menu_buttons = []
        self.npc_dialogue_index = 0
        self.town_resident_dialogue_index = {}
        self.world_map = WorldMap()

        for area in self.world_map.areas.values():
            area.visited = False
        for area_x, area_y in data.get("world", {}).get("visited_areas", []):
            area = self.world_map.areas.get((area_x, area_y))
            if area:
                area.visited = True

        area_x, area_y = data.get("world", {}).get("current_area", [1, 1])
        self.world_map.current_area_x = max(0, min(WORLD_SIZE - 1, int(area_x)))
        self.world_map.current_area_y = max(0, min(WORLD_SIZE - 1, int(area_y)))
        self.spawn_story_enemies()
        current_area = self.world_map.get_current_area()
        if current_area:
            current_area.visited = True
            self.enemies = current_area.enemies
            self.items = current_area.items
        else:
            self.enemies = []
            self.items = []
        self.world_map.update_camera(self.player.x, self.player.y)
        self.state = "overworld"
        self.set_town_service_message("Save loaded.")
        if self.SFX_ENTER:
            self.SFX_ENTER.play()
        return True

    def get_player_progression_status(self):
        if not self.player:
            return None
        return get_progression_status(
            self.player.level,
            self.player.last_boss_level,
            self.player.boss_cooldown,
            self.boss_defeated,
        )

    def apply_town_reward(self, reward):
        messages = []
        exp = reward.get("exp", 0)
        score = reward.get("score", 0)
        reputation = reward.get("reputation", 0)

        if exp:
            self.player.gain_exp(exp)
            messages.append(f"{exp} EXP")
        if score:
            self.score += score
            messages.append(f"{score} score")
        if reputation:
            self.town_reputation += reputation
            messages.append(f"+{reputation} town rep")

        for item_type, amount in reward.get("items", {}).items():
            added = self.player.add_inventory_item(item_type, amount)
            if added:
                messages.append(f"{item_type} x{added}")

        for item_key, amount in reward.get("story_items", {}).items():
            self.player.add_story_item(item_key, int(amount))
            item = get_story_reward_item(item_key) or {}
            messages.append(f"{item.get('label', item_key.replace('_', ' ').title())} keepsake")

        # BEGINNER NOTE: Town rewards can now grant owned equipment too.
        # Gear does not auto-equip here because players should choose loadouts
        # from Inventory. Story rewards can still auto-equip when needed.
        equipment_keys = list(reward.get("equipment", ()))
        class_equipment = reward.get("equipment_by_class", {})
        equipment_keys.extend(class_equipment.get(self.player.type, ()))
        for equipment_key in equipment_keys:
            if self.player.add_equipment_item(equipment_key, auto_equip=False):
                profile = get_equipment_item(equipment_key) or {}
                messages.append(f"{profile.get('label', equipment_key)} gear")

        return ", ".join(messages)

    def start_story_dialogue(self, dialogue_key, repeat=False):
        """Begin a story dialogue overlay.

        Beginner note:
            This method opens the conversation box.

            It does not decide *when* a conversation should happen. Other code
            decides that, then sends this method a `dialogue_key`. A dialogue key
            is just a short nickname, such as "plains_ranger_waymarks", used to
            find the matching conversation in game_data/story.py.

            `repeat=True` means the player has already seen the full scene and
            is talking to the same person again. Repeat dialogue does not give
            rewards again.
        """
        # STEP 1: Look up the conversation data by its nickname.
        dialogue = get_story_dialogue(dialogue_key)
        if not dialogue:
            return False

        # STEP 2: If the player already finished this conversation, block the
        # first-time version. The caller must ask for repeat dialogue instead.
        already_seen = dialogue_key in self.seen_story_dialogues
        if already_seen and not repeat:
            return False

        # STEP 3: Choose which words to show. First-time talks use `lines`.
        # Later talks use `repeat_lines` when those exist.
        if repeat and dialogue.get("repeat_lines"):
            lines = list(dialogue["repeat_lines"])
        else:
            lines = list(dialogue.get("lines", ()))
        if not lines:
            return False

        # STEP 4: Store the active conversation on the Game object. The draw
        # method reads these values every frame until the conversation closes.
        self.active_story_dialogue_key = dialogue_key
        self.active_story_dialogue = dialogue
        self.active_story_lines = lines
        self.active_story_line_index = 0
        self.active_story_repeat = bool(repeat)

        # STEP 5: Hide other overlays. This prevents the map, inventory, pause
        # menu, or log from covering the story box.
        self.show_world_map = False
        self.show_journal = False
        self.show_inventory = False
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        if self.SFX_ENTER:
            self.SFX_ENTER.play()
        return True

    def advance_story_dialogue(self):
        """Move to the next story line, or close the box after the last line."""
        if not self.active_story_dialogue:
            return False

        # Move the page counter forward by one line.
        self.active_story_line_index += 1

        # If there are still lines left, keep the box open.
        if self.active_story_line_index < len(self.active_story_lines):
            if self.SFX_CLICK:
                self.SFX_CLICK.play()
            return True

        # If the player advanced past the final line, close the conversation.
        self.finish_story_dialogue()
        return True

    def finish_story_dialogue(self):
        """Close the story dialogue and apply any first-time reward."""
        # Save the active conversation values before clearing them. The reward
        # code still needs to know which conversation just ended.
        dialogue_key = self.active_story_dialogue_key
        dialogue = self.active_story_dialogue
        repeat = self.active_story_repeat

        # Clear the active conversation. After this, draw_story_dialogue() has
        # nothing to draw and normal gameplay can continue.
        self.active_story_dialogue_key = None
        self.active_story_dialogue = None
        self.active_story_lines = []
        self.active_story_line_index = 0
        self.active_story_repeat = False

        if not dialogue_key or not dialogue or repeat:
            return

        # Mark this conversation as completed so future talks use repeat lines.
        self.seen_story_dialogues.add(dialogue_key)
        self.apply_story_reward(dialogue_key, dialogue)

    def apply_story_reward(self, dialogue_key, dialogue):
        """Apply a one-time story reward such as the Lion Sage blessing.

        Beginner note:
            Rewards are written beside the dialogue in game_data/story.py because
            the reward belongs to that story moment.

            This method turns those written reward values into actual player
            changes: experience, score, supplies, keepsakes, gear, or SPECIAL.
        """
        # If the dialogue has no reward, or this reward was already claimed,
        # leave immediately. This is what prevents farming the same side-story
        # keepsake over and over.
        reward = dialogue.get("reward")
        if not reward or dialogue_key in self.claimed_story_rewards or not self.player:
            return

        self.claimed_story_rewards.add(dialogue_key)
        exp_gain = int(reward.get("exp", 0))
        health_gain = int(reward.get("health", 0))
        mana_gain = int(reward.get("mana", 0))
        level_before = self.player.level

        # Experience can level the player up, so it is applied before checking
        # the special Lion Sage boss-cooldown rule below.
        if exp_gain:
            self.player.gain_exp(exp_gain)

        # Direct HP/MP restoration is supported for special scenes, even though
        # most side-story rewards use potion items instead.
        if health_gain:
            self.player.health = min(self.player.max_health, self.player.health + health_gain)
        if mana_gain:
            self.player.mana = min(self.player.max_mana, self.player.mana + mana_gain)

        # Score and reputation are simple counters on the Game object.
        if reward.get("score"):
            self.score += int(reward["score"])
        if reward.get("reputation"):
            self.town_reputation += int(reward["reputation"])

        # Consumable supplies go into the normal potion/item inventory.
        for item_type, amount in reward.get("items", {}).items():
            self.player.add_inventory_item(item_type, int(amount))

        # Keepsakes are permanent story souvenirs shown in the Inventory trophy
        # panel. They are separate from consumable potions and wearable gear.
        for item_key, amount in reward.get("story_items", {}).items():
            self.player.add_story_item(item_key, int(amount))

        # Equipment rewards use gear keys from game_data/equipment.py.
        for equipment_key in reward.get("equipment", ()):
            self.player.add_equipment_item(equipment_key, auto_equip=True)

        # This is how Lion Sage enables the SPECIAL battle button.
        if reward.get("unlock_special"):
            self.player.special_unlocked = True
        if reward.get("calm_boss_pressure") and self.player.level > level_before:
            # BEGINNER NOTE: Story training can grant one or more levels. We do
            # not want the automatic dragon-boss trigger to fire the moment the
            # Lion Sage dialogue closes, because the Sage is also pointing the
            # player toward Ghost Face. Mark the hero as recovering so the next
            # boss waits until the player trains again.
            self.player.just_leveled_up = False
            self.player.boss_cooldown = True

        message_template = reward.get("message", "Story reward received.")
        self.set_town_service_message(
            message_template.format(exp=exp_gain, health=health_gain, mana=mana_gain)
        )
        if self.SFX_LEVELUP:
            self.SFX_LEVELUP.play()

    def apply_story_enemy_reward(self, enemy):
        """Apply first-clear or repeat rewards for respawning story enemies.

        Beginner note:
            Story enemies such as Ghost Face are allowed to respawn. The defeat
            count only decides which reward table is used: first-clear rewards
            can grant trophies, while repeat clears give smaller farm rewards.
        """
        enemy_type = getattr(enemy, "enemy_type", None)
        defeat_count = self.story_enemy_defeats.get(enemy_type, 0)
        reward = get_story_enemy_reward(enemy_type, repeat=defeat_count > 0)
        if not reward:
            return False

        self.story_enemy_defeats[enemy_type] = defeat_count + 1
        exp_gain = int(reward.get("exp", 0))
        score_gain = int(reward.get("score", 0))
        if exp_gain:
            self.player.gain_exp(exp_gain)
        if score_gain:
            self.score += score_gain
        for item_type, amount in reward.get("items", {}).items():
            self.player.add_inventory_item(item_type, int(amount))
        for item_key, amount in reward.get("story_items", {}).items():
            self.player.add_story_item(item_key, int(amount))
        for equipment_key in reward.get("equipment", ()):
            self.player.add_equipment_item(equipment_key, auto_equip=True)

        message = reward.get("message", "Story enemy reward received.")
        self.set_town_service_message(message.format(exp=exp_gain, score=score_gain))
        return True

    def trigger_area_story_dialogue(self, current_area):
        """Start one-shot dialogue when entering a special world area."""
        if not current_area or self.active_story_dialogue:
            return False

        # This only handles automatic area-entry scenes. Side-story NPCs use
        # `trigger: "talk_npc"`, so they wait until the player walks up and talks.
        for dialogue_key, dialogue in get_story_dialogues_for_area(current_area.area_x, current_area.area_y):
            if dialogue.get("trigger") != "enter_area":
                continue

            # A conversation key in `seen_story_dialogues` means the player has
            # already finished that first-time scene.
            if dialogue_key not in self.seen_story_dialogues:
                return self.start_story_dialogue(dialogue_key)
        return False

    def get_story_npc_world_position(self, current_area, npc):
        """Convert an NPC's local area position into world coordinates."""
        # Story data stores positions inside one map tile because that is easier
        # for humans to edit. The game world is larger than one screen, so we add
        # the tile's top-left world position to get the real world position.
        area_world_x, area_world_y = current_area.get_world_position()
        local_x, local_y = npc["local_position"]
        return area_world_x + local_x, area_world_y + local_y

    def get_nearby_story_npc(self, current_area):
        """Return the friendly story NPC close enough for ENTER interaction."""
        if not current_area or not self.player:
            return None

        # Use the center of the player sprite, not its top-left corner, so the
        # talk radius feels natural around the visible character.
        player_center = (self.player.x + PLAYER_SIZE // 2, self.player.y + PLAYER_SIZE // 2)

        # Only check NPCs that belong to the same map tile the player is in.
        for npc_key, npc in get_story_npcs_for_area(current_area.area_x, current_area.area_y):
            npc_x, npc_y = self.get_story_npc_world_position(current_area, npc)
            distance = math.hypot(player_center[0] - npc_x, player_center[1] - npc_y)
            # A slightly larger talk radius makes friendly NPCs easier to use on
            # touch screens and on the scaled Android APK.
            if distance <= 160:
                return npc_key, npc
        return None

    def get_nearby_town_resident(self, current_area):
        """Return the outdoor town resident close enough for interaction."""
        if not current_area or current_area.area_type != "town" or not self.player:
            return None

        area_world_x, area_world_y = current_area.get_world_position()
        player_center = (
            self.player.x - area_world_x + PLAYER_SIZE // 2,
            self.player.y - area_world_y + PLAYER_SIZE // 2,
        )
        for resident_key, resident in iter_town_residents():
            resident_x, resident_y = resident["local_position"]
            distance = math.hypot(player_center[0] - resident_x, player_center[1] - resident_y)
            if distance <= resident.get("interact_radius", 82):
                return resident_key, resident
        return None

    def draw_town_population(self, screen, current_area):
        """Draw outdoor town residents and their nearby talk prompt."""
        if not current_area or current_area.area_type != "town":
            return
        nearby = self.get_nearby_town_resident(current_area)
        nearby_key = nearby[0] if nearby else None
        draw_town_residents(
            screen,
            iter_town_residents(),
            nearby_key,
            self.completed_resident_errands,
            self.game_time,
            font_tiny,
            UI_BG,
        )

    def draw_town_service_marker(self, screen, current_area):
        """Show town doorway markers and highlight the currently usable one.

        Beginner note:
            The town has buildings close together, so this marker is the visual
            promise that pressing OK/USE will enter that exact building. The
            rectangle comes from `WorldArea.get_nearby_town_service`, which is
            also the method used by the actual interaction code.
        """
        if (
            not current_area
            or current_area.area_type != "town"
            or not self.player
            or self.active_story_dialogue
            or self.show_world_map
            or self.show_journal
            or self.show_inventory
            or self.show_pause_menu
        ):
            return
        if (
            current_area.cutscene_active
            and current_area.cutscene_phase < 2
            and current_area.guard
        ):
            return

        service = current_area.get_nearby_town_service(self.player.x, self.player.y)
        active_entry_rect = service.get("entry_rect") if service else None

        # Draw a quiet marker for every enterable building first. The active
        # doorway is drawn again below with the larger prompt.
        for building in current_area.buildings:
            service_type = building.get("type")
            service_info = TOWN_SERVICES.get(service_type)
            if not service_info:
                continue
            entry = current_area.get_building_entry_rect(building)
            active = active_entry_rect and entry == active_entry_rect
            status = get_service_completion_label(service_type, self.completed_town_errands)
            marker_color = (255, 224, 104) if active else ((124, 202, 132) if status == "DONE" else (128, 154, 172))
            label_color = (255, 246, 174) if active else (188, 205, 214)
            pygame.draw.rect(screen, marker_color, entry, 2 if active else 1, border_radius=6)
            marker_x = entry.centerx
            marker_y = max(34, entry.y - 17)
            pygame.draw.circle(screen, marker_color, (marker_x, marker_y), 6 if active else 4)
            if not active:
                label = render_fitted_text(get_service_map_label(service_type), label_color, 92, (font_tiny,))
                label_panel = pygame.Rect(
                    max(8, min(SCREEN_WIDTH - label.get_width() - 18, marker_x - label.get_width() // 2 - 9)),
                    max(8, marker_y - 27),
                    label.get_width() + 18,
                    22,
                )
                pygame.draw.rect(screen, UI_BG, label_panel, border_radius=5)
                pygame.draw.rect(screen, marker_color, label_panel, 1, border_radius=5)
                screen.blit(label, (label_panel.x + 9, label_panel.y + 4))

        if not service:
            return

        entry_rect = service.get("entry_rect")
        if not entry_rect:
            return

        pulse = int(math.sin(self.game_time * 0.12) * 3)
        marker_x = entry_rect.centerx
        marker_y = max(34, entry_rect.y - 22)
        marker_color = (255, 224, 104)
        prompt_color = (255, 246, 174)
        service_type = service["type"]
        status = get_service_completion_label(service_type, self.completed_town_errands)
        role = service.get("role", "Town Service")
        purpose = service.get("purpose", "Town service.")

        # Outline the exact doorway instead of the larger tap zone. This keeps
        # the town readable and avoids making neighboring buildings look active.
        pygame.draw.rect(screen, marker_color, entry_rect, 2, border_radius=6)
        pygame.draw.circle(screen, marker_color, (marker_x, marker_y), 12 + pulse)
        pygame.draw.circle(screen, UI_BG, (marker_x, marker_y), 6)
        pygame.draw.polygon(
            screen,
            marker_color,
            [
                (marker_x, marker_y + 18 + pulse),
                (marker_x - 8, marker_y + 7 + pulse),
                (marker_x + 8, marker_y + 7 + pulse),
            ],
        )

        title = render_fitted_text(f"{service['name']} [{status}]", prompt_color, 292, (font_tiny,))
        detail = render_fitted_text(purpose, (220, 225, 220), 292, (font_tiny,))
        subtitle = render_fitted_text(f"{role} - OK/USE to enter", (196, 220, 235), 292, (font_tiny,))
        panel_w = max(title.get_width(), detail.get_width(), subtitle.get_width()) + 24
        panel_x = max(12, min(SCREEN_WIDTH - panel_w - 12, marker_x - panel_w // 2))
        panel_y = max(12, marker_y - 64)
        panel = pygame.Rect(panel_x, panel_y, panel_w, 66)
        pygame.draw.rect(screen, UI_BG, panel, border_radius=6)
        pygame.draw.rect(screen, marker_color, panel, 2, border_radius=6)
        screen.blit(title, (panel.x + 12, panel.y + 7))
        screen.blit(detail, (panel.x + 12, panel.y + 27))
        screen.blit(subtitle, (panel.x + 12, panel.y + 47))

    def talk_to_town_resident(self, resident_key, resident):
        """Talk to an outdoor resident and complete their one-time errand.

        Beginner note:
            Resident dialogue data lives in `game_data/town_population.py`.
            This method only decides whether to grant a reward, show a locked
            message, or rotate a normal dialogue line.
        """
        quest = get_town_resident_quest(resident)
        quest_key = resident.get("quest_key")
        if quest and quest_key not in self.completed_resident_errands:
            available, reason = is_town_resident_quest_available(
                quest,
                self.town_reputation,
                self.completed_town_errands,
            )
            if available:
                self.completed_resident_errands.add(quest_key)
                reward_text = self.apply_town_reward(quest.get("reward", {}))
                message_template = quest.get("complete_message", "{name}: Errand complete. ({reward})")
                self.set_town_service_message(
                    message_template.format(name=resident["name"], reward=reward_text or "thanks")
                )
                if self.SFX_ITEM:
                    self.SFX_ITEM.play()
                return True
            locked_message = quest.get("locked_message")
            if locked_message:
                self.set_town_service_message(locked_message.format(name=resident["name"], reason=reason))
            else:
                self.set_town_service_message(f"{resident['name']}: {reason}")
            return True

        lines = resident.get("completed_lines" if quest_key in self.completed_resident_errands else "lines", ())
        if not lines:
            self.set_town_service_message(f"{resident['name']}: Safe roads.")
            return True

        line_index = self.town_resident_dialogue_index.get(resident_key, 0)
        self.town_resident_dialogue_index[resident_key] = line_index + 1
        self.set_town_service_message(lines[line_index % len(lines)])
        if self.SFX_CLICK:
            self.SFX_CLICK.play()
        return True

    def draw_story_npcs(self, screen, current_area):
        """Draw friendly main-story and side-story NPCs on the overworld map."""
        if not current_area:
            return

        # First find the nearby NPC, if any. Drawing uses this to highlight that
        # person's name and show the interaction prompt.
        nearby = self.get_nearby_story_npc(current_area)
        nearby_key = nearby[0] if nearby else None

        for npc_key, npc in get_story_npcs_for_area(current_area.area_x, current_area.area_y):
            # STEP 1: Convert the NPC's map-tile position into camera/screen
            # coordinates. World position is where the person is in the full map.
            # Screen position is where the camera should draw them this frame.
            world_x, world_y = self.get_story_npc_world_position(current_area, npc)
            screen_x, screen_y = self.world_map.world_to_screen(world_x, world_y)

            # STEP 2: Load the imported PNG for this NPC. If the file is missing,
            # the fallback circles below still draw a simple placeholder.
            sprite_path = get_story_sprite_path(npc.get("sprite_key"))
            sprite = load_sprite_by_height(sprite_path, npc.get("sprite_height", 120)) if sprite_path else None
            dialogue_key = npc.get("dialogue_key", npc_key)

            # STEP 3: Draw the shadow and aura. The aura makes friendly story NPCs
            # visually different from enemies, so players know they can talk.
            aura_color = npc.get("aura_color", TEXT_COLOR)
            pulse = 6 + int(math.sin(self.game_time * 0.08) * 3)
            pygame.draw.ellipse(screen, (0, 0, 0), (screen_x - 42, screen_y - 14, 84, 22))
            pygame.draw.circle(screen, aura_color, (int(screen_x), int(screen_y - 70)), 42 + pulse, 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y - 70)), 30 + pulse, 1)

            # STEP 4: Draw a floating marker only before the first conversation is
            # complete. Once the dialogue key is in `seen_story_dialogues`, the
            # player can still talk, but the "new" marker disappears.
            if dialogue_key not in self.seen_story_dialogues:
                pygame.draw.line(screen, aura_color, (screen_x, screen_y - 136), (screen_x, screen_y - 178 - pulse), 3)
                pygame.draw.polygon(
                    screen,
                    (255, 245, 180),
                    [
                        (screen_x, screen_y - 190 - pulse),
                        (screen_x - 10, screen_y - 172 - pulse),
                        (screen_x + 10, screen_y - 172 - pulse),
                    ],
                )

            # STEP 5: Draw the actual imported character art, or a basic fallback
            # if the PNG failed to load.
            if sprite:
                screen.blit(sprite, (int(screen_x - sprite.get_width() / 2), int(screen_y - sprite.get_height())))
            else:
                # Fallback drawing if the imported PNG is missing.
                pygame.draw.circle(screen, aura_color, (int(screen_x), int(screen_y - 65)), 36)
                pygame.draw.circle(screen, (255, 215, 100), (int(screen_x), int(screen_y - 92)), 22)

            # STEP 6: Draw the NPC name. The nearby NPC gets a brighter name.
            name_color = (255, 245, 160) if npc_key == nearby_key else aura_color
            label = font_tiny.render(npc["name"], True, name_color)
            screen.blit(label, (screen_x - label.get_width() // 2, screen_y + 8))

            # STEP 7: If the player is close enough, draw the prompt telling them
            # which button starts the conversation.
            if npc_key == nearby_key:
                prompt = font_tiny.render(npc["prompt"], True, (255, 245, 160))
                panel_w = prompt.get_width() + 24
                panel = pygame.Rect(int(screen_x - panel_w / 2), int(screen_y + 32), panel_w, 30)
                pygame.draw.rect(screen, UI_BG, panel, border_radius=6)
                pygame.draw.rect(screen, aura_color, panel, 2, border_radius=6)
                screen.blit(prompt, (panel.x + 12, panel.y + 7))

    def draw_story_dialogue(self, screen):
        """Draw the active story dialogue overlay with portrait and wrapped text."""
        if not self.active_story_dialogue:
            return

        dialogue = self.active_story_dialogue
        line = self.active_story_lines[self.active_story_line_index]
        draw_story_dialogue_overlay(
            screen,
            dialogue,
            line,
            self.active_story_line_index,
            len(self.active_story_lines),
            font_small=font_small,
            font_tiny=font_tiny,
            screen_width=SCREEN_WIDTH,
            screen_height=SCREEN_HEIGHT,
            ui_bg=UI_BG,
            text_color=TEXT_COLOR,
            android_mode=is_android(),
            get_story_sprite_path=get_story_sprite_path,
            load_sprite_by_height=load_sprite_by_height,
            wrap_text_to_width=wrap_text_to_width,
        )

    def draw_pause_menu(self, screen):
        """Draw the shared in-game pause menu for keyboard and Android players."""
        if not self.show_pause_menu:
            return

        if not self.pause_menu_buttons:
            self.rebuild_pause_menu_buttons()
        self.set_selected_buttons(self.pause_menu_buttons, self.pause_menu_index)
        draw_pause_menu_overlay(
            screen,
            self.pause_menu_buttons,
            font_large=font_large,
            font_tiny=font_tiny,
            screen_width=SCREEN_WIDTH,
            screen_height=SCREEN_HEIGHT,
            ui_bg=UI_BG,
            android_mode=is_android(),
        )

    def complete_town_errand(self, service_type):
        errand = get_town_errand(service_type)
        if not errand or service_type in self.completed_town_errands:
            return None

        self.completed_town_errands.add(service_type)
        reward_text = self.apply_town_reward(errand["reward"])
        if reward_text:
            return f"Errand complete: {errand['title']} ({reward_text})."
        return f"Errand complete: {errand['title']}."

    def append_town_service_message(self, extra_message):
        if not extra_message:
            return
        base_message = self.town_service_message or ""
        separator = " " if base_message else ""
        self.set_town_service_message(f"{base_message}{separator}{extra_message}")

    def apply_town_service(self, service):
        service_type = service["type"]
        npc_name = service["npc"]

        if service_type == "inn":
            self.set_town_service_message(apply_inn_rest_service(self.player, npc_name))
        elif service_type == "shop":
            health_added = self.player.add_inventory_item("health")
            mana_added = self.player.add_inventory_item("mana")
            if health_added or mana_added:
                self.set_town_service_message(
                    f"{npc_name}: Packed HP +{health_added}, MP +{mana_added}. "
                    f"Bag now HP x{self.player.get_inventory_count('health')}, "
                    f"MP x{self.player.get_inventory_count('mana')}."
                )
            else:
                self.set_town_service_message(f"{npc_name}: Your potion pouch is full. Spend a few before restocking.")
        elif service_type == "blacksmith":
            self.set_town_service_message(apply_blacksmith_forge_service(self.player, npc_name))
        elif service_type == "library":
            claim_key = ("library", self.player.level)
            if claim_key in self.player.town_service_claims:
                self.set_town_service_message(f"{npc_name}: Study more after your next level.")
            else:
                self.player.town_service_claims.add(claim_key)
                insight = 20 + self.player.level * 5
                self.player.gain_exp(insight)
                self.set_town_service_message(f"{npc_name}: Copied dragon notes into the Log. Lore insight grants {insight} EXP.")
        elif service_type == "town_hall":
            progress = self.get_player_progression_status()
            if progress:
                message = f"{progress['title']} - {progress['lines'][0]}"
            else:
                message = "No active reports."
            self.set_town_service_message(f"{npc_name}: {message} Open the Log from the menu for the full route.")
        elif service_type == "house":
            claim_key = ("house", self.player.level)
            if claim_key in self.player.town_service_claims:
                self.set_town_service_message(f"{npc_name}: The stew pot needs time before another meal.")
            else:
                self.player.town_service_claims.add(claim_key)
                healed = min(12 + self.player.level * 2, self.player.max_health - self.player.health)
                restored_mana = min(8 + self.player.level, self.player.max_mana - self.player.mana)
                self.player.health += healed
                self.player.mana += restored_mana
                if healed or restored_mana:
                    self.set_town_service_message(f"{npc_name}: Shared a meal. HP +{healed}, MP +{restored_mana}.")
                else:
                    self.set_town_service_message(f"{npc_name}: Shared a meal for the road. You are already fully recovered.")
        elif service_type == "stall":
            healed = min(10 + self.player.level, self.player.max_health - self.player.health)
            restored_mana = min(6 + self.player.level, self.player.max_mana - self.player.mana)
            self.player.health += healed
            self.player.mana += restored_mana
            if healed or restored_mana:
                self.set_town_service_message(f"{npc_name}: Travel stew warms you. HP +{healed}, MP +{restored_mana}.")
            else:
                self.set_town_service_message(f"{npc_name}: Travel stew packed. You are already topped off.")
        else:
            self.set_town_service_message(f"{npc_name}: Safe travels.")

        self.append_town_service_message(self.complete_town_errand(service_type))

        for _ in range(12):
            x = random.randint(self.player.x, self.player.x + PLAYER_SIZE)
            y = random.randint(self.player.y, self.player.y + PLAYER_SIZE)
            self.particle_system.add_particle(
                x, y, (255, 215, 0),
                (random.uniform(-0.4, 0.4), random.uniform(-1, -0.2)),
                2, 25
            )

    @staticmethod
    def shade_color(color, amount):
        return tuple(max(0, min(255, value + amount)) for value in color)

    def build_interior_service_menu_entries(self):
        """Return the active building-menu commands.

        Beginner note:
            Each tuple is `(command_key, button_label)`.
            `command_key` is what code uses.
            `button_label` is what the player taps or sees highlighted.
        """
        if not self.current_interior_service:
            return []
        service_type = self.current_interior_service["type"]
        return [
            ("service", get_service_action_label(service_type)),
            ("talk", "TALK"),
            ("journal", "LOG"),
            ("leave", "LEAVE"),
            ("close", "BACK"),
        ]

    def rebuild_interior_service_menu_buttons(self):
        """Create clickable buttons for the interior service menu."""
        entries = self.build_interior_service_menu_entries()
        button_width = 250
        button_height = 42
        gap = 8
        start_y = 222
        self.interior_service_menu_buttons = []
        for index, (command, label) in enumerate(entries):
            button = Button(
                SCREEN_WIDTH // 2 - button_width // 2,
                start_y + index * (button_height + gap),
                button_width,
                button_height,
                label,
                color=(86, 118, 154),
            )
            button.command = command
            self.interior_service_menu_buttons.append(button)

        if self.interior_service_menu_buttons:
            self.interior_service_menu_index = max(
                0,
                min(self.interior_service_menu_index, len(self.interior_service_menu_buttons) - 1),
            )
        else:
            self.interior_service_menu_index = 0

    def get_current_town_reward_preview(self):
        """Return the reward line shown in the current building service menu."""
        if not self.current_interior_service:
            return ""
        service_type = self.current_interior_service["type"]
        errand = get_town_errand(service_type)
        if errand and service_type not in self.completed_town_errands:
            return format_town_reward_preview(errand.get("reward", {}), self.player.type if self.player else None)

        repeat_lines = get_service_overview_lines(service_type)
        if len(repeat_lines) >= 4:
            return f"Repeat: {repeat_lines[3]}"
        return "Repeat: service remains available after the first errand."

    def open_interior_service_menu(self):
        """Open the building action menu and hide conflicting overlays."""
        if not self.current_interior_service:
            return
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.show_journal = False
        self.show_inventory = False
        self.show_world_map = False
        self.interior_service_menu_open = True
        self.interior_service_menu_index = 0
        self.rebuild_interior_service_menu_buttons()
        if self.SFX_CLICK:
            self.SFX_CLICK.play()

    def close_interior_service_menu(self, play_sound=True):
        """Close the building action menu without leaving the room."""
        self.interior_service_menu_open = False
        self.interior_service_menu_buttons = []
        if play_sound and self.SFX_CLICK:
            self.SFX_CLICK.play()

    def activate_interior_service_menu_command(self, command):
        """Run one command from the interior service menu."""
        if command == "service":
            self.close_interior_service_menu(play_sound=False)
            self.apply_town_service(self.current_interior_service)
            if self.SFX_ITEM:
                self.SFX_ITEM.play()
            return

        if command == "talk":
            self.close_interior_service_menu(play_sound=False)
            self.talk_to_current_npc()
            return

        if command == "journal":
            self.close_interior_service_menu(play_sound=False)
            self.show_journal = True
            self.show_inventory = False
            self.show_world_map = False
            if self.SFX_CLICK:
                self.SFX_CLICK.play()
            return

        if command == "leave":
            self.close_interior_service_menu(play_sound=False)
            self.exit_town_interior()
            return

        self.close_interior_service_menu(play_sound=True)

    def activate_interior_service_menu_selection(self):
        """Run the currently highlighted interior service-menu button."""
        if not self.interior_service_menu_buttons:
            self.rebuild_interior_service_menu_buttons()
        if not self.interior_service_menu_buttons:
            return
        command = getattr(
            self.interior_service_menu_buttons[self.interior_service_menu_index],
            "command",
            None,
        )
        if command:
            self.activate_interior_service_menu_command(command)

    def enter_town_interior(self, service):
        room = TOWN_INTERIORS.get(service["type"])
        if not room:
            self.apply_town_service(service)
            return

        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.interior_service_menu_open = False
        self.interior_service_menu_buttons = []
        self.current_interior = room
        self.current_interior_service = dict(service)
        self.interior_return_position = (self.player.x, self.player.y) if self.player else None
        self.interior_player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.interior_player_y = 500
        self.npc_dialogue_index = 0
        self.show_world_map = False
        self.show_journal = False
        self.state = "interior"
        self.set_town_service_message(f"Entered {room['title']}.")
        if self.SFX_ENTER:
            self.SFX_ENTER.play()

    def exit_town_interior(self):
        room_title = self.current_interior["title"] if self.current_interior else "building"
        if self.player and self.interior_return_position:
            self.player.x, self.player.y = self.interior_return_position

        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.interior_service_menu_open = False
        self.interior_service_menu_buttons = []
        self.current_interior = None
        self.current_interior_service = None
        self.interior_return_position = None
        self.show_journal = False
        self.state = "overworld"
        self.set_town_service_message(f"Left {room_title}.")
        if self.SFX_ENTER:
            self.SFX_ENTER.play()

    def use_current_town_service(self):
        if not self.current_interior_service:
            return
        self.open_interior_service_menu()

    def get_interior_blockers(self):
        if not self.current_interior:
            return []
        blocking_kinds = {
            "bed", "counter", "table", "desk", "shelf", "bookcase", "hearth",
            "forge", "anvil", "rack", "crate", "crystal", "map", "notice",
            "barrel", "plant", "lamp", "chest", "stool", "cauldron", "sign",
        }
        blockers = []
        for prop in self.current_interior["props"]:
            if prop["kind"] in blocking_kinds:
                rect = pygame.Rect(prop["rect"])
                blockers.append(rect.inflate(8, 8))
        return blockers

    def move_interior_player(self, dx, dy):
        new_x = self.interior_player_x + dx * GRID_SIZE
        new_y = self.interior_player_y + dy * GRID_SIZE
        player_rect = pygame.Rect(new_x, new_y, PLAYER_SIZE, PLAYER_SIZE)
        if not INTERIOR_WALK_BOUNDS.contains(player_rect):
            return False
        for blocker in self.get_interior_blockers():
            if player_rect.colliderect(blocker):
                return False
        self.interior_player_x = new_x
        self.interior_player_y = new_y
        if self.SFX_ARROW:
            self.SFX_ARROW.play()
        return True

    def interior_player_near_npc(self):
        if not self.current_interior:
            return False
        npc_x, npc_y = self.current_interior["npc_position"]
        player_center = (self.interior_player_x + PLAYER_SIZE // 2, self.interior_player_y + PLAYER_SIZE // 2)
        return math.hypot(player_center[0] - npc_x, player_center[1] - npc_y) <= 210

    def talk_to_current_npc(self):
        if not self.current_interior_service:
            return
        service_type = self.current_interior_service["type"]
        dialogue = get_town_service_dialogue(service_type)
        if not dialogue:
            self.set_town_service_message(f"{self.current_interior_service['npc']}: Safe travels.")
            return
        message = dialogue[self.npc_dialogue_index % len(dialogue)]
        self.npc_dialogue_index += 1
        self.set_town_service_message(message)
        if self.SFX_CLICK:
            self.SFX_CLICK.play()

    def get_nearby_interior_inspect(self):
        if not self.current_interior:
            return None
        player_rect = pygame.Rect(self.interior_player_x, self.interior_player_y, PLAYER_SIZE, PLAYER_SIZE)
        for point in self.current_interior.get("inspect_points", ()):
            inspect_rect = pygame.Rect(point["rect"]).inflate(70, 70)
            if player_rect.colliderect(inspect_rect):
                return point
        return None

    def inspect_current_interior_point(self):
        point = self.get_nearby_interior_inspect()
        if not point:
            return False
        service_type = self.current_interior_service["type"] if self.current_interior_service else "town"
        detail_key = (service_type, point["label"])
        self.set_town_service_message(point["message"])
        if detail_key not in self.inspected_town_details:
            self.inspected_town_details.add(detail_key)
            insight = 3 + self.player.level
            self.player.gain_exp(insight)
            self.score += 1
            self.append_town_service_message(f"Insight gained: {insight} EXP, 1 score.")
        if self.SFX_CLICK:
            self.SFX_CLICK.play()
        return True

    def draw_journal_line(self, screen, text, x, y, color=(225, 225, 215), font_obj=font_tiny, max_width=None):
        """Draw one Log/Inventory line and return the next y position.

        Beginner note:
            `max_width` is optional so older calls keep working. Newer Log
            panels pass a width because Android screens can make long quest
            labels collide with panel borders.
        """
        if max_width:
            rendered = render_fitted_text(text, color, max_width, (font_obj, font_tiny))
        else:
            rendered = font_obj.render(text, True, color)
        screen.blit(rendered, (x, y))
        return y + rendered.get_height() + 7

    def draw_journal(self, screen):
        if not self.player:
            return

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 188))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(95, 54, 810, 574)
        pygame.draw.rect(screen, UI_BG, panel, border_radius=12)
        pygame.draw.rect(screen, UI_BORDER, panel, 3, border_radius=12)

        title = font_large.render("QUEST LOG", True, (255, 215, 0))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 18))

        progress = self.get_player_progression_status()
        left_x = panel.x + 34
        right_x = panel.x + 420
        y = panel.y + 92

        if progress:
            quest_panel = pygame.Rect(left_x, y, 342, 136)
            pygame.draw.rect(screen, (20, 20, 30), quest_panel, border_radius=8)
            pygame.draw.rect(screen, progress["color"], quest_panel, 2, border_radius=8)
            line_y = self.draw_journal_line(screen, progress["title"], left_x + 14, y + 12, progress["color"], font_small)
            for line in progress["lines"]:
                line_y = self.draw_journal_line(screen, line, left_x + 14, line_y, (225, 225, 215))

        hero_panel = pygame.Rect(right_x, y, 336, 136)
        pygame.draw.rect(screen, (20, 20, 30), hero_panel, border_radius=8)
        pygame.draw.rect(screen, TEXT_COLOR, hero_panel, 2, border_radius=8)
        class_profile = get_character_class_profile(self.player.type)
        line_y = self.draw_journal_line(screen, f"HERO: {self.player.type}  LV.{self.player.level}", right_x + 14, y + 12, TEXT_COLOR, font_small)
        line_y = self.draw_journal_line(screen, class_profile.get("role", "Adventurer"), right_x + 14, line_y, (245, 235, 180))
        line_y = self.draw_journal_line(screen, f"HP {self.player.health}/{self.player.max_health}   MP {self.player.mana}/{self.player.max_mana}", right_x + 14, line_y)
        line_y = self.draw_journal_line(
            screen,
            f"STR {self.player.effective_strength()}   DEF {self.player.effective_defense()}   SPD {self.player.effective_speed()}",
            right_x + 14,
            line_y,
        )
        self.draw_journal_line(
            screen,
            f"Bag HP x{self.player.get_inventory_count('health')} MP x{self.player.get_inventory_count('mana')}  Rep {self.town_reputation}",
            right_x + 14,
            line_y,
            (255, 215, 0),
        )

        y += 160
        current_area = self.world_map.get_current_area()
        area_panel = pygame.Rect(left_x, y, 342, 150)
        pygame.draw.rect(screen, (20, 20, 30), area_panel, border_radius=8)
        pygame.draw.rect(screen, (150, 230, 150), area_panel, 2, border_radius=8)
        if current_area:
            visited_count = sum(1 for area in self.world_map.areas.values() if area.visited)
            line_y = self.draw_journal_line(screen, f"AREA: {current_area.area_type.upper()}", left_x + 14, y + 12, (150, 230, 150), font_small)
            line_y = self.draw_journal_line(screen, AREA_DESCRIPTIONS.get(current_area.area_type, "Unknown region"), left_x + 14, line_y)
            mechanic = AREA_MECHANICS.get(current_area.area_type)
            if mechanic:
                line_y = self.draw_journal_line(screen, f"Effect: {mechanic['label']}", left_x + 14, line_y, mechanic["color"])
            self.draw_journal_line(screen, f"Visited areas: {visited_count}/{WORLD_SIZE * WORLD_SIZE}", left_x + 14, line_y)

        service_panel = pygame.Rect(right_x, y, 336, 206)
        pygame.draw.rect(screen, (20, 20, 30), service_panel, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 0), service_panel, 2, border_radius=8)
        service_line_width = service_panel.width - 28
        line_y = self.draw_journal_line(screen, "TOWN HUB", right_x + 14, y + 12, (255, 215, 0), font_small, service_line_width)
        completed_count = len(self.completed_town_errands)
        total_count = get_town_errand_count()
        resident_count = len(self.completed_resident_errands)
        resident_total = get_town_resident_errand_count()
        line_y = self.draw_journal_line(screen, f"Buildings {completed_count}/{total_count}   Residents {resident_count}/{resident_total}", right_x + 14, line_y, max_width=service_line_width)
        open_errands = [
            (key, errand)
            for key, errand in TOWN_ERRANDS.items()
            if key not in self.completed_town_errands
        ]
        if open_errands:
            line_y = self.draw_journal_line(screen, "Open building errands:", right_x + 14, line_y, (245, 235, 180), max_width=service_line_width)
            for service_key, errand in open_errands[:2]:
                service_info = TOWN_SERVICES.get(service_key, {})
                service_label = get_service_map_label(service_key)
                role = service_info.get("role", "Town")
                line_y = self.draw_journal_line(
                    screen,
                    f"{service_label}: {errand['title']} [{role}]",
                    right_x + 22,
                    line_y,
                    (225, 225, 215),
                    max_width=service_line_width - 8,
                )
                if line_y < service_panel.bottom - 54:
                    line_y = self.draw_journal_line(
                        screen,
                        format_town_reward_preview(errand.get("reward", {}), self.player.type, max_parts=3),
                        right_x + 28,
                        line_y,
                        (205, 216, 190),
                        max_width=service_line_width - 14,
                    )
            if len(open_errands) > 2:
                line_y = self.draw_journal_line(screen, f"+{len(open_errands) - 2} more buildings marked in town.", right_x + 22, line_y, (200, 210, 220), max_width=service_line_width - 8)
        else:
            line_y = self.draw_journal_line(screen, "All building errands complete.", right_x + 14, line_y, (120, 230, 150), max_width=service_line_width)

        resident_hint = get_next_town_resident_errand_status(
            self.town_reputation,
            self.completed_town_errands,
            self.completed_resident_errands,
        )
        if resident_hint and line_y < service_panel.bottom - 64:
            status_color = (130, 235, 150) if resident_hint["available"] else (255, 195, 110)
            line_y = self.draw_journal_line(
                screen,
                f"Resident: {resident_hint['resident']} [{resident_hint['status']}]",
                right_x + 14,
                line_y,
                status_color,
                max_width=service_line_width,
            )
            line_y = self.draw_journal_line(
                screen,
                resident_hint["title"],
                right_x + 22,
                line_y,
                (225, 225, 215),
                max_width=service_line_width - 8,
            )
        if line_y < service_panel.bottom - 48 and self.state == "interior" and self.current_interior_service:
            service_type = self.current_interior_service["type"]
            errand_status = "done" if service_type in self.completed_town_errands else "open"
            line_y = self.draw_journal_line(screen, f"Inside: {self.current_interior_service['name']} ({errand_status})", right_x + 14, line_y, max_width=service_line_width)
            for detail in get_service_overview_lines(service_type)[:1]:
                line_y = self.draw_journal_line(screen, detail, right_x + 14, line_y, (210, 220, 230), max_width=service_line_width)
        elif line_y < service_panel.bottom - 48 and current_area:
            service = current_area.get_nearby_town_service(self.player.x, self.player.y)
            if service:
                status = get_service_completion_label(service["type"], self.completed_town_errands)
                line_y = self.draw_journal_line(screen, f"Nearby: {service['name']} [{status}]", right_x + 14, line_y, max_width=service_line_width)
                for detail in get_service_overview_lines(service["type"])[:1]:
                    line_y = self.draw_journal_line(screen, detail, right_x + 14, line_y, (210, 220, 230), max_width=service_line_width)
                self.draw_journal_line(screen, "OK/USE enters the marked doorway.", right_x + 14, line_y, max_width=service_line_width)
            else:
                resident = self.get_nearby_town_resident(current_area)
                if resident:
                    _, resident_profile = resident
                    quest = get_town_resident_quest(resident_profile)
                    quest_key = resident_profile.get("quest_key")
                    if quest_key in self.completed_resident_errands:
                        resident_status = "DONE"
                    elif quest:
                        available, reason = is_town_resident_quest_available(
                            quest,
                            self.town_reputation,
                            self.completed_town_errands,
                        )
                        resident_status = "READY" if available else reason
                    else:
                        resident_status = "TALK"
                    line_y = self.draw_journal_line(screen, f"Nearby: {resident_profile['name']}", right_x + 14, line_y, max_width=service_line_width)
                    line_y = self.draw_journal_line(screen, f"{resident_profile['role']} [{resident_status}]", right_x + 14, line_y, max_width=service_line_width)
                    if quest:
                        self.draw_journal_line(screen, quest["title"], right_x + 14, line_y, (210, 220, 230), max_width=service_line_width)
                else:
                    self.draw_journal_line(screen, "Walk to a labeled doorway marker.", right_x + 14, line_y, max_width=service_line_width)

        y += 228
        controls_panel = pygame.Rect(left_x, y, 722, 92)
        pygame.draw.rect(screen, (20, 20, 30), controls_panel, border_radius=8)
        pygame.draw.rect(screen, (180, 180, 220), controls_panel, 2, border_radius=8)
        if is_android():
            controls = (
                "Move: touch d-pad or arrows/WASD    Use: USE or SPACE",
                "Menu: MENU touch button or ESC    OK: confirm / talk / inspect",
                "Pause menu buttons: Log, Map, Save, Load    Save path: " + str(DEFAULT_SAVE_PATH),
            )
        else:
            controls = (
                "Move: arrows/WASD    Interact: SPACE    Confirm/Talk: ENTER",
                "Log: J    Map: M    Save: F5    Load: F9    Close/Menu: ESC",
                "Save path: " + str(DEFAULT_SAVE_PATH),
            )
        line_y = y + 14
        for line in controls:
            line_y = self.draw_journal_line(screen, line, left_x + 14, line_y, (210, 210, 225))

    def draw_inventory(self, screen):
        """Draw the pause-menu Inventory screen.

        Beginner note:
            This gives the player a readable place to see consumable potions,
            owned equipment, equipped gear bonuses, and permanent story rewards
            such as trophies. It is also an equipment menu:

            - Left/right changes the active slot.
            - Up/down chooses owned gear for that slot.
            - OK equips the selected gear.
            - USE unequips the active slot.
        """
        if not self.player:
            return

        def draw_equipment_icon(profile, rect):
            """Draw one equipment icon, with a simple fallback if PNG is missing."""
            rarity_color = get_equipment_rarity_color(profile.get("rarity", "common"))
            pygame.draw.rect(screen, (12, 12, 22), rect, border_radius=6)
            pygame.draw.rect(screen, rarity_color, rect, 2, border_radius=6)
            icon_path = get_equipment_icon_path(profile.get("icon"))
            icon = load_scaled_sprite(icon_path, max(1, rect.width - 8)) if icon_path else None
            if icon:
                icon_rect = icon.get_rect(center=rect.center)
                screen.blit(icon, icon_rect)
            else:
                pygame.draw.circle(screen, rarity_color, rect.center, max(5, rect.width // 4))

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 188))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(80, 48, 840, 590)
        pygame.draw.rect(screen, UI_BG, panel, border_radius=12)
        pygame.draw.rect(screen, (255, 215, 0), panel, 3, border_radius=12)

        title = font_large.render("INVENTORY", True, (255, 215, 0))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 18))

        left_x = panel.x + 34
        right_x = panel.x + 420
        y = panel.y + 92

        consumables_panel = pygame.Rect(left_x, y, 350, 92)
        pygame.draw.rect(screen, (20, 20, 30), consumables_panel, border_radius=8)
        pygame.draw.rect(screen, TEXT_COLOR, consumables_panel, 2, border_radius=8)
        line_y = self.draw_journal_line(screen, "CONSUMABLES", left_x + 14, y + 12, TEXT_COLOR, font_small)
        self.draw_journal_line(
            screen,
            f"Health potions: {self.player.get_inventory_count('health')}    Mana tonics: {self.player.get_inventory_count('mana')}",
            left_x + 14,
            line_y,
        )

        equipment_panel = pygame.Rect(left_x, y + 112, 350, 228)
        pygame.draw.rect(screen, (20, 20, 30), equipment_panel, border_radius=8)
        pygame.draw.rect(screen, (180, 180, 220), equipment_panel, 2, border_radius=8)
        line_y = self.draw_journal_line(screen, "EQUIPPED", left_x + 14, equipment_panel.y + 12, (180, 180, 220), font_small)
        active_slot = self.get_active_inventory_slot()
        for slot in self.inventory_slots:
            item_key = self.player.equipment.get(slot)
            profile = get_equipment_item(item_key) if item_key else None
            label = profile.get("label", "None") if profile else "None"
            bonus_text = format_equipment_bonus(profile.get("bonuses", {})) if profile else "No bonus"
            rarity_color = get_equipment_rarity_color(profile.get("rarity", "common")) if profile else (210, 210, 225)
            row = pygame.Rect(equipment_panel.x + 12, line_y - 2, equipment_panel.width - 24, 52)
            if slot == active_slot:
                pygame.draw.rect(screen, (42, 48, 76), row, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), row, 2, border_radius=6)
            if profile:
                draw_equipment_icon(profile, pygame.Rect(row.x + 6, row.y + 6, 40, 40))
            slot_text = render_fitted_text(
                f"{get_equipment_slot_label(slot)}: {label}",
                rarity_color,
                row.width - 62,
                (font_tiny,),
            )
            bonus_surface = render_fitted_text(bonus_text, (210, 210, 225), row.width - 62, (font_tiny,))
            screen.blit(slot_text, (row.x + 54, row.y + 8))
            screen.blit(bonus_surface, (row.x + 54, row.y + 29))
            line_y += 58

        message_panel = pygame.Rect(left_x, y + 358, 350, 76)
        pygame.draw.rect(screen, (18, 18, 28), message_panel, border_radius=8)
        pygame.draw.rect(screen, (140, 220, 255), message_panel, 2, border_radius=8)
        message_lines = wrap_text_to_width(self.inventory_message, font_tiny, message_panel.width - 28)
        line_y = message_panel.y + 12
        for line in message_lines[:2]:
            line_y = self.draw_journal_line(screen, line, message_panel.x + 14, line_y, (220, 235, 255))

        gear_panel = pygame.Rect(right_x, y, 362, 340)
        pygame.draw.rect(screen, (20, 20, 30), gear_panel, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 0), gear_panel, 2, border_radius=8)
        slot_label = get_equipment_slot_label(active_slot).upper()
        header = font_small.render(f"OWNED {slot_label}", True, (255, 215, 0))
        screen.blit(header, (gear_panel.x + 14, gear_panel.y + 12))

        slot_items = self.get_inventory_slot_items()
        if slot_items:
            self.inventory_item_index = max(0, min(self.inventory_item_index, len(slot_items) - 1))
        else:
            self.inventory_item_index = 0

        selected_item_key = slot_items[self.inventory_item_index] if slot_items else None
        equipped_item_key = self.player.equipment.get(active_slot)

        row_y = gear_panel.y + 48
        if not slot_items:
            self.draw_journal_line(screen, "No owned gear in this slot yet.", gear_panel.x + 14, row_y, (210, 210, 225))
        else:
            visible_limit = 4
            visible_rows = slot_items[:visible_limit]
            if self.inventory_item_index >= visible_limit:
                start_index = max(0, min(self.inventory_item_index - (visible_limit - 1), len(slot_items) - visible_limit))
                visible_rows = slot_items[start_index:start_index + visible_limit]
            else:
                start_index = 0
            for offset, item_key in enumerate(visible_rows):
                index = start_index + offset
                profile = get_equipment_item(item_key) or {}
                selected = index == self.inventory_item_index
                equipped = self.player.equipment.get(active_slot) == item_key
                rarity_color = get_equipment_rarity_color(profile.get("rarity", "common"))
                row = pygame.Rect(gear_panel.x + 12, row_y, gear_panel.width - 24, 48)
                if selected:
                    pygame.draw.rect(screen, (48, 42, 76), row, border_radius=6)
                    pygame.draw.rect(screen, (255, 215, 0), row, 2, border_radius=6)
                elif equipped:
                    pygame.draw.rect(screen, (28, 54, 44), row, border_radius=6)
                    pygame.draw.rect(screen, (120, 220, 160), row, 1, border_radius=6)
                draw_equipment_icon(profile, pygame.Rect(row.x + 6, row.y + 6, 40, 40))
                count = self.player.owned_equipment.get(item_key, 0)
                count_text = f" x{count}" if count > 1 else ""
                equipped_text = " [ON]" if equipped else ""
                label = render_fitted_text(
                    f"{profile.get('label', item_key)}{count_text}{equipped_text}",
                    rarity_color,
                    row.width - 64,
                    (font_tiny,),
                )
                bonus_text = render_fitted_text(
                    format_equipment_bonus(profile.get("bonuses", {})),
                    (210, 210, 225),
                    row.width - 64,
                    (font_tiny,),
                )
                screen.blit(label, (row.x + 54, row.y + 8))
                screen.blit(bonus_text, (row.x + 54, row.y + 29))
                row_y += 52

            if len(slot_items) > visible_limit:
                scroll_text = font_tiny.render(f"{self.inventory_item_index + 1}/{len(slot_items)}", True, (210, 210, 225))
                screen.blit(scroll_text, (gear_panel.right - scroll_text.get_width() - 16, gear_panel.y + 238))

        preview_panel = pygame.Rect(gear_panel.x + 12, gear_panel.bottom - 82, gear_panel.width - 24, 70)
        pygame.draw.rect(screen, (16, 18, 28), preview_panel, border_radius=8)
        pygame.draw.rect(screen, (120, 150, 210), preview_panel, 2, border_radius=8)
        if selected_item_key:
            selected_profile = get_equipment_item(selected_item_key) or {}
            rarity = selected_profile.get("rarity", "common")
            rarity_color = get_equipment_rarity_color(rarity)
            tier = selected_profile.get("tier", 1)
            comparison = format_equipment_delta(selected_item_key, equipped_item_key)
            power_delta = get_equipment_power(selected_item_key) - get_equipment_power(equipped_item_key)
            change_color = (120, 230, 150) if power_delta > 0 else (255, 185, 110) if power_delta < 0 else (220, 220, 230)
            preview_title = render_fitted_text(
                f"{selected_profile.get('label', selected_item_key)}  T{tier} {rarity.upper()}",
                rarity_color,
                preview_panel.width - 24,
                (font_tiny,),
            )
            preview_change = render_fitted_text(
                f"Change: {comparison}",
                change_color,
                preview_panel.width - 24,
                (font_tiny,),
            )
            description_lines = wrap_text_to_width(selected_profile.get("description", ""), font_tiny, preview_panel.width - 24)
            screen.blit(preview_title, (preview_panel.x + 12, preview_panel.y + 8))
            screen.blit(preview_change, (preview_panel.x + 12, preview_panel.y + 27))
            if description_lines:
                desc = render_fitted_text(description_lines[0], (205, 210, 225), preview_panel.width - 24, (font_tiny,))
                screen.blit(desc, (preview_panel.x + 12, preview_panel.y + 48))
        else:
            self.draw_journal_line(screen, "Forge or earn gear to compare it here.", preview_panel.x + 12, preview_panel.y + 18, (210, 210, 225))

        trophy_panel = pygame.Rect(right_x, y + 358, 362, 120)
        pygame.draw.rect(screen, (20, 20, 30), trophy_panel, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 0), trophy_panel, 2, border_radius=8)
        line_y = self.draw_journal_line(screen, "TROPHIES / STORY ITEMS", trophy_panel.x + 14, trophy_panel.y + 12, (255, 215, 0), font_small)
        story_items = getattr(self.player, "story_items", {})
        if not story_items:
            self.draw_journal_line(screen, "No trophies yet.", trophy_panel.x + 14, line_y, (210, 210, 225))
        else:
            for item_key, count in sorted(story_items.items()):
                item = get_story_reward_item(item_key) or {}
                label = item.get("label", item_key.replace("_", " ").title())
                kind = item.get("kind", "misc").upper()
                count_text = f" x{count}" if count > 1 else ""
                line_y = self.draw_journal_line(screen, f"{kind}: {label}{count_text}", trophy_panel.x + 14, line_y, (245, 235, 180))
                description = item.get("description", "")
                if description:
                    for wrapped in wrap_text_to_width(description, font_tiny, trophy_panel.width - 28)[:1]:
                        line_y = self.draw_journal_line(screen, wrapped, trophy_panel.x + 14, line_y, (210, 210, 225))
                line_y += 4
                if line_y > trophy_panel.bottom - 34:
                    self.draw_journal_line(screen, "More hidden.", trophy_panel.x + 14, line_y, (255, 170, 120))
                    break

        prompt = font_tiny.render("LEFT/RIGHT slot  UP/DOWN gear  OK equip  USE unequip  ESC/CLOSE exits", True, (210, 210, 225))
        screen.blit(prompt, (panel.centerx - prompt.get_width() // 2, panel.bottom - 34))

    def draw_interior_prop(self, screen, prop, room):
        kind = prop["kind"]
        rect = pygame.Rect(prop["rect"])
        color = prop["color"]
        accent = room["accent_color"]
        shadow = self.shade_color(color, -35)
        dark = self.shade_color(color, -55)
        light = self.shade_color(color, 30)

        # BEGINNER NOTE: Interior props can optionally use imported sprites.
        # The rectangle still controls collision/inspection placement, while
        # `sprite` controls the art. If the PNG fails to load, the normal
        # Python-drawn prop below is used instead.
        sprite_name = prop.get("sprite")
        if sprite_name:
            sprite_path = get_scenery_asset_path(sprite_name)
            if draw_sprite_in_rect(
                screen,
                sprite_path,
                rect,
                prop.get("sprite_preserve_aspect", True),
                prop.get("sprite_anchor", "center"),
            ):
                return

        if kind == "rug":
            pygame.draw.ellipse(screen, shadow, rect.move(4, 5))
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.ellipse(screen, self.shade_color(color, -25), rect, 4)
            pygame.draw.ellipse(screen, self.shade_color(color, 25), rect.inflate(-36, -22), 2)
        elif kind == "bed":
            pygame.draw.rect(screen, dark, rect.move(5, 5), border_radius=6)
            pygame.draw.rect(screen, shadow, rect, border_radius=6)
            mattress = rect.inflate(-18, -14)
            pygame.draw.rect(screen, color, mattress, border_radius=5)
            pillow = pygame.Rect(mattress.x + 10, mattress.y + 8, 42, 22)
            pygame.draw.rect(screen, self.shade_color(color, 45), pillow, border_radius=5)
            pygame.draw.rect(screen, dark, rect, 2, border_radius=6)
        elif kind in ("counter", "table", "desk"):
            pygame.draw.rect(screen, dark, rect.move(5, 6), border_radius=5)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, light, (rect.x, rect.y, rect.width, 12), border_radius=5)
            pygame.draw.rect(screen, dark, rect, 3, border_radius=5)
            if kind == "desk":
                paper = pygame.Rect(rect.x + 22, rect.y + 15, 45, 26)
                pygame.draw.rect(screen, (230, 218, 175), paper, border_radius=2)
                pygame.draw.line(screen, (118, 90, 62), paper.midleft, paper.midright, 1)
        elif kind in ("shelf", "bookcase"):
            pygame.draw.rect(screen, dark, rect.move(5, 5))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, dark, rect, 3)
            shelf_count = 4 if kind == "bookcase" else 3
            shelf_height = rect.height // shelf_count
            book_colors = ((220, 80, 80), (80, 180, 220), (240, 200, 80), (130, 220, 130))
            for shelf in range(shelf_count):
                shelf_y = rect.y + shelf * shelf_height + shelf_height - 8
                pygame.draw.line(screen, light, (rect.x + 8, shelf_y), (rect.right - 8, shelf_y), 4)
                for i in range(5):
                    book_x = rect.x + 14 + i * 23
                    book_h = 24 + (i % 3) * 8
                    book_y = shelf_y - book_h
                    pygame.draw.rect(screen, book_colors[(shelf + i) % len(book_colors)], (book_x, book_y, 12, book_h))
        elif kind == "hearth":
            pygame.draw.rect(screen, dark, rect.move(4, 4), border_radius=5)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, self.shade_color(color, -20), rect.inflate(-18, -14), border_radius=4)
            flame_offset = int(math.sin(self.game_time * 0.15) * 4)
            flame = [
                (rect.centerx, rect.y + 18 + flame_offset),
                (rect.centerx - 22, rect.bottom - 16),
                (rect.centerx + 22, rect.bottom - 16),
            ]
            pygame.draw.polygon(screen, (255, 98, 38), flame)
            pygame.draw.polygon(screen, (255, 210, 72), [(rect.centerx, rect.y + 30), (rect.centerx - 12, rect.bottom - 18), (rect.centerx + 12, rect.bottom - 18)])
        elif kind == "forge":
            pygame.draw.rect(screen, dark, rect.move(6, 6), border_radius=8)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            mouth = pygame.Rect(rect.x + 28, rect.y + 58, rect.width - 56, rect.height - 82)
            pygame.draw.rect(screen, (36, 22, 16), mouth, border_radius=8)
            flame_top = mouth.y + 10 + int(math.sin(self.game_time * 0.2) * 5)
            pygame.draw.polygon(screen, (255, 72, 30), [(mouth.centerx, flame_top), (mouth.x + 12, mouth.bottom - 8), (mouth.right - 12, mouth.bottom - 8)])
            pygame.draw.polygon(screen, (255, 208, 58), [(mouth.centerx, flame_top + 18), (mouth.x + 34, mouth.bottom - 8), (mouth.right - 34, mouth.bottom - 8)])
            pygame.draw.rect(screen, dark, rect, 3, border_radius=8)
        elif kind == "anvil":
            base = pygame.Rect(rect.x + 34, rect.y + 45, rect.width - 68, 22)
            pygame.draw.rect(screen, dark, base.move(4, 4))
            pygame.draw.rect(screen, color, base)
            top = [
                (rect.x + 12, rect.y + 26),
                (rect.x + 42, rect.y + 14),
                (rect.x + rect.width - 20, rect.y + 16),
                (rect.x + rect.width - 8, rect.y + 34),
                (rect.x + 34, rect.y + 42),
            ]
            pygame.draw.polygon(screen, dark, [(x + 4, y + 4) for x, y in top])
            pygame.draw.polygon(screen, color, top)
            pygame.draw.polygon(screen, light, top, 2)
        elif kind == "rack":
            pygame.draw.rect(screen, dark, rect.move(4, 4))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, dark, rect, 3)
            for i in range(4):
                x = rect.x + 28 + i * 28
                pygame.draw.line(screen, (200, 200, 190), (x, rect.y + 22), (x - 12, rect.bottom - 18), 4)
                pygame.draw.polygon(screen, accent, [(x, rect.y + 12), (x - 7, rect.y + 28), (x + 7, rect.y + 28)])
        elif kind == "crystal":
            points = [
                (rect.centerx, rect.y),
                (rect.right, rect.y + rect.height // 3),
                (rect.centerx + 18, rect.bottom),
                (rect.centerx - 18, rect.bottom),
                (rect.x, rect.y + rect.height // 3),
            ]
            pygame.draw.polygon(screen, self.shade_color(color, -35), [(x + 4, y + 5) for x, y in points])
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, self.shade_color(color, 45), points, 3)
            pygame.draw.circle(screen, color, rect.center, rect.width // 2, 1)
        elif kind == "crate":
            pygame.draw.rect(screen, dark, rect.move(4, 4))
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, dark, rect, 3)
            pygame.draw.line(screen, dark, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(screen, dark, rect.topright, rect.bottomleft, 2)
        elif kind == "barrel":
            pygame.draw.ellipse(screen, dark, rect.move(4, 5))
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.rect(screen, color, (rect.x, rect.y + rect.height // 4, rect.width, rect.height // 2))
            pygame.draw.arc(screen, dark, rect, 0, math.pi, 3)
            pygame.draw.arc(screen, dark, rect, math.pi, math.tau, 3)
            for band_y in (rect.y + rect.height // 3, rect.y + rect.height * 2 // 3):
                pygame.draw.line(screen, dark, (rect.x + 4, band_y), (rect.right - 4, band_y), 3)
        elif kind == "plant":
            pot = pygame.Rect(rect.x + rect.width // 4, rect.y + rect.height - 26, rect.width // 2, 24)
            pygame.draw.rect(screen, dark, pot.move(3, 3), border_radius=4)
            pygame.draw.rect(screen, self.shade_color(color, -35), pot, border_radius=4)
            for i in range(5):
                angle = -70 + i * 35
                leaf_x = rect.centerx + int(math.cos(math.radians(angle)) * 22)
                leaf_y = pot.y - 5 + int(math.sin(math.radians(angle)) * 26)
                pygame.draw.ellipse(screen, color, (leaf_x - 13, leaf_y - 18, 26, 36))
                pygame.draw.ellipse(screen, self.shade_color(color, -45), (leaf_x - 13, leaf_y - 18, 26, 36), 2)
        elif kind == "lamp":
            stem_x = rect.centerx
            pygame.draw.line(screen, dark, (stem_x + 3, rect.bottom), (stem_x + 3, rect.y + 18), 5)
            pygame.draw.line(screen, color, (stem_x, rect.bottom), (stem_x, rect.y + 18), 4)
            pygame.draw.circle(screen, self.shade_color(color, 35), (stem_x, rect.y + 16), 16)
            pygame.draw.circle(screen, color, (stem_x, rect.y + 16), 10)
        elif kind == "chest":
            pygame.draw.rect(screen, dark, rect.move(4, 4), border_radius=5)
            pygame.draw.rect(screen, color, rect, border_radius=5)
            pygame.draw.rect(screen, dark, rect, 3, border_radius=5)
            pygame.draw.arc(screen, self.shade_color(color, 35), (rect.x, rect.y - 10, rect.width, 32), math.pi, math.tau, 4)
            pygame.draw.rect(screen, (220, 180, 70), (rect.centerx - 6, rect.centery - 4, 12, 10), border_radius=2)
        elif kind == "stool":
            pygame.draw.ellipse(screen, dark, rect.move(4, 5))
            seat = pygame.Rect(rect.x + 3, rect.y, rect.width - 6, rect.height // 2)
            pygame.draw.ellipse(screen, color, seat)
            pygame.draw.ellipse(screen, dark, seat, 2)
            for leg_x in (rect.x + 10, rect.right - 14):
                pygame.draw.line(screen, dark, (leg_x, rect.y + rect.height // 2), (leg_x - 4, rect.bottom), 4)
        elif kind == "cauldron":
            pygame.draw.ellipse(screen, dark, rect.move(5, 5))
            pygame.draw.ellipse(screen, color, rect)
            mouth = rect.inflate(-10, -rect.height // 2)
            mouth.y += 4
            pygame.draw.ellipse(screen, self.shade_color(color, -35), mouth)
            pygame.draw.ellipse(screen, (100, 220, 150), mouth.inflate(-10, -8))
            for i in range(3):
                bubble_x = mouth.x + 15 + i * 14
                bubble_y = mouth.y + 4 - (self.game_time + i * 9) % 12
                pygame.draw.circle(screen, (150, 255, 190), (bubble_x, bubble_y), 3)
        elif kind == "sign":
            pygame.draw.rect(screen, dark, rect.move(4, 4), border_radius=4)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, dark, rect, 3, border_radius=4)
            for i in range(2):
                line_y = rect.y + 14 + i * 14
                pygame.draw.line(screen, self.shade_color(color, -55), (rect.x + 12, line_y), (rect.right - 12, line_y), 2)
        elif kind == "banner":
            pygame.draw.rect(screen, dark, rect.move(4, 4))
            banner_points = [(rect.x, rect.y), (rect.right, rect.y), (rect.right, rect.bottom - 25), (rect.centerx, rect.bottom), (rect.x, rect.bottom - 25)]
            pygame.draw.polygon(screen, color, banner_points)
            pygame.draw.polygon(screen, accent, [(rect.centerx, rect.y + 26), (rect.x + 18, rect.y + 78), (rect.right - 18, rect.y + 78)])
            pygame.draw.polygon(screen, dark, banner_points, 3)
        elif kind == "map":
            pygame.draw.rect(screen, dark, rect.move(5, 5), border_radius=4)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, dark, rect, 3, border_radius=4)
            route = [(rect.x + 25, rect.y + 95), (rect.x + 78, rect.y + 58), (rect.x + 128, rect.y + 82), (rect.x + 196, rect.y + 32)]
            pygame.draw.lines(screen, (138, 48, 42), False, route, 4)
            for point in route:
                pygame.draw.circle(screen, (80, 36, 32), point, 6)
        elif kind == "notice":
            pygame.draw.rect(screen, dark, rect.move(5, 5), border_radius=4)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, dark, rect, 3, border_radius=4)
            for i in range(3):
                note = pygame.Rect(rect.x + 18, rect.y + 16 + i * 42, rect.width - 36, 28)
                pygame.draw.rect(screen, (224, 202, 156), note, border_radius=2)
                pygame.draw.line(screen, (98, 70, 48), (note.x + 8, note.y + 9), (note.right - 8, note.y + 9), 1)
        else:
            pygame.draw.rect(screen, dark, rect.move(4, 4), border_radius=4)
            pygame.draw.rect(screen, color, rect, border_radius=4)
            pygame.draw.rect(screen, dark, rect, 2, border_radius=4)

    def draw_progression_board(self, screen):
        progress = self.get_player_progression_status()
        if not progress:
            return

        panel = pygame.Rect(250, 112, 500, 108)
        color = progress["color"]
        pygame.draw.rect(screen, UI_BG, panel, border_radius=8)
        pygame.draw.rect(screen, color, panel, 3, border_radius=8)

        title = font_small.render(progress["title"], True, color)
        screen.blit(title, (panel.x + 16, panel.y + 10))

        for index, line in enumerate(progress["lines"]):
            text = font_tiny.render(line, True, (225, 225, 215))
            screen.blit(text, (panel.x + 16, panel.y + 38 + index * 21))

    def draw_town_errand_board(self, screen):
        completed_count = len(self.completed_town_errands)
        total_count = get_town_errand_count()
        resident_count = len(self.completed_resident_errands)
        resident_total = get_town_resident_errand_count()
        panel = pygame.Rect(250, 230, 500, 116)
        pygame.draw.rect(screen, UI_BG, panel, border_radius=8)
        pygame.draw.rect(screen, (255, 215, 92), panel, 3, border_radius=8)

        title = font_small.render(
            f"TOWN ERRANDS {completed_count + resident_count}/{total_count + resident_total}  REP {self.town_reputation}",
            True,
            (255, 215, 92),
        )
        screen.blit(title, (panel.x + 16, panel.y + 10))

        service_order = ("inn", "shop", "blacksmith", "library", "house", "stall", "town_hall")
        visible = service_order[:3]
        if completed_count >= 3:
            visible = service_order[3:6]
        if completed_count >= 6:
            visible = service_order[-3:]

        for index, service_type in enumerate(visible):
            errand = get_town_errand(service_type)
            if not errand:
                continue
            status = "DONE" if service_type in self.completed_town_errands else "OPEN"
            color = (150, 230, 150) if status == "DONE" else (225, 225, 215)
            text = font_tiny.render(f"{status}: {errand['title']}", True, color)
            screen.blit(text, (panel.x + 16, panel.y + 42 + index * 22))

    def draw_interior(self, screen):
        room = self.current_interior
        if not room:
            return

        wall_color = room["wall_color"]
        floor_color = room["floor_color"]
        trim_color = room["trim_color"]
        accent_color = room["accent_color"]

        for y in range(0, SCREEN_HEIGHT, 4):
            amount = -50 + int((y / SCREEN_HEIGHT) * 45)
            pygame.draw.rect(screen, self.shade_color(wall_color, amount), (0, y, SCREEN_WIDTH, 4))

        room_rect = pygame.Rect(85, 105, 830, 500)
        back_wall = pygame.Rect(room_rect.x, room_rect.y, room_rect.width, 190)
        floor_top = back_wall.bottom
        floor_points = [
            (room_rect.x, floor_top),
            (room_rect.right, floor_top),
            (room_rect.right + 50, room_rect.bottom),
            (room_rect.x - 50, room_rect.bottom),
        ]
        left_wall = [(room_rect.x, room_rect.y), (room_rect.x, floor_top), (room_rect.x - 50, room_rect.bottom), (room_rect.x - 25, room_rect.y + 35)]
        right_wall = [(room_rect.right, room_rect.y), (room_rect.right, floor_top), (room_rect.right + 50, room_rect.bottom), (room_rect.right + 25, room_rect.y + 35)]

        pygame.draw.rect(screen, self.shade_color(wall_color, -70), room_rect.move(8, 8), border_radius=8)
        pygame.draw.polygon(screen, self.shade_color(wall_color, -18), left_wall)
        pygame.draw.polygon(screen, self.shade_color(wall_color, -28), right_wall)
        pygame.draw.rect(screen, wall_color, back_wall)
        pygame.draw.polygon(screen, floor_color, floor_points)
        pygame.draw.rect(screen, trim_color, room_rect, 5, border_radius=8)
        pygame.draw.line(screen, trim_color, (room_rect.x, floor_top), (room_rect.right, floor_top), 5)

        for x in range(room_rect.x - 40, room_rect.right + 80, 80):
            pygame.draw.line(screen, self.shade_color(floor_color, -18), (x, room_rect.bottom), (room_rect.centerx, floor_top), 1)
        for y in range(floor_top + 45, room_rect.bottom, 45):
            pygame.draw.line(screen, self.shade_color(floor_color, -18), (room_rect.x - 30, y), (room_rect.right + 30, y), 1)

        draw_interior_service_card(
            screen,
            room,
            self.current_interior_service,
            self.player,
            font_tiny,
            UI_BG,
            render_fitted_text,
            wrap_text_to_width,
        )

        exit_rect = INTERIOR_EXIT_ZONE
        pygame.draw.rect(screen, self.shade_color(floor_color, -25), exit_rect, border_radius=6)
        pygame.draw.rect(screen, trim_color, exit_rect, 2, border_radius=6)
        exit_label = font_tiny.render("EXIT", True, (220, 220, 210))
        screen.blit(exit_label, (exit_rect.centerx - exit_label.get_width() // 2, exit_rect.y + 10))

        for prop in room["props"]:
            self.draw_interior_prop(screen, prop, room)

        draw_interior_npc(screen, room, self.current_interior_service, font_tiny, UI_BG)

        nearby_inspect = self.get_nearby_interior_inspect()
        for point in room.get("inspect_points", ()):
            rect = pygame.Rect(point["rect"])
            marker_color = (255, 245, 160) if point is nearby_inspect else self.shade_color(accent_color, 15)
            pygame.draw.circle(screen, marker_color, (rect.centerx, rect.y - 8), 7)
            pygame.draw.circle(screen, UI_BG, (rect.centerx, rect.y - 8), 3)

        if self.player:
            original_x, original_y = self.player.x, self.player.y
            self.player.x = self.interior_player_x
            self.player.y = self.interior_player_y
            self.player.draw(screen)
            self.player.x, self.player.y = original_x, original_y

        title_panel = pygame.Rect(270, 24, 460, 70)
        pygame.draw.rect(screen, UI_BG, title_panel, border_radius=8)
        pygame.draw.rect(screen, accent_color, title_panel, 3, border_radius=8)
        title = font_medium.render(room["title"], True, accent_color)
        subtitle = font_tiny.render(room["subtitle"], True, (220, 220, 210))
        screen.blit(title, (title_panel.centerx - title.get_width() // 2, title_panel.y + 12))
        screen.blit(subtitle, (title_panel.centerx - subtitle.get_width() // 2, title_panel.y + 43))

        service_type = self.current_interior_service["type"] if self.current_interior_service else None
        if service_type == "town_hall":
            self.draw_progression_board(screen)
            self.draw_town_errand_board(screen)

        if self.player:
            # Compact indoor HUD. The renderer receives the usable inside width
            # so HP/MP/EXP labels stay inside the panel instead of overflowing.
            indoor_hud = pygame.Rect(16, 16, 250, 136)
            pygame.draw.rect(screen, UI_BG, indoor_hud, border_radius=8)
            pygame.draw.rect(screen, UI_BORDER, indoor_hud, 3, border_radius=8)
            self.player.draw_stats(screen, indoor_hud.x + 10, indoor_hud.y + 10, indoor_hud.width - 20)

        if self.town_service_message and self.town_service_message_timer > 0:
            message = self.town_service_message
            message_color = (255, 235, 160)
        else:
            flavor = room["flavor"]
            message = flavor[(self.game_time // 240) % len(flavor)]
            message_color = (210, 210, 200)
        draw_interior_message_panel(
            screen,
            room,
            message,
            message_color,
            nearby_inspect,
            self.interior_player_near_npc(),
            is_android(),
            font_tiny,
            UI_BG,
            SCREEN_HEIGHT,
            wrap_text_to_width,
            render_fitted_text,
        )

    def draw_interior_service_menu(self, screen):
        """Draw the active building action menu if it is open."""
        if not self.interior_service_menu_open:
            return
        if not self.interior_service_menu_buttons:
            self.rebuild_interior_service_menu_buttons()
        draw_interior_service_menu_overlay(
            screen,
            self.current_interior,
            self.current_interior_service,
            self.interior_service_menu_buttons,
            self.interior_service_menu_index,
            self.get_current_town_reward_preview(),
            font_large,
            font_small,
            font_tiny,
            UI_BG,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            wrap_text_to_width,
            render_fitted_text,
        )

    def emit_area_particles(self, current_area):
        area_world_x, area_world_y = current_area.get_world_position()
        for profile in AREA_PARTICLE_PROFILES.get(current_area.area_type, ()):
            for _ in range(profile["count"]):
                x = area_world_x + random.randint(0, AREA_WIDTH)
                y = area_world_y + random.randint(0, AREA_HEIGHT)
                velocity = (
                    random.uniform(*profile["velocity_x"]),
                    random.uniform(*profile["velocity_y"]),
                )
                self.particle_system.add_particle(
                    x, y, profile["color"], velocity,
                    profile["size"], profile["lifetime"]
                )

    def describe_area_effect(self, mechanic, health_delta, actual_health, mana_delta, actual_mana):
        effects = []
        if actual_health:
            verb = "restores" if health_delta > 0 else "costs"
            effects.append(f"{verb} {actual_health} HP")
        if actual_mana:
            verb = "restores" if mana_delta > 0 else "drains"
            effects.append(f"{verb} {actual_mana} MP")
        return f"{mechanic['label']} {' and '.join(effects)}."

    def apply_area_mechanics(self, current_area):
        mechanic = AREA_MECHANICS.get(current_area.area_type)
        if not mechanic:
            return

        self.area_effect_timer += 1
        if self.area_effect_timer < mechanic["interval"]:
            return
        self.area_effect_timer = 0

        health_delta = mechanic.get("health", 0)
        mana_delta = mechanic.get("mana", 0)
        actual_health = 0
        actual_mana = 0

        if health_delta > 0:
            before = self.player.health
            self.player.health = min(self.player.max_health, self.player.health + health_delta)
            actual_health = self.player.health - before
        elif health_delta < 0:
            before = self.player.health
            self.player.health = max(1, self.player.health + health_delta)
            actual_health = before - self.player.health

        if mana_delta > 0:
            before = self.player.mana
            self.player.mana = min(self.player.max_mana, self.player.mana + mana_delta)
            actual_mana = self.player.mana - before
        elif mana_delta < 0:
            before = self.player.mana
            self.player.mana = max(0, self.player.mana + mana_delta)
            actual_mana = before - self.player.mana

        if actual_health or actual_mana:
            self.area_effect_message = self.describe_area_effect(
                mechanic, health_delta, actual_health, mana_delta, actual_mana
            )
            self.area_effect_message_timer = 120
            color = mechanic["color"]
            for _ in range(10):
                x = random.randint(self.player.x, self.player.x + PLAYER_SIZE)
                y = random.randint(self.player.y, self.player.y + PLAYER_SIZE)
                self.particle_system.add_particle(
                    x, y, color,
                    (random.uniform(-0.4, 0.4), random.uniform(-0.9, -0.2)),
                    2, 28
                )
    
    def spawn_enemy(self):
        current_area = self.world_map.get_current_area()
        # Don't spawn enemies in town areas
        if current_area and current_area.area_type != "town" and len(current_area.enemies) < 3:
            # Spawn enemy in current area
            enemy = Enemy(self.player.level if self.player else 1)

            # Set enemy type based on area
            available_types = AREA_ENEMY_TYPES.get(
                current_area.area_type, ["fiery", "shadow", "ice"]
            )
            enemy.set_type(random.choice(available_types))
            
            # Position enemy randomly within the current area
            area_world_x, area_world_y = current_area.get_world_position()
            enemy.x = area_world_x + random.randint(100, AREA_WIDTH - 100)
            enemy.y = area_world_y + random.randint(100, AREA_HEIGHT - 100)
            current_area.enemies.append(enemy)
            self.enemies.append(enemy)

    def spawn_story_enemies(self):
        forest_area = self.world_map.areas.get((1, 0))
        if not forest_area:
            return
        if any(getattr(enemy, "enemy_type", None) == "ghost_face" for enemy in forest_area.enemies):
            return

        enemy = Enemy(self.player.level if self.player else 1)
        enemy.set_type("ghost_face")
        level = self.player.level if self.player else 1
        enemy.health = max(enemy.health, 85 + level * 12)
        enemy.max_health = enemy.health
        enemy.strength = max(enemy.strength + 8, 14 + level * 4)
        enemy.speed = max(enemy.speed + 4, 9 + level)
        area_world_x, area_world_y = forest_area.get_world_position()
        enemy.x = area_world_x + (AREA_WIDTH // 2) - (enemy.size // 2)
        enemy.y = area_world_y + (AREA_HEIGHT // 2) - (enemy.size // 2)
        forest_area.enemies.append(enemy)

        if forest_area == self.world_map.get_current_area():
            self.enemies.append(enemy)
    
    def spawn_item(self):
        current_area = self.world_map.get_current_area()
        if current_area and len(current_area.items) < 2:
            # Spawn item in current area
            item = Item()
            # Position item randomly within the current area
            area_world_x, area_world_y = current_area.get_world_position()
            item.x = area_world_x + random.randint(100, AREA_WIDTH - 100)
            item.y = area_world_y + random.randint(100, AREA_HEIGHT - 100)
            current_area.items.append(item)
            self.items.append(item)
    
    def start_transition(self):
        self.transition_state = "in"
        self.transition_alpha = 0
    
    def update(self):
        """
        Main game update loop - called every frame to update all game systems.
        Handles different update logic based on current game state.
        """
        # ========================================
        # VISUAL EFFECTS UPDATES
        # ========================================
        # Update starfield animation
        for star in self.starfield:
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = SCREEN_WIDTH
                star[1] = random.randint(0, SCREEN_HEIGHT)
        
        # Update flying dragons
        for dragon in self.flying_dragons:
            dragon['x'] += dragon['speed']
            dragon['flap'] += 0.05
            if dragon['x'] > SCREEN_WIDTH + 50:
                dragon['x'] = -50
                dragon['y'] = random.randint(0, SCREEN_HEIGHT)
                dragon['speed'] = random.uniform(0.5, 2.0)
        
        # ========================================
        # SYSTEM UPDATES
        # ========================================
        # Update particle effects
        self.particle_system.update()
        if self.state not in ["overworld", "interior"] and self.town_service_message_timer > 0:
            self.town_service_message_timer -= 1
        
        # Update dynamic music system based on game state
        is_boss_battle = (
            self.state == "battle" and 
            self.battle_screen and 
            hasattr(self.battle_screen.enemy, 'enemy_type') and 
            "boss_dragon" in self.battle_screen.enemy.enemy_type
        )
        current_area = self.world_map.get_current_area() if hasattr(self, 'world_map') else None
        self.music.update(self.state, is_boss_battle, current_area)
        
        # ========================================
        # TRANSITION EFFECTS
        # ========================================
        # Handle screen transition animations (fade in/out)
        if self.transition_state == "in":
            self.transition_alpha += self.transition_speed
            if self.transition_alpha >= 255:
                self.transition_alpha = 255
                self.transition_state = "out"
        elif self.transition_state == "out":
            self.transition_alpha -= self.transition_speed
            if self.transition_alpha <= 0:
                self.transition_alpha = 0
                self.transition_state = "none"
        
        # ========================================
        # GAME STATE-SPECIFIC UPDATES
        # ========================================
        if self.state == "start_menu":
            # Title screen with animated dragon
            self.dragon.update()
            self.fire_timer += 1
            if self.fire_timer > 120:
                self.dragon.breathe_fire()
                self.fire_timer = 0
                
        elif self.state == "opening_cutscene":
            # Story introduction sequence
            next_state = self.opening_cutscene.update()
            if next_state:
                self.state = next_state
                
        elif self.state == "character_select":
            # Character selection screen (no updates needed)
            return

        elif self.state == "interior" and self.player:
            if self.show_pause_menu or self.show_inventory:
                return
            self.game_time += 1
            self.player.update_animation()
            if self.town_service_message_timer > 0:
                self.town_service_message_timer -= 1
                
        elif self.state == "overworld" and self.player:
            if self.show_pause_menu or self.show_inventory:
                return
            # Main gameplay area with movement and exploration
            self.game_time += 1
            self.spawn_timer += 1
            self.item_timer += 1
            self.movement_cooldown = max(0, self.movement_cooldown - 1)
            self.player.update_animation()
            if self.pickup_message_timer > 0:
                self.pickup_message_timer -= 1
            if self.area_effect_message_timer > 0:
                self.area_effect_message_timer -= 1
            if self.town_service_message_timer > 0:
                self.town_service_message_timer -= 1
            
            # Update camera to follow player
            self.world_map.update_camera(self.player.x, self.player.y)
            
            # Update area transition effect
            self.world_map.update_transition()
            
            # Check for area transition
            if self.world_map.check_area_transition(self.player.x, self.player.y):
                # Area changed, update enemy and item lists
                current_area = self.world_map.get_current_area()
                self.enemies = current_area.enemies
                self.items = current_area.items
                self.area_effect_timer = 0
                
                # If entering town area, position player at the gate (4 squares lower)
                if current_area and current_area.area_type == "town":
                    area_world_x, area_world_y = current_area.get_world_position()
                    # Position at gate (center horizontally, 4 squares lower)
                    self.player.x = area_world_x + (AREA_WIDTH // 2)  # Center horizontally
                    self.player.y = area_world_y + 260  # 4 squares lower from top (200 + 60 = 260)

                # BEGINNER NOTE: Story area intros start right after the area
                # changes. The dialogue overlay is not a new game state; it is
                # a pause layer on top of the overworld.
                self.trigger_area_story_dialogue(current_area)

            if self.active_story_dialogue:
                # Keep the camera and dialogue visible, but pause enemy spawns,
                # enemy collisions, and item pickups until the player advances
                # through the story text.
                return
            
            # Add area-specific particle effects
            current_area = self.world_map.get_current_area()
            if current_area:
                self.apply_area_mechanics(current_area)
                current_area.particle_timer += 1
                if current_area.particle_timer >= current_area.particle_interval:
                    current_area.particle_timer = 0
                    
                    self.emit_area_particles(current_area)
                    if current_area.area_type == "town":
                        # Town-specific particles (smoke, fountain, leaves)
                        current_area.generate_town_particles(self.particle_system)
                        
                        # Check for town entrance cutscene
                        if current_area.check_entrance_cutscene(self.player.x, self.player.y):
                            print("Town entrance cutscene triggered!")
                        
                        # Update town cutscene if active
                        current_area.update_cutscene()
            
            for item in self.items:
                item.update()
            if self.spawn_timer >= 300:
                self.spawn_enemy()
                self.spawn_timer = 0
            if self.item_timer >= 600:
                self.spawn_item()
                self.item_timer = 0
            for enemy in self.enemies:
                enemy.update(self.player.x, self.player.y)
                enemy.update_animation()
            # --- Check for boss battle after level up ---
            if (
                self.player.just_leveled_up and
                self.player.level > 1 and
                not self.player.boss_cooldown and
                self.player.level > self.player.last_boss_level and
                current_area and current_area.area_type != "town"
            ):
                # At the final milestone, spawn Malakor; earlier levels use named drakes.
                if self.player.level >= FINAL_BOSS_LEVEL:
                    self.battle_screen = BattleScreen(self.player, BossDragon())
                else:
                    self.battle_screen = BattleScreen(self.player, DragonBoss(self.player.level))
                self.battle_screen.start_transition()
                self.state = "battle"
                self.player.boss_cooldown = True  # Prevent immediate retrigger
                self.player.just_leveled_up = False
                return
            for enemy in self.enemies[:]:
                if self.player:  # Ensure player exists
                    player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.size, enemy.size)
                    if player_rect.colliderect(enemy_rect):
                        self.battle_screen = BattleScreen(self.player, enemy)
                        self.battle_screen.start_transition()
                        self.state = "battle"
                        # Remove enemy from both lists
                        self.enemies.remove(enemy)
                        current_area = self.world_map.get_current_area()
                        if current_area and enemy in current_area.enemies:
                            current_area.enemies.remove(enemy)
                        self.player_moved = False
                        break
            for item in self.items[:]:
                if self.player:  # Ensure player exists
                    item_rect = pygame.Rect(item.x, item.y, ITEM_SIZE, ITEM_SIZE)
                    player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                    if player_rect.colliderect(item_rect):
                        self.apply_world_item(item)
                        self.player.items_collected += 1
                        # Remove item from both lists
                        if item in self.items:
                            self.items.remove(item)
                        current_area = self.world_map.get_current_area()
                        if current_area and item in current_area.items:
                            current_area.items.remove(item)
    
    def draw(self, screen):
        screen.fill(BACKGROUND)
        
        # Draw starfield background
        for x, y, speed in self.starfield:
            alpha = min(255, int(speed * 100))
            pygame.draw.circle(screen, (200, 200, 255, alpha), (int(x), int(y)), 1)
        
        # Draw flying dragons
        for dragon in self.flying_dragons:
            wing_offset = math.sin(dragon['flap']) * dragon['size']
            color = (200, 200, 255, min(255, int(dragon['size'] * 40)))
            
            pygame.draw.line(
                screen, color,
                (dragon['x'], dragon['y']),
                (dragon['x'] + 5 * dragon['size'], dragon['y']),
                max(1, dragon['size'] // 2)
            )
            
            pygame.draw.line(
                screen, color,
                (dragon['x'] + 2 * dragon['size'], dragon['y']),
                (dragon['x'] + dragon['size'], dragon['y'] - 3 * dragon['size'] - wing_offset),
                max(1, dragon['size'] // 2)
            )
            pygame.draw.line(
                screen, color,
                (dragon['x'] + 2 * dragon['size'], dragon['y']),
                (dragon['x'] + dragon['size'], dragon['y'] + 3 * dragon['size'] + wing_offset),
                max(1, dragon['size'] // 2)
            )
            
            pygame.draw.line(
                screen, color,
                (dragon['x'] + 5 * dragon['size'], dragon['y']),
                (dragon['x'] + 7 * dragon['size'], dragon['y'] - dragon['size']),
                max(1, dragon['size'] // 2)
            )
            
            pygame.draw.line(
                screen, color,
                (dragon['x'], dragon['y']),
                (dragon['x'] - 2 * dragon['size'], dragon['y'] + dragon['size']),
                max(1, dragon['size'] // 2)
            )
        
        if self.state == "start_menu":
            self.reset_menu_buttons()
            self.set_selected_buttons(
                self.start_menu_buttons(),
                self.start_menu_index,
            )
            
            title = font_large.render("DRAGON'S LAIR", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            
            subtitle = font_medium.render("A RETRO RPG ADVENTURE", True, TEXT_COLOR)
            screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
            
            self.dragon.draw(screen, boss_level=self.get_title_dragon_boss_level())
            self.draw_title_dragon_progress_badge(screen)
            
            self.start_button.draw(screen)
            self.load_button.draw(screen)
            self.update_button.draw(screen)
            self.quit_button.draw(screen)
            
            instructions = [
                "SELECT YOUR HERO AND EMBARK ON A QUEST",
                "DEFEAT THE DRAGON'S MINIONS AND SURVIVE!",
                "ARROWS/WASD OR TOUCH: MOVE    ENTER/SPACE: SELECT",
            ]
            
            for i, line in enumerate(instructions):
                text = font_tiny.render(line, True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 320 + i*24))

            update_color = (255, 215, 0) if self.update_available else (180, 180, 200)
            update_text = render_fitted_text(self.update_status, update_color, 760, (font_tiny,))

            # BEGINNER NOTE: This is only status text. The button click itself
            # is handled in activate_start_menu_selection() -> open_update_link().
            screen.blit(update_text, (SCREEN_WIDTH//2 - update_text.get_width()//2, 640))

            if self.town_service_message and self.town_service_message_timer > 0:
                message_text = font_tiny.render(self.town_service_message, True, (255, 235, 160))
                msg_rect = pygame.Rect(SCREEN_WIDTH//2 - 260, 660, 520, 30)
                pygame.draw.rect(screen, UI_BG, msg_rect, border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), msg_rect, 2, border_radius=6)
                screen.blit(message_text, (msg_rect.centerx - message_text.get_width() // 2, msg_rect.y + 6))
            
        elif self.state == "opening_cutscene":
            # Draw the opening cutscene
            self.opening_cutscene.draw(screen)
            
        elif self.state == "character_select":
            self.set_button(self.back_button, "BACK", pygame.Rect(20, 20, 100, 40))
            self.set_selected_buttons(
                [self.warrior_button, self.mage_button, self.rogue_button, self.back_button],
                self.character_menu_index,
            )
            title = font_large.render("CHOOSE YOUR HERO", True, TEXT_COLOR)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            
            warrior_desc = [
                "THE WARRIOR",
                "- HIGH HEALTH",
                "- STRONG ATTACKS",
                "- GOOD DEFENSE",
                "- MEDIUM SPEED"
            ]
            
            mage_desc = [
                "THE MAGE",
                "- HIGH MANA",
                "- MAGIC ATTACKS",
                "- LOW DEFENSE",
                "- MEDIUM SPEED"
            ]
            
            rogue_desc = [
                "THE ROGUE",
                "- BALANCED STATS",
                "- QUICK ATTACKS",
                "- AVERAGE DEFENSE",
                "- HIGH SPEED"
            ]
            
            y_pos = 480
            for line in warrior_desc:
                text = font_tiny.render(line, True, (0, 255, 0))
                screen.blit(text, (SCREEN_WIDTH//2 - 300, y_pos))
                y_pos += 25
            
            y_pos = 480
            for line in mage_desc:
                text = font_tiny.render(line, True, (0, 200, 255))
                screen.blit(text, (SCREEN_WIDTH//2 - 50, y_pos))
                y_pos += 25
            
            y_pos = 480
            for line in rogue_desc:
                text = font_tiny.render(line, True, (255, 100, 0))
                screen.blit(text, (SCREEN_WIDTH//2 + 200, y_pos))
                y_pos += 25
            
            # BEGINNER NOTE: Character select previews use the same imported
            # PNG files as the overworld and battle screens. If you replace
            # assets/processed/characters/mage.png, this menu updates too.
            character_cards = [
                (self.warrior_button, "Warrior", (0, 255, 0)),
                (self.mage_button, "Mage", (0, 200, 255)),
                (self.rogue_button, "Rogue", (255, 100, 0)),
            ]
            for card_index, (button, char_type, label_color) in enumerate(character_cards):
                button.draw(screen)
                draw_character_sprite(
                    screen,
                    char_type,
                    button.rect.centerx,
                    button.rect.y + 120,
                    116,
                )

                label_rect = pygame.Rect(button.rect.x + 12, button.rect.bottom - 34, button.rect.width - 24, 26)
                pygame.draw.rect(screen, UI_BG, label_rect, border_radius=5)
                border_color = (255, 215, 0) if self.character_menu_index == card_index else label_color
                pygame.draw.rect(screen, border_color, label_rect, 1, border_radius=5)
                label = font_tiny.render(char_type.upper(), True, label_color)
                screen.blit(label, (label_rect.centerx - label.get_width() // 2, label_rect.y + 5))

            self.back_button.draw(screen)
            
        elif self.state == "overworld" and self.player:
            # Draw world background
            current_area = self.world_map.get_current_area()
            if current_area:
                screen.fill(current_area.background_color)
                # Draw town if this is a town area
                if current_area.area_type == "town":
                    current_area.draw_town(screen)
            else:
                screen.fill(BACKGROUND)

            # Draw area boundaries more prominently
            pygame.draw.rect(screen, (255, 255, 255), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 3)
            
            # Draw items (convert world coordinates to screen coordinates)
            for item in self.items:
                screen_x, screen_y = self.world_map.world_to_screen(item.x, item.y)
                if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                    # Temporarily set item position for drawing
                    original_x, original_y = item.x, item.y
                    item.x, item.y = screen_x, screen_y
                    item.draw(screen)
                    item.x, item.y = original_x, original_y
                
            # Draw enemies (convert world coordinates to screen coordinates)
            for enemy in self.enemies:
                screen_x, screen_y = self.world_map.world_to_screen(enemy.x, enemy.y)
                if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
                    # Temporarily set enemy position for drawing
                    original_x, original_y = enemy.x, enemy.y
                    enemy.x, enemy.y = screen_x, screen_y
                    enemy.draw(screen)
                    enemy.x, enemy.y = original_x, original_y

            # BEGINNER NOTE: Friendly story NPCs are drawn separately from
            # enemies so they never start battles by touching the player.
            self.draw_story_npcs(screen, current_area)
            self.draw_town_population(screen, current_area)
            self.draw_town_service_marker(screen, current_area)
            
            # Draw player (convert world coordinates to screen coordinates)
            screen_x, screen_y = self.world_map.world_to_screen(self.player.x, self.player.y)
            original_x, original_y = self.player.x, self.player.y
            self.player.x, self.player.y = screen_x, screen_y
            self.player.draw(screen)
            self.player.x, self.player.y = original_x, original_y

            # Draw particles
            self.particle_system.draw(screen, self.world_map)
            
            # Draw area transition effect
            if self.world_map.transitioning:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, self.world_map.area_transition_alpha))
                screen.blit(overlay, (0, 0))
            
            # Draw world map overlay
            if self.show_world_map:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                # Draw world map grid
                map_size = 300
                map_x = (SCREEN_WIDTH - map_size) // 2
                map_y = (SCREEN_HEIGHT - map_size) // 2
                cell_size = map_size // 3
                
                # Draw background
                pygame.draw.rect(screen, UI_BG, (map_x, map_y, map_size, map_size), border_radius=8)
                pygame.draw.rect(screen, UI_BORDER, (map_x, map_y, map_size, map_size), 3, border_radius=8)
                
                # Draw areas
                for y in range(3):
                    for x in range(3):
                        area = self.world_map.areas.get((x, y))
                        if area:
                            cell_x = map_x + x * cell_size
                            cell_y = map_y + y * cell_size
                            
                            # Color based on area type and visited status
                            if area == self.world_map.get_current_area():
                                color = (100, 255, 100)  # Current area - bright green
                            elif area.visited:
                                color = (50, 150, 50)    # Visited area - dark green
                            else:
                                color = (50, 50, 50)     # Unvisited area - dark gray
                            
                            pygame.draw.rect(screen, color, (cell_x + 2, cell_y + 2, cell_size - 4, cell_size - 4))
                            pygame.draw.rect(screen, UI_BORDER, (cell_x, cell_y, cell_size, cell_size), 1)
                            
                            # Draw area name
                            name_text = font_tiny.render(area.area_type[:3].upper(), True, TEXT_COLOR)
                            text_x = cell_x + (cell_size - name_text.get_width()) // 2
                            text_y = cell_y + (cell_size - name_text.get_height()) // 2
                            screen.blit(name_text, (text_x, text_y))
                
                # Draw player position
                player_world_x, player_world_y = self.player.x, self.player.y
                player_area_x = player_world_x // AREA_WIDTH
                player_area_y = player_world_y // AREA_HEIGHT
                player_cell_x = map_x + player_area_x * cell_size + cell_size // 2
                player_cell_y = map_y + player_area_y * cell_size + cell_size // 2
                pygame.draw.circle(screen, (255, 255, 0), (player_cell_x, player_cell_y), 4)
                
                # Draw title
                title = font_medium.render("WORLD MAP", True, TEXT_COLOR)
                screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, map_y - 40))
                
                # Draw instructions
                instructions = font_tiny.render("Press M to close", True, (180, 180, 200))
                screen.blit(instructions, (SCREEN_WIDTH//2 - instructions.get_width()//2, map_y + map_size + 10))
            
            # Draw the top-left player HUD. The panel is intentionally wider
            # than the old one so long HP/MP values still have breathing room.
            hud_panel = pygame.Rect(10, 10, 280, 144)
            pygame.draw.rect(screen, UI_BG, hud_panel, border_radius=8)
            pygame.draw.rect(screen, UI_BORDER, hud_panel, 3, border_radius=8)
            
            # Draw player stats inside the panel's padding.
            self.player.draw_stats(screen, hud_panel.x + 10, hud_panel.y + 10, hud_panel.width - 20)

            if self.pickup_message and self.pickup_message_timer > 0:
                message_text = font_small.render(self.pickup_message, True, (255, 215, 0))
                panel_width = max(260, message_text.get_width() + 24)
                pygame.draw.rect(screen, UI_BG, (20, 170, panel_width, 38), border_radius=6)
                pygame.draw.rect(screen, (255, 215, 0), (20, 170, panel_width, 38), 2, border_radius=6)
                screen.blit(message_text, (32, 178))

            progression = self.get_player_progression_status()
            if progression:
                quest_text = font_tiny.render(progression["short"], True, progression["color"])
                panel_width = max(360, quest_text.get_width() + 24)
                pygame.draw.rect(screen, UI_BG, (20, 215, panel_width, 30), border_radius=6)
                pygame.draw.rect(screen, progression["color"], (20, 215, panel_width, 30), 2, border_radius=6)
                screen.blit(quest_text, (32, 222))
            
            # Draw score and other info
            score_text = font_medium.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
            
            time_text = font_small.render(f"TIME: {self.game_time//FPS}s", True, TEXT_COLOR)
            screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 60))
            
            kills_text = font_small.render(f"KILLS: {self.player.kills}", True, TEXT_COLOR)
            screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 20, 90))
            
            # Draw area information
            current_area = self.world_map.get_current_area()
            if current_area:
                area_text = font_small.render(f"AREA: {current_area.area_type.upper()}", True, TEXT_COLOR)
                screen.blit(area_text, (SCREEN_WIDTH - area_text.get_width() - 20, 120))
                
                desc = AREA_DESCRIPTIONS.get(current_area.area_type, "")
                if desc:
                    desc_text = font_tiny.render(desc, True, (180, 180, 200))
                    screen.blit(desc_text, (SCREEN_WIDTH - desc_text.get_width() - 20, 145))

                mechanic = AREA_MECHANICS.get(current_area.area_type)
                if mechanic:
                    effect_text = font_tiny.render(f"EFFECT: {mechanic['label']}", True, mechanic["color"])
                    screen.blit(effect_text, (SCREEN_WIDTH - effect_text.get_width() - 20, 165))

                if self.area_effect_message and self.area_effect_message_timer > 0:
                    effect_message = font_tiny.render(self.area_effect_message, True, mechanic["color"] if mechanic else (220, 220, 180))
                    screen.blit(effect_message, (SCREEN_WIDTH - effect_message.get_width() - 20, 185))

                service = current_area.get_nearby_town_service(self.player.x, self.player.y)
                if service:
                    service_text = font_tiny.render(service["prompt"], True, (255, 215, 0))
                    screen.blit(service_text, (20, SCREEN_HEIGHT - 210))
                else:
                    resident = self.get_nearby_town_resident(current_area)
                    if resident:
                        _, resident_profile = resident
                        resident_text = font_tiny.render(resident_profile["prompt"], True, (255, 230, 150))
                        screen.blit(resident_text, (20, SCREEN_HEIGHT - 210))

                if self.town_service_message and self.town_service_message_timer > 0:
                    message_text = font_tiny.render(self.town_service_message, True, (255, 235, 160))
                    pygame.draw.rect(screen, UI_BG, (20, SCREEN_HEIGHT - 245, max(420, message_text.get_width() + 24), 32), border_radius=6)
                    pygame.draw.rect(screen, (255, 215, 0), (20, SCREEN_HEIGHT - 245, max(420, message_text.get_width() + 24), 32), 2, border_radius=6)
                    screen.blit(message_text, (32, SCREEN_HEIGHT - 237))
                
                # Draw mini-map
                mini_map_size = 80
                mini_map_x = SCREEN_WIDTH - mini_map_size - 20
                mini_map_y = 210
                
                # Draw mini-map background
                pygame.draw.rect(screen, UI_BG, (mini_map_x, mini_map_y, mini_map_size, mini_map_size), border_radius=4)
                pygame.draw.rect(screen, UI_BORDER, (mini_map_x, mini_map_y, mini_map_size, mini_map_size), 2, border_radius=4)
                
                # Draw visited areas
                cell_size = mini_map_size // 3
                for y in range(3):
                    for x in range(3):
                        area = self.world_map.areas.get((x, y))
                        if area and area.visited:
                            color = (100, 200, 100) if area == current_area else (50, 100, 50)
                            pygame.draw.rect(screen, color, 
                                           (mini_map_x + x * cell_size, mini_map_y + y * cell_size, 
                                            cell_size, cell_size))
                            pygame.draw.rect(screen, UI_BORDER, 
                                           (mini_map_x + x * cell_size, mini_map_y + y * cell_size, 
                                            cell_size, cell_size), 1)
            
            # Draw town entrance cutscene if active
            current_area = self.world_map.get_current_area()
            if current_area and current_area.cutscene_active:
                current_area.draw_cutscene(screen)
            
            # Draw desktop controls only. Android/touch play uses the visible
            # on-screen buttons instead of a keyboard legend in the corner.
            if not self.android_touch_enabled:
                controls = [
                    "CONTROLS:",
                    "ARROWS/WASD - MOVE",
                    "SPACE/ENTER - INTERACT",
                    "J - LOG / M - MAP",
                    "F5 SAVE / F9 LOAD",
                    "ESC - MENU",
                ]

                for i, line in enumerate(controls):
                    text = font_tiny.render(line, True, (180, 180, 200))
                    screen.blit(text, (20, SCREEN_HEIGHT - 140 + i * 25))

        elif self.state == "interior" and self.player:
            self.draw_interior(screen)
            
        elif self.state == "battle" and self.battle_screen:
            self.battle_screen.draw(screen)
            
        elif self.state == "game_over" and self.player:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            title = font_large.render("GAME OVER", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
            
            stats = [
                f"HERO: {self.player.type}",
                f"LEVEL: {self.player.level}",
                f"SCORE: {self.score}",
                f"KILLS: {self.player.kills}",
                f"ITEMS: {self.player.items_collected}",
                f"TIME: {self.game_time//FPS} SECONDS"
            ]
            
            y_pos = 220
            for stat in stats:
                text = font_medium.render(stat, True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 40
                
            # Play again button
            self.start_button.text = "PLAY AGAIN"
            self.start_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 20, 240, 60)
            self.start_button.text_surf = font_medium.render(self.start_button.text, True, TEXT_COLOR)
            self.start_button.text_rect = self.start_button.text_surf.get_rect(center=self.start_button.rect.center)
            self.set_selected_buttons([self.start_button, self.back_button], self.end_menu_index)
            self.start_button.draw(screen)
            
            # Back to menu button
            self.back_button.text = "BACK TO MENU"
            self.back_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 100, 240, 60)
            self.back_button.text_surf = font_medium.render(self.back_button.text, True, TEXT_COLOR)
            self.back_button.text_rect = self.back_button.text_surf.get_rect(center=self.back_button.rect.center)
            self.set_selected_buttons([self.start_button, self.back_button], self.end_menu_index)
            self.back_button.draw(screen)
            
        if self.show_journal and self.state in ["overworld", "interior"] and self.player:
            self.draw_journal(screen)

        if self.show_inventory and self.state in ["overworld", "interior"] and self.player:
            self.draw_inventory(screen)

        if self.active_story_dialogue and self.state == "overworld":
            self.draw_story_dialogue(screen)

        if self.interior_service_menu_open and self.state == "interior":
            self.draw_interior_service_menu(screen)

        if self.show_pause_menu and self.state in ["overworld", "interior"]:
            self.draw_pause_menu(screen)

        if self.transition_state != "none":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(overlay, (0, 0))
            
        # BEGINNER NOTE:
        # Android touch buttons are built fresh each frame so the layout can
        # change for dialogue, journal, map, and normal exploration.
        if self.android_touch_enabled:
            touch_buttons = build_android_touch_buttons(self, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw_android_touch_buttons(screen, touch_buttons, font_small, font_tiny)
        
        if self.state == "victory" and self.player:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 220))
            screen.blit(overlay, (0, 0))
            title = font_large.render("YOU WIN!", True, (255, 255, 0))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
            stats = [
                f"HERO: {self.player.type}",
                f"LEVEL: {self.player.level}",
                f"SCORE: {self.score}",
                f"KILLS: {self.player.kills}",
                f"ITEMS: {self.player.items_collected}",
                f"TIME: {self.game_time//FPS} SECONDS"
            ]
            y_pos = 240
            for stat in stats:
                text = font_medium.render(stat, True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 40
            win_text = font_medium.render("Congratulations! You defeated Malakor!", True, (255, 215, 0))
            screen.blit(win_text, (SCREEN_WIDTH//2 - win_text.get_width()//2, y_pos + 40))
            
            # Play again button
            self.start_button.text = "PLAY AGAIN"
            self.start_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 80, 240, 60)
            self.start_button.text_surf = font_medium.render(self.start_button.text, True, TEXT_COLOR)
            self.start_button.text_rect = self.start_button.text_surf.get_rect(center=self.start_button.rect.center)
            self.set_selected_buttons([self.start_button, self.back_button], self.end_menu_index)
            self.start_button.draw(screen)
            
            # Back to menu button
            self.back_button.text = "BACK TO MENU"
            self.back_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 160, 240, 60)
            self.back_button.text_surf = font_medium.render(self.back_button.text, True, TEXT_COLOR)
            self.back_button.text_rect = self.back_button.text_surf.get_rect(center=self.back_button.rect.center)
            self.set_selected_buttons([self.start_button, self.back_button], self.end_menu_index)
            self.back_button.draw(screen)
        
        present_frame()
    
    def run(self):
        running = True
        
        while running:
            mouse_pos = get_game_mouse_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                    # BEGINNER NOTE:
                    # Android touch buttons are not part of the normal menu
                    # Button class. We detect them here and then translate the
                    # touch into the same action system used by the keyboard.
                    if self.android_touch_enabled:
                        # BEGINNER NOTE:
                        # Android can report touch coordinates in two different
                        # spaces: real device pixels or this game's fixed
                        # 1000x700 screen. We test both positions so visible
                        # buttons and clickable areas stay lined up.
                        raw_touch_pos = event.pos
                        mapped_touch_pos = display_to_game_pos(raw_touch_pos)
                        if (
                            display_surface is not screen
                            and 0 <= raw_touch_pos[0] <= SCREEN_WIDTH
                            and 0 <= raw_touch_pos[1] <= SCREEN_HEIGHT
                        ):
                            touch_positions = (raw_touch_pos, mapped_touch_pos)
                        else:
                            touch_positions = (mapped_touch_pos, raw_touch_pos)
                        touch_buttons = build_android_touch_buttons(self, SCREEN_WIDTH, SCREEN_HEIGHT)
                        touched_button = find_android_touch_button_at_positions(touch_buttons, touch_positions)
                        if touched_button and self.handle_android_touch_command(touched_button["action"]):
                            mouse_click = False
                            continue

                    if self.state == "opening_cutscene":
                        self.opening_cutscene.skip()
                        continue

                    if self.state == "battle" and self.battle_screen:
                        self.battle_screen.handle_input(event, self)
                        mouse_click = False
                        continue
                
                if event.type == pygame.KEYDOWN:
                    action = action_for_key(event.key)

                    if action == LOAD and self.state in ["start_menu", "overworld", "interior", "game_over", "victory"]:
                        self.load_saved_game()
                        continue
                    if action == SAVE and self.state in ["overworld", "interior"]:
                        self.save_current_game()
                        continue

                    if self.state == "start_menu":
                        if action in [MOVE_UP, MOVE_LEFT]:
                            self.move_menu_selection("start_menu_index", len(self.start_menu_buttons()), -1)
                            continue
                        if action in [MOVE_DOWN, MOVE_RIGHT]:
                            self.move_menu_selection("start_menu_index", len(self.start_menu_buttons()), 1)
                            continue
                        if action in [CONFIRM, INTERACT]:
                            running = self.activate_start_menu_selection()
                            continue
                        if action == CANCEL:
                            running = False
                            continue

                    if self.state == "character_select":
                        if action in [MOVE_UP, MOVE_LEFT]:
                            self.move_menu_selection("character_menu_index", 4, -1)
                            continue
                        if action in [MOVE_DOWN, MOVE_RIGHT]:
                            self.move_menu_selection("character_menu_index", 4, 1)
                            continue
                        if action in [CONFIRM, INTERACT]:
                            self.activate_character_menu_selection()
                            continue

                    if self.state in ["game_over", "victory"]:
                        if action in [MOVE_UP, MOVE_LEFT, MOVE_DOWN, MOVE_RIGHT]:
                            self.move_menu_selection("end_menu_index", 2, 1)
                            continue
                        if action in [CONFIRM, INTERACT]:
                            self.activate_end_menu_selection()
                            continue

                    if self.show_pause_menu and self.state in ["overworld", "interior"]:
                        if not self.pause_menu_buttons:
                            self.rebuild_pause_menu_buttons()
                        if action in [MOVE_UP, MOVE_LEFT]:
                            self.move_menu_selection("pause_menu_index", len(self.pause_menu_buttons), -1)
                            continue
                        if action in [MOVE_DOWN, MOVE_RIGHT]:
                            self.move_menu_selection("pause_menu_index", len(self.pause_menu_buttons), 1)
                            continue
                        if action in [CONFIRM, INTERACT]:
                            self.activate_pause_menu_selection()
                            continue
                        if action == JOURNAL:
                            self.activate_pause_menu_command("journal")
                            continue
                        if action == MAP and self.state == "overworld":
                            self.activate_pause_menu_command("map")
                            continue
                        if action == CANCEL:
                            self.close_pause_menu(play_sound=True)
                            continue

                    if self.interior_service_menu_open and self.state == "interior":
                        if not self.interior_service_menu_buttons:
                            self.rebuild_interior_service_menu_buttons()
                        if action in [MOVE_UP, MOVE_LEFT]:
                            self.move_menu_selection(
                                "interior_service_menu_index",
                                len(self.interior_service_menu_buttons),
                                -1,
                            )
                            continue
                        if action in [MOVE_DOWN, MOVE_RIGHT]:
                            self.move_menu_selection(
                                "interior_service_menu_index",
                                len(self.interior_service_menu_buttons),
                                1,
                            )
                            continue
                        if action in [CONFIRM, INTERACT]:
                            self.activate_interior_service_menu_selection()
                            continue
                        if action == JOURNAL:
                            self.activate_interior_service_menu_command("journal")
                            continue
                        if action == CANCEL:
                            self.close_interior_service_menu(play_sound=True)
                            continue
                        continue

                    if self.active_story_dialogue and self.state == "overworld":
                        if action in [CONFIRM, INTERACT, CANCEL]:
                            self.advance_story_dialogue()
                        continue

                    if self.show_journal and self.state in ["overworld", "interior"]:
                        if action in [CANCEL, CONFIRM, INTERACT, JOURNAL, MAP]:
                            self.show_journal = False
                            if self.SFX_CLICK:
                                self.SFX_CLICK.play()
                        continue

                    if self.show_inventory and self.state in ["overworld", "interior"]:
                        if action == MOVE_LEFT:
                            self.move_inventory_slot(-1)
                            continue
                        if action == MOVE_RIGHT:
                            self.move_inventory_slot(1)
                            continue
                        if action == MOVE_UP:
                            self.move_inventory_selection(-1)
                            continue
                        if action == MOVE_DOWN:
                            self.move_inventory_selection(1)
                            continue
                        if action == CONFIRM:
                            self.equip_inventory_selection()
                            continue
                        if action == INTERACT:
                            self.unequip_inventory_slot()
                            continue
                        if action in [CANCEL, JOURNAL, MAP]:
                            self.show_inventory = False
                            if self.SFX_CLICK:
                                self.SFX_CLICK.play()
                        continue

                    if self.show_world_map and self.state == "overworld":
                        if action in [CANCEL, CONFIRM, INTERACT, MAP]:
                            self.show_world_map = False
                            if self.SFX_CLICK:
                                self.SFX_CLICK.play()
                        continue

                    if action == JOURNAL and self.state in ["overworld", "interior"] and self.player:
                        self.show_journal = True
                        self.show_inventory = False
                        self.show_world_map = False
                        if self.SFX_CLICK:
                            self.SFX_CLICK.play()
                        continue

                    if action == CANCEL:
                        if self.state in ["overworld", "interior"] and self.player:
                            self.toggle_pause_menu()
                            continue
                        elif self.state == "game_over":
                            self.state = "start_menu"
                            continue
                        elif self.state == "character_select":
                            self.state = "start_menu"
                            continue
                        elif self.state == "opening_cutscene":
                            self.opening_cutscene.skip()
                            continue
                    
                    # Handle skip for cutscene
                    if self.state == "opening_cutscene":
                        self.opening_cutscene.skip()
                        continue

                    if self.state == "interior" and self.player:
                        if action in MOVE_DELTAS:
                            dx, dy = MOVE_DELTAS[action]
                            self.move_interior_player(dx, dy)
                            continue
                        if action == INTERACT:
                            self.use_current_town_service()
                            continue
                        if action == CONFIRM:
                            player_rect = pygame.Rect(self.interior_player_x, self.interior_player_y, PLAYER_SIZE, PLAYER_SIZE)
                            if self.interior_player_near_npc():
                                self.talk_to_current_npc()
                            elif self.inspect_current_interior_point():
                                continue
                            elif player_rect.colliderect(INTERIOR_EXIT_ZONE):
                                self.exit_town_interior()
                            else:
                                self.exit_town_interior()
                            continue
                    
                    # Handle world map toggle
                    if self.state == "overworld" and action == MAP:
                        self.show_world_map = not self.show_world_map
                        self.show_journal = False
                        if self.SFX_CLICK:
                            self.SFX_CLICK.play()
                        continue
                    
                    # Handle movement in overworld
                    if self.state == "overworld" and self.player and self.movement_cooldown <= 0 and action in MOVE_DELTAS:
                        original_x = self.player.x
                        original_y = self.player.y
                        dx, dy = MOVE_DELTAS[action]
                        if self.SFX_ARROW:
                            self.SFX_ARROW.play()
                        self.player.move(dx, dy)
                        current_area = self.world_map.get_current_area()
                        if current_area and current_area.check_building_collision(self.player.x, self.player.y):
                            self.player.x = original_x
                            self.player.y = original_y
                        else:
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        continue
                    
                    # Handle town cutscene dialogue advancement and town service entry
                    if self.state == "overworld" and action in [INTERACT, CONFIRM] and self.player:
                        current_area = self.world_map.get_current_area()
                        if (
                            current_area and
                            current_area.cutscene_active and
                            current_area.cutscene_phase < 2 and
                            current_area.guard
                        ):
                            current_area.guard["current_dialogue"] += 1
                            current_area.cutscene_timer = 0
                            if current_area.guard["current_dialogue"] >= len(current_area.guard["dialogue"]):
                                current_area.cutscene_phase = 2
                                current_area.cutscene_active = False
                                current_area.guard["visible"] = False
                        elif current_area:
                            service = current_area.get_nearby_town_service(self.player.x, self.player.y)
                            if service:
                                self.enter_town_interior(service)
                            else:
                                town_resident = self.get_nearby_town_resident(current_area)
                                if town_resident:
                                    resident_key, resident = town_resident
                                    self.talk_to_town_resident(resident_key, resident)
                                else:
                                    story_npc = self.get_nearby_story_npc(current_area)
                                    if story_npc:
                                        _, npc = story_npc
                                        dialogue_key = npc.get("dialogue_key")
                                        repeat = dialogue_key in self.seen_story_dialogues
                                        self.start_story_dialogue(dialogue_key, repeat=repeat)
                        continue
                    
                    # Pass input to battle screen
                    if self.state == "battle" and self.battle_screen:
                        self.battle_screen.handle_input(event, self)
            
            # Handle button clicks
            if self.interior_service_menu_open and self.state == "interior":
                if not self.interior_service_menu_buttons:
                    self.rebuild_interior_service_menu_buttons()
                for index, button in enumerate(self.interior_service_menu_buttons):
                    if button.update(mouse_pos):
                        self.interior_service_menu_index = index
                    if button.is_clicked(mouse_pos, mouse_click):
                        self.interior_service_menu_index = index
                        self.activate_interior_service_menu_selection()
                        mouse_click = False
                        break

            elif self.show_pause_menu and self.state in ["overworld", "interior"]:
                if not self.pause_menu_buttons:
                    self.rebuild_pause_menu_buttons()
                for index, button in enumerate(self.pause_menu_buttons):
                    if button.update(mouse_pos):
                        self.pause_menu_index = index
                    if button.is_clicked(mouse_pos, mouse_click):
                        self.pause_menu_index = index
                        self.activate_pause_menu_selection()
                        mouse_click = False
                        break

            elif self.state == "start_menu":
                if self.start_button.update(mouse_pos):
                    self.start_menu_index = 0
                if self.load_button.update(mouse_pos):
                    self.start_menu_index = 1
                if self.update_button.update(mouse_pos):
                    self.start_menu_index = 2
                if self.quit_button.update(mouse_pos):
                    self.start_menu_index = 3
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    self.start_menu_index = 0
                    self.activate_start_menu_selection()

                if self.load_button.is_clicked(mouse_pos, mouse_click):
                    self.start_menu_index = 1
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.load_saved_game()

                if self.update_button.is_clicked(mouse_pos, mouse_click):
                    self.start_menu_index = 2
                    self.activate_start_menu_selection()
                    
                if self.quit_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    running = False
                    
            elif self.state == "character_select":
                if self.warrior_button.update(mouse_pos):
                    self.character_menu_index = 0
                if self.mage_button.update(mouse_pos):
                    self.character_menu_index = 1
                if self.rogue_button.update(mouse_pos):
                    self.character_menu_index = 2
                if self.back_button.update(mouse_pos):
                    self.character_menu_index = 3
                
                if self.warrior_button.is_clicked(mouse_pos, mouse_click):
                    self.choose_hero("Warrior")
                    
                if self.mage_button.is_clicked(mouse_pos, mouse_click):
                    self.choose_hero("Mage")
                    
                if self.rogue_button.is_clicked(mouse_pos, mouse_click):
                    self.choose_hero("Rogue")
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.state = "start_menu"
                    
            elif self.state == "battle":
                battle_ended = self.battle_screen.update()
                
                if battle_ended:
                    # Boss battle win
                    if hasattr(self.battle_screen.enemy, 'enemy_type') and "boss_dragon" in self.battle_screen.enemy.enemy_type:
                        if self.battle_screen.result == "win":
                            self.player.just_leveled_up = False
                            self.player.kills += 1
                            defeated_boss_level = getattr(self.battle_screen.enemy, "boss_level", self.player.level)
                            reward = get_boss_reward(self.battle_screen.enemy)
                            exp_reward = reward["exp"]
                            score_reward = reward["score"]
                            self.player.gain_exp(exp_reward)
                            self.score += score_reward
                            self.player.add_inventory_item("health")
                            self.player.add_inventory_item("mana")
                            self.set_town_service_message(reward["message"])
                            self.player.boss_cooldown = True  # Set cooldown after boss battle
                            self.player.last_boss_level = max(self.player.last_boss_level, defeated_boss_level)
                            if self.battle_screen.enemy.enemy_type == "boss_dragon":
                                self.boss_defeated = True
                                self.state = "victory"
                                self.battle_screen = None
                                self.music.update(self.state, False)  # Explicitly reset music state
                            else:
                                print(f"Boss battle ended - transitioning to overworld")
                                self.state = "overworld"
                                self.battle_screen = None
                                self.music.update(self.state, False)  # Explicitly reset music state
                            continue
                        elif self.battle_screen.result == "lose":
                            self.state = "game_over"
                            self.battle_screen = None
                            self.music.update(self.state, False)  # Explicitly reset music state
                            continue
                        elif self.battle_screen.result == "escape":
                            self.player.exp = 0
                            self.player.just_leveled_up = False
                            self.player.boss_cooldown = True  # Set cooldown after boss battle
                            self.player.last_boss_level = self.player.level  # Set after the fight
                            print(f"Boss battle escaped - transitioning to overworld")
                            self.state = "overworld"
                            self.battle_screen = None
                            self.music.update(self.state, False)  # Explicitly reset music state
                            continue
                    else:
                        if self.battle_screen.result == "win":
                            defeated_enemy = self.battle_screen.enemy
                            self.player.kills += 1
                            if not self.apply_story_enemy_reward(defeated_enemy):
                                reward = get_regular_enemy_reward(defeated_enemy)
                                self.player.gain_exp(reward["exp"])
                                self.score += reward["score"]
                                self.set_town_service_message(reward["message"])
                            self.start_transition()
                            print(f"Battle ended - transitioning to overworld")
                            self.state = "overworld"
                            self.battle_screen = None
                            self.music.update(self.state, False)  # Explicitly reset music state
                        elif self.battle_screen.result == "lose":
                            self.state = "game_over"
                            self.battle_screen = None
                            self.music.update(self.state, False)  # Explicitly reset music state
                        elif self.battle_screen.result == "escape":
                            self.player.exp = 0
                            self.player.just_leveled_up = False
                            print(f"Battle escaped - transitioning to overworld")
                            self.state = "overworld"
                            self.battle_screen = None
                            self.music.update(self.state, False)  # Explicitly reset music state
                            continue
            
            elif self.state == "game_over":
                if self.start_button.update(mouse_pos):
                    self.end_menu_index = 0
                if self.back_button.update(mouse_pos):
                    self.end_menu_index = 1
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    self.end_menu_index = 0
                    self.activate_end_menu_selection()
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    self.end_menu_index = 1
                    self.activate_end_menu_selection()
                    
            elif self.state == "victory":
                if self.start_button.update(mouse_pos):
                    self.end_menu_index = 0
                if self.back_button.update(mouse_pos):
                    self.end_menu_index = 1
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    self.end_menu_index = 0
                    self.activate_end_menu_selection()
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    self.end_menu_index = 1
                    self.activate_end_menu_selection()
            
            self.update()
            self.draw(screen)
            
            # Handle victory music completion
            if self.state == "victory" and not pygame.mixer.music.get_busy():
                # After victory music plays once, return to menu
                self.state = "start_menu"
                self.music.update(self.state)
            
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
    
    def start_game(self):
        # Reset game state for a new game
        self.enemies = []
        self.items = []
        self.score = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.item_timer = 0
        self.player_moved = False
        self.movement_cooldown = 0
        self.boss_battle_triggered = False
        self.boss_defeated = False
        self.show_world_map = False
        self.show_journal = False
        self.show_inventory = False
        self.show_pause_menu = False
        self.pause_menu_buttons = []
        self.interior_service_menu_open = False
        self.interior_service_menu_buttons = []
        self.pickup_message = None
        self.pickup_message_timer = 0
        self.area_effect_timer = 0
        self.area_effect_message = None
        self.area_effect_message_timer = 0
        self.town_service_message = None
        self.town_service_message_timer = 0
        self.current_interior = None
        self.current_interior_service = None
        self.interior_return_position = None
        self.interior_player_x = SCREEN_WIDTH // 2 - PLAYER_SIZE // 2
        self.interior_player_y = 500
        self.npc_dialogue_index = 0
        self.town_reputation = 0
        self.completed_town_errands = set()
        self.completed_resident_errands = set()
        self.inspected_town_details = set()
        self.town_resident_dialogue_index = {}
        self.seen_story_dialogues = set()
        self.claimed_story_rewards = set()
        self.story_enemy_defeats = {}
        self.active_story_dialogue_key = None
        self.active_story_dialogue = None
        self.active_story_lines = []
        self.active_story_line_index = 0
        self.active_story_repeat = False
        if self.player:
            self.player.special_unlocked = False
        
        # Reset world map
        self.world_map = WorldMap()
        self.spawn_story_enemies()
        
        # Position player in center area (1,1) at center position
        if self.player:
            self.player.x = AREA_WIDTH + (AREA_WIDTH // 2)
            self.player.y = AREA_HEIGHT + (AREA_HEIGHT // 2)
        
        # Spawn initial enemies and items in starting area
        for _ in range(3):
            self.spawn_enemy()
        for _ in range(2):
            self.spawn_item()

# ============================================================================
# MUSIC SYSTEM - Procedural Chiptune Music Generation
# ============================================================================
class MusicSystem:
    """
    Generates dynamic chiptune music that changes based on game state.
    Creates different musical themes for different areas and situations.
    
    Music Types:
    - Start Menu: Epic title theme
    - Overworld: Calm adventure theme
    - Town: Peaceful town theme
    - Battle: Intense combat theme
    - Boss Battle: Epic boss theme
    - Victory: Triumphant victory theme
    - Game Over: Somber ending theme

    Beginner note:
        The music is generated from note names and simple wave math instead of
        loaded from MP3/OGG files. `generate_chiptune_song` converts note
        patterns into WAV bytes that pygame can play.
    """
    def __init__(self):
        self.current_track = None
        self.last_state = None
        self.last_area_type = None
        self.boss_battle_active = False
        self.town_music_bytes = None
        self.start_menu_music_bytes = None
        self.overworld_music_bytes = None
        self.battle_music_bytes = None
        self.boss_music_bytes = None
        self.victory_music_bytes = None
        self.game_over_music_bytes = None

        if not pygame.mixer.get_init():
            return

        try:
            self.start_menu_music_bytes = self.generate_start_menu_music()
            self.overworld_music_bytes = self.generate_overworld_music()
            self.town_music_bytes = self.generate_town_music()
            self.battle_music_bytes = self.generate_battle_music()
            self.boss_music_bytes = self.generate_boss_music()
            self.victory_music_bytes = self.generate_victory_music()
            self.game_over_music_bytes = self.generate_game_over_music()
            print('Music bytes created successfully')
        except Exception as e:
            print(f"Failed to create music bytes: {e}")
            self.start_menu_music_bytes = self.overworld_music_bytes = self.battle_music_bytes = None
            self.boss_music_bytes = self.victory_music_bytes = self.game_over_music_bytes = None
    
    def note_freq(self, note_name):
        if note_name in (None, "R", "REST", 0):
            return 0

        note_name = str(note_name).strip().upper()
        pitch = note_name[:-1]
        octave = int(note_name[-1])
        semitone = {
            "C": -9, "C#": -8, "DB": -8, "D": -7, "D#": -6, "EB": -6,
            "E": -5, "F": -4, "F#": -3, "GB": -3, "G": -2, "G#": -1,
            "AB": -1, "A": 0, "A#": 1, "BB": 1, "B": 2,
        }[pitch] + (octave - 4) * 12
        return 440.0 * (2 ** (semitone / 12))

    def notes(self, pattern):
        return [(self.note_freq(note), beats) for note, beats in pattern]

    def drum_loop(self, bars=4, busy=False):
        pattern = []
        base = [(220, 0.25), (0, 0.25), (520, 0.25), (0, 0.25)]
        fill = [(220, 0.25), (760, 0.125), (520, 0.125), (760, 0.25), (220, 0.25)]
        for bar in range(bars):
            pattern.extend(fill if busy and bar % 4 == 3 else base)
        return pattern

    def generate_start_menu_music(self):
        # Original title theme: heroic minor-key hook with an answer phrase.
        melody = self.notes([
            ("E4", .5), ("G4", .5), ("A4", .5), ("C5", .5), ("B4", .5), ("A4", .25), ("G4", .25), ("E4", 1),
            ("D4", .5), ("E4", .5), ("G4", .5), ("B4", .5), ("A4", .5), ("G4", .25), ("E4", .25), ("D4", 1),
            ("E4", .5), ("G4", .5), ("A4", .5), ("C5", .5), ("D5", .5), ("C5", .25), ("B4", .25), ("A4", 1),
            ("G4", .5), ("A4", .5), ("C5", .5), ("E5", .5), ("D5", .5), ("B4", .25), ("A4", .25), ("E4", 1),
        ])
        bass = self.notes([
            ("E2", .5), ("E3", .5), ("E2", .5), ("B2", .5),
            ("C3", .5), ("C4", .5), ("C3", .5), ("G2", .5),
            ("D3", .5), ("D4", .5), ("D3", .5), ("A2", .5),
            ("E2", .5), ("E3", .5), ("B2", .5), ("E3", .5),
        ] * 2)
        lead = self.notes([
            ("E5", .25), ("B4", .25), ("G4", .25), ("B4", .25),
            ("C5", .25), ("G4", .25), ("E4", .25), ("G4", .25),
            ("D5", .25), ("A4", .25), ("F#4", .25), ("A4", .25),
            ("E5", .25), ("B4", .25), ("G4", .25), ("B4", .25),
        ] * 2)
        return self.generate_chiptune_song(melody, bass, self.drum_loop(8), lead, bpm=126, volume=0.18)
    
    def play_music_bytes(self, music_bytes, loops=-1):
        pygame.mixer.music.load(io.BytesIO(music_bytes), "wav")
        pygame.mixer.music.play(loops)

    def update(self, game_state, is_boss_battle=False, current_area=None):
        if not pygame.mixer.get_init():
            return

        area_type = current_area.area_type if current_area else None

        # Only update when state or boss battle status changes
        if (
            game_state == self.last_state and
            is_boss_battle == self.boss_battle_active and
            area_type == self.last_area_type
        ):
            return
        
        print(f'MusicSystem: State change detected! "{self.last_state}" -> "{game_state}", boss: {self.boss_battle_active} -> {is_boss_battle}')
        self.last_state = game_state
        self.last_area_type = area_type
        self.boss_battle_active = is_boss_battle
        pygame.mixer.music.stop()
        pygame.mixer.music.set_volume(0.5)
        
        try:
            if game_state == "start_menu" and self.start_menu_music_bytes:
                print('MusicSystem: Playing start menu music')
                self.play_music_bytes(self.start_menu_music_bytes)
            elif game_state == "opening_cutscene" and self.start_menu_music_bytes:
                print('MusicSystem: Playing cutscene music')
                self.play_music_bytes(self.start_menu_music_bytes)
            elif game_state == "character_select" and self.start_menu_music_bytes:
                print('MusicSystem: Playing character select music')
                self.play_music_bytes(self.start_menu_music_bytes)
            elif game_state == "overworld":
                # Check if we're in a town area
                if current_area and current_area.area_type == "town" and self.town_music_bytes:
                    print('MusicSystem: Playing town music')
                    self.play_music_bytes(self.town_music_bytes)
                elif self.overworld_music_bytes:
                    print('MusicSystem: Playing overworld music')
                    self.play_music_bytes(self.overworld_music_bytes)
            elif game_state == "interior" and self.town_music_bytes:
                print('MusicSystem: Playing town interior music')
                self.play_music_bytes(self.town_music_bytes)
            elif game_state == "battle":
                if is_boss_battle and self.boss_music_bytes:
                    print('MusicSystem: Playing boss music')
                    self.play_music_bytes(self.boss_music_bytes)
                elif self.battle_music_bytes:
                    print('MusicSystem: Playing battle music')
                    self.play_music_bytes(self.battle_music_bytes)
                else:
                    print('MusicSystem: WARNING - No battle music available!')
            elif game_state == "victory" and self.victory_music_bytes:
                print('MusicSystem: Playing victory music')
                self.play_music_bytes(self.victory_music_bytes, 0)
            elif game_state == "game_over" and self.game_over_music_bytes:
                print('MusicSystem: Playing game over music')
                self.play_music_bytes(self.game_over_music_bytes, 0)
            else:
                print(f'MusicSystem: No music for state: {game_state}')
        except Exception as e:
            print(f"Music playback error: {e}")
    def generate_overworld_music(self):
        # Driving adventure loop with an actual 8-bar phrase.
        melody = self.notes([
            ("A4", .5), ("C5", .25), ("D5", .25), ("E5", .5), ("D5", .25), ("C5", .25), ("A4", .5), ("G4", .5),
            ("A4", .5), ("C5", .25), ("D5", .25), ("E5", .5), ("G5", .5), ("E5", .5), ("D5", .5),
            ("F4", .5), ("A4", .25), ("C5", .25), ("D5", .5), ("C5", .25), ("A4", .25), ("G4", .5), ("E4", .5),
            ("G4", .5), ("A4", .25), ("C5", .25), ("D5", .5), ("E5", .5), ("C5", .5), ("A4", .5),
        ])
        bass = self.notes([
            ("A2", .5), ("A3", .5), ("E3", .5), ("A3", .5),
            ("F2", .5), ("F3", .5), ("C3", .5), ("F3", .5),
            ("G2", .5), ("G3", .5), ("D3", .5), ("G3", .5),
            ("E2", .5), ("E3", .5), ("B2", .5), ("E3", .5),
        ] * 2)
        lead = self.notes([
            ("A5", .125), ("E5", .125), ("C5", .125), ("E5", .125),
            ("G5", .125), ("D5", .125), ("B4", .125), ("D5", .125),
        ] * 8)
        return self.generate_chiptune_song(melody, bass, self.drum_loop(8), lead, bpm=132, volume=0.16)
    
    def generate_town_music(self):
        # Softer town melody with call-and-response bells.
        melody = self.notes([
            ("C5", .5), ("E5", .5), ("G5", .5), ("E5", .5), ("D5", .5), ("C5", .5), ("A4", 1),
            ("B4", .5), ("D5", .5), ("F5", .5), ("D5", .5), ("C5", .5), ("B4", .5), ("G4", 1),
            ("A4", .5), ("C5", .5), ("E5", .5), ("G5", .5), ("A5", .5), ("G5", .5), ("E5", 1),
            ("D5", .5), ("E5", .5), ("G5", .5), ("E5", .5), ("C5", .5), ("D5", .5), ("C5", 1),
        ])
        bass = self.notes([
            ("C3", 1), ("G2", 1), ("A2", 1), ("E2", 1),
            ("F2", 1), ("C3", 1), ("G2", 1), ("C3", 1),
        ] * 2)
        percussion = [(90, .5), (0, .5), (130, .5), (0, .5)] * 8
        lead = self.notes([
            ("G5", .25), ("R", .25), ("E5", .25), ("R", .25),
            ("A5", .25), ("R", .25), ("G5", .25), ("R", .25),
            ("E5", .25), ("R", .25), ("D5", .25), ("R", .25),
            ("C5", .25), ("R", .25), ("E5", .25), ("R", .25),
        ] * 2)
        return self.generate_chiptune_song(melody, bass, percussion, lead, bpm=104, volume=0.13)
    def generate_battle_music(self):
        # Fast combat theme with a hook and a second phrase instead of one run.
        melody = self.notes([
            ("D5", .25), ("F5", .25), ("G5", .25), ("A5", .25), ("G5", .25), ("F5", .25), ("D5", .25), ("C5", .25),
            ("D5", .25), ("F5", .25), ("A5", .25), ("C6", .25), ("A5", .25), ("G5", .25), ("F5", .25), ("D5", .25),
            ("E5", .25), ("G5", .25), ("A#5", .25), ("D6", .25), ("C6", .25), ("A#5", .25), ("G5", .25), ("E5", .25),
            ("F5", .25), ("G5", .25), ("A5", .25), ("C6", .25), ("D6", .5), ("C6", .25), ("A5", .25),
        ] * 2)
        bass = self.notes([
            ("D2", .25), ("D3", .25), ("A2", .25), ("D3", .25),
            ("C2", .25), ("C3", .25), ("G2", .25), ("C3", .25),
            ("A#1", .25), ("A#2", .25), ("F2", .25), ("A#2", .25),
            ("A1", .25), ("A2", .25), ("E2", .25), ("A2", .25),
        ] * 4)
        lead = self.notes([
            ("D6", .125), ("A5", .125), ("F5", .125), ("A5", .125),
            ("C6", .125), ("G5", .125), ("E5", .125), ("G5", .125),
        ] * 8)
        percussion = self.drum_loop(16, busy=True)
        return self.generate_chiptune_song(melody, bass, percussion=percussion, lead=lead, bpm=158, volume=0.19)
    def generate_boss_music(self):
        # Boss theme: darker, heavier, and more aggressive.
        melody = self.notes([
            ("E4", .25), ("G4", .25), ("A#4", .25), ("B4", .25), ("E5", .5), ("D5", .25), ("B4", .25),
            ("E4", .25), ("G4", .25), ("A#4", .25), ("B4", .25), ("F5", .5), ("E5", .25), ("D5", .25),
            ("C5", .25), ("B4", .25), ("A#4", .25), ("G4", .25), ("A#4", .5), ("C5", .5),
            ("B4", .25), ("A#4", .25), ("G4", .25), ("E4", .25), ("F#4", .5), ("B4", .5),
        ] * 2)
        bass = self.notes([
            ("E1", .25), ("E2", .25), ("E1", .25), ("B1", .25),
            ("G1", .25), ("G2", .25), ("G1", .25), ("D2", .25),
            ("C2", .25), ("C3", .25), ("C2", .25), ("G1", .25),
            ("B1", .25), ("B2", .25), ("F#2", .25), ("B2", .25),
        ] * 4)
        lead = self.notes([
            ("E5", .125), ("B4", .125), ("G4", .125), ("B4", .125),
            ("F5", .125), ("C5", .125), ("A#4", .125), ("C5", .125),
            ("G5", .125), ("D5", .125), ("B4", .125), ("D5", .125),
            ("B5", .125), ("F#5", .125), ("D5", .125), ("F#5", .125),
        ] * 4)
        percussion = [(260, .125), (760, .125), (0, .125), (520, .125), (260, .125), (0, .125), (760, .125), (520, .125)] * 8
        return self.generate_chiptune_song(melody, bass, percussion, lead, bpm=168, volume=0.21)
    def generate_victory_music(self):
        melody = self.notes([
            ("C5", .25), ("E5", .25), ("G5", .25), ("C6", .5), ("B5", .25), ("A5", .5),
            ("G5", .25), ("A5", .25), ("C6", .25), ("E6", .75), ("D6", .25), ("C6", 1),
        ])
        bass = self.notes([("C3", .5), ("G3", .5), ("A3", .5), ("E3", .5), ("F3", .5), ("G3", .5), ("C4", 1)])
        percussion = [(300, .1), (0, .1), (460, .1), (0, .1), (620, .1), (0, .1), (760, .6)]
        return self.generate_chiptune_song(melody, bass, percussion, bpm=128, volume=0.24)
    def generate_game_over_music(self):
        melody = self.notes([
            ("C4", 1), ("B3", 1), ("A3", 1), ("E3", 1.5), ("R", .5),
            ("F3", 1), ("E3", 1), ("D3", 1), ("C3", 2),
        ])
        bass = self.notes([("C2", 2), ("A1", 2), ("F1", 2), ("G1", 2), ("C1", 2)])
        return self.generate_chiptune_song(melody, bass, bpm=66, volume=0.2)
    def generate_chiptune_song(self, melody, bass, percussion=None, lead=None, bpm=220, volume=0.16):
        """
        Core chiptune generation algorithm that combines multiple musical tracks.
        
        Args:
            melody: List of (frequency, duration) tuples for main melody
            bass: List of (frequency, duration) tuples for bass line
            percussion: Optional list of (frequency, duration) tuples for drums
            lead: Optional list of (frequency, duration) tuples for lead synth
            bpm: Beats per minute for tempo
            volume: Overall volume level (0.0 to 1.0)
        """
        melody = [list(note) for note in melody]
        bass = [list(note) for note in bass]
        if percussion is not None:
            percussion = [list(note) for note in percussion]
        if lead is not None:
            lead = [list(note) for note in lead]
        pcm = bytearray()
        melody_idx = bass_idx = perc_idx = lead_idx = 0
        melody_len = len(melody)
        bass_len = len(bass)
        perc_len = len(percussion) if percussion is not None else 0
        lead_len = len(lead) if lead is not None else 0
        while (melody_idx < melody_len or bass_idx < bass_len or
               (percussion is not None and perc_idx < perc_len) or
               (lead is not None and lead_idx < lead_len)):
            if melody_idx < melody_len:
                m_freq, m_beats = melody[melody_idx]
            else:
                m_freq, m_beats = 0, 0.25
            if bass_idx < bass_len:
                b_freq, b_beats = bass[bass_idx]
            else:
                b_freq, b_beats = 0, 0.25
            if percussion is not None and perc_idx < perc_len:
                p_freq, p_beats = percussion[perc_idx]
            else:
                p_freq, p_beats = 0, 0.25
            if lead is not None and lead_idx < lead_len:
                l_freq, l_beats = lead[lead_idx]
            else:
                l_freq, l_beats = 0, 0.25
            step_beats = min(m_beats, b_beats, p_beats, l_beats)
            step_duration = 60 / bpm * step_beats
            sample_count = int(SAMPLE_RATE * step_duration)
            for sample_index in range(sample_count):
                t = sample_index / SAMPLE_RATE
                note_pos = sample_index / max(1, sample_count)
                attack = min(1.0, note_pos / 0.04)
                release = min(1.0, (1.0 - note_pos) / 0.10)
                envelope = max(0.0, min(attack, release))

                if m_freq > 0:
                    phase = m_freq * 2 * math.pi * t
                    square = 1.0 if math.sin(phase) >= 0 else -1.0
                    triangle = (2 / math.pi) * math.asin(math.sin(phase))
                    m_wave = 0.42 * (0.72 * square + 0.28 * triangle) * envelope
                else:
                    m_wave = 0.0

                if b_freq > 0:
                    phase = b_freq * 2 * math.pi * t
                    square = 1.0 if math.sin(phase) >= 0 else -1.0
                    sub = 1.0 if math.sin((b_freq / 2) * 2 * math.pi * t) >= 0 else -1.0
                    b_wave = 0.24 * (0.75 * square + 0.25 * sub) * envelope
                else:
                    b_wave = 0.0

                if percussion is not None and p_freq > 0:
                    decay = max(0.0, 1.0 - note_pos) ** 3
                    noise = math.sin((p_freq + (sample_index % 23) * 31) * 2 * math.pi * t)
                    click = 1.0 if math.sin(p_freq * 2 * math.pi * t) >= 0 else -1.0
                    p_wave = 0.22 * (0.65 * noise + 0.35 * click) * decay
                else:
                    p_wave = 0.0

                if lead is not None and l_freq > 0:
                    phase = l_freq * 2 * math.pi * t
                    pulse = 1.0 if math.sin(phase) > 0.45 else -1.0
                    shimmer = math.sin(l_freq * 4 * math.pi * t) * 0.25
                    l_wave = 0.18 * (pulse + shimmer) * envelope
                else:
                    l_wave = 0.0

                mixed = (m_wave + b_wave + p_wave + l_wave) * volume
                append_stereo_sample(pcm, math.tanh(mixed * 1.8))
            # Update note durations
            if melody_idx < melody_len:
                melody[melody_idx][1] -= step_beats
                if melody[melody_idx][1] <= 0:
                    melody_idx += 1
            if bass_idx < bass_len:
                bass[bass_idx][1] -= step_beats
                if bass[bass_idx][1] <= 0:
                    bass_idx += 1
            if percussion is not None and perc_idx < perc_len:
                percussion[perc_idx][1] -= step_beats
                if percussion[perc_idx][1] <= 0:
                    perc_idx += 1
            if lead is not None and lead_idx < lead_len:
                lead[lead_idx][1] -= step_beats
                if lead[lead_idx][1] <= 0:
                    lead_idx += 1
        return pcm_to_wav_bytes(bytes(pcm))

# --- DragonBoss: Progressive boss for each level ---
# ============================================================================
# BOSS ENEMY CLASSES - Special enemies with unique abilities
# ============================================================================
class DragonBoss(Enemy):
    """
    Special boss enemy with enhanced abilities and unique visual effects.
    More powerful than regular enemies with special attack patterns.

    Beginner note:
        This is the repeatable/progression dragon boss class. Boss tuning data
        such as name, title, and hint comes from `game_data/progression.py`.
    """
    def __init__(self, boss_level):
        super().__init__(player_level=5 + boss_level * 2)
        boss_profile = get_boss_profile(boss_level)
        self.size = 120
        self.x = 700
        self.y = 180
        self.enemy_type = f"boss_dragon_{boss_level}"
        self.name = boss_profile["name"]
        self.boss_title = boss_profile["title"]
        self.boss_hint = boss_profile["hint"]
        # Stat scaling
        self.health = self.max_health = 180 + boss_level * 52
        self.strength = int(17 + boss_level * 3.5)
        self.speed = 5 + boss_level // 2
        # Color cycling
        color_idx = (boss_level - 1) % len(DRAGON_BOSS_COLORS)
        self.dragon_color, self.fire_color = DRAGON_BOSS_COLORS[color_idx]
        self.color = self.dragon_color
        self.movement_cooldown = 0
        self.movement_delay = 40
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        self.fire_breathing = False
        self.fire_breath_timer = 0
        self.boss_level = boss_level
        # BEGINNER NOTE: Bosses are quest milestones, not ordinary random
        # fights. Their EXP is intentionally high enough to push leveling
        # forward so the next dragon objective does not feel like a grind wall.
        self.exp_reward = 105 + boss_level * 35
        self.score_reward = 40 + boss_level * 15
        self.phase_thresholds = (
            {
                "name": "Wounded",
                "threshold": 0.66,
                "strength_bonus": 1 + boss_level,
                "color": self.fire_color,
                "shake": 5,
                "attack_message": "The dragon's wounded fury intensifies!",
            },
            {
                "name": "Enraged",
                "threshold": 0.33,
                "strength_bonus": 3 + boss_level,
                "color": (255, 60, 40),
                "shake": 8,
                "attack_message": "The dragon erupts into an enraged assault!",
            },
        )
    def start_attack_animation(self):
        self.attack_animation = 20
        self.fire_breathing = True
        self.fire_breath_timer = 20
    def update_animation(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        if self.attack_animation > 0:
            self.attack_animation -= 1
        if self.hit_animation > 0:
            self.hit_animation -= 1
        if self.fire_breathing:
            self.fire_breath_timer -= 1
            if self.fire_breath_timer <= 0:
                self.fire_breathing = False
    def draw(self, surface):
        offset_x = 0
        offset_y = self.animation_offset
        if self.attack_animation > 0:
            offset_x = 10 * math.sin(self.attack_animation * 0.2)
        if self.hit_animation > 0:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
        x = self.x + offset_x
        y = self.y + offset_y
        # --- Draw a more dragon-like boss, facing left ---
        # Body
        pygame.draw.ellipse(surface, self.dragon_color, (x, y + 60, 180, 60))
        # Tail
        pygame.draw.polygon(surface, (200, 50, 50), [
            (x + 180, y + 90), (x + 240, y + 80), (x + 180, y + 110)
        ])
        # Legs
        pygame.draw.rect(surface, (120, 40, 20), (x + 120, y + 110, 18, 30), border_radius=8)
        pygame.draw.rect(surface, (120, 40, 20), (x + 40, y + 110, 18, 30), border_radius=8)
        # Claws
        pygame.draw.polygon(surface, (255, 255, 255), [
            (x + 120, y + 140), (x + 118, y + 150), (x + 124, y + 150)
        ])
        pygame.draw.polygon(surface, (255, 255, 255), [
            (x + 40, y + 140), (x + 38, y + 150), (x + 44, y + 150)
        ])
        # Wings (bat-like, flipped)
        wing_y = y + 60
        pygame.draw.polygon(surface, (180, 50, 50), [
            (x + 120, wing_y), (x + 170, wing_y - 60), (x + 60, wing_y - 80), (x + 10, wing_y - 40), (x + 60, wing_y)
        ])
        pygame.draw.polygon(surface, (180, 50, 50), [
            (x + 60, wing_y), (x + 10, wing_y - 60), (x, wing_y - 20), (x + 20, wing_y + 10)
        ])
        # Head (distinct, with open mouth, facing left)
        head_x = x - 40
        head_y = y + 70
        pygame.draw.ellipse(surface, self.dragon_color, (head_x, head_y, 60, 40))
        # Jaw (open)
        pygame.draw.polygon(surface, (200, 50, 50), [
            (head_x + 20, head_y + 30), (head_x, head_y + 50), (head_x + 5, head_y + 35), (head_x + 10, head_y + 30)
        ])
        # Teeth
        for i in range(3):
            pygame.draw.polygon(surface, (255, 255, 255), [
                (head_x + 12 + i*6, head_y + 38), (head_x + 10 + i*6, head_y + 45), (head_x + 14 + i*6, head_y + 38)
            ])
        # Horns
        pygame.draw.polygon(surface, (220, 220, 220), [
            (head_x + 50, head_y + 5), (head_x + 60, head_y - 25), (head_x + 45, head_y + 5)
        ])
        pygame.draw.polygon(surface, (220, 220, 220), [
            (head_x + 10, head_y + 5), (head_x, head_y - 25), (head_x + 15, head_y + 5)
        ])
        # Nostrils
        pygame.draw.circle(surface, (80, 0, 0), (head_x + 15, head_y + 25), 3)
        pygame.draw.circle(surface, (80, 0, 0), (head_x + 25, head_y + 28), 3)
        # Eye
        pygame.draw.circle(surface, (255, 255, 255), (head_x + 15, head_y + 15), 7)
        pygame.draw.circle(surface, (0, 0, 0), (head_x + 13, head_y + 15), 3)
        # Fire breath animation (large cone from mouth to player, facing left)
        if self.fire_breathing:
            mouth_x = head_x - 10
            mouth_y = head_y + 40
            player_x = 200 + 25
            player_y = 300 + 25
            for i in range(30):
                t = i / 30
                fx = int(mouth_x * (1-t) + player_x * t + random.randint(-10, 10))
                fy = int(mouth_y * (1-t) + player_y * t + random.randint(-10, 10))
                size = int(10 * (1-t) + 40 * t)
                # Use the boss's fire color, fade alpha
                base = self.fire_color
                color = (base[0], base[1], base[2], max(0, 200 - i * 6))
                fire_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, color, (size, size), size)
                surface.blit(fire_surf, (fx - size, fy - size))
        # Health bar (with HP numbers)
        bar_width = 120
        bar_x = x + 60
        bar_y = y + 20
        pygame.draw.rect(surface, (20, 20, 30), (bar_x, bar_y, bar_width, 16), border_radius=2)
        health_width = (bar_width - 2) * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (bar_x + 1, bar_y + 1, health_width, 14), border_radius=2)
        # HP numbers
        hp_text = font_small.render(f"{self.health}/{self.max_health}", True, (255,255,255))
        hp_rect = hp_text.get_rect(center=(bar_x + bar_width//2, bar_y + 8))
        surface.blit(hp_text, hp_rect)
        # Name
        name_text = font_medium.render(self.name, True, (255, 215, 0))
        name_rect = name_text.get_rect(midtop=(x + 120, y - 10))
        surface.blit(name_text, name_rect)

# Place BossDragon right after DragonBoss for proper definition order
# --- DragonBoss: Progressive boss for each level ---
# ... existing code for DragonBoss ...

class BossDragon(Enemy):
    """
    Final boss enemy with the most powerful abilities and unique visual design.
    Represents the ultimate challenge in the game.

    Beginner note:
        This is the final dragon, separate from `DragonBoss` so the last fight
        can have fixed stats and final-boss phase names.
    """
    def __init__(self):
        super().__init__(player_level=10)
        boss_profile = get_boss_profile(FINAL_BOSS_LEVEL)
        self.size = 120
        self.x = 700
        self.y = 180
        self.enemy_type = "boss_dragon"
        self.name = boss_profile["name"]
        self.boss_title = boss_profile["title"]
        self.boss_hint = boss_profile["hint"]
        self.health = 360
        self.max_health = 360
        self.strength = 31
        self.speed = 9
        self.color = (255, 69, 0)
        self.movement_cooldown = 0
        self.movement_delay = 40
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        self.fire_breathing = False
        self.fire_breath_timer = 0
        self.exp_reward = 250
        self.score_reward = 200
        self.phase_thresholds = (
            {
                "name": "Ancient Wrath",
                "threshold": 0.66,
                "strength_bonus": 6,
                "color": (255, 140, 0),
                "shake": 8,
                "attack_message": "Malakor's ancient wrath scorches the arena!",
            },
            {
                "name": "Doomfire",
                "threshold": 0.33,
                "strength_bonus": 11,
                "color": (255, 30, 20),
                "shake": 12,
                "attack_message": "Doomfire coils around Malakor's claws!",
            },
        )
    def start_attack_animation(self):
        self.attack_animation = 20
        self.fire_breathing = True
        self.fire_breath_timer = 20
    def update_animation(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        if self.attack_animation > 0:
            self.attack_animation -= 1
        if self.hit_animation > 0:
            self.hit_animation -= 1
        if self.fire_breathing:
            self.fire_breath_timer -= 1
            if self.fire_breath_timer <= 0:
                self.fire_breathing = False
    def draw(self, surface):
        offset_x = 0
        offset_y = self.animation_offset
        if self.attack_animation > 0:
            offset_x = 10 * math.sin(self.attack_animation * 0.2)
        if self.hit_animation > 0:
            offset_x = random.randint(-4, 4)
            offset_y = random.randint(-4, 4)
        x = self.x + offset_x
        y = self.y + offset_y
        # --- Draw a more dragon-like boss, facing left ---
        # Body
        pygame.draw.ellipse(surface, DRAGON_COLOR, (x, y + 60, 180, 60))
        # Tail
        pygame.draw.polygon(surface, (200, 50, 50), [
            (x + 180, y + 90), (x + 240, y + 80), (x + 180, y + 110)
        ])
        # Legs
        pygame.draw.rect(surface, (120, 40, 20), (x + 120, y + 110, 18, 30), border_radius=8)
        pygame.draw.rect(surface, (120, 40, 20), (x + 40, y + 110, 18, 30), border_radius=8)
        # Claws
        pygame.draw.polygon(surface, (255, 255, 255), [
            (x + 120, y + 140), (x + 118, y + 150), (x + 124, y + 150)
        ])
        pygame.draw.polygon(surface, (255, 255, 255), [
            (x + 40, y + 140), (x + 38, y + 150), (x + 44, y + 150)
        ])
        # Wings (bat-like, flipped)
        wing_y = y + 60
        pygame.draw.polygon(surface, (180, 50, 50), [
            (x + 120, wing_y), (x + 170, wing_y - 60), (x + 60, wing_y - 80), (x + 10, wing_y - 40), (x + 60, wing_y)
        ])
        pygame.draw.polygon(surface, (180, 50, 50), [
            (x + 60, wing_y), (x + 10, wing_y - 60), (x, wing_y - 20), (x + 20, wing_y + 10)
        ])
        # Head (distinct, with open mouth, facing left)
        head_x = x - 40
        head_y = y + 70
        pygame.draw.ellipse(surface, DRAGON_COLOR, (head_x, head_y, 60, 40))
        # Jaw (open)
        pygame.draw.polygon(surface, (200, 50, 50), [
            (head_x + 20, head_y + 30), (head_x, head_y + 50), (head_x + 5, head_y + 35), (head_x + 10, head_y + 30)
        ])
        # Teeth
        for i in range(3):
            pygame.draw.polygon(surface, (255, 255, 255), [
                (head_x + 12 + i*6, head_y + 38), (head_x + 10 + i*6, head_y + 45), (head_x + 14 + i*6, head_y + 38)
            ])
        # Horns
        pygame.draw.polygon(surface, (220, 220, 220), [
            (head_x + 50, head_y + 5), (head_x + 60, head_y - 25), (head_x + 45, head_y + 5)
        ])
        pygame.draw.polygon(surface, (220, 220, 220), [
            (head_x + 10, head_y + 5), (head_x, head_y - 25), (head_x + 15, head_y + 5)
        ])
        # Nostrils
        pygame.draw.circle(surface, (80, 0, 0), (head_x + 15, head_y + 25), 3)
        pygame.draw.circle(surface, (80, 0, 0), (head_x + 25, head_y + 28), 3)
        # Eye
        pygame.draw.circle(surface, (255, 255, 255), (head_x + 15, head_y + 15), 7)
        pygame.draw.circle(surface, (0, 0, 0), (head_x + 13, head_y + 15), 3)
        # Fire breath animation (large cone from mouth to player, facing left)
        if self.fire_breathing:
            mouth_x = head_x - 10
            mouth_y = head_y + 40
            player_x = 200 + 25
            player_y = 300 + 25
            for i in range(30):
                t = i / 30
                fx = int(mouth_x * (1-t) + player_x * t + random.randint(-10, 10))
                fy = int(mouth_y * (1-t) + player_y * t + random.randint(-10, 10))
                size = int(10 * (1-t) + 40 * t)
                color = (255, 140 + random.randint(0, 100), 0, max(0, 200 - i * 6))
                fire_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, color, (size, size), size)
                surface.blit(fire_surf, (fx - size, fy - size))
        # Health bar (with HP numbers)
        bar_width = 120
        bar_x = x + 60
        bar_y = y + 20
        pygame.draw.rect(surface, (20, 20, 30), (bar_x, bar_y, bar_width, 16), border_radius=2)
        health_width = (bar_width - 2) * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (bar_x + 1, bar_y + 1, health_width, 14), border_radius=2)
        # HP numbers
        hp_text = font_small.render(f"{self.health}/{self.max_health}", True, (255,255,255))
        hp_rect = hp_text.get_rect(center=(bar_x + bar_width//2, bar_y + 8))
        surface.blit(hp_text, hp_rect)
        # Name
        name_text = font_medium.render(self.name, True, (255, 215, 0))
        name_rect = name_text.get_rect(midtop=(x + 120, y - 10))
        surface.blit(name_text, name_rect)

if __name__ == "__main__":
    game = Game()
    game.run()
