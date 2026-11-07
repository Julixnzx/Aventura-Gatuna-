import pygame
from settings import WIDTH, HEIGHT


class Camera:
    def __init__(self, map_width, map_height):
        # El offset indica cuánto debemos mover la pantalla
        self.offset = pygame.Vector2(0, 0)
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target_position):
        # Centramos la cámara en la posición del objetivo (el gato)
        x = target_position.x - WIDTH // 2
        y = target_position.y - HEIGHT // 2

        # Limitamos la cámara para que no muestre el vacío fuera del mapa
        x = max(0, min(x, self.map_width - WIDTH))
        y = max(0, min(y, self.map_height - HEIGHT))

        self.offset = pygame.Vector2(x, y)