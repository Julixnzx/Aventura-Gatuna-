import math
import random
import pygame


# ==============================================================================
# 1. ENEMIGO NUEVO: PEZ VOLADOR (Nivel 5)
# ==============================================================================
class FlyingFishEnemy:

    def __init__(self, x, y, jump_height=400):
        self.x = x
        self.start_y = y
        self.y = y
        self.jump_height = jump_height

        self.vel_y = -random.uniform(9, 12)  # Impulso inicial de salto
        self.gravity = 0.35
        self.anim_timer = 0
        self.direction = 1

    def update(self):
        self.anim_timer += 1
        self.y += self.vel_y
        self.vel_y += self.gravity

        # Si vuelve a caer por debajo de su punto de inicio, recarga el salto
        if self.y > self.start_y:
            self.y = self.start_y
            self.vel_y = -random.uniform(9, 13)

    def draw(self, screen, camera):
        draw_x = self.x - camera.offset.x
        draw_y = self.y - camera.offset.y

        surf = pygame.Surface((40, 32), pygame.SRCALPHA)
        flap = math.sin(self.anim_timer * 0.4) * 4

        # Colores del Pez
        body_dark = (20, 80, 140)
        body_mid = (40, 140, 210)
        belly_light = (180, 230, 255)
        fin_color = (255, 120, 50, 200)

        # 1. Aleta Caudal (Cola)
        pygame.draw.polygon(
            surf, fin_color, [(5, 16), (0, 6 + flap), (0, 26 - flap)]
        )

        # 2. Cuerpo Hidrodinámico
        pygame.draw.ellipse(surf, body_dark, (4, 8, 32, 16))
        pygame.draw.ellipse(surf, body_mid, (6, 9, 28, 13))
        pygame.draw.ellipse(surf, belly_light, (10, 15, 20, 7))  # Panza brillante

        # 3. Grandes Aletas Pectorales "Alas" (Translúcidas)
        pygame.draw.polygon(
            surf,
            fin_color,
            [(18, 12), (6, 2 - flap), (26, 6)],
        )

        # 4. Ojo Expresivo de Pez
        pygame.draw.circle(surf, (255, 255, 255), (30, 13), 4)
        pygame.draw.circle(surf, (10, 10, 30), (31, 13), 2)
        pygame.draw.circle(surf, (255, 255, 255), (30, 12), 1)

        # 5. Escamas (Detalle visual)
        pygame.draw.arc(surf, (255, 255, 255, 120), (14, 11, 6, 8), 0, 3.14, 1)
        pygame.draw.arc(surf, (255, 255, 255, 120), (20, 11, 6, 8), 0, 3.14, 1)

        screen.blit(surf, (draw_x, draw_y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 32, 24)


# ==============================================================================
# 2. PROYECTIL HUESO
# ==============================================================================
class Bone:

    def __init__(self, x, y, target_x):
        self.x = x
        self.y = y
        self.speed_y = -7
        self.speed_x = -4 if target_x < x else 4
        self.gravity = 0.3
        self.rotation = 0
        self.active = True

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.rotation += 12

        if self.y > 800:
            self.active = False

    def draw(self, screen, camera):
        draw_x = self.x - camera.offset.x
        draw_y = self.y - camera.offset.y

        surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Esferas de los extremos
        pygame.draw.circle(surf, (240, 240, 220), (5, 5), 4)
        pygame.draw.circle(surf, (240, 240, 220), (5, 19), 4)
        pygame.draw.circle(surf, (240, 240, 220), (19, 5), 4)
        pygame.draw.circle(surf, (240, 240, 220), (19, 19), 4)
        pygame.draw.line(surf, (240, 240, 220), (5, 12), (19, 12), 6)

        rotated_surf = pygame.transform.rotate(surf, self.rotation)
        new_rect = rotated_surf.get_rect(center=(draw_x, draw_y))
        screen.blit(rotated_surf, new_rect.topleft)

    def get_rect(self):
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)


# ==============================================================================
# 3. JEFE FINAL (CON FASE DE FURIA)
# ==============================================================================
class BossEnemy:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 10
        self.max_hp = 10
        self.base_speed = 2.0
        self.speed = self.base_speed
        self.direction = -1

        self.vel_y = 0
        self.is_jumping = False
        self.jump_timer = 0
        self.shoot_timer = 0
        self.bones = []
        self.hurt_timer = 0
        self.tail_angle = 0
        self.is_enraged = False

    def update(self, player_pos, platforms):
        # Transición a Fase Final (Furia)
        if self.hp <= 3 and not self.is_enraged:
            self.is_enraged = True

        if self.is_enraged:
            self.speed = 3.6
            shoot_cooldown = 45
            jump_cooldown = 60
            tail_speed = 0.45
        else:
            self.speed = self.base_speed
            shoot_cooldown = 90
            jump_cooldown = 120
            tail_speed = 0.2

        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        self.direction = -1 if player_pos.x < self.x else 1
        self.x += self.speed * self.direction

        # Lógica de Salto / Pisotón
        self.jump_timer += 1
        if self.jump_timer > jump_cooldown and not self.is_jumping:
            self.is_jumping = True
            self.vel_y = -13
            self.jump_timer = 0

        if self.is_jumping:
            if abs(self.x - player_pos.x) < 40 and self.vel_y < 0:
                self.vel_y = 3
            self.vel_y += 0.5
            self.y += self.vel_y

            boss_rect = self.get_rect()
            for plat in platforms:
                if boss_rect.colliderect(plat) and self.vel_y > 0:
                    self.y = plat.top - 65
                    self.is_jumping = False
                    self.vel_y = 0

        # Lógica de proyectiles
        self.shoot_timer += 1
        if self.shoot_timer > shoot_cooldown:
            self.bones.append(Bone(self.x + 40, self.y + 20, player_pos.x))
            self.shoot_timer = 0

        for bone in self.bones[:]:
            bone.update()
            if not bone.active:
                self.bones.remove(bone)

        self.tail_angle += tail_speed

    def take_damage(self):
        if self.hurt_timer == 0:
            self.hp -= 1
            self.hurt_timer = 30

    def draw(self, screen, camera):
        draw_x = self.x - camera.offset.x
        draw_y = self.y - camera.offset.y

        for bone in self.bones:
            bone.draw(screen, camera)

        surf = pygame.Surface((120, 90), pygame.SRCALPHA)

        # Paletas de color por estado
        if self.is_enraged:
            fur_base = (70, 35, 25)
            belly_base = (130, 80, 60)
            ear_color = (40, 20, 15)
            eye_color = (255, 30, 30)
        else:
            fur_base = (140, 85, 45)
            belly_base = (210, 160, 110)
            ear_color = (90, 50, 25)
            eye_color = (255, 255, 255)

        fur_color = (
            (240, 50, 50) if self.hurt_timer % 6 > 3 else fur_base
        )
        belly_color = (
            (250, 120, 120) if self.hurt_timer % 6 > 3 else belly_base
        )
        collar_color = (220, 40, 40) if not self.is_enraged else (180, 0, 220)

        # Partículas de Aura en la Fase Final
        if self.is_enraged:
            for _ in range(3):
                px = random.randint(15, 95)
                py = random.randint(20, 70)
                pradius = random.randint(3, 7)
                pygame.draw.circle(
                    surf, (255, 50, 0, 120), (px, py), pradius
                )

        # Sombra
        pygame.draw.ellipse(surf, (0, 0, 0, 70), (15, 78, 80, 10))

        # Cola animada
        tail_swing = math.sin(self.tail_angle) * 10
        tail_start = (85, 45) if self.direction < 0 else (25, 45)
        tail_end = (
            (105 + tail_swing, 28)
            if self.direction < 0
            else (5 - tail_swing, 28)
        )
        pygame.draw.line(surf, fur_color, tail_start, tail_end, 8)

        # Cuerpo y Panza
        pygame.draw.ellipse(surf, fur_color, (20, 30, 70, 45))
        pygame.draw.ellipse(surf, belly_color, (30, 42, 50, 28))

        # Patas
        for px in (25, 42, 58, 75):
            pygame.draw.rect(surf, fur_color, (px, 60, 12, 20), border_radius=4)

        head_x = 10 if self.direction < 0 else 55

        # Collar con medalla
        pygame.draw.rect(surf, collar_color, (head_x + 8, 38, 26, 6))
        pygame.draw.circle(surf, (255, 215, 0), (head_x + 21, 44), 4)

        # Cabeza y Hocico
        pygame.draw.circle(surf, fur_color, (head_x + 20, 24), 20)
        hocico_x = head_x - 5 if self.direction < 0 else head_x + 23
        pygame.draw.ellipse(surf, belly_color, (hocico_x, 22, 22, 16))

        # Nariz
        nose_x = hocico_x - 2 if self.direction < 0 else hocico_x + 18
        pygame.draw.circle(surf, (20, 20, 20), (nose_x + 3, 26), 4)

        # Oreja caída
        ear_x = head_x + 24 if self.direction < 0 else head_x - 2
        pygame.draw.ellipse(surf, ear_color, (ear_x, 14, 12, 24))

        # Ojo
        eye_x = head_x + (10 if self.direction < 0 else 24)
        pygame.draw.circle(surf, eye_color, (eye_x, 20), 5)
        pupil = (0, 0, 0) if not self.is_enraged else (255, 255, 0)
        pygame.draw.circle(surf, pupil, (eye_x, 20), 2)

        screen.blit(surf, (draw_x - 10, draw_y - 10))

        # Barra de Vida Superior
        bar_w = 300
        bar_x = (800 - bar_w) // 2
        bar_y = 25
        pygame.draw.rect(
            screen, (30, 30, 30), (bar_x - 4, bar_y - 4, bar_w + 8, 20), border_radius=4
        )
        curr_w = max(0, int((self.hp / self.max_hp) * bar_w))
        hp_color = (
            (255, 0, 0) if self.is_enraged else ((240, 180, 40) if self.hp <= 6 else (50, 200, 80))
        )
        pygame.draw.rect(screen, hp_color, (bar_x, bar_y, curr_w, 12), border_radius=3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 80, 65)


# ==============================================================================
# 4. BUG ENEMY REDISEÑADO
# ==============================================================================
class BugEnemy:

    def __init__(self, x, y, walk_dist=120):
        self.x = x
        self.y = y
        self.start_x = x
        self.walk_dist = walk_dist
        self.speed = 1.5
        self.direction = 1
        self.anim_timer = 0

    def update(self):
        self.x += self.speed * self.direction
        if abs(self.x - self.start_x) > self.walk_dist:
            self.direction *= -1
        self.anim_timer += 1

    def draw(self, screen, camera):
        draw_x = self.x - camera.offset.x
        draw_y = self.y - camera.offset.y

        surf = pygame.Surface((36, 32), pygame.SRCALPHA)
        flap = math.sin(self.anim_timer * 0.35) * 3
        leg_phase = (self.anim_timer // 6) % 2
        facing_left = self.direction < 0

        # Sombra
        pygame.draw.ellipse(surf, (0, 0, 0, 70), (8, 25, 20, 5))

        # Alas
        wing_color = (205, 130, 225, 170)
        pygame.draw.ellipse(surf, wing_color, (4, 5 + flap, 14, 9))
        pygame.draw.ellipse(surf, wing_color, (18, 5 - flap, 14, 9))

        # Patas
        leg_color = (25, 15, 30)
        for i, lx in enumerate((12, 18, 24)):
            bend = 3 if (i + leg_phase) % 2 == 0 else -3
            pygame.draw.line(surf, leg_color, (lx, 20), (lx + bend, 27), 2)

        # Caparazón Segmentado
        pygame.draw.ellipse(surf, (95, 20, 120), (7, 12, 22, 14))
        pygame.draw.ellipse(surf, (150, 40, 180), (8, 11, 20, 12))
        pygame.draw.ellipse(surf, (200, 110, 220), (11, 11, 10, 5))

        # Cabeza
        head_x = 5 if facing_left else 29
        pygame.draw.circle(surf, (95, 20, 120), (head_x, 15), 5)
        eye_x = head_x + (1 if facing_left else -1)
        pygame.draw.circle(surf, (255, 60, 60), (eye_x, 14), 2)

        screen.blit(surf, (draw_x, draw_y))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 28, 20)


# ==============================================================================
# 5. GOBLIN ENEMY REDISEÑADO
# ==============================================================================
class GoblinEnemy:

    def __init__(self, x, y, walk_dist=100):
        self.x = x
        self.y = y
        self.start_x = x
        self.walk_dist = walk_dist
        self.speed = 2.0
        self.direction = 1
        self.anim_timer = 0

    def update(self):
        self.x += self.speed * self.direction
        if abs(self.x - self.start_x) > self.walk_dist:
            self.direction *= -1
        self.anim_timer += 1

    def draw(self, screen, camera):
        draw_x = self.x - camera.offset.x
        draw_y = self.y - camera.offset.y

        surf = pygame.Surface((44, 48), pygame.SRCALPHA)
        facing_right = self.direction >= 0
        leg_swing = math.sin(self.anim_timer * 0.25) * 4
        cx = 22

        # Sombra
        pygame.draw.ellipse(surf, (0, 0, 0, 70), (8, 42, 28, 5))

        # Piernas
        pygame.draw.line(surf, (20, 90, 35), (cx - 6, 34), (cx - 6 - leg_swing, 45), 4)
        pygame.draw.line(surf, (20, 90, 35), (cx + 6, 34), (cx + 6 + leg_swing, 45), 4)

        # Orejas
        pygame.draw.polygon(surf, (20, 90, 35), [(cx - 16, 12), (cx - 10, 5), (cx - 8, 16)])
        pygame.draw.polygon(surf, (20, 90, 35), [(cx + 16, 12), (cx + 10, 5), (cx + 8, 16)])

        # Torso y Cinturón
        pygame.draw.rect(surf, (110, 25, 25), (cx - 10, 22, 20, 16), border_radius=3)
        pygame.draw.rect(surf, (150, 40, 40), (cx - 10, 22, 20, 9), border_radius=3)
        pygame.draw.line(surf, (90, 60, 20), (cx - 10, 32), (cx + 10, 32), 2)

        # Cabeza
        pygame.draw.circle(surf, (20, 90, 35), (cx, 14), 11)
        pygame.draw.circle(surf, (35, 130, 55), (cx - 2, 13), 10)

        # Ojos amarillos
        eye_off = 3 if facing_right else -3
        pygame.draw.circle(surf, (255, 230, 0), (cx - 4 + eye_off, 13), 3)
        pygame.draw.circle(surf, (255, 230, 0), (cx + 4 + eye_off, 13), 3)

        # Garrote
        club_base = (cx + 16, 34) if facing_right else (cx - 16, 34)
        club_tip = (cx + 20, 20) if facing_right else (cx - 20, 20)
        pygame.draw.line(surf, (110, 70, 30), club_base, club_tip, 4)

        screen.blit(surf, (draw_x - 6, draw_y - 8))

        def get_rect(self):
            return pygame.Rect(self.x, self.y, 32, 40)