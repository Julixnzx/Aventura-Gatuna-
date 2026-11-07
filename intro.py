import pygame
import settings


class IntroScene:

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Georgia", 32)
        self.small_font = pygame.font.SysFont("Arial", 20)

        # Cargar historia desde settings de forma segura
        fallback_texts = {
            "es": [
                "Durante siglos, el Reino vivió en paz...",
                "¡Tu viaje comienza ahora!",
            ],
            "en": [
                "For centuries, the Kingdom lived in peace...",
                "Your journey begins now!",
            ],
        }

        intro_dict = getattr(settings, "INTRO_TEXTS", fallback_texts)
        lang = getattr(settings, "CURRENT_LANGUAGE", "es")
        self.lines = intro_dict.get(lang, fallback_texts["es"])

        self.current_line = 0
        self.alpha = 0  # Control de transparencia (Fade-in)
        self.fade_speed = 3
        self.timer = 0
        self.line_delay = 120  # Frames por línea
        self.finished = False

    def update(self):
        # Transición de transparencia
        if self.alpha < 255:
            self.alpha += self.fade_speed
            if self.alpha > 255:
                self.alpha = 255
        else:
            # Contador de tiempo antes de cambiar de línea
            self.timer += 1
            if self.timer >= self.line_delay:
                self.timer = 0
                self.alpha = 0
                self.current_line += 1

                # Finaliza la cinemática al terminar los textos
                if self.current_line >= len(self.lines):
                    self.finished = True

    def draw(self):
        self.screen.fill((10, 10, 15))  # Fondo oscuro

        if self.current_line < len(self.lines):
            line_text = self.lines[self.current_line]

            # Renderizado del texto principal
            text_surface = self.font.render(line_text, True, (240, 220, 180))
            text_surface.set_alpha(int(self.alpha))

            rect = text_surface.get_rect(
                center=(settings.WIDTH // 2, settings.HEIGHT // 2)
            )
            self.screen.blit(text_surface, rect)

        # Indicador para saltar la intro
        lang = getattr(settings, "CURRENT_LANGUAGE", "es")
        skip_text = (
            "Presiona [ESPACIO] para saltar"
            if lang == "es"
            else "Press [SPACE] to skip"
        )
        skip_surf = self.small_font.render(skip_text, True, (100, 100, 120))
        self.screen.blit(
            skip_surf, (settings.WIDTH - 280, settings.HEIGHT - 40)
        )

    def handle_event(self, event):
        # Permite saltar la cinemática presionando Espacio o Enter
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.finished = True