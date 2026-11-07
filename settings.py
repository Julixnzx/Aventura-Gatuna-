# ==========================================
# PANTALLA Y GENERAL
# ==========================================
WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "RPG Legends"
TILE_SIZE = 64

# Estado de la pantalla
IS_FULLSCREEN = False

# ==========================================
# CONFIGURACIÓN DE IDIOMA Y DIFICULTAD
# ==========================================
CURRENT_LANGUAGE = "es"  # "es" o "en"
CURRENT_DIFFICULTY = "NORMAL"  # "EASY", "NORMAL", "HARD"

# ==========================================
# CONFIGURACIÓN DE AUDIO
# ==========================================
IS_MUTED = False
MUSIC_VOLUME = 0.5


def toggle_mute():
    global IS_MUTED
    IS_MUTED = not IS_MUTED


# ==========================================
# HISTORIA DEL JUEGO (INTRO / LORE)
# ==========================================
INTRO_TEXTS = {
    "es": [
        "Durante siglos, el Reino de Eldoria vivió en paz...",
        "Pero la sombra del Rey Canino despertó de las profundidades,",
        "trayendo consigo una plaga de criaturas y goblins feroces.",
        "",
        "Las antiguas tierras han sido divididas y conquistadas.",
        "Solo un guerrero tiene el valor de enfrentar al tirano...",
        "",
        "¡Tu viaje hacia la leyenda comienza ahora!",
    ],
    "en": [
        "For centuries, the Kingdom of Eldoria lived in peace...",
        "But the shadow of the Canine King awoke from the depths,",
        "bringing forth a plague of creatures and fierce goblins.",
        "",
        "The ancient lands have been divided and conquered.",
        "Only one warrior has the courage to face the tyrant...",
        "",
        "Your journey to legend begins now!",
    ],
}


# ==========================================
# DICCIONARIO DE TRADUCCIONES (UI)
# ==========================================
TEXTS = {
    "es": {
        "difficulty": "Dificultad",
        "pause": "PAUSA",
        "skip": "Presiona [ESPACIO] para saltar",
    },
    "en": {
        "difficulty": "Difficulty",
        "pause": "PAUSE",
        "skip": "Press [SPACE] to skip",
    },
}


def get_text(key):
    """Devuelve la traducción correspondiente al idioma actual."""
    return TEXTS.get(CURRENT_LANGUAGE, TEXTS["es"]).get(key, key)