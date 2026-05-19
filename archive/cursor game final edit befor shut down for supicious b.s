import os
os.environ['SDL_AUDIODRIVER'] = 'directsound'  # or 'winmm' or 'waveout'
import pygame
import sys
import random
import math
from pygame import gfxdraw
import numpy as np

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700
PLAYER_SIZE = 50
ENEMY_SIZE = 40
ITEM_SIZE = 30
FPS = 60

# Retro 80s Color Palette with expanded colors for effects
BACKGROUND = (10, 10, 30)
UI_BG = (20, 15, 40)
UI_BORDER = (255, 105, 180)  # Hot pink
TEXT_COLOR = (0, 255, 255)   # Cyan
PLAYER_COLOR = (0, 255, 0)   # Green
ENEMY_COLOR = (255, 0, 0)    # Red
HEALTH_COLOR = (255, 105, 180)  # Hot pink
MANA_COLOR = (0, 255, 255)   # Cyan
EXP_COLOR = (255, 255, 0)    # Yellow
ITEM_COLOR = (255, 215, 0)   # Gold
DRAGON_COLOR = (255, 69, 0)  # Red-orange
GRID_COLOR = (50, 50, 80)    # Grid lines

# Effect colors
FIRE_COLORS = [(255, 100, 0), (255, 150, 0), (255, 200, 50)]
ICE_COLORS = [(100, 200, 255), (150, 220, 255), (200, 240, 255)]
SHADOW_COLORS = [(40, 40, 80), (70, 70, 120), (100, 100, 150)]
MAGIC_COLORS = [(150, 0, 255), (200, 50, 255), (255, 100, 255)]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dragon's Lair RPG")
clock = pygame.time.Clock()

# Fonts
try:
    font_large = pygame.font.Font("freesansbold.ttf", 48)
    font_medium = pygame.font.Font("freesansbold.ttf", 32)
    font_small = pygame.font.Font("freesansbold.ttf", 24)
    font_tiny = pygame.font.Font("freesansbold.ttf", 18)
    font_cinematic = pygame.font.Font("freesansbold.ttf", 28)
except:
    font_large = pygame.font.SysFont("Courier", 48, bold=True)
    font_medium = pygame.font.SysFont("Courier", 32, bold=True)
    font_small = pygame.font.SysFont("Courier", 24, bold=True)
    font_tiny = pygame.font.SysFont("Courier", 18, bold=True)
    font_cinematic = pygame.font.SysFont("Courier", 28, bold=True)

# Grid settings
GRID_SIZE = 50
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

class Particle:
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
            gfxdraw.filled_circle(surface, int(self.x), int(self.y), radius, color)

class ParticleSystem:
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
        
    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class Button:
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

class Character:
    def __init__(self, char_type="Warrior"):
        self.type = char_type
        self.level = 1
        self.exp = 0
        self.exp_to_level = 100
        
        if char_type == "Warrior":
            self.max_health = 120
            self.max_mana = 50
            self.strength = 15
            self.defense = 10
            self.speed = 7
        elif char_type == "Mage":
            self.max_health = 80
            self.max_mana = 120
            self.strength = 8
            self.defense = 6
            self.speed = 8
        else:  # Rogue
            self.max_health = 100
            self.max_mana = 70
            self.strength = 12
            self.defense = 8
            self.speed = 12
            
        self.health = self.max_health
        self.mana = self.max_mana
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.attack_cooldown = 0
        self.kills = 0
        self.items_collected = 0
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        
    def move(self, dx, dy):
        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE
        
        if 0 <= new_x < SCREEN_WIDTH:
            self.x = new_x
        if 0 <= new_y < SCREEN_HEIGHT:
            self.y = new_y
            
    def update_animation(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.005) * 2
        
        if self.attack_animation > 0:
            self.attack_animation -= 1
            
        if self.hit_animation > 0:
            self.hit_animation -= 1
            
    def draw(self, surface):
        offset_x = 0
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
        
        if self.type == "Warrior":
            pygame.draw.rect(surface, (0, 150, 0), (x, y + 10, PLAYER_SIZE, PLAYER_SIZE - 10))
            pygame.draw.circle(surface, (240, 200, 150), (x + PLAYER_SIZE//2, y + 8), 8)
            pygame.draw.rect(surface, (150, 75, 0), (x + 5, y + 20, 10, 20))
            sword_offset = 0
            if self.attack_animation > 0:
                sword_offset = -10 * (1 - self.attack_animation / 10)
            pygame.draw.rect(surface, (200, 200, 200), (x + 30 + sword_offset, y + 15, 5, 25))
            pygame.draw.polygon(surface, (200, 200, 200), 
                              [(x + 30 + sword_offset, y + 15), 
                               (x + 40 + sword_offset, y + 10),
                               (x + 35 + sword_offset, y + 15)])
            pygame.draw.rect(surface, (0, 100, 0), (x, y + 10, 10, 10))
            pygame.draw.rect(surface, (0, 100, 0), (x + PLAYER_SIZE - 10, y + 10, 10, 10))
            
        elif self.type == "Mage":
            pygame.draw.rect(surface, (0, 100, 150), (x, y + 15, PLAYER_SIZE, PLAYER_SIZE - 15))
            pygame.draw.circle(surface, (240, 200, 150), (x + PLAYER_SIZE//2, y + 10), 10)
            hat_offset = 0
            if self.attack_animation > 0:
                hat_offset = -5 * (1 - self.attack_animation / 10)
            pygame.draw.polygon(surface, (100, 50, 200), 
                              [(x + PLAYER_SIZE//2 - 15, y + 10 + hat_offset), 
                               (x + PLAYER_SIZE//2 + 15, y + 10 + hat_offset),
                               (x + PLAYER_SIZE//2, y - 10 + hat_offset)])
            staff_top_offset = 0
            if self.attack_animation > 0:
                staff_top_offset = -10 * (1 - self.attack_animation / 10)
            pygame.draw.line(surface, (180, 150, 100), (x + 10, y + 10), (x + 10, y + PLAYER_SIZE), 3)
            pygame.draw.circle(surface, (200, 200, 100), (x + 10, y + 10 + staff_top_offset), 6)
            
        else:  # Rogue
            pygame.draw.rect(surface, (150, 0, 0), (x, y + 15, PLAYER_SIZE, PLAYER_SIZE - 15))
            pygame.draw.circle(surface, (240, 200, 150), (x + PLAYER_SIZE//2, y + 8), 8)
            pygame.draw.polygon(surface, (100, 0, 0), 
                              [(x + 10, y + 15), 
                               (x + PLAYER_SIZE - 10, y + 15),
                               (x + PLAYER_SIZE//2, y - 5)])
            dagger_offset = 0
            if self.attack_animation > 0:
                dagger_offset = -15 * (1 - self.attack_animation / 10)
            pygame.draw.polygon(surface, (180, 180, 200), 
                              [(x + 15 + dagger_offset, y + 20), 
                               (x + 20 + dagger_offset, y + 15),
                               (x + 25 + dagger_offset, y + 20)])
            pygame.draw.polygon(surface, (180, 180, 200), 
                              [(x + PLAYER_SIZE - 15 - dagger_offset, y + 20), 
                               (x + PLAYER_SIZE - 20 - dagger_offset, y + 15),
                               (x + PLAYER_SIZE - 25 - dagger_offset, y + 20)])
            pygame.draw.rect(surface, (50, 50, 50), (x, y + 35, PLAYER_SIZE, 5))
    
    def start_attack_animation(self):
        self.attack_animation = 10
        
    def start_hit_animation(self):
        self.hit_animation = 5
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 3)
        self.health -= actual_damage
        self.start_hit_animation()
        return actual_damage
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level:
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
        
    def draw_stats(self, surface, x, y):
        pygame.draw.rect(surface, (20, 20, 30), (x, y, 200, 25), border_radius=3)
        health_width = 196 * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (x + 2, y + 2, health_width, 21), border_radius=3)
        health_text = font_small.render(f"HP: {self.health}/{self.max_health}", True, TEXT_COLOR)
        surface.blit(health_text, (x + 205, y + 4))
        
        pygame.draw.rect(surface, (20, 20, 30), (x, y + 30, 200, 20), border_radius=3)
        mana_width = 196 * (self.mana / self.max_mana)
        pygame.draw.rect(surface, MANA_COLOR, (x + 2, y + 32, mana_width, 16), border_radius=3)
        mana_text = font_small.render(f"MP: {self.mana}/{self.max_mana}", True, TEXT_COLOR)
        surface.blit(mana_text, (x + 205, y + 32))
        
        pygame.draw.rect(surface, (20, 20, 30), (x, y + 55, 200, 15), border_radius=3)
        exp_width = 196 * (self.exp / self.exp_to_level)
        pygame.draw.rect(surface, EXP_COLOR, (x + 2, y + 57, exp_width, 11), border_radius=3)
        exp_text = font_small.render(f"Level: {self.level}  Exp: {self.exp}/{self.exp_to_level}", True, TEXT_COLOR)
        surface.blit(exp_text, (x, y + 75))
        
        stats_text = font_small.render(f"Str: {self.strength}  Def: {self.defense}  Spd: {self.speed}", True, TEXT_COLOR)
        surface.blit(stats_text, (x, y + 100))

class Enemy:
    def __init__(self, player_level):
        self.size = ENEMY_SIZE
        self.x = random.randint(0, GRID_WIDTH-1) * GRID_SIZE
        self.y = random.randint(0, GRID_HEIGHT-1) * GRID_SIZE
        self.enemy_type = random.choice(["fiery", "shadow", "ice"])
        
        # Generate enemy name based on type
        if self.enemy_type == "fiery":
            names = ["Fire Imp", "Lava Sprite", "Magma Beast", "Inferno Hound", "Blaze Fiend"]
        elif self.enemy_type == "shadow":
            names = ["Dark Shade", "Night Phantom", "Void Walker", "Gloom Stalker", "Shadow Fiend"]
        else:  # ice
            names = ["Frost Sprite", "Ice Golem", "Blizzard Elemental", "Frozen Wraith", "Chill Specter"]
        self.name = random.choice(names)
        
        self.health = random.randint(20, 30) + player_level * 5
        self.max_health = self.health
        self.strength = random.randint(5, 10) + player_level * 2
        self.speed = random.randint(3, 6) + player_level // 2
        self.color = ENEMY_COLOR
        self.movement_cooldown = 0
        self.movement_delay = 60
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        
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
        
        if self.enemy_type == "fiery":
            pygame.draw.ellipse(surface, (200, 50, 0), (x, y, self.size, self.size))
            flame_size = 15
            if self.attack_animation > 0:
                flame_size = 20 * (1 - self.attack_animation / 10)
            for i in range(8):
                angle = i * math.pi / 4
                flame_x = x + self.size//2 + math.cos(angle) * flame_size
                flame_y = y + self.size//2 + math.sin(angle) * flame_size
                pygame.draw.polygon(surface, (255, 150, 0), 
                                  [(x + self.size//2, y + self.size//2),
                                   (flame_x, flame_y),
                                   (flame_x + math.cos(angle+0.3)*5, flame_y + math.sin(angle+0.3)*5)])
            pygame.draw.circle(surface, (255, 255, 0), (x + 15, y + 15), 4)
            pygame.draw.circle(surface, (255, 255, 0), (x + self.size - 15, y + 15), 4)
            pygame.draw.arc(surface, (255, 100, 0), (x + 10, y + 20, self.size - 20, 15), 0, math.pi, 2)
            
        elif self.enemy_type == "shadow":
            pygame.draw.ellipse(surface, (40, 40, 80), (x, y, self.size, self.size))
            smoke_count = 6
            if self.attack_animation > 0:
                smoke_count = 12 * (1 - self.attack_animation / 10)
            for i in range(int(smoke_count)):
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                pygame.draw.circle(surface, (70, 70, 120), 
                                 (x + self.size//2 + offset_x, y + self.size//2 + offset_y), 
                                 random.randint(3, 8))
            pygame.draw.circle(surface, (0, 255, 255), (x + 20, y + 20), 5)
            pygame.draw.circle(surface, (0, 255, 255), (x + self.size - 20, y + 20), 5)
            claw_length = 10
            if self.attack_animation > 0:
                claw_length = 15 * (1 - self.attack_animation / 10)
            pygame.draw.line(surface, (0, 200, 200), (x, y + self.size), (x - claw_length, y + self.size + claw_length), 2)
            pygame.draw.line(surface, (0, 200, 200), (x + self.size, y + self.size), (x + self.size + claw_length, y + self.size + claw_length), 2)
            
        else:  # Ice enemy
            pygame.draw.ellipse(surface, (150, 220, 255), (x, y, self.size, self.size))
            shard_length = 20
            if self.attack_animation > 0:
                shard_length = 30 * (1 - self.attack_animation / 10)
            for i in range(8):
                angle = i * math.pi / 4
                shard_x = x + self.size//2 + math.cos(angle) * shard_length
                shard_y = y + self.size//2 + math.sin(angle) * shard_length
                pygame.draw.line(surface, (200, 240, 255), 
                               (x + self.size//2, y + self.size//2),
                               (shard_x, shard_y), 2)
            pygame.draw.circle(surface, (0, 100, 200), (x + 15, y + 15), 4)
            pygame.draw.circle(surface, (0, 100, 200), (x + self.size - 15, y + 15), 4)
            breath_width = 10
            if self.attack_animation > 0:
                breath_width = 20 * (1 - self.attack_animation / 10)
            pygame.draw.arc(surface, (100, 200, 255), (x + 10, y + 25, self.size - 20, breath_width), 0, math.pi, 2)
            
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
            
            if 0 <= new_x < SCREEN_WIDTH:
                self.x = new_x
            if 0 <= new_y < SCREEN_HEIGHT:
                self.y = new_y

class Item:
    def __init__(self):
        self.size = ITEM_SIZE
        self.x = random.randint(0, GRID_WIDTH-1) * GRID_SIZE
        self.y = random.randint(0, GRID_HEIGHT-1) * GRID_SIZE
        self.type = random.choice(["health", "mana"])
        self.color = ITEM_COLOR if self.type == "health" else MANA_COLOR
        self.pulse = 0
        self.float_offset = 0
        
    def update(self):
        self.pulse += 0.1
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 3
        
    def draw(self, surface):
        pulse_size = self.size//2 + math.sin(self.pulse) * 3
        y_pos = self.y + self.float_offset
        
        pygame.draw.circle(surface, self.color, (self.x + self.size//2, y_pos + self.size//2), pulse_size)
        
        if self.type == "health":
            pygame.draw.rect(surface, (255, 255, 255), (self.x + 10, y_pos + 8, 10, 14), border_radius=2)
        else:
            pygame.draw.polygon(surface, (255, 255, 255), 
                              [(self.x + 15, y_pos + 8),
                               (self.x + 8, y_pos + 22),
                               (self.x + 22, y_pos + 22)])

class Dragon:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.animation_frame = 0
        self.fire_frame = 0
        self.fire_active = False
        self.flap_direction = 1
        self.flap_speed = 0.1
        
    def draw(self, surface):
        pygame.draw.ellipse(surface, DRAGON_COLOR, (self.x, self.y + 30, 180, 70))
        pygame.draw.circle(surface, DRAGON_COLOR, (self.x + 180, self.y + 50), 35)
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
        
        pygame.draw.polygon(surface, DRAGON_COLOR, [
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
            for i in range(15):
                fire_size = 5 + i * 1.5
                alpha = max(0, 200 - i * 10)
                fire_color = (255, 215, 0, alpha)
                
                fire_surf = pygame.Surface((fire_size*2, fire_size*2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, fire_color, (fire_size, fire_size), fire_size)
                surface.blit(
                    fire_surf, 
                    (
                        self.x + 180 + 35 + i*15 + self.fire_frame*2, 
                        self.y + 40
                    )
                )
        
        self.animation_frame += self.flap_speed
        
    def breathe_fire(self):
        self.fire_active = True
        self.fire_frame = 0
        
    def update(self):
        if self.fire_active:
            self.fire_frame += 1
            if self.fire_frame > 30:
                self.fire_active = False

class BattleScreen:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy
        self.state = "player_turn"
        self.battle_log = ["Battle started!", "It's your turn!"]
        self.buttons = [
            Button(50, 450, 180, 50, "ATTACK"),
            Button(250, 450, 180, 50, "MAGIC"),
            Button(450, 450, 180, 50, "ITEM"),
            Button(650, 450, 180, 50, "RUN")
        ]
        self.selected_option = 0
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
        self.magic_effect = {
            'active': False,
            'x': 0, 'y': 0,
            'radius': 0,
            'max_radius': 50,
            'color': MAGIC_COLORS[0]
        }
        self.is_boss = hasattr(enemy, 'enemy_type') and enemy.enemy_type == "boss_dragon"
        self.pending_elemental_effect = None
        self.elemental_effect_timer = 0
        
    def start_transition(self):
        self.transition_state = "in"
        self.transition_alpha = 0
        
    def add_screen_shake(self, intensity=5, duration=10):
        self.screen_shake = duration
        self.shake_intensity = intensity
        
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
        player_x, player_y = 200 + shake_offset_x, 300 + shake_offset_y
        enemy_x, enemy_y = 700 + shake_offset_x, 200 + shake_offset_y
        
        # Draw player
        if self.player.type == "Warrior":
            pygame.draw.rect(temp_surface, (0, 120, 0), (player_x, player_y + 10, 50, 40))
            pygame.draw.circle(temp_surface, (240, 200, 150), (player_x + 25, player_y + 15), 10)
            pygame.draw.rect(temp_surface, (150, 75, 0), (player_x + 5, player_y + 20, 10, 20))
            sword_x = player_x + 50
            sword_y = player_y + 15
            pygame.draw.rect(temp_surface, (200, 200, 200), (sword_x, sword_y, 30, 5))
            pygame.draw.rect(temp_surface, (180, 180, 180), (sword_x, sword_y - 5, 5, 15))
            
        elif self.player.type == "Mage":
            pygame.draw.rect(temp_surface, (0, 100, 150), (player_x, player_y + 15, 50, 35))
            pygame.draw.circle(temp_surface, (240, 200, 150), (player_x + 25, player_y + 15), 10)
            pygame.draw.polygon(temp_surface, (100, 50, 200), 
                              [(player_x + 10, player_y + 15), 
                               (player_x + 40, player_y + 15),
                               (player_x + 25, player_y - 10)])
            pygame.draw.line(temp_surface, (180, 150, 100), (player_x + 10, player_y + 10), (player_x + 10, player_y + 50), 3)
            pygame.draw.circle(temp_surface, (200, 200, 100), (player_x + 10, player_y + 10), 6)
            
        else:  # Rogue
            pygame.draw.rect(temp_surface, (150, 0, 0), (player_x, player_y + 15, 50, 35))
            pygame.draw.circle(temp_surface, (240, 200, 150), (player_x + 25, player_y + 15), 10)
            pygame.draw.polygon(temp_surface, (100, 0, 0), 
                              [(player_x + 10, player_y + 15), 
                               (player_x + 40, player_y + 15),
                               (player_x + 25, player_y - 5)])
            left_dagger_x = player_x + 15
            right_dagger_x = player_x + 35
            dagger_y = player_y + 20
            pygame.draw.polygon(temp_surface, (180, 180, 200), 
                              [(left_dagger_x, dagger_y), 
                               (left_dagger_x + 5, dagger_y - 5),
                               (left_dagger_x + 10, dagger_y)])
            pygame.draw.polygon(temp_surface, (180, 180, 200), 
                              [(right_dagger_x, dagger_y), 
                               (right_dagger_x - 5, dagger_y - 5),
                               (right_dagger_x - 10, dagger_y)])
        
        # Draw enemy
        if hasattr(self.enemy, 'enemy_type') and self.enemy.enemy_type == "boss_dragon":
            # Draw the boss using its own draw method, at the correct position
            # Use a temp surface so boss can draw with transparency
            boss_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            # Place boss at (enemy_x, enemy_y) as its top-left
            self.enemy.x = enemy_x
            self.enemy.y = enemy_y
            self.enemy.draw(boss_surf)
            temp_surface.blit(boss_surf, (0, 0))
        elif self.enemy.enemy_type == "fiery":
            pygame.draw.ellipse(temp_surface, (220, 80, 0), (enemy_x, enemy_y, 60, 60))
            for i in range(12):
                angle = i * math.pi / 6
                flame_length = random.randint(10, 20)
                flame_x = enemy_x + 30 + math.cos(angle) * flame_length
                flame_y = enemy_y + 30 + math.sin(angle) * flame_length
                flame_color = random.choice(FIRE_COLORS)
                pygame.draw.line(temp_surface, flame_color, 
                               (enemy_x + 30, enemy_y + 30),
                               (flame_x, flame_y), 3)
            pygame.draw.circle(temp_surface, (255, 255, 0), (enemy_x + 20, enemy_y + 25), 6)
            pygame.draw.circle(temp_surface, (255, 255, 0), (enemy_x + 40, enemy_y + 25), 6)
        elif self.enemy.enemy_type == "shadow":
            pygame.draw.ellipse(temp_surface, (30, 30, 60), (enemy_x, enemy_y, 60, 60))
            for i in range(10):
                offset_x = random.randint(-10, 10)
                offset_y = random.randint(-10, 10)
                size = random.randint(5, 15)
                alpha = random.randint(50, 150)
                smoke_surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (70, 70, 120, alpha), (size, size), size)
                temp_surface.blit(smoke_surf, (enemy_x + 30 - size + offset_x, enemy_y + 30 - size + offset_y))
            pygame.draw.circle(temp_surface, (0, 255, 255), (enemy_x + 20, enemy_y + 25), 7)
            pygame.draw.circle(temp_surface, (0, 255, 255), (enemy_x + 40, enemy_y + 25), 7)
        else:  # Ice enemy
            pygame.draw.ellipse(temp_surface, (180, 230, 255), (enemy_x, enemy_y, 60, 60))
            for i in range(8):
                angle = i * math.pi / 4
                crystal_length = random.randint(10, 20)
                crystal_x = enemy_x + 30 + math.cos(angle) * crystal_length
                crystal_y = enemy_y + 30 + math.sin(angle) * crystal_length
                pygame.draw.line(temp_surface, (220, 240, 255), 
                               (enemy_x + 30, enemy_y + 30),
                               (crystal_x, crystal_y), 3)
            pygame.draw.circle(temp_surface, (0, 100, 200), (enemy_x + 20, enemy_y + 25), 6)
            pygame.draw.circle(temp_surface, (0, 100, 200), (enemy_x + 40, enemy_y + 25), 6)
        
        # Draw attack effect if active
        if self.attack_effect_timer > 0:
            # Draw a simple slash effect
            effect_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            pygame.draw.line(
                effect_surf, 
                (255, 255, 255, 150),
                (player_x + 50, player_y + 25),
                (enemy_x, enemy_y + 30),
                5
            )
            temp_surface.blit(effect_surf, (0, 0))
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
        
        # Draw health bars
        player_health_width = 150 * (self.player.health / max(1, self.player.max_health))
        # Only draw enemy health bar if not boss
        pygame.draw.rect(temp_surface, (30, 30, 50), (180, 360, 160, 20))
        pygame.draw.rect(temp_surface, HEALTH_COLOR, (182, 362, player_health_width, 16))
        player_text = font_small.render(f"{self.player.health}/{self.player.max_health}", True, TEXT_COLOR)
        text_rect = player_text.get_rect(center=(180 + 80, 360 + 10))
        temp_surface.blit(player_text, text_rect)
        if not (hasattr(self.enemy, 'enemy_type') and self.enemy.enemy_type == "boss_dragon"):
            enemy_health_width = 150 * (self.enemy.health / max(1, self.enemy.max_health))
            pygame.draw.rect(temp_surface, (30, 30, 50), (680, 260, 160, 20))
            pygame.draw.rect(temp_surface, HEALTH_COLOR, (682, 262, enemy_health_width, 16))
            enemy_text = font_small.render(f"{self.enemy.health}/{self.enemy.max_health}", True, TEXT_COLOR)
            text_rect = enemy_text.get_rect(center=(680 + 80, 260 + 10))
            temp_surface.blit(enemy_text, text_rect)
        # Draw enemy name (not for boss)
        if not (hasattr(self.enemy, 'enemy_type') and self.enemy.enemy_type == "boss_dragon"):
            enemy_name = font_small.render(self.enemy.name, True, (255, 215, 0))
            name_rect = enemy_name.get_rect(midtop=(enemy_x + 30, enemy_y - 25))
            temp_surface.blit(enemy_name, name_rect)
        
        # Draw battle log
        pygame.draw.rect(temp_surface, UI_BG, (100, 50, 800, 100), border_radius=8)
        pygame.draw.rect(temp_surface, UI_BORDER, (100, 50, 800, 100), 3, border_radius=8)
        
        start_idx = max(0, len(self.battle_log) - self.log_lines_per_page)
        end_idx = min(len(self.battle_log), start_idx + self.log_lines_per_page)
        
        for i, log in enumerate(self.battle_log[start_idx:end_idx]):
            log_text = font_small.render(log, True, TEXT_COLOR)
            temp_surface.blit(log_text, (120, 70 + i * 30))
        
        if self.waiting_for_continue:
            continue_text = font_small.render("(Press ENTER to continue...)", True, (255, 215, 0))
            temp_surface.blit(continue_text, (120, 70 + self.log_lines_per_page * 30))
        
        # Draw buttons
        if self.state == "player_turn" and not self.waiting_for_continue:
            for i, button in enumerate(self.buttons):
                button.selected = (i == self.selected_option)
                button.draw(temp_surface)
        
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
            
        # Show summary after battle
        if self.battle_ended and self.show_summary:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            temp_surface.blit(overlay, (0, 0))
            
            if self.result == "win":
                summary = [
                    "VICTORY!",
                    f"EXP GAINED: 25",
                    f"KILLS: {self.player.kills}",
                    "Press ENTER to continue..."
                ]
            elif self.result == "lose":
                summary = [
                    "DEFEAT...",
                    "Press ENTER to continue..."
                ]
            elif self.result == "escape":
                summary = [
                    "You Escaped!",
                    "Press ENTER to continue..."
                ]
                
            for i, line in enumerate(summary):
                text = font_large.render(line, True, TEXT_COLOR)
                temp_surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i*60))
        
        # Draw the temporary surface to the screen
        surface.blit(temp_surface, (0, 0))

    def update(self):
        self.player.update_animation()
        self.enemy.update_animation()
        self.particle_system.update()
        
        # Update magic effect
        if self.magic_effect['active']:
            self.magic_effect['radius'] += 3
            if self.magic_effect['radius'] > self.magic_effect['max_radius']:
                self.magic_effect['active'] = False
                self.magic_effect['radius'] = 0
        
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
            return True
        elif self.player.health <= 0:
            self.battle_ended = True
            self.result = "lose"
            self.add_log("You were defeated...")
            self.show_summary = True
            return True
        
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
            damage = max(1, self.enemy.strength - self.player.defense // 3)
            self.player.health -= damage
            self.add_log(f"{self.enemy.name} attacks for {damage} damage!")
            self.damage_target = "player"
            self.damage_amount = damage
            self.damage_effect_timer = 20
            self.enemy.start_attack_animation()
            self.player.start_hit_animation()
            self.add_screen_shake(3, 5)
            # Elemental effect after dialog
            self.pending_elemental_effect = self.enemy.enemy_type
            self.elemental_effect_timer = 20
            self.state = "player_turn"
            self.add_log("It's your turn!")
            self.action_cooldown = self.action_delay
            
        return False
    
    def add_log(self, message):
        self.battle_log.append(message)
        self.waiting_for_continue = True
    
    def handle_input(self, event, game=None):
        if self.waiting_for_continue:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                self.waiting_for_continue = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.waiting_for_continue = False
            return
            
        if self.battle_ended and self.show_summary:
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                if self.result == "escape" and game:
                    self.show_summary = False
                    game.state = "overworld"
                    game.battle_screen = None
                else:
                    self.show_summary = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.result == "escape" and game:
                    self.show_summary = False
                    game.state = "overworld"
                    game.battle_screen = None
                else:
                    self.show_summary = False
        elif self.state == "player_turn" and not self.battle_ended and self.action_cooldown == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_option = (self.selected_option + 1) % 4
                    if game and hasattr(game, 'SFX_ARROW') and game.SFX_ARROW: game.SFX_ARROW.play()
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_option = (self.selected_option - 1) % 4
                    if game and hasattr(game, 'SFX_ARROW') and game.SFX_ARROW: game.SFX_ARROW.play()
                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 2) % 4
                    if game and hasattr(game, 'SFX_ARROW') and game.SFX_ARROW: game.SFX_ARROW.play()
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 2) % 4
                    if game and hasattr(game, 'SFX_ARROW') and game.SFX_ARROW: game.SFX_ARROW.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if game and hasattr(game, 'SFX_ENTER') and game.SFX_ENTER: game.SFX_ENTER.play()
                    self.handle_action(game)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.buttons):
                    if button.rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        if game and hasattr(game, 'SFX_ENTER') and game.SFX_ENTER: game.SFX_ENTER.play()
                        self.handle_action(game)
    
    def handle_action(self, game=None):
        if self.state != "player_turn" or self.battle_ended or self.action_cooldown > 0:
            return
        if self.selected_option == 0:  # Attack
            if game and hasattr(game, 'SFX_ATTACK') and game.SFX_ATTACK: game.SFX_ATTACK.play()
            self.action_steps = [
                lambda: self.add_log("You attack!"),
                lambda: self.start_attack_animation(),
                lambda: self.execute_attack()
            ]
        elif self.selected_option == 1:  # Magic
            if self.player.mana >= 20:
                if game and hasattr(game, 'SFX_MAGIC') and game.SFX_MAGIC: game.SFX_MAGIC.play()
                self.action_steps = [
                    lambda: self.add_log("You cast a fireball!"),
                    lambda: self.start_magic_animation(),
                    lambda: self.execute_magic()
                ]
            else:
                if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
                self.add_log("Not enough mana!")
        elif self.selected_option == 2:  # Item
            if game and hasattr(game, 'SFX_ITEM') and game.SFX_ITEM: game.SFX_ITEM.play()
            self.action_steps = [
                lambda: self.add_log("You used a health potion!"),
                lambda: self.execute_item()
            ]
        elif self.selected_option == 3:  # Run
            if game and hasattr(game, 'SFX_CLICK') and game.SFX_CLICK: game.SFX_CLICK.play()
            self.action_steps = [
                lambda: self.add_log("You attempt to escape..."),
                lambda: self.execute_run()
            ]
    
    def start_attack_animation(self):
        self.player.start_attack_animation()
        self.attack_effect_timer = 20
        
        # Create particles for attack animation
        for _ in range(15):
            angle = random.uniform(0, math.pi*2)
            dist = random.uniform(0, 10)
            px = 200 + 50 + math.cos(angle) * dist
            py = 300 + 25 + math.sin(angle) * dist
            self.particle_system.add_particle(
                px, py, 
                (255, 255, 200),
                (math.cos(angle) * 0.5, math.sin(angle) * 0.5),
                3, 30
            )
    
    def start_magic_animation(self):
        self.player.start_attack_animation()
        self.magic_effect = {
            'active': True,
            'x': 200 + 10,  # Staff top x
            'y': 300,       # Staff top y
            'radius': 0,
            'max_radius': 100,
            'color': random.choice(MAGIC_COLORS)
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
    
    def execute_attack(self):
        damage = self.player.strength
        self.enemy.health -= damage
        self.add_log(f"You dealt {damage} damage to {self.enemy.name}!")
        self.damage_target = "enemy"
        self.damage_amount = damage
        self.damage_effect_timer = 20
        self.enemy.start_hit_animation()
        self.add_screen_shake(5, 8)
        
        if self.enemy.enemy_type == "fiery":
            self.particle_system.add_explosion(
                700 + 30, 200 + 30, FIRE_COLORS[0], 
                count=30, size_range=(2, 6), speed_range=(1, 4), lifetime_range=(15, 30)
            )
        elif self.enemy.enemy_type == "shadow":
            self.particle_system.add_explosion(
                700 + 30, 200 + 30, SHADOW_COLORS[1], 
                count=20, size_range=(3, 8), speed_range=(0.5, 2), lifetime_range=(20, 40)
            )
        else:  # Ice
            self.particle_system.add_explosion(
                700 + 30, 200 + 30, ICE_COLORS[2], 
                count=25, size_range=(2, 5), speed_range=(1, 3), lifetime_range=(15, 25)
            )
        
        self.state = "enemy_turn"
        self.action_cooldown = self.action_delay
    
    def execute_magic(self):
        damage = self.player.strength * 2
        self.enemy.health -= damage
        self.player.mana -= 20
        self.add_log(f"Fireball dealt {damage} damage to {self.enemy.name}!")
        self.damage_target = "enemy"
        self.damage_amount = damage
        self.damage_effect_timer = 20
        self.enemy.start_hit_animation()
        self.add_screen_shake(8, 10)
        
        self.particle_system.add_beam(
            200 + 10, 300,  # Staff top
            700 + 30, 200 + 30,  # Enemy center
            self.magic_effect['color'], width=5, particle_count=15, speed=3
        )
        
        self.particle_system.add_explosion(
            700 + 30, 200 + 30, self.magic_effect['color'],
            count=40, size_range=(3, 7), speed_range=(1, 5), lifetime_range=(15, 30)
        )
        
        self.state = "enemy_turn"
        self.action_cooldown = self.action_delay
    
    def execute_item(self):
        heal_amount = 30
        self.player.health = min(self.player.max_health, self.player.health + heal_amount)
        self.add_log(f"Restored {heal_amount} HP!")
        
        for _ in range(20):
            x = random.randint(200, 200 + PLAYER_SIZE)
            y = random.randint(300, 300 + PLAYER_SIZE)
            self.particle_system.add_particle(
                x, y, HEALTH_COLOR,
                (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)),
                3, 30
            )
        
        self.state = "enemy_turn"
        self.action_cooldown = self.action_delay
    
    def execute_run(self):
        if random.random() < 0.7:  # 70% chance to escape
            self.add_log("You successfully escaped!")
            self.battle_ended = True
            self.result = "escape"
            self.show_summary = True
        else:
            self.add_log("Escape failed! The enemy attacks!")
            self.state = "enemy_turn"
            self.action_cooldown = self.action_delay

class OpeningCutscene:
    def __init__(self):
        self.state = "intro"
        self.timer = 0
        self.scene_duration = 300  # 5 seconds per scene at 60 FPS
        self.scene_index = 0
        self.transition_alpha = 0
        self.transition_speed = 5
        self.text_alpha = 0
        self.text_appear_speed = 3
        self.text_disappear_speed = 2
        self.particle_system = ParticleSystem()
        self.scroll_y = SCREEN_HEIGHT
        self.scroll_speed = 1
        self.transition_state = "none"  # Initialize transition_state
        
    def update(self):
        self.timer += 1
        self.particle_system.update()
        
        # Update text alpha
        if self.timer < 120:  # First 2 seconds: text appears
            self.text_alpha = min(255, self.text_alpha + self.text_appear_speed)
        elif self.timer > 180:  # Last 2 seconds: text disappears
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
        
        # Scroll text for scene 3
        if self.scene_index == 2:
            self.scroll_y -= self.scroll_speed
            if self.scroll_y < -600:
                self.scroll_y = SCREEN_HEIGHT
        
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
            skip_text = font_small.render("Press any key to skip...", True, (200, 200, 200))
            screen.blit(skip_text, (SCREEN_WIDTH - skip_text.get_width() - 20, SCREEN_HEIGHT - 40))
    
    def draw_intro_scene(self, screen):
        # Draw starfield background
        screen.fill(BACKGROUND)
        for i in range(100):
            x = i * 10
            y = math.sin(pygame.time.get_ticks() * 0.001 + i) * 50 + SCREEN_HEIGHT//2
            pygame.draw.circle(screen, (200, 200, 255), (x, int(y)), 1)
        
        # Draw title
        title = font_large.render("DRAGON'S LAIR", True, (255, 50, 50))
        title_shadow = font_large.render("DRAGON'S LAIR", True, (150, 0, 0))
        screen.blit(title_shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 103))
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
        
        # Draw subtitle
        subtitle = font_medium.render("A RETRO RPG ADVENTURE", True, TEXT_COLOR)
        subtitle_shadow = font_medium.render("A RETRO RPG ADVENTURE", True, (0, 100, 100))
        screen.blit(subtitle_shadow, (SCREEN_WIDTH//2 - subtitle.get_width()//2 + 2, 162))
        screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 160))
        
        # Draw intro text
        intro_text = [
            "LONG AGO, IN THE KINGDOM OF PIXELONIA,",
            "AN ANCIENT EVIL AWOKE FROM ITS SLUMBER.",
            "THE DRAGON MALAKOR, RULER OF SHADOWS,",
            "THREATENED TO PLUNGE THE WORLD INTO DARKNESS."
        ]
        
        y_pos = 250
        for line in intro_text:
            text = font_cinematic.render(line, True, TEXT_COLOR)
            text.set_alpha(self.text_alpha)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 50
    
    def draw_dragon_scene(self, screen):
        # Draw dark background
        screen.fill((10, 5, 20))
        
        # Draw mountains
        for i in range(10):
            height = 150 + random.randint(0, 50)
            pygame.draw.polygon(screen, (30, 30, 60), [
                (i * 100, SCREEN_HEIGHT),
                (i * 100 + 50, SCREEN_HEIGHT - height),
                (i * 100 + 100, SCREEN_HEIGHT)
            ])
        
        # Draw dragon silhouette
        dragon_x = SCREEN_WIDTH//2 - 100
        dragon_y = SCREEN_HEIGHT//2 - 50
        
        # Body
        pygame.draw.ellipse(screen, (60, 20, 20), (dragon_x, dragon_y, 200, 80))
        # Head
        pygame.draw.circle(screen, (60, 20, 20), (dragon_x + 200, dragon_y + 40), 40)
        # Wings
        wing_offset = math.sin(pygame.time.get_ticks() * 0.005) * 10
        pygame.draw.polygon(screen, (80, 30, 30), [
            (dragon_x + 50, dragon_y + 40),
            (dragon_x - 50, dragon_y - 50 - wing_offset),
            (dragon_x + 50, dragon_y - 30 - wing_offset)
        ])
        pygame.draw.polygon(screen, (80, 30, 30), [
            (dragon_x + 50, dragon_y + 40),
            (dragon_x - 50, dragon_y + 130 + wing_offset),
            (dragon_x + 50, dragon_y + 110 + wing_offset)
        ])
        
        # Draw fire breath
        for i in range(20):
            x = dragon_x + 230 + i * 10
            y = dragon_y + 40 + math.sin(pygame.time.get_ticks() * 0.01 + i) * 10
            size = 10 - i * 0.4
            if size > 0:
                pygame.draw.circle(screen, (255, 150, 0), (x, y), int(size))
        
        # Draw scene text
        scene_text = [
            "THE DRAGON MALAKOR RAVAGED THE LAND,",
            "BURNING VILLAGES AND TERRIFYING THE PEOPLE.",
            "THE KING CALLED FOR HEROES TO RISE UP",
            "AND CHALLENGE THE ANCIENT EVIL."
        ]
        
        y_pos = 100
        for line in scene_text:
            text = font_cinematic.render(line, True, (255, 200, 100))
            text.set_alpha(self.text_alpha)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 50
    
    def draw_story_scene(self, screen):
        # Draw parchment background
        screen.fill((200, 180, 120))
        pygame.draw.rect(screen, (180, 150, 100), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100))
        pygame.draw.rect(screen, (150, 120, 80), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 3)
        
        # Draw story text (scrolling)
        story = [
            "YOUR QUEST BEGINS...",
            "",
            "THE KINGDOM OF PIXELONIA NEEDS A HERO.",
            "MALAKOR THE TERRIBLE HAS RETURNED,",
            "AND ONLY YOU CAN STOP HIM.",
            "",
            "TRAVEL THROUGH PERILOUS LANDS,",
            "BATTLE FIERCE MONSTERS,",
            "AND GATHER POWERFUL ARTIFACTS.",
            "",
            "YOUR JOURNEY LEADS TO THE DRAGON'S LAIR,",
            "WHERE THE FINAL CONFRONTATION AWAITS.",
            "",
            "CHOOSE YOUR HERO WISELY,",
            "FOR THE FATE OF THE KINGDOM RESTS IN YOUR HANDS."
        ]
        
        y_pos = self.scroll_y
        for line in story:
            text = font_cinematic.render(line, True, (60, 40, 20))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, y_pos))
            screen.blit(text, text_rect)
            y_pos += 50
        
        # Draw decorative elements
        pygame.draw.line(screen, (100, 80, 60), (100, 100), (100, SCREEN_HEIGHT - 100), 2)
        pygame.draw.line(screen, (100, 80, 60), (SCREEN_WIDTH - 100, 100), (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 2)
        
        # Draw scroll top and bottom
        pygame.draw.rect(screen, (150, 120, 80), (40, 40, SCREEN_WIDTH - 80, 20))
        pygame.draw.rect(screen, (150, 120, 80), (40, SCREEN_HEIGHT - 60, SCREEN_WIDTH - 80, 20))
        
        # Draw continue prompt
        if self.timer > 180 and pygame.time.get_ticks() % 1000 < 500:
            prompt = font_medium.render("PRESS ENTER TO CONTINUE", True, (100, 60, 30))
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT - 80))
    
    def skip(self):
        # Skip to the end of the cutscene
        self.scene_index = 3

def is_android():
    return (
        sys.platform.startswith("android") or
        "ANDROID_ARGUMENT" in os.environ
    )

class Game:
    def __init__(self):
        self.state = "start_menu"
        self.player = None
        self.enemies = []
        self.items = []
        self.score = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.item_timer = 0
        self.starfield = []
        self.dragon = Dragon(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 120)
        self.fire_timer = 0
        self.battle_screen = None
        self.transition_alpha = 0
        self.transition_state = "none"
        self.transition_speed = 10
        self.player_moved = False
        self.movement_cooldown = 0
        self.movement_delay = 10
        self.particle_system = ParticleSystem()
        self.opening_cutscene = OpeningCutscene()
        self.boss_battle_triggered = False
        self.boss_defeated = False
        
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
        self.start_button = Button(SCREEN_WIDTH//2 - 120, 500, 240, 60, "START QUEST", UI_BORDER)
        self.quit_button = Button(SCREEN_WIDTH//2 - 120, 580, 240, 60, "QUIT", UI_BORDER)
        self.back_button = Button(20, 20, 100, 40, "BACK")
        
        # Character buttons
        self.warrior_button = Button(SCREEN_WIDTH//2 - 300, 300, 200, 150, "WARRIOR", (0, 255, 0))
        self.mage_button = Button(SCREEN_WIDTH//2 - 50, 300, 200, 150, "MAGE", (0, 200, 255))
        self.rogue_button = Button(SCREEN_WIDTH//2 + 200, 300, 200, 150, "ROGUE", (255, 100, 0))
        
        # === RETRO COMPUTER-GENERATED SOUND EFFECTS ===
        def generate_tone(frequency=440, duration_ms=100, volume=0.5, sample_rate=44100, waveform='sine'):
            t = np.linspace(0, duration_ms / 1000, int(sample_rate * duration_ms / 1000), False)
            if waveform == 'sine':
                wave = np.sin(frequency * 2 * np.pi * t)
            elif waveform == 'square':
                wave = np.sign(np.sin(frequency * 2 * np.pi * t))
            elif waveform == 'noise':
                wave = np.random.uniform(-1, 1, t.shape)
            else:
                wave = np.sin(frequency * 2 * np.pi * t)
            audio = (wave * volume * 32767).astype(np.int16)
            # Make it stereo by duplicating the mono channel
            audio_stereo = np.column_stack((audio, audio))
            return pygame.sndarray.make_sound(audio_stereo)
        try:
            pygame.mixer.init()
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
        
        # === RETRO COMPUTER-GENERATED BACKGROUND MUSIC ===
        # Transpose melody down a whole step (approx -2 semitones)
        # New scale: Bb, Db, Eb, F, Ab, Bb
        Bb5 = 932.33
        Db5 = 554.37
        Eb5 = 622.25
        F5 = 698.46
        Ab5 = 830.61
        Bb5 = 932.33
        Bb3 = 233.08
        F3 = 174.61
        Eb3 = 155.56
        Ab3 = 207.65
        Db4 = 277.18
        Bb2 = 116.54
        # Keep bass as is for now
        C3 = 130.81
        G3 = 196.00

        # Dream-like chiptune song
        melody_A = [
            (Db5, 0.4), (Eb5, 0.2), (F5, 0.3), (0, 0.2),
            (Eb5, 0.3), (Db5, 0.2), (Bb5, 0.4), (0, 0.2),
        ]
        melody_B = [
            (F5, 0.3), (Ab5, 0.2), (Bb5, 0.3), (0, 0.2),
            (Ab5, 0.3), (F5, 0.2), (Eb5, 0.4), (0, 0.2),
        ]
        melody_C = [
            (Db5, 0.3), (Eb5, 0.2), (F5, 0.3), (Ab5, 0.2),
            (Bb5, 0.3), (Ab5, 0.2), (F5, 0.4), (0, 0.2),
        ]
        melody_D = [
            (Eb5, 0.3), (Db5, 0.2), (Bb5, 0.3), (0, 0.2),
            (Db5, 0.3), (F5, 0.2), (Ab5, 0.4), (0, 0.2),
        ]
        climax_melody = [
            (Bb5, 0.2), (Db5, 0.2), (Eb5, 0.2), (F5, 0.2),
            (Ab5, 0.2), (F5, 0.2), (Db5, 0.2), (Bb5, 0.4),
        ]
        melody_notes = melody_A + melody_B + melody_C + melody_D + climax_melody

        bass_A = [
            (Db4, 0.8), (0, 0.2), (Bb3, 0.8), (0, 0.2),
        ]
        bass_B = [
            (F3, 0.8), (0, 0.2), (Ab3, 0.8), (0, 0.2),
        ]
        bass_C = [
            (Eb3, 0.8), (0, 0.2), (Db4, 0.8), (0, 0.2),
        ]
        bass_D = [
            (Bb3, 0.8), (0, 0.2), (F3, 0.8), (0, 0.2),
        ]
        climax_bass = [
            (Db4, 0.4), (Ab3, 0.4), (Bb3, 0.4), (F3, 0.4),
        ]
        bass_notes = bass_A + bass_B + bass_C + bass_D + climax_bass

        # Percussion: only in climax
        main_perc = [(0, 0.2)] * (len(melody_notes) - 8)
        climax_perc = [(1800, 0.05) if i % 2 == 0 else (0, 0.15) for i in range(8)]
        percussion_notes = main_perc + climax_perc

        # Lead: only in climax
        lead_notes = [(0, 0.2)] * (len(melody_notes) - 8) + [
            (1865, 0.1), (0, 0.1), (2093, 0.1), (0, 0.1),
            (2349, 0.1), (0, 0.1), (2489, 0.1), (0, 0.1),
        ]

        self.music = generate_chiptune_song(
            melody_notes, bass_notes, percussion=percussion_notes, lead=lead_notes, bpm=98, volume=0.18
        )
        self.music_channel = pygame.mixer.Channel(1)
        self.music_channel.play(self.music, loops=-1)
        
        # Virtual button setup for Android
        self.android_buttons = {}
        if is_android():
            button_size = 80
            button_margin = 20
            screen_w, screen_h = SCREEN_WIDTH, SCREEN_HEIGHT
            # D-pad
            self.android_buttons['up'] = pygame.Rect(button_margin + button_size, screen_h - 3*button_size, button_size, button_size)
            self.android_buttons['down'] = pygame.Rect(button_margin + button_size, screen_h - button_size, button_size, button_size)
            self.android_buttons['left'] = pygame.Rect(button_margin, screen_h - 2*button_size, button_size, button_size)
            self.android_buttons['right'] = pygame.Rect(button_margin + 2*button_size, screen_h - 2*button_size, button_size, button_size)
            # Enter/Space
            self.android_buttons['enter'] = pygame.Rect(screen_w - button_margin - button_size, screen_h - 2*button_size, button_size, button_size)
            self.android_buttons['space'] = pygame.Rect(screen_w - button_margin - 2*button_size, screen_h - 2*button_size, button_size, button_size)
    
    def spawn_enemy(self):
        if len(self.enemies) < 5:
            self.enemies.append(Enemy(self.player.level if self.player else 1))
    
    def spawn_item(self):
        if len(self.items) < 3:
            self.items.append(Item())
    
    def start_transition(self):
        self.transition_state = "in"
        self.transition_alpha = 0
    
    def update(self):
        # Update starfield
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
        
        # Update particles
        self.particle_system.update()
        
        # Handle transition
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
        
        if self.state == "start_menu":
            self.dragon.update()
            self.fire_timer += 1
            if self.fire_timer > 120:
                self.dragon.breathe_fire()
                self.fire_timer = 0
                
        elif self.state == "opening_cutscene":
            # Update cutscene
            next_state = self.opening_cutscene.update()
            if next_state:
                self.state = next_state
                
        elif self.state == "character_select":
            pass
                
        elif self.state == "overworld" and self.player:
            self.game_time += 1
            self.spawn_timer += 1
            self.item_timer += 1
            self.movement_cooldown = max(0, self.movement_cooldown - 1)
            
            self.player.update_animation()
            
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
                
            for enemy in self.enemies[:]:
                if self.player:  # Ensure player exists
                    player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, ENEMY_SIZE, ENEMY_SIZE)
                    
                    if player_rect.colliderect(enemy_rect):
                        self.battle_screen = BattleScreen(self.player, enemy)
                        self.battle_screen.start_transition()
                        self.state = "battle"
                        self.enemies.remove(enemy)
                        self.player_moved = False
                        break
                    
            for item in self.items[:]:
                if self.player:  # Ensure player exists
                    item_rect = pygame.Rect(item.x, item.y, ITEM_SIZE, ITEM_SIZE)
                    player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                    
                    if player_rect.colliderect(item_rect):
                        if item.type == "health":
                            self.player.health = min(self.player.max_health, self.player.health + 30)
                            for _ in range(15):
                                x = random.randint(self.player.x, self.player.x + PLAYER_SIZE)
                                y = random.randint(self.player.y, self.player.y + PLAYER_SIZE)
                                self.particle_system.add_particle(
                                    x, y, HEALTH_COLOR,
                                    (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)),
                                    3, 30
                                )
                        else:
                            self.player.mana = min(self.player.max_mana, self.player.mana + 40)
                            for _ in range(15):
                                x = random.randint(self.player.x, self.player.x + PLAYER_SIZE)
                                y = random.randint(self.player.y, self.player.y + PLAYER_SIZE)
                                self.particle_system.add_particle(
                                    x, y, MANA_COLOR,
                                    (random.uniform(-0.5, 0.5), random.uniform(-1, -0.5)),
                                    3, 30
                                )
                        self.player.items_collected += 1
                        self.items.remove(item)
    
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
            if self.start_button.text != "START QUEST":
                self.start_button.text = "START QUEST"
                self.start_button.text_surf = font_medium.render(self.start_button.text, True, TEXT_COLOR)
                self.start_button.text_rect = self.start_button.text_surf.get_rect(center=self.start_button.rect.center)
            
            title = font_large.render("DRAGON'S LAIR", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            
            subtitle = font_medium.render("A RETRO RPG ADVENTURE", True, TEXT_COLOR)
            screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
            
            self.dragon.draw(screen)
            
            self.start_button.draw(screen)
            self.quit_button.draw(screen)
            
            instructions = [
                "SELECT YOUR HERO AND EMBARK ON A QUEST",
                "DEFEAT THE DRAGON'S MINIONS AND SURVIVE!",
                "",
                "CONTROLS:",
                "ARROWS/WASD - MOVE",
                "ENTER - SELECT",
                "ESC - QUIT"
            ]
            
            for i, line in enumerate(instructions):
                text = font_tiny.render(line, True, TEXT_COLOR)
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 350 + i*25))
            
        elif self.state == "opening_cutscene":
            # Draw the opening cutscene
            self.opening_cutscene.draw(screen)
            
        elif self.state == "character_select":
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
            
            self.warrior_button.draw(screen)
            self.mage_button.draw(screen)
            self.rogue_button.draw(screen)
            self.back_button.draw(screen)
            
        elif self.state == "overworld" and self.player:
            # Draw grid
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT), 1)
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y), 1)
                
            # Draw items
            for item in self.items:
                item.draw(screen)
                
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(screen)
            
            # Draw player
            self.player.draw(screen)
            
            # Draw particles
            self.particle_system.draw(screen)
            
            # Draw UI panel
            pygame.draw.rect(screen, UI_BG, (10, 10, 250, 130), border_radius=8)
            pygame.draw.rect(screen, UI_BORDER, (10, 10, 250, 130), 3, border_radius=8)
            
            # Draw player stats
            self.player.draw_stats(screen, 20, 20)
            
            # Draw score and other info
            score_text = font_medium.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
            
            time_text = font_small.render(f"TIME: {self.game_time//FPS}s", True, TEXT_COLOR)
            screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 60))
            
            kills_text = font_small.render(f"KILLS: {self.player.kills}", True, TEXT_COLOR)
            screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 20, 90))
            
            # Draw controls info
            controls = [
                "CONTROLS:",
                "ARROWS/WASD - MOVE",
                "ENTER - SELECT",
                "ESC - MENU"
            ]
            
            for i, line in enumerate(controls):
                text = font_tiny.render(line, True, (180, 180, 200))
                screen.blit(text, (20, SCREEN_HEIGHT - 140 + i * 25))
            
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
            self.start_button.draw(screen)
            
            # Back to menu button
            self.back_button.text = "BACK TO MENU"
            self.back_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 100, 240, 60)
            self.back_button.text_surf = font_medium.render(self.back_button.text, True, TEXT_COLOR)
            self.back_button.text_rect = self.back_button.text_surf.get_rect(center=self.back_button.rect.center)
            self.back_button.draw(screen)
            
        if self.state in ["character_select", "game_over"]:
            self.back_button.draw(screen)
            
        if self.transition_state != "none":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(overlay, (0, 0))
            
        # Draw Android virtual controls if on Android
        if is_android() and self.android_buttons:
            # D-pad
            pygame.draw.rect(screen, (200,200,200), self.android_buttons['up'], border_radius=20)
            pygame.draw.polygon(screen, (100,100,100), [
                (self.android_buttons['up'].centerx, self.android_buttons['up'].top+15),
                (self.android_buttons['up'].left+15, self.android_buttons['up'].bottom-15),
                (self.android_buttons['up'].right-15, self.android_buttons['up'].bottom-15)
            ])
            pygame.draw.rect(screen, (200,200,200), self.android_buttons['down'], border_radius=20)
            pygame.draw.polygon(screen, (100,100,100), [
                (self.android_buttons['down'].centerx, self.android_buttons['down'].bottom-15),
                (self.android_buttons['down'].left+15, self.android_buttons['down'].top+15),
                (self.android_buttons['down'].right-15, self.android_buttons['down'].top+15)
            ])
            pygame.draw.rect(screen, (200,200,200), self.android_buttons['left'], border_radius=20)
            pygame.draw.polygon(screen, (100,100,100), [
                (self.android_buttons['left'].left+15, self.android_buttons['left'].centery),
                (self.android_buttons['left'].right-15, self.android_buttons['left'].top+15),
                (self.android_buttons['left'].right-15, self.android_buttons['left'].bottom-15)
            ])
            pygame.draw.rect(screen, (200,200,200), self.android_buttons['right'], border_radius=20)
            pygame.draw.polygon(screen, (100,100,100), [
                (self.android_buttons['right'].right-15, self.android_buttons['right'].centery),
                (self.android_buttons['right'].left+15, self.android_buttons['right'].top+15),
                (self.android_buttons['right'].left+15, self.android_buttons['right'].bottom-15)
            ])
            # Enter
            pygame.draw.rect(screen, (255,215,0), self.android_buttons['enter'], border_radius=20)
            enter_text = font_small.render('ENT', True, (0,0,0))
            screen.blit(enter_text, enter_text.get_rect(center=self.android_buttons['enter'].center))
            # Space
            pygame.draw.rect(screen, (0,255,255), self.android_buttons['space'], border_radius=20)
            space_text = font_small.render('SPC', True, (0,0,0))
            screen.blit(space_text, space_text.get_rect(center=self.android_buttons['space'].center))
        
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
            pygame.display.flip()
            return
        
        pygame.display.flip()
    
    def run(self):
        running = True
        
        while running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                    # Android virtual controls
                    if is_android() and self.android_buttons:
                        mx, my = event.pos
                        for name, rect in self.android_buttons.items():
                            if rect.collidepoint(mx, my):
                                if name == 'up':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
                                    pygame.event.post(fake_event)
                                elif name == 'down':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
                                    pygame.event.post(fake_event)
                                elif name == 'left':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
                                    pygame.event.post(fake_event)
                                elif name == 'right':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
                                    pygame.event.post(fake_event)
                                elif name == 'enter':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
                                    pygame.event.post(fake_event)
                                elif name == 'space':
                                    fake_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
                                    pygame.event.post(fake_event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "overworld":
                            self.state = "game_over"
                        elif self.state == "game_over":
                            self.state = "start_menu"
                        elif self.state == "character_select":
                            self.state = "start_menu"
                        elif self.state == "opening_cutscene":
                            self.opening_cutscene.skip()
                    
                    # Handle skip for cutscene
                    if self.state == "opening_cutscene":
                        self.opening_cutscene.skip()
                    
                    # Handle movement in overworld
                    if self.state == "overworld" and self.player and self.movement_cooldown <= 0:
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            if self.SFX_ARROW: self.SFX_ARROW.play()
                            self.player.move(0, -1)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            if self.SFX_ARROW: self.SFX_ARROW.play()
                            self.player.move(0, 1)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            if self.SFX_ARROW: self.SFX_ARROW.play()
                            self.player.move(-1, 0)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            if self.SFX_ARROW: self.SFX_ARROW.play()
                            self.player.move(1, 0)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                    
                    # Pass input to battle screen
                    if self.state == "battle" and self.battle_screen:
                        self.battle_screen.handle_input(event, self)
            
            # Handle button clicks
            if self.state == "start_menu":
                self.start_button.update(mouse_pos)
                self.quit_button.update(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.state = "opening_cutscene"
                    self.opening_cutscene = OpeningCutscene()  # Reset cutscene
                    
                if self.quit_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    running = False
                    
            elif self.state == "character_select":
                self.warrior_button.update(mouse_pos)
                self.mage_button.update(mouse_pos)
                self.rogue_button.update(mouse_pos)
                self.back_button.update(mouse_pos)
                
                if self.warrior_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.player = Character("Warrior")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.mage_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.player = Character("Mage")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.rogue_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.player = Character("Rogue")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.state = "start_menu"
                    
            elif self.state == "overworld":
                pass
                    
            elif self.state == "battle":
                battle_ended = self.battle_screen.update()
                
                if battle_ended:
                    # Boss battle win
                    if hasattr(self.battle_screen.enemy, 'enemy_type') and self.battle_screen.enemy.enemy_type == "boss_dragon":
                        if self.battle_screen.result == "win":
                            self.boss_defeated = True
                            self.state = "victory"
                            self.battle_screen = None
                        elif self.battle_screen.result == "lose":
                            self.state = "game_over"
                            self.battle_screen = None
                        elif self.battle_screen.result == "escape":
                            self.state = "overworld"
                            self.battle_screen = None
                    else:
                        if self.battle_screen.result == "win":
                            self.player.kills += 1
                            self.player.gain_exp(25)
                            self.score += 10
                            # Boss trigger
                            if self.player.level >= 2 and not self.boss_battle_triggered and not self.boss_defeated:
                                self.boss_battle_triggered = True
                                self.battle_screen = BattleScreen(self.player, BossDragon())
                                self.battle_screen.start_transition()
                                self.state = "battle"
                                continue
                            self.start_transition()
                            self.state = "overworld"
                            self.battle_screen = None
                        elif self.battle_screen.result == "lose":
                            self.state = "game_over"
                            self.battle_screen = None
                        elif self.battle_screen.result == "escape":
                            self.start_transition()
                            self.state = "overworld"
                            self.battle_screen = None
            
            elif self.state == "game_over":
                self.start_button.update(mouse_pos)
                self.back_button.update(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.state = "character_select"
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    if self.SFX_CLICK: self.SFX_CLICK.play()
                    self.state = "start_menu"
            
            self.update()
            self.draw(screen)
            
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
        
        # Spawn initial enemies and items
        for _ in range(3):
            self.spawn_enemy()
        for _ in range(2):
            self.spawn_item()

def generate_chiptune_song(melody, bass, percussion=None, lead=None, bpm=220, sample_rate=44100, volume=0.16):
    melody = [list(note) for note in melody]
    bass = [list(note) for note in bass]
    if percussion is not None:
        percussion = [list(note) for note in percussion]
    if lead is not None:
        lead = [list(note) for note in lead]
    song = np.zeros((0, 2), dtype=np.int16)
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
        step_beats = min(
            m_beats, b_beats,
            p_beats if percussion is not None else m_beats,
            l_beats if lead is not None else m_beats
        )
        step_duration = 60 / bpm * step_beats
        t = np.linspace(0, step_duration, int(sample_rate * step_duration), False)
        m_wave = np.sin(m_freq * 2 * np.pi * t) if m_freq > 0 else np.zeros_like(t)
        b_wave = 0.25 * np.sign(np.sin(b_freq * 2 * np.pi * t)) if b_freq > 0 else np.zeros_like(t)
        p_wave = 0.18 * np.sign(np.sin(p_freq * 2 * np.pi * t)) if percussion is not None and p_freq > 0 else np.zeros_like(t)
        l_wave = 0.18 * np.sin(l_freq * 2 * np.pi * t) if lead is not None and l_freq > 0 else np.zeros_like(t)
        wave = m_wave + b_wave + p_wave + l_wave
        wave = np.clip(wave, -1, 1)
        audio = (wave * volume * 32767).astype(np.int16)
        audio_stereo = np.column_stack((audio, audio))
        song = np.concatenate((song, audio_stereo))
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
    return pygame.sndarray.make_sound(song)

class BossDragon(Enemy):
    def __init__(self):
        super().__init__(player_level=10)
        self.size = 120
        self.x = 700
        self.y = 180
        self.enemy_type = "boss_dragon"
        self.name = "Malakor, the Dragon"
        self.health = 400
        self.max_health = 400
        self.strength = 35
        self.speed = 10
        self.color = (255, 69, 0)
        self.movement_cooldown = 0
        self.movement_delay = 40
        self.animation_offset = 0
        self.attack_animation = 0
        self.hit_animation = 0
        self.fire_breathing = False
        self.fire_breath_timer = 0
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