import pygame

from settings import WIDTH, HEIGHT, FPS, TITLE
from entities.player import Player


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)

        self.clock = pygame.time.Clock()

        # Crear el jugador
        self.player = Player()

        self.running = True

    def run(self):

        while self.running:

            self.clock.tick(FPS)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

            # Actualizar jugador
            self.player.update()

            # Dibujar fondo
            self.screen.fill((30, 30, 40))

            # Dibujar jugador
            self.player.draw(self.screen)

            pygame.display.flip()

        pygame.quit()