import pygame

try:
    if not pygame.get_init():
        pygame.init()
except Exception:
    pass

# Window sizes
MENU_WIDTH = 1200
MENU_HEIGHT = 650

GAME_WIDTH = 1280
GAME_HEIGHT = 650

FPS = 60

# Basic colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURE_WHITE = (255, 255, 255)
OFF_WHITE = (245, 245, 245)
LIGHT_GRAY = (220, 220, 220)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Accent colors
PRIMARY_BLUE = (64, 156, 255)
SECONDARY_BLUE = (52, 152, 219)
ACCENT_BLUE = (155, 89, 182)
DEEP_BLUE = (41, 128, 185)

SUCCESS_GREEN = (46, 213, 115)
SUCCESS_DARK = (39, 174, 96)

WARNING_ORANGE = (255, 159, 67)
WARNING_DARK = (230, 126, 34)

ERROR_RED = (255, 107, 107)
ERROR_DARK = (231, 76, 60)

NEUTRAL_GRAY = (149, 165, 166)
NEUTRAL_DARK = (127, 140, 141)

# Background shades
BG_DARKEST = (8, 12, 18)
BG_DARKER = (12, 18, 28)
BG_DARK = (18, 25, 38)
BG_MEDIUM = (25, 35, 50)
BG_LIGHT = (35, 45, 65)

# Glass overlays (with alpha)
GLASS_DARK = (20, 30, 45, 180)
GLASS_MEDIUM = (30, 40, 55, 160)
GLASS_LIGHT = (40, 50, 70, 140)

# Gradients
GRADIENT_START = (12, 18, 28)
GRADIENT_END = (18, 25, 38)
GRADIENT_ACCENT = (25, 35, 50)

# States
MENU = "menu"
GAME = "game"
RESULTS = "results"
SETTINGS = "settings"

