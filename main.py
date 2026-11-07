import math
import os
import random
import pygame
import array
from intro import IntroScene
import settings

# -------------------------------------------------------------
# 1. INICIALIZACIÓN
# -------------------------------------------------------------
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

screen = pygame.display.set_mode(
    (settings.WIDTH, settings.HEIGHT),
    pygame.FULLSCREEN if settings.IS_FULLSCREEN else 0,
)
pygame.display.set_caption(settings.TITLE)
clock = pygame.time.Clock()

font_ui = pygame.font.SysFont("Arial", 20, bold=True)
font_title = pygame.font.SysFont("Georgia", 44, bold=True)
font_dialog = pygame.font.SysFont("Arial", 22)
font_option = pygame.font.SysFont("Arial", 28)

GRAVITY = 0.55
LEVEL_WIDTH = 3200  # Niveles extensos
game_state = "INTRO"
current_level = 1
unlocked_levels = 1
MAX_LEVELS = 5
intro = IntroScene(screen)

menu_selected_index = 0

# -------------------------------------------------------------
# 2. GENERADOR DE MÚSICA RELAJANTE Y AMBIENTAL 8-BIT
# -------------------------------------------------------------
def generate_relaxing_sound(melody, tempo=85):
    """Genera ondas sintéticas suavemente atenuadas para un sonido relajante."""
    sample_rate = 22050
    note_duration = int(sample_rate * (60 / tempo) * 0.35)
    total_samples = note_duration * len(melody)
    buf = array.array('h', [0] * total_samples)

    notes_freq = {
        'C3': 130.81, 'D3': 146.83, 'E3': 164.81, 'G3': 196.00, 'A3': 220.00,
        'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'G4': 392.00, 'A4': 440.00,
        'C5': 523.25, 'D5': 587.33, 'E5': 659.25, '-': 0
    }

    for idx, note in enumerate(melody):
        freq = notes_freq.get(note, 0)
        start = idx * note_duration
        for i in range(note_duration):
            if freq > 0:
                t = float(i) / sample_rate
                # Onda suave con decaimiento de volumen por nota (Efecto Piano/Lute)
                env = max(0.0, 1.0 - (float(i) / note_duration))
                val = math.sin(2 * math.pi * freq * t) * 10000 * env
                buf[start + i] = int(val)
            else:
                buf[start + i] = 0

    return pygame.mixer.Sound(buffer=buf)

# Melodías relajantes y pausadas
RELAXING_MELODIES = {
    1: ["C4", "E4", "G4", "C5", "-", "G4", "E4", "-", "A3", "C4", "E4", "A4", "-", "E4", "C4", "-"],
    2: ["E4", "-", "G4", "-", "B4", "E5", "-", "B4", "D4", "-", "F4", "-", "A4", "D5", "-", "A4"],
    3: ["A3", "C4", "E4", "-", "G3", "B3", "D4", "-", "F3", "A3", "C4", "-", "E3", "G3", "B3", "-"],
    4: ["C4", "D4", "E4", "G4", "A4", "-", "G4", "-", "E4", "D4", "C4", "A3", "C4", "-", "-", "-"],
    5: ["A3", "C4", "E4", "G4", "E4", "C4", "A3", "-", "D4", "F4", "A4", "C5", "A4", "F4", "D4", "-"]
}

current_music_channel = None
def play_level_soundtrack(level):
    global current_music_channel
    if current_music_channel:
        current_music_channel.stop()
    sound = generate_relaxing_sound(RELAXING_MELODIES.get(level, RELAXING_MELODIES[1]))
    current_music_channel = sound.play(loops=-1)

# -------------------------------------------------------------
# 3. CLASE JUGADOR (GATO ANIMADO LINDO + GAME FEEL ENHANCEMENTS)
# -------------------------------------------------------------
class CuteCat(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.rect = pygame.Rect(x, y, 42, 42)
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5.5
        self.jump_power = -12.5
        self.on_ground = False
        self.facing_right = True
        
        self.lives = 5
        self.max_lives = 5
        self.invulnerable_timer = 0
        self.jumps_left = 2
        
        # Game Feel: Coyote Time & Jump Buffer
        self.coyote_timer = 0
        self.jump_buffer = 0

        self.anim_frame = 0
        self.blink_timer = random.randint(100, 200)
        self.is_scratching = False
        self.scratch_timer = 0
        self.scratch_rect = pygame.Rect(0, 0, 0, 0)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                self.jump_buffer = 6  # Registra la intención de saltar por 6 frames

            if event.key in (pygame.K_j, pygame.K_z):
                if not self.is_scratching:
                    self.is_scratching = True
                    self.scratch_timer = 12

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = self.speed
            self.facing_right = True

        if self.vel_x != 0 and self.on_ground:
            self.anim_frame += 0.25
        else:
            self.anim_frame = 0

        self.vel_y += GRAVITY
        if self.vel_y > 14:
            self.vel_y = 14

        # Gestión de Coyote Time
        if self.on_ground:
            self.coyote_timer = 6
            self.jumps_left = 2
        else:
            self.coyote_timer = max(0, self.coyote_timer - 1)

        # Gestión de Jump Buffer
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.coyote_timer > 0:
                self.vel_y = self.jump_power
                self.jumps_left = 1
                self.coyote_timer = 0
                self.jump_buffer = 0
                self.on_ground = False
            elif self.jumps_left > 0:
                self.vel_y = self.jump_power
                self.jumps_left -= 1
                self.jump_buffer = 0
                self.on_ground = False

        # Movimiento Horizontal
        self.rect.x += self.vel_x
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right

        # Movimiento Vertical
        self.rect.y += self.vel_y
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 0

        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        self.blink_timer -= 1
        if self.blink_timer <= 0:
            self.blink_timer = random.randint(120, 240)

        if self.is_scratching:
            self.scratch_timer -= 1
            offset = 42 if self.facing_right else -28
            self.scratch_rect = pygame.Rect(self.rect.x + offset, self.rect.y + 5, 28, 28)
            if self.scratch_timer <= 0:
                self.is_scratching = False

    def take_damage(self):
        if self.invulnerable_timer == 0:
            self.lives -= 1
            self.invulnerable_timer = 60
            self.vel_y = -7

    def draw(self, surface, camera_x):
        if self.invulnerable_timer % 6 in (1, 2, 3):
            return

        rx = self.rect.x - camera_x
        ry = self.rect.y
        surf = pygame.Surface((42, 42), pygame.SRCALPHA)

        cat_orange = (250, 140, 45)
        cat_dark_orange = (210, 100, 20)
        pink = (255, 170, 180)

        tail_wave = math.sin(pygame.time.get_ticks() * 0.01) * 4
        pygame.draw.arc(surf, cat_dark_orange, (2 if self.facing_right else 26, 18 + tail_wave, 14, 20), 0, 3.14, 4)
        pygame.draw.ellipse(surf, cat_orange, (6, 12, 30, 26))

        head_x = 18 if self.facing_right else 4
        pygame.draw.circle(surf, cat_orange, (head_x + 10, 16), 12)

        e1 = [(head_x + 2, 8), (head_x + 6, 0), (head_x + 10, 8)]
        e2 = [(head_x + 10, 8), (head_x + 14, 0), (head_x + 18, 8)]
        pygame.draw.polygon(surf, cat_dark_orange, e1)
        pygame.draw.polygon(surf, cat_dark_orange, e2)
        pygame.draw.polygon(surf, pink, [(e1[0][0]+1, e1[0][1]), (e1[1][0], e1[1][1]+2), (e1[2][0]-1, e1[2][1])])

        eye_x = head_x + (14 if self.facing_right else 6)
        if self.blink_timer < 10:
            pygame.draw.line(surf, (40, 20, 10), (eye_x - 3, 16), (eye_x + 3, 16), 2)
        else:
            pygame.draw.circle(surf, (40, 20, 10), (eye_x, 15), 4)
            pygame.draw.circle(surf, (255, 255, 255), (eye_x - 1, 14), 1.5)

        pygame.draw.circle(surf, pink, (head_x + (17 if self.facing_right else 3), 18), 2)

        leg_offset = math.sin(self.anim_frame) * 5
        pygame.draw.rect(surf, cat_dark_orange, (10 + leg_offset, 34, 6, 8), border_radius=3)
        pygame.draw.rect(surf, cat_dark_orange, (24 - leg_offset, 34, 6, 8), border_radius=3)

        surface.blit(surf, (rx, ry))

        if self.is_scratching:
            sx = self.scratch_rect.x - camera_x
            sy = self.scratch_rect.y
            for i in range(3):
                pygame.draw.arc(surface, (255, 230, 80), (sx, sy + (i*6), 25, 20), 0.2, 1.8, 3)

# -------------------------------------------------------------
# 4. PLATAFORMAS, ENEMIGOS, PROYECTILES Y JEFE CANICHE
# -------------------------------------------------------------
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, plat_type="dirt"):
        super().__init__()
        self.image = pygame.Surface((width, height))
        if plat_type == "dirt":
            self.image.fill((110, 75, 45))
            pygame.draw.rect(self.image, (60, 140, 50), (0, 0, width, 8))
        elif plat_type == "wood":
            self.image.fill((140, 90, 40))
            for i in range(0, width, 25):
                pygame.draw.line(self.image, (90, 50, 20), (i, 0), (i, height), 2)
        elif plat_type == "stone":
            self.image.fill((90, 95, 105))
            pygame.draw.rect(self.image, (60, 65, 75), (0, 0, width, height), 3)
        elif plat_type == "dark_stone":
            self.image.fill((45, 45, 60))
            pygame.draw.rect(self.image, (25, 25, 35), (0, 0, width, height), 3)
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="goblin", platform_width=140):
        super().__init__()
        self.enemy_type = enemy_type
        self.start_x = x
        self.max_x = x + platform_width - 36
        self.speed = 2.0 if enemy_type == "goblin" else 3.0
        self.direction = 1
        self.image = pygame.Surface((36, 36), pygame.SRCALPHA)
        
        if enemy_type == "goblin":
            pygame.draw.ellipse(self.image, (60, 140, 50), (4, 8, 28, 24))
            pygame.draw.circle(self.image, (255, 220, 0), (12, 16), 3)
            pygame.draw.circle(self.image, (255, 220, 0), (24, 16), 3)
        else:
            pygame.draw.ellipse(self.image, (40, 40, 40), (6, 10, 24, 18))
            pygame.draw.ellipse(self.image, (220, 180, 0), (10, 12, 16, 14))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.fly_angle = random.random() * 5

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.enemy_type == "insect":
            self.fly_angle += 0.08
            self.rect.y += math.sin(self.fly_angle) * 1.5

        if self.rect.x <= self.start_x or self.rect.x >= self.max_x:
            self.direction *= -1

class BoneProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (240, 240, 230), (4, 3, 12, 4))
        pygame.draw.circle(self.image, (240, 240, 230), (3, 3), 3)
        pygame.draw.circle(self.image, (240, 240, 230), (3, 7), 3)
        pygame.draw.circle(self.image, (240, 240, 230), (17, 3), 3)
        pygame.draw.circle(self.image, (240, 240, 230), (17, 7), 3)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6 * direction

    def update(self):
        self.rect.x += self.speed
        if self.rect.x < 0 or self.rect.x > LEVEL_WIDTH:
            self.kill()

class PoodleBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((100, 100), pygame.SRCALPHA)
        fur = (245, 240, 235)
        dark_pink = (230, 90, 140)

        pygame.draw.circle(self.image, fur, (50, 60), 32)
        pygame.draw.circle(self.image, fur, (50, 32), 24)
        pygame.draw.circle(self.image, fur, (22, 30), 12)
        pygame.draw.circle(self.image, fur, (78, 30), 12)

        pygame.draw.polygon(self.image, (255, 215, 0), [(38, 12), (44, 2), (50, 10), (56, 2), (62, 12)])

        pygame.draw.circle(self.image, (20, 20, 20), (42, 30), 4)
        pygame.draw.circle(self.image, (20, 20, 20), (58, 30), 4)
        pygame.draw.circle(self.image, dark_pink, (50, 36), 5)

        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 15
        self.max_hp = 15
        self.speed = 3.5
        self.direction = -1
        self.hit_timer = 0
        self.shoot_timer = 0

    def update(self, projectiles):
        self.rect.x += self.speed * self.direction
        if self.rect.left <= 2200 or self.rect.right >= LEVEL_WIDTH - 50:
            self.direction *= -1

        if self.hit_timer > 0:
            self.hit_timer -= 1

        self.shoot_timer += 1
        if self.shoot_timer >= 90:
            self.shoot_timer = 0
            projectiles.add(BoneProjectile(self.rect.centerx, self.rect.centery, self.direction))

    def draw_health(self, surface):
        bar_w = 400
        bar_h = 22
        x = (settings.WIDTH - bar_w) // 2
        y = 50
        fill = int((self.hp / self.max_hp) * bar_w)
        pygame.draw.rect(surface, (60, 10, 10), (x, y, bar_w, bar_h))
        pygame.draw.rect(surface, (230, 50, 80), (x, y, fill, bar_h))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, bar_w, bar_h), 2)
        txt = font_ui.render("REY CANICHE MALVADO (JEFE)", True, (255, 255, 255))
        surface.blit(txt, (x + 70, y - 25))

class LevelGoal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 80), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (180, 180, 180), (5, 0, 6, 80))
        pygame.draw.polygon(self.image, (255, 215, 0), [(11, 5), (38, 20), (11, 35)])
        self.rect = self.image.get_rect(topleft=(x, y))

# -------------------------------------------------------------
# 5. CARGADOR DE NIVELES
# -------------------------------------------------------------
def load_level_data(level_num):
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    boss = None
    goal = LevelGoal(LEVEL_WIDTH - 120, settings.HEIGHT - 120)

    h = settings.HEIGHT
    p_type = ["dirt", "wood", "stone", "dark_stone", "dark_stone"][level_num - 1]

    for x in range(0, LEVEL_WIDTH, 450):
        if x not in (900, 1800, 2400):
            platforms.add(Platform(x, h - 40, 360, 40, p_type))

    # Control de alturas para garantizar que los saltos sean alcanzables
    for x in range(200, LEVEL_WIDTH - 500, 220):
        py = h - random.choice([120, 180, 240])
        plat_w = 140
        plat = Platform(x, py, plat_w, 20, p_type)
        platforms.add(plat)

        if random.random() > 0.35:
            e_type = "goblin" if level_num in (1, 3, 4) else "insect"
            enemies.add(Enemy(x + 10, py - 36, e_type, platform_width=plat_w))

    if level_num == 5:
        boss = PoodleBoss(2500, h - 140)

    return platforms, enemies, projectiles, boss, goal

# -------------------------------------------------------------
# 6. BUCLE PRINCIPAL
# -------------------------------------------------------------
player = CuteCat(50, settings.HEIGHT - 100)
platforms, enemies, projectiles, boss, goal = load_level_data(current_level)
camera_x = 0

story_dialogs = [
    "¡El Reino Caniche ha robado la reserva sagrada de pescados!",
    "Como el Gran Gato Naranja, debes atravesar 5 reinos peligrosos.",
    "Derrota a duendes e insectos para enfrentarte al Rey Caniche."
]
story_index = 0

play_level_soundtrack(1)  # Iniciar música relajante desde el principio

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                settings.IS_FULLSCREEN = not settings.IS_FULLSCREEN
                screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), pygame.FULLSCREEN if settings.IS_FULLSCREEN else 0)

            # --- NAVEGACIÓN ENTRE ESTADOS ---
            elif game_state == "INTRO":
                intro.handle_event(event)
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state = "STORY"
                    story_index = 0

            elif game_state == "STORY":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    story_index += 1
                    if story_index >= len(story_dialogs):
                        game_state = "MAIN_MENU"

            elif game_state == "MAIN_MENU":
                if event.key == pygame.K_UP:
                    menu_selected_index = (menu_selected_index - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_selected_index = (menu_selected_index + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if menu_selected_index == 0:
                        current_level = 1
                        player = CuteCat(50, settings.HEIGHT - 100)
                        platforms, enemies, projectiles, boss, goal = load_level_data(current_level)
                        play_level_soundtrack(current_level)
                        game_state = "GAME"
                    elif menu_selected_index == 1:
                        game_state = "STORY"
                        story_index = 0
                    elif menu_selected_index == 2:
                        running = False

            elif game_state == "GAME":
                player.handle_input(event)
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    game_state = "PAUSE"

            elif game_state == "PAUSE":
                if event.key in (pygame.K_p, pygame.K_ESCAPE):
                    game_state = "GAME"
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state = "MAIN_MENU"

            elif game_state == "WIN":
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game_state = "MAIN_MENU"

    # --- LÓGICA DE JUEGO ---
    if game_state == "GAME":
        player.update(platforms)
        enemies.update()
        projectiles.update()
        if boss:
            boss.update(projectiles)

        camera_x = max(0, min(player.rect.x - settings.WIDTH // 3, LEVEL_WIDTH - settings.WIDTH))

        # Ataque del jugador
        if player.is_scratching:
            for enemy in enemies:
                if player.scratch_rect.colliderect(enemy.rect):
                    enemy.kill()
            if boss and player.scratch_rect.colliderect(boss.rect):
                if boss.hit_timer == 0:
                    boss.hp -= 1
                    boss.hit_timer = 20
                    if boss.hp <= 0:
                        boss = None
                        game_state = "WIN"  # Ir a la pantalla de victoria al derrotar al Jefe

        # Colisiones de daño
        for enemy in enemies:
            if player.rect.colliderect(enemy.rect):
                player.take_damage()
        for proj in projectiles:
            if player.rect.colliderect(proj.rect):
                player.take_damage()
                proj.kill()
        if boss and player.rect.colliderect(boss.rect):
            player.take_damage()

        # Reiniciar si cae al vacío o pierde vidas
        if player.rect.y > settings.HEIGHT or player.lives <= 0:
            player = CuteCat(50, settings.HEIGHT - 100)
            platforms, enemies, projectiles, boss, goal = load_level_data(current_level)

        # Meta de nivel
        if player.rect.colliderect(goal.rect) and not boss:
            if current_level < MAX_LEVELS:
                current_level += 1
                player = CuteCat(50, settings.HEIGHT - 100)
                platforms, enemies, projectiles, boss, goal = load_level_data(current_level)
                play_level_soundtrack(current_level)
            else:
                game_state = "WIN"

    # --- DIBUJADO DE PANTALLA ---
    screen.fill((25, 25, 40))

    if game_state == "INTRO":
        intro.update()
        intro.draw()

    elif game_state == "STORY":
        title_s = font_title.render("HISTORIA DE LA AVENTURA", True, (255, 215, 0))
        screen.blit(title_s, title_s.get_rect(center=(settings.WIDTH // 2, 120)))
        
        dialog_box = pygame.Rect(100, settings.HEIGHT // 2 - 40, settings.WIDTH - 200, 120)
        pygame.draw.rect(screen, (10, 10, 20), dialog_box, border_radius=10)
        pygame.draw.rect(screen, (255, 215, 0), dialog_box, width=3, border_radius=10)

        txt_d = font_dialog.render(story_dialogs[story_index], True, (255, 255, 255))
        screen.blit(txt_d, txt_d.get_rect(center=dialog_box.center))
        
        txt_sub = font_ui.render("Presiona [ENTER] para continuar...", True, (180, 180, 180))
        screen.blit(txt_sub, (settings.WIDTH // 2 - 120, settings.HEIGHT - 80))

    elif game_state in ("GAME", "PAUSE"):
        # Renderizado del nivel
        screen.blit(goal.image, (goal.rect.x - camera_x, goal.rect.y))
        
        for plat in platforms:
            screen.blit(plat.image, (plat.rect.x - camera_x, plat.rect.y))
        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y))
        for proj in projectiles:
            screen.blit(proj.image, (proj.rect.x - camera_x, proj.rect.y))

        if boss:
            screen.blit(boss.image, (boss.rect.x - camera_x, boss.rect.y))
            boss.draw_health(screen)

        player.draw(screen, camera_x)

        # UI: Vidas
        for i in range(player.max_lives):
            color = (255, 70, 110) if i < player.lives else (80, 80, 90)
            pygame.draw.circle(screen, color, (30 + (i * 28), 30), 8)

        # UI: Nivel actual
        txt_ui = font_ui.render(f"Nivel {current_level} / {MAX_LEVELS}", True, (255, 255, 255))
        screen.blit(txt_ui, (settings.WIDTH - 140, 20))

        # Overlay del Menú de Pausa
        if game_state == "PAUSE":
            overlay = pygame.Surface((settings.WIDTH, settings.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            txt_pause = font_title.render("JUEGO EN PAUSA", True, (255, 215, 0))
            txt_sub = font_dialog.render("Presiona [P] para continuar o [ENTER] para salir al Menú Principal", True, (255, 255, 255))
            
            screen.blit(txt_pause, txt_pause.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 30)))
            screen.blit(txt_sub, txt_sub.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 30)))

    elif game_state == "WIN":
        title_win = font_title.render("¡VICTORIA REAL!", True, (255, 215, 0))
        sub_win = font_dialog.render("¡Has recuperado la reserva sagrada de pescados!", True, (255, 255, 255))
        prompt_win = font_ui.render("Presiona [ENTER] para volver al menú principal", True, (180, 180, 180))

        screen.blit(title_win, title_win.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 60)))
        screen.blit(sub_win, sub_win.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2)))
        screen.blit(prompt_win, prompt_win.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + 70)))

    elif game_state == "MAIN_MENU":
        title = font_title.render("AVENTURA GATUNA", True, (255, 215, 0))
        screen.blit(title, title.get_rect(center=(settings.WIDTH // 2, 150)))
        for i, option in enumerate(["Jugar", "Historia", "Salir"]):
            col = (255, 215, 0) if i == menu_selected_index else (180, 180, 180)
            txt = font_option.render(f"> {option} <" if i == menu_selected_index else option, True, col)
            screen.blit(txt, txt.get_rect(center=(settings.WIDTH // 2, 300 + i * 50)))

    pygame.display.flip()
    clock.tick(settings.FPS)

pygame.quit()