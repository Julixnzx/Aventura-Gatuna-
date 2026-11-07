import pygame
from settings import TILE_SIZE


# Paletas de color por tema. Cada nivel puede usar un tema distinto
# pasando Map(theme="cave"), Map(theme="desert"), etc. en main.py
THEMES = {
    "forest": {
        0: (86, 168, 84),    # pasto claro
        1: (68, 148, 68),    # pasto oscuro
        2: (196, 156, 110),  # tierra / camino
        "deco": "forest",
    },
    "cave": {
        0: (58, 56, 68),     # piedra clara
        1: (44, 42, 54),     # piedra oscura
        2: (92, 80, 68),     # tierra de cueva
        "deco": "cave",
    },
    "desert": {
        0: (226, 198, 132),  # arena clara
        1: (210, 178, 108),  # arena oscura
        2: (178, 138, 78),   # duna / camino
        "deco": "desert",
    },
    "snow": {
        0: (226, 236, 246),  # nieve clara
        1: (204, 220, 236),  # nieve oscura
        2: (176, 178, 192),  # hielo / camino
        "deco": "snow",
    },
    "castle": {
        0: (92, 92, 104),    # piso claro
        1: (72, 72, 84),     # piso oscuro
        2: (54, 50, 60),     # alfombra / camino
        "deco": "castle",
    },
}


def _hash01(ix, iy, seed=0):
    """Genera un número pseudoaleatorio determinista en [0, 1) a partir
    de una posición de tile. Así cada tile siempre se ve igual entre
    frames, pero distinto de sus vecinos, sin tener que guardar estado."""
    n = (ix * 374761393 + iy * 668265263 + seed * 1274126177) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) & 0xFFFFFFFF
    n = (n * 1274126177) & 0xFFFFFFFF
    n = (n ^ (n >> 16)) & 0xFFFFFFFF
    return n / 0xFFFFFFFF


def _jitter_color(color, amount, ix, iy, seed=0):
    h = _hash01(ix, iy, seed)
    delta = int((h - 0.5) * 2 * amount)
    return tuple(max(0, min(255, c + delta)) for c in color)


class Map:
    def __init__(self, theme="forest"):
        # Mapa extendido (30 columnas x 16 filas)
        self.grid = [
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 2, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 2, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
        ]

        # Dimensiones totales en píxeles
        self.width = len(self.grid[0]) * TILE_SIZE
        self.height = len(self.grid) * TILE_SIZE

        # Tema visual del nivel (bosque, cueva, desierto, nieve, castillo)
        self.theme = theme if theme in THEMES else "forest"
        palette = THEMES[self.theme]
        self.deco_style = palette["deco"]
        self.colors = {0: palette[0], 1: palette[1], 2: palette[2]}

    # ------------------------------------------------------------------
    # Dibujo principal
    # ------------------------------------------------------------------
    def draw(self, screen, camera):
        cam_x, cam_y = camera.offset.x, camera.offset.y

        # Calculamos qué rango de tiles es visible para no dibujar de más
        first_col = max(0, int(cam_x // TILE_SIZE) - 1)
        first_row = max(0, int(cam_y // TILE_SIZE) - 1)
        last_col = min(len(self.grid[0]), first_col + int(screen.get_width() / TILE_SIZE) + 3)
        last_row = min(len(self.grid), first_row + int(screen.get_height() / TILE_SIZE) + 3)

        for row_idx in range(first_row, last_row):
            row = self.grid[row_idx]
            for col_idx in range(first_col, last_col):
                tile = row[col_idx]
                base_color = self.colors.get(tile, (0, 0, 0))
                color = _jitter_color(base_color, 10, col_idx, row_idx, seed=tile)

                screen_x = col_idx * TILE_SIZE - cam_x
                screen_y = row_idx * TILE_SIZE - cam_y
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

                pygame.draw.rect(screen, color, rect)
                self._draw_bevel(screen, rect, color)
                self._draw_decoration(screen, rect, tile, col_idx, row_idx)

    def _draw_bevel(self, screen, rect, color):
        """Da una sensación de relieve/profundidad a cada baldosa."""
        light = tuple(min(255, c + 22) for c in color)
        dark = tuple(max(0, c - 22) for c in color)
        pygame.draw.line(screen, light, rect.topleft, rect.topright, 2)
        pygame.draw.line(screen, light, rect.topleft, rect.bottomleft, 2)
        pygame.draw.line(screen, dark, rect.bottomleft, rect.bottomright, 2)
        pygame.draw.line(screen, dark, rect.topright, rect.bottomright, 2)

    # ------------------------------------------------------------------
    # Decoraciones según el tema del nivel
    # ------------------------------------------------------------------
    def _draw_decoration(self, screen, rect, tile, ix, iy):
        style = self.deco_style
        if style == "forest":
            self._deco_forest(screen, rect, tile, ix, iy)
        elif style == "cave":
            self._deco_cave(screen, rect, tile, ix, iy)
        elif style == "desert":
            self._deco_desert(screen, rect, tile, ix, iy)
        elif style == "snow":
            self._deco_snow(screen, rect, tile, ix, iy)
        elif style == "castle":
            self._deco_castle(screen, rect, tile, ix, iy)

    def _deco_forest(self, screen, rect, tile, ix, iy):
        h = _hash01(ix, iy, seed=99)
        cx, cy = rect.center
        if tile in (0, 1):
            # matas de pasto
            if h < 0.45:
                blade_color = (40, 110, 40)
                bx = rect.x + 10 + int(h * 40)
                for i in range(3):
                    ox = -4 + i * 4
                    pygame.draw.line(screen, blade_color, (bx + ox, rect.bottom - 6),
                                      (bx + ox + 2, rect.bottom - 16), 2)
            # florecita ocasional
            if 0.85 < h < 0.93:
                fx, fy = cx - 6, cy + 8
                for dx, dy in ((0, -3), (0, 3), (-3, 0), (3, 0)):
                    pygame.draw.circle(screen, (255, 240, 120), (fx + dx, fy + dy), 2)
                pygame.draw.circle(screen, (255, 180, 40), (fx, fy), 2)
        else:
            # camino de tierra: piedritas y grietas
            if h < 0.5:
                px = rect.x + 8 + int(h * 44)
                py = rect.y + 10 + int((h * 7) % 40)
                pygame.draw.circle(screen, (150, 115, 80), (px, py), 2)
            if 0.5 <= h < 0.7:
                pygame.draw.line(screen, (160, 125, 85),
                                  (rect.x + 12, rect.y + 46), (rect.x + 30, rect.y + 30), 1)

    def _deco_cave(self, screen, rect, tile, ix, iy):
        h = _hash01(ix, iy, seed=17)
        if tile in (0, 1):
            # grietas y motas minerales en la roca
            crack_color = (25, 24, 32)
            if h < 0.4:
                pygame.draw.line(screen, crack_color,
                                  (rect.x + 8, rect.y + 10), (rect.x + 26, rect.y + 40), 1)
            if 0.4 <= h < 0.55:
                pygame.draw.circle(screen, (120, 150, 200), (rect.x + 20 + int(h * 20), rect.y + 18), 2)
            if 0.8 < h < 0.9:
                # pequeña estalactita/roca colgante
                pygame.draw.polygon(screen, (30, 28, 38),
                                     [(rect.x + 24, rect.y), (rect.x + 30, rect.y), (rect.x + 27, rect.y + 14)])
        else:
            # tierra del túnel con guijarros
            if h < 0.5:
                pygame.draw.circle(screen, (60, 50, 42), (rect.x + 14 + int(h * 30), rect.y + 34), 2)

    def _deco_desert(self, screen, rect, tile, ix, iy):
        h = _hash01(ix, iy, seed=55)
        cx, cy = rect.center
        if tile in (0, 1):
            # ondas de arena
            if h < 0.5:
                wave = (196, 168, 100)
                pygame.draw.arc(screen, wave, (rect.x + 4, rect.y + 30, 56, 20), 3.4, 6.0, 2)
            # cactus ocasional
            if 0.9 < h < 0.95:
                stem = (60, 130, 70)
                pygame.draw.rect(screen, stem, (cx - 3, rect.y + 10, 6, 30), border_radius=3)
                pygame.draw.rect(screen, stem, (cx - 10, rect.y + 18, 7, 5), border_radius=2)
        else:
            # camino agrietado
            if h < 0.4:
                pygame.draw.line(screen, (140, 100, 55),
                                  (rect.x + 10, rect.y + 20), (rect.x + 34, rect.y + 44), 1)

    def _deco_snow(self, screen, rect, tile, ix, iy):
        h = _hash01(ix, iy, seed=33)
        if tile in (0, 1):
            # brillos de nieve
            if h < 0.35:
                sx = rect.x + 8 + int(h * 48)
                sy = rect.y + 8 + int((h * 13) % 48)
                pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 1)
            if 0.9 < h < 0.95:
                # montoncito de nieve
                pygame.draw.ellipse(screen, (245, 250, 255), (rect.x + 14, rect.y + 40, 24, 10))
        else:
            # hielo con grietas azuladas
            if h < 0.4:
                pygame.draw.line(screen, (140, 170, 200),
                                  (rect.x + 8, rect.y + 12), (rect.x + 28, rect.y + 38), 1)

    def _deco_castle(self, screen, rect, tile, ix, iy):
        h = _hash01(ix, iy, seed=77)
        if tile in (0, 1):
            # losas con líneas de junta
            joint = (40, 40, 48)
            pygame.draw.line(screen, joint, (rect.centerx, rect.top), (rect.centerx, rect.bottom), 1)
            pygame.draw.line(screen, joint, (rect.left, rect.centery), (rect.right, rect.centery), 1)
            if 0.85 < h < 0.9:
                pygame.draw.circle(screen, (255, 210, 90), (rect.centerx, rect.centery), 3)  # antorcha lejana
        else:
            # alfombra con borde decorativo
            border = (110, 30, 30)
            pygame.draw.rect(screen, border, rect, 3)
            if h < 0.3:
                pygame.draw.circle(screen, (180, 150, 60), rect.center, 3)
