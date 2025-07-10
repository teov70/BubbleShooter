# config.py
from math import sqrt
from utils import load_bubble_surfaces

# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
TOOLBAR_HEIGHT = 100
FPS = 60

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (0, 100, 120)

# Bubble
BUBBLE_RADIUS = 15
BUBBLE_COLOR_PAIRS = [
    ((255, 0, 0), "red"),
    ((0, 255, 0), "green"),
    ((0, 0, 255), "blue"),
    ((255, 255, 0), "yellow"),
    ((255, 0, 255), "magenta"),
    ((0, 255, 255), "cyan"),
]
BUBBLE_COLORS = [color for color, _ in BUBBLE_COLOR_PAIRS]

# Grid
GRID_TOP_OFFSET = 50
GRID_LEFT_OFFSET = 50
GRID_COLS = 17
GRID_ROWS = 15
COL_WIDTH = (BUBBLE_RADIUS + 3) * 2
ROW_HEIGHT = (BUBBLE_RADIUS + 3) * sqrt(3)
#Game Field
FIELD_WIDTH = COL_WIDTH * GRID_COLS
FIELD_DRAW_WIDTH = FIELD_WIDTH + 0.5 * COL_WIDTH
FIELD_HEIGHT = ROW_HEIGHT * GRID_ROWS
FIELD_COLOR = (180, 220, 255, 10)
# Shooter
SHOOTER_Y = GRID_TOP_OFFSET + FIELD_HEIGHT + ROW_HEIGHT
SHOOTER_X = GRID_LEFT_OFFSET + FIELD_WIDTH // 2
PROJECTILE_SPEED = 500