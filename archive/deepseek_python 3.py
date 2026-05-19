import pygame
import sys
import random
import math
import os

# Initialize Pygame
pygame.init()
pygame.font.init()

# Game constants - Increased screen size
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 700  # Larger screen
PLAYER_SIZE = 50
ENEMY_SIZE = 40
ITEM_SIZE = 30
FPS = 60

# Retro 80s Color Palette
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

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dragon's Lair RPG")
clock = pygame.time.Clock()

# Fonts - Using retro-style fonts
try:
    # Try loading a pixel font
    font_large = pygame.font.Font("freesansbold.ttf", 48)
    font_medium = pygame.font.Font("freesansbold.ttf", 32)
    font_small = pygame.font.Font("freesansbold.ttf", 24)
    font_tiny = pygame.font.Font("freesansbold.ttf", 18)  # Added smaller font
except:
    # Fallback to system fonts
    font_large = pygame.font.SysFont("Courier", 48, bold=True)
    font_medium = pygame.font.SysFont("Courier", 32, bold=True)
    font_small = pygame.font.SysFont("Courier", 24, bold=True)
    font_tiny = pygame.font.SysFont("Courier", 18, bold=True)  # Added smaller font

# Grid settings
GRID_SIZE = 50
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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
        
    def draw(self, surface):
        # Draw glow effect
        if self.glow > 0:
            glow_surf = pygame.Surface((self.rect.width + self.glow*2, self.rect.height + self.glow*2), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.current_color[:3], 50), glow_surf.get_rect(), border_radius=12)
            surface.blit(glow_surf, (self.rect.x - self.glow, self.rect.y - self.glow))
        
        pygame.draw.rect(surface, UI_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.current_color, self.rect, 3, border_radius=8)
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
        
        # Base stats based on character type
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
        
    def move(self, dx, dy):
        # Move to grid position
        new_x = self.x + dx * GRID_SIZE
        new_y = self.y + dy * GRID_SIZE
        
        # Boundary checking
        if 0 <= new_x < SCREEN_WIDTH:
            self.x = new_x
        if 0 <= new_y < SCREEN_HEIGHT:
            self.y = new_y
            
    def draw(self, surface):
        pygame.draw.rect(surface, PLAYER_COLOR, (self.x, self.y, PLAYER_SIZE, PLAYER_SIZE))
        
        # Draw character type icon
        if self.type == "Warrior":
            pygame.draw.polygon(surface, (200, 200, 220), 
                               [(self.x + 25, self.y + 10), 
                                (self.x + 15, self.y + 30),
                                (self.x + 35, self.y + 30)])
        elif self.type == "Mage":
            pygame.draw.circle(surface, (240, 240, 100), (self.x + 25, self.y + 20), 8)
        else:  # Rogue
            pygame.draw.rect(surface, (180, 80, 100), (self.x + 15, self.y + 15, 20, 20))
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense // 3)
        self.health -= actual_damage
        return actual_damage
    
    def gain_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_level:
            self.level_up()
            
    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_level
        self.exp_to_level = int(self.exp_to_level * 1.5)
        
        # Improve stats
        self.max_health += 20
        self.max_mana += 15
        self.strength += 3
        self.defense += 2
        self.speed += 1
        
        # Restore health and mana
        self.health = self.max_health
        self.mana = self.max_mana
        
    def draw_stats(self, surface, x, y):
        # Health bar
        pygame.draw.rect(surface, (20, 20, 30), (x, y, 200, 25), border_radius=3)
        health_width = 196 * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (x + 2, y + 2, health_width, 21), border_radius=3)
        health_text = font_small.render(f"HP: {self.health}/{self.max_health}", True, TEXT_COLOR)
        surface.blit(health_text, (x + 205, y + 4))
        
        # Mana bar
        pygame.draw.rect(surface, (20, 20, 30), (x, y + 30, 200, 20), border_radius=3)
        mana_width = 196 * (self.mana / self.max_mana)
        pygame.draw.rect(surface, MANA_COLOR, (x + 2, y + 32, mana_width, 16), border_radius=3)
        mana_text = font_small.render(f"MP: {self.mana}/{self.max_mana}", True, TEXT_COLOR)
        surface.blit(mana_text, (x + 205, y + 32))
        
        # Exp bar
        pygame.draw.rect(surface, (20, 20, 30), (x, y + 55, 200, 15), border_radius=3)
        exp_width = 196 * (self.exp / self.exp_to_level)
        pygame.draw.rect(surface, EXP_COLOR, (x + 2, y + 57, exp_width, 11), border_radius=3)
        exp_text = font_small.render(f"Level: {self.level}  Exp: {self.exp}/{self.exp_to_level}", True, TEXT_COLOR)
        surface.blit(exp_text, (x, y + 75))
        
        # Stats
        stats_text = font_small.render(f"Str: {self.strength}  Def: {self.defense}  Spd: {self.speed}", True, TEXT_COLOR)
        surface.blit(stats_text, (x, y + 100))

class Enemy:
    def __init__(self, player_level):
        self.size = ENEMY_SIZE
        self.x = random.randint(0, GRID_WIDTH-1) * GRID_SIZE
        self.y = random.randint(0, GRID_HEIGHT-1) * GRID_SIZE
        
        # Scale enemy stats based on player level
        self.health = random.randint(20, 30) + player_level * 5
        self.max_health = self.health
        self.strength = random.randint(5, 10) + player_level * 2
        self.speed = random.randint(3, 6) + player_level // 2
        self.color = ENEMY_COLOR
        self.movement_cooldown = 0
        self.movement_delay = 60  # Move every 1 second at 60 FPS
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))
        
        # Health bar
        bar_width = 40
        pygame.draw.rect(surface, (20, 20, 30), (self.x - 5, self.y - 15, bar_width, 8), border_radius=2)
        health_width = (bar_width - 2) * (self.health / self.max_health)
        pygame.draw.rect(surface, HEALTH_COLOR, (self.x - 4, self.y - 14, health_width, 6), border_radius=2)
        
    def update(self, player_x, player_y):
        # Move randomly with a cooldown
        self.movement_cooldown -= 1
        if self.movement_cooldown <= 0:
            self.movement_cooldown = self.movement_delay
            
            # Move in a random direction (or stay still)
            dx, dy = random.choice([(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)])
            new_x = self.x + dx * GRID_SIZE
            new_y = self.y + dy * GRID_SIZE
            
            # Boundary checking
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
        
    def draw(self, surface):
        # Pulsing effect
        pulse_size = self.size//2 + math.sin(self.pulse) * 3
        pygame.draw.circle(surface, self.color, (self.x + self.size//2, self.y + self.size//2), pulse_size)
        
        # Draw icon
        if self.type == "health":
            pygame.draw.rect(surface, (255, 255, 255), (self.x + 10, self.y + 8, 10, 14), border_radius=2)
        else:
            pygame.draw.polygon(surface, (255, 255, 255), 
                              [(self.x + 15, self.y + 8),
                               (self.x + 8, self.y + 22),
                               (self.x + 22, self.y + 22)])
        self.pulse += 0.1

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
        # Body
        pygame.draw.ellipse(surface, DRAGON_COLOR, (self.x, self.y + 30, 180, 70))  # Larger dragon
        
        # Head
        pygame.draw.circle(surface, DRAGON_COLOR, (self.x + 180, self.y + 50), 35)
        
        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (self.x + 195, self.y + 45), 10)
        pygame.draw.circle(surface, (0, 0, 0), (self.x + 195, self.y + 45), 5)
        
        # Wings - animate flapping
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
        
        # Tail
        pygame.draw.polygon(surface, DRAGON_COLOR, [
            (self.x, self.y + 50),
            (self.x - 50, self.y + 20),
            (self.x - 50, self.y + 80)
        ])
        
        # Fire breath - FIXED: expands as it moves away
        if self.fire_active:
            for i in range(15):  # More fire particles
                # Start small and get bigger as it moves away
                fire_size = 5 + i * 1.5
                alpha = max(0, 200 - i * 10)  # Fade out with distance
                fire_color = (255, 215, 0, alpha)  # Gold color with transparency
                
                fire_surf = pygame.Surface((fire_size*2, fire_size*2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, fire_color, (fire_size, fire_size), fire_size)
                surface.blit(
                    fire_surf, 
                    (
                        self.x + 180 + 35 + i*15 + self.fire_frame*2, 
                        self.y + 40
                    )
                )
        
        # Update animation
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
        self.state = "player_turn"  # player_turn, enemy_turn, battle_end
        self.battle_log = ["Battle started!", "It's your turn!"]
        # Adjust button positions
        self.buttons = [
            Button(50, 450, 180, 50, "ATTACK"),   # Lowered Y position
            Button(250, 450, 180, 50, "MAGIC"),   # Lowered Y position
            Button(450, 450, 180, 50, "ITEM"),    # Lowered Y position
            Button(650, 450, 180, 50, "RUN")      # Lowered Y position
        ]
        self.selected_option = 0
        self.battle_ended = False
        self.result = None  # "win" or "lose"
        self.transition_alpha = 0
        self.transition_state = "in"  # "in", "out", "none"
        self.transition_speed = 8
        self.show_summary = False  # Show summary after battle
        self.damage_effect_timer = 0
        self.damage_target = None  # "player" or "enemy"
        self.damage_amount = 0
        self.action_cooldown = 0  # Cooldown after actions
        self.action_delay = 30  # Frames to wait after an action
        
    def start_transition(self):
        self.transition_state = "in"
        self.transition_alpha = 0
        
    def draw(self, surface):
        # Draw battle background
        surface.fill((20, 10, 40))
        
        # --- Cool Player Battle Avatar ---
        player_x, player_y = 200, 300
        shield_surf = pygame.Surface((PLAYER_SIZE+24, PLAYER_SIZE+24), pygame.SRCALPHA)
        pygame.draw.ellipse(shield_surf, (0, 255, 255, 80), (0, 0, PLAYER_SIZE+24, PLAYER_SIZE+24))
        surface.blit(shield_surf, (player_x-12, player_y-12))
        pygame.draw.ellipse(surface, (0, 200, 255), (player_x-8, player_y+8, 32, 40))
        pygame.draw.ellipse(surface, (0, 255, 255), (player_x-8, player_y+8, 32, 40), 3)
        pygame.draw.rect(surface, (220, 220, 220), (player_x+35, player_y+10, 8, 38))
        pygame.draw.rect(surface, (255, 215, 0), (player_x+33, player_y+40, 12, 8))
        sword_surf = pygame.Surface((24, 48), pygame.SRCALPHA)
        pygame.draw.ellipse(sword_surf, (255, 255, 255, 60), (0, 0, 24, 48))
        surface.blit(sword_surf, (player_x+28, player_y+2))
        pygame.draw.rect(surface, PLAYER_COLOR, (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
        pygame.draw.ellipse(surface, (180, 180, 180), (player_x+8, player_y-10, 34, 24))
        pygame.draw.rect(surface, (0, 255, 255), (player_x+18, player_y-2, 14, 8))
        pygame.draw.circle(surface, (0, 0, 0), (player_x+24, player_y+6), 3)
        pygame.draw.circle(surface, (0, 0, 0), (player_x+32, player_y+6), 3)
        
        # --- Cool Enemy Battle Avatars ---
        enemy_x, enemy_y = 700, 200
        # Draw enemy based on strength
        if self.enemy.strength > 15:
            # Fiery Demon
            aura_surf = pygame.Surface((ENEMY_SIZE+40, ENEMY_SIZE+40), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (255, 69, 0, 90), (0, 0, ENEMY_SIZE+40, ENEMY_SIZE+40))
            surface.blit(aura_surf, (enemy_x-20, enemy_y-20))
            pygame.draw.ellipse(surface, (180, 0, 0), (enemy_x, enemy_y, ENEMY_SIZE+20, ENEMY_SIZE))
            pygame.draw.circle(surface, (255, 255, 0), (enemy_x+ENEMY_SIZE//2+10, enemy_y+18), 7)
            pygame.draw.circle(surface, (255, 255, 0), (enemy_x+ENEMY_SIZE//2+30, enemy_y+18), 7)
            pygame.draw.circle(surface, (0, 0, 0), (enemy_x+ENEMY_SIZE//2+10, enemy_y+18), 3)
            pygame.draw.circle(surface, (0, 0, 0), (enemy_x+ENEMY_SIZE//2+30, enemy_y+18), 3)
            pygame.draw.polygon(surface, (255, 215, 0), [(enemy_x+15, enemy_y+5), (enemy_x+5, enemy_y-20), (enemy_x+25, enemy_y+5)])
            pygame.draw.polygon(surface, (255, 215, 0), [(enemy_x+ENEMY_SIZE+5, enemy_y+5), (enemy_x+ENEMY_SIZE+15, enemy_y-20), (enemy_x+ENEMY_SIZE-15, enemy_y+5)])
            pygame.draw.arc(surface, (255, 255, 255), (enemy_x+25, enemy_y+35, 30, 15), math.pi, 2*math.pi, 3)
        else:
            # Shadow Beast
            aura_surf = pygame.Surface((ENEMY_SIZE+30, ENEMY_SIZE+30), pygame.SRCALPHA)
            pygame.draw.ellipse(aura_surf, (0, 0, 0, 100), (0, 0, ENEMY_SIZE+30, ENEMY_SIZE+30))
            surface.blit(aura_surf, (enemy_x-15, enemy_y-15))
            pygame.draw.ellipse(surface, (50, 50, 80), (enemy_x, enemy_y, ENEMY_SIZE+10, ENEMY_SIZE+10))
            pygame.draw.circle(surface, (0, 255, 255), (enemy_x+ENEMY_SIZE//2+5, enemy_y+20), 6)
            pygame.draw.circle(surface, (0, 255, 255), (enemy_x+ENEMY_SIZE//2+25, enemy_y+20), 6)
            pygame.draw.circle(surface, (0, 0, 0), (enemy_x+ENEMY_SIZE//2+5, enemy_y+20), 2)
            pygame.draw.circle(surface, (0, 0, 0), (enemy_x+ENEMY_SIZE//2+25, enemy_y+20), 2)
            pygame.draw.line(surface, (0, 255, 255), (enemy_x+10, enemy_y+ENEMY_SIZE+5), (enemy_x+5, enemy_y+ENEMY_SIZE+20), 4)
            pygame.draw.line(surface, (0, 255, 255), (enemy_x+ENEMY_SIZE+10, enemy_y+ENEMY_SIZE+5), (enemy_x+ENEMY_SIZE+15, enemy_y+ENEMY_SIZE+20), 4)
            pygame.draw.arc(surface, (255, 0, 0), (enemy_x+20, enemy_y+35, 30, 15), math.pi, 2*math.pi, 2)
        
        # Draw health bars
        player_health_width = 150 * (self.player.health / max(1, self.player.max_health))
        enemy_health_width = 150 * (self.enemy.health / max(1, self.enemy.max_health))
        
        # Player health
        pygame.draw.rect(surface, (30, 30, 50), (180, 360, 160, 20))
        pygame.draw.rect(surface, HEALTH_COLOR, (182, 362, player_health_width, 16))
        
        # Enemy health
        pygame.draw.rect(surface, (30, 30, 50), (680, 260, 160, 20))
        pygame.draw.rect(surface, HEALTH_COLOR, (682, 262, enemy_health_width, 16))
        
        # Center health text in health bars
        player_text = font_small.render(f"{self.player.health}/{self.player.max_health}", True, TEXT_COLOR)
        text_rect = player_text.get_rect(center=(180 + 80, 360 + 10))
        surface.blit(player_text, text_rect)
        
        enemy_text = font_small.render(f"{self.enemy.health}/{self.enemy.max_health}", True, TEXT_COLOR)
        text_rect = enemy_text.get_rect(center=(680 + 80, 260 + 10))
        surface.blit(enemy_text, text_rect)
        
        # Draw battle log at the top
        pygame.draw.rect(surface, UI_BG, (100, 50, 800, 100), border_radius=8)
        pygame.draw.rect(surface, UI_BORDER, (100, 50, 800, 100), 3, border_radius=8)
        for i, log in enumerate(self.battle_log[-3:]):
            log_text = font_small.render(log, True, TEXT_COLOR)
            surface.blit(log_text, (120, 70 + i * 30))
        
        # Draw buttons with state awareness
        for i, button in enumerate(self.buttons):
            if self.state == "player_turn" and i == self.selected_option:
                button.color = (255, 215, 0)  # Highlight selected
            elif self.state != "player_turn":
                button.color = (100, 100, 100)  # Grey out when not player's turn
            else:
                button.color = UI_BORDER
            button.draw(surface)
        
        # Draw damage effect
        if self.damage_effect_timer > 0:
            effect_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            if self.damage_target == "player":
                pygame.draw.rect(effect_surf, (255, 0, 0, 100), (player_x, player_y, PLAYER_SIZE, PLAYER_SIZE))
            elif self.damage_target == "enemy":
                pygame.draw.rect(effect_surf, (255, 0, 0, 100), (enemy_x, enemy_y, ENEMY_SIZE, ENEMY_SIZE))
            
            damage_text = font_medium.render(f"-{self.damage_amount}", True, (255, 50, 50))
            if self.damage_target == "player":
                surface.blit(damage_text, (player_x + 20, player_y - 30))
            elif self.damage_target == "enemy":
                surface.blit(damage_text, (enemy_x + 20, enemy_y - 30))
                
            surface.blit(effect_surf, (0, 0))
            self.damage_effect_timer -= 1
        
        # Draw transition overlay if active
        if self.transition_state != "none":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            surface.blit(overlay, (0, 0))
            
        # Show summary after battle
        if self.battle_ended and self.show_summary:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))
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
                surface.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 250 + i*60))

    def update(self):
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
                
        # Action cooldown
        if self.action_cooldown > 0:
            self.action_cooldown -= 1
            return False
        
        # Check battle end conditions
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
        
        # Handle enemy turn
        if self.state == "enemy_turn" and not self.battle_ended:
            # Enemy attacks
            damage = max(1, self.enemy.strength - self.player.defense // 3)
            self.player.health -= damage
            self.add_log(f"Enemy attacks for {damage} damage!")
            self.damage_target = "player"
            self.damage_amount = damage
            self.damage_effect_timer = 20
            self.state = "player_turn"
            self.add_log("It's your turn!")
            self.action_cooldown = self.action_delay  # Add cooldown after enemy action
        
        return False
    
    def add_log(self, message):
        self.battle_log.append(message)
    
    def handle_input(self, event):
        if self.battle_ended and self.show_summary:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.show_summary = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.show_summary = False
        elif self.state == "player_turn" and not self.battle_ended and self.action_cooldown == 0:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.selected_option = (self.selected_option + 1) % 4
                elif event.key == pygame.K_LEFT:
                    self.selected_option = (self.selected_option - 1) % 4
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 2) % 4
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 2) % 4
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.handle_action()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.buttons):
                    if button.rect.collidepoint(mouse_pos):
                        self.selected_option = i
                        self.handle_action()
    
    def handle_action(self):
        if self.state != "player_turn" or self.battle_ended or self.action_cooldown > 0:
            return
            
        if self.selected_option == 0:  # Attack
            damage = self.player.strength
            self.enemy.health -= damage
            self.add_log(f"You attack for {damage} damage!")
            self.damage_target = "enemy"
            self.damage_amount = damage
            self.damage_effect_timer = 20
            self.state = "enemy_turn"
            self.add_log("Enemy's turn!")
            self.action_cooldown = self.action_delay  # Add cooldown after player action
        elif self.selected_option == 1:  # Magic
            if self.player.mana >= 20:
                damage = self.player.strength * 2
                self.enemy.health -= damage
                self.player.mana -= 20
                self.add_log(f"You cast a fireball for {damage} damage!")
                self.damage_target = "enemy"
                self.damage_amount = damage
                self.damage_effect_timer = 20
                self.state = "enemy_turn"
                self.add_log("Enemy's turn!")
                self.action_cooldown = self.action_delay
            else:
                self.add_log("Not enough mana!")
        elif self.selected_option == 2:  # Item
            heal_amount = 30
            self.player.health = min(self.player.max_health, self.player.health + heal_amount)
            self.add_log(f"You used a health potion! Restored {heal_amount} HP.")
            self.state = "enemy_turn"
            self.add_log("Enemy's turn!")
            self.action_cooldown = self.action_delay
        elif self.selected_option == 3:  # Run
            if random.random() < 0.7:  # 70% chance to escape
                self.add_log("You successfully escaped!")
                self.battle_ended = True
                self.result = "escape"
                self.show_summary = True
            else:
                self.add_log("Escape failed!")
                self.state = "enemy_turn"
                self.add_log("Enemy's turn!")
                self.action_cooldown = self.action_delay

class Game:
    def __init__(self):
        self.state = "start_menu"  # start_menu, character_select, overworld, battle, game_over
        self.player = None
        self.enemies = []
        self.items = []
        self.score = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.item_timer = 0
        self.starfield = []
        self.dragon = Dragon(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 120)  # Adjusted position
        self.fire_timer = 0
        self.battle_screen = None
        self.transition_alpha = 0
        self.transition_state = "none"  # "in", "out", "none"
        self.transition_speed = 10
        self.player_moved = False  # Track if player has moved this turn
        self.movement_cooldown = 0  # Cooldown between moves
        self.movement_delay = 10  # Frames to wait before next move
        
        # Initialize starfield
        for _ in range(150):  # More stars for larger screen
            self.starfield.append([
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.random() * 2 + 0.5  # Star speed
            ])
        
        # Add flying dragons to the background
        self.flying_dragons = []
        for _ in range(5):  # Create 5 flying dragons
            self.flying_dragons.append({
                'x': random.randint(-200, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(2, 5),
                'flap': random.random() * 2 * math.pi
            })
        
        # UI Elements - adjusted positions for larger screen
        self.start_button = Button(SCREEN_WIDTH//2 - 120, 500, 240, 60, "START QUEST", UI_BORDER)
        self.quit_button = Button(SCREEN_WIDTH//2 - 120, 580, 240, 60, "QUIT", UI_BORDER)
        self.back_button = Button(20, 20, 100, 40, "BACK")
        
        # Character buttons with more spacing
        self.warrior_button = Button(SCREEN_WIDTH//2 - 300, 300, 200, 150, "WARRIOR", (0, 255, 0))
        self.mage_button = Button(SCREEN_WIDTH//2 - 50, 300, 200, 150, "MAGE", (0, 200, 255))
        self.rogue_button = Button(SCREEN_WIDTH//2 + 200, 300, 200, 150, "ROGUE", (255, 100, 0))
        
    def spawn_enemy(self):
        if len(self.enemies) < 5:  # Fewer enemies for turn-based game
            self.enemies.append(Enemy(self.player.level))
    
    def spawn_item(self):
        if len(self.items) < 3:  # Fewer items for turn-based game
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
            # Update dragon animation
            self.dragon.update()
            self.fire_timer += 1
            if self.fire_timer > 120:  # Breathe fire every 2 seconds
                self.dragon.breathe_fire()
                self.fire_timer = 0
                
        elif self.state == "overworld" and self.player:
            # Update timers
            self.game_time += 1
            self.spawn_timer += 1
            self.item_timer += 1
            self.movement_cooldown = max(0, self.movement_cooldown - 1)  # Decrement movement timer
            
            # Spawn enemies and items periodically
            if self.spawn_timer >= 300:  # 5 seconds at 60 FPS
                self.spawn_enemy()
                self.spawn_timer = 0
                
            if self.item_timer >= 600:  # 10 seconds
                self.spawn_item()
                self.item_timer = 0
                
            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.player.x, self.player.y)
                
            # Check collision with enemies
            for enemy in self.enemies[:]:
                player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                enemy_rect = pygame.Rect(enemy.x, enemy.y, ENEMY_SIZE, ENEMY_SIZE)
                
                if player_rect.colliderect(enemy_rect):
                    self.battle_screen = BattleScreen(self.player, enemy)
                    self.battle_screen.start_transition()
                    self.state = "battle"
                    self.enemies.remove(enemy)
                    self.player_moved = False  # Reset movement flag
                    break
                    
            # Check item collection
            for item in self.items[:]:
                item_rect = pygame.Rect(item.x, item.y, ITEM_SIZE, ITEM_SIZE)
                player_rect = pygame.Rect(self.player.x, self.player.y, PLAYER_SIZE, PLAYER_SIZE)
                
                if player_rect.colliderect(item_rect):
                    if item.type == "health":
                        self.player.health = min(self.player.max_health, self.player.health + 30)
                    else:
                        self.player.mana = min(self.player.max_mana, self.player.mana + 40)
                    self.player.items_collected += 1
                    self.items.remove(item)
    
    def draw(self, screen):
        screen.fill(BACKGROUND)
        
        # Draw starfield background
        for x, y, speed in self.starfield:
            alpha = min(255, int(speed * 100))
            pygame.draw.circle(screen, (200, 200, 255, alpha), (int(x), int(y)), 1)
        
        # Draw flying dragons in background
        for dragon in self.flying_dragons:
            # Simple dragon silhouette made of lines
            wing_offset = math.sin(dragon['flap']) * dragon['size']
            color = (200, 200, 255, min(255, int(dragon['size'] * 40)))
            
            # Body
            pygame.draw.line(
                screen, color,
                (dragon['x'], dragon['y']),
                (dragon['x'] + 5 * dragon['size'], dragon['y']),
                max(1, dragon['size'] // 2)
            )
            
            # Wings
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
            
            # Head
            pygame.draw.line(
                screen, color,
                (dragon['x'] + 5 * dragon['size'], dragon['y']),
                (dragon['x'] + 7 * dragon['size'], dragon['y'] - dragon['size']),
                max(1, dragon['size'] // 2)
            )
            
            # Tail
            pygame.draw.line(
                screen, color,
                (dragon['x'], dragon['y']),
                (dragon['x'] - 2 * dragon['size'], dragon['y'] + dragon['size']),
                max(1, dragon['size'] // 2)
            )
        
        if self.state == "start_menu":
            # Reset button text if needed
            if self.start_button.text != "START QUEST":
                self.start_button.text = "START QUEST"
                self.start_button.text_surf = font_medium.render(self.start_button.text, True, TEXT_COLOR)
                self.start_button.text_rect = self.start_button.text_surf.get_rect(center=self.start_button.rect.center)
            
            # Draw dragon's lair title
            title = font_large.render("DRAGON'S LAIR", True, (255, 50, 50))
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 80))
            
            subtitle = font_medium.render("A RETRO RPG ADVENTURE", True, TEXT_COLOR)
            screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 140))
            
            # Draw dragon - centered with more space
            self.dragon.draw(screen)
            
            # Draw buttons - moved down
            self.start_button.draw(screen)
            self.quit_button.draw(screen)
            
            # Draw instructions with smaller font and more spacing
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
                text = font_tiny.render(line, True, TEXT_COLOR)  # Smaller font
                screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 350 + i*25))  # More vertical spacing
            
        elif self.state == "character_select":
            # Draw character selection screen
            title = font_large.render("CHOOSE YOUR HERO", True, TEXT_COLOR)
            screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))
            
            # Draw character descriptions with more spacing
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
            
            # Adjusted positions for better spacing
            y_pos = 480  # Lower position
            for line in warrior_desc:
                text = font_tiny.render(line, True, (0, 255, 0))  # Smaller font
                screen.blit(text, (SCREEN_WIDTH//2 - 300, y_pos))
                y_pos += 25  # Increased spacing
            
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
                
            # Draw gameplay elements
            for item in self.items:
                item.draw(screen)
                
            for enemy in self.enemies:
                enemy.draw(screen)
            
            self.player.draw(screen)
            
            # Draw UI
            pygame.draw.rect(screen, UI_BG, (10, 10, 250, 130), border_radius=8)
            pygame.draw.rect(screen, UI_BORDER, (10, 10, 250, 130), 3, border_radius=8)
            
            self.player.draw_stats(screen, 20, 20)
            
            score_text = font_medium.render(f"SCORE: {self.score}", True, TEXT_COLOR)
            screen.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 20, 20))
            
            time_text = font_small.render(f"TIME: {self.game_time//FPS}s", True, TEXT_COLOR)
            screen.blit(time_text, (SCREEN_WIDTH - time_text.get_width() - 20, 60))
            
            kills_text = font_small.render(f"KILLS: {self.player.kills}", True, TEXT_COLOR)
            screen.blit(kills_text, (SCREEN_WIDTH - kills_text.get_width() - 20, 90))
            
            # Draw controls help
            controls = [
                "CONTROLS:",
                "ARROWS/WASD - MOVE",
                "ENTER - SELECT",
                "ESC - MENU"
            ]
            
            for i, line in enumerate(controls):
                text = font_tiny.render(line, True, (180, 180, 200))  # Smaller font
                screen.blit(text, (20, SCREEN_HEIGHT - 140 + i * 25))  # Adjusted position
            
        elif self.state == "battle" and self.battle_screen:
            self.battle_screen.draw(screen)
            
        elif self.state == "game_over" and self.player:
            # Draw game over screen
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
                
            self.start_button.text = "PLAY AGAIN"
            self.start_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 20, 240, 60)  # Position below stats
            self.start_button.text_surf = font_medium.render(self.start_button.text, True, TEXT_COLOR)
            self.start_button.text_rect = self.start_button.text_surf.get_rect(center=self.start_button.rect.center)
            self.start_button.draw(screen)
            
            self.back_button.rect = pygame.Rect(SCREEN_WIDTH//2 - 120, y_pos + 100, 240, 60)  # Position below play button
            self.back_button.text_surf = font_medium.render(self.back_button.text, True, TEXT_COLOR)
            self.back_button.text_rect = self.back_button.text_surf.get_rect(center=self.back_button.rect.center)
            self.back_button.draw(screen)
            
        # Draw back button where applicable
        if self.state in ["character_select", "game_over"]:
            self.back_button.draw(screen)
            
        # Draw transition overlay if active
        if self.transition_state != "none":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, self.transition_alpha))
            screen.blit(overlay, (0, 0))
            
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
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "overworld":
                            self.state = "game_over"
                        elif self.state == "game_over":
                            self.state = "start_menu"
                    
                    # Handle overworld movement
                    if self.state == "overworld" and self.player and self.movement_cooldown <= 0:
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            self.player.move(0, -1)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            self.player.move(0, 1)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            self.player.move(-1, 0)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            self.player.move(1, 0)
                            self.player_moved = True
                            self.movement_cooldown = self.movement_delay
                    
                    # Handle battle input
                    if self.state == "battle" and self.battle_screen:
                        self.battle_screen.handle_input(event)
            
            # Update UI elements
            if self.state == "start_menu":
                self.start_button.update(mouse_pos)
                self.quit_button.update(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    self.state = "character_select"
                    
                if self.quit_button.is_clicked(mouse_pos, mouse_click):
                    running = False
                    
            elif self.state == "character_select":
                self.warrior_button.update(mouse_pos)
                self.mage_button.update(mouse_pos)
                self.rogue_button.update(mouse_pos)
                self.back_button.update(mouse_pos)
                
                if self.warrior_button.is_clicked(mouse_pos, mouse_click):
                    self.player = Character("Warrior")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.mage_button.is_clicked(mouse_pos, mouse_click):
                    self.player = Character("Mage")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.rogue_button.is_clicked(mouse_pos, mouse_click):
                    self.player = Character("Rogue")
                    self.state = "overworld"
                    self.start_game()
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    self.state = "start_menu"
                    
            elif self.state == "overworld":
                # Movement is now handled in the event loop above
                pass
                    
            elif self.state == "battle":
                # Update battle screen
                battle_ended = self.battle_screen.update()
                
                if battle_ended:
                    if self.battle_screen.result == "win":
                        self.player.kills += 1
                        self.player.gain_exp(25)
                        self.score += 10
                        # Start transition back to overworld
                        self.start_transition()
                        self.state = "overworld"
                        self.battle_screen = None  # Clear battle screen
                    elif self.battle_screen.result == "lose":
                        self.state = "game_over"
                        self.battle_screen = None  # Clear battle screen
                    elif self.battle_screen.result == "escape":
                        # Start transition back to overworld
                        self.start_transition()
                        self.state = "overworld"
                        self.battle_screen = None
            
            elif self.state == "game_over":
                self.start_button.update(mouse_pos)
                self.back_button.update(mouse_pos)
                
                if self.start_button.is_clicked(mouse_pos, mouse_click):
                    self.state = "character_select"
                    
                if self.back_button.is_clicked(mouse_pos, mouse_click):
                    self.state = "start_menu"
            
            # Update game state
            self.update()
            self.draw(screen)
            
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()
    
    def start_game(self):
        # Reset game state
        self.enemies = []
        self.items = []
        self.score = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.item_timer = 0
        self.player_moved = False
        self.movement_cooldown = 0
        
        # Spawn initial enemies and items
        for _ in range(3):  # Fewer initial enemies
            self.spawn_enemy()
        for _ in range(2):  # Fewer initial items
            self.spawn_item()

# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()