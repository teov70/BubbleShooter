# config.py
from math import sqrt

# Screen
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
TOOLBAR_HEIGHT = 100
FPS = 144

PROJECTILE_SPEED = 500

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

# Sounds
POP_SOUND_PATHS = [
    "assets/sounds/pop_1.wav",
    "assets/sounds/pop_2.wav",
    "assets/sounds/pop_3.wav"
]
PLOP_SOUND_PATH = "assets/sounds/plop.wav"

# Game Over Popup
GAME_OVER_ASSETS = [
("popup", "assets/sprites/game_over.png"),
("yes", "assets/sprites/yes_button.png"),
("quit", "assets/sprites/quit_button.png"),
("cross", "assets/sprites/cross_button.png"),
("yes_hover", "assets/sprites/yes_button_hover.png"),
("quit_hover", "assets/sprites/quit_button_hover.png"),
("cross_hover", "assets/sprites/cross_button_hover.png")
]

# Game Over Popup geometry
POP_W, POP_H = 337, 220
POP_X = (SCREEN_WIDTH - POP_W) // 2          # 331
POP_Y = (SCREEN_HEIGHT - POP_H) // 2          # 290

WIDGET_ASSETS = [
("widget", "assets/sprites/widget.png"),
("previous", "assets/sprites/previous_btn.png"),
("next", "assets/sprites/next_btn.png"),
("previous_hover", "assets/sprites/previous_btn_hover.png"),
("next_hover", "assets/sprites/next_btn_hover.png"),
("play", "assets/sprites/play_btn.png"),
("play_hover", "assets/sprites/play_btn_hover.png"),
("pause", "assets/sprites/pause_btn.png"),
("pause_hover", "assets/sprites/pause_btn_hover.png")
]

WIDGET_W, WIDGET_H = 500, 175
WIDGET_X, WIDGET_Y = 236, SCREEN_HEIGHT - WIDGET_H


# Bubble
BUBBLE_RADIUS = 15
BUBBLE_COLOR_PAIRS = [
    ((255, 0, 0), "red"),
    ((0, 255, 0), "green"),
    ((0, 0, 255), "blue"),
    ((255, 255, 0), "yellow"),
    ((255, 0, 255), "magenta"),
    ((0, 255, 255), "cyan"),
    ((128, 128, 128), "gray")
]

BUBBLE_COLORS = [color for color, name in BUBBLE_COLOR_PAIRS if name != "gray"]

STARTING_ROWS = 11
# Grid
GRID_TOP_OFFSET = 50
GRID_LEFT_OFFSET = 50
GRID_COLS = 17
GRID_ROWS = 15
COL_WIDTH = (BUBBLE_RADIUS + 3) * 2
ROW_HEIGHT = (BUBBLE_RADIUS + 3) * sqrt(3)

DIRECTIONS = ["top_left", "top_right", "left", "right", "bottom_left", "bottom_right"]
REVERSE_DIR = {
            "left": "right", "right": "left",
            "top_left": "bottom_right", "bottom_right": "top_left",
            "top_right": "bottom_left", "bottom_left": "top_right"}
#Game Field
FIELD_WIDTH = COL_WIDTH * GRID_COLS
FIELD_DRAW_WIDTH = FIELD_WIDTH + 0.5 * COL_WIDTH
FIELD_HEIGHT = ROW_HEIGHT * GRID_ROWS
FIELD_COLOR = (180, 220, 255, 10)
#Bar Field
BAR_COLOR = (181, 242, 255, 50)
# Shooter
SHOOTER_Y = GRID_TOP_OFFSET + FIELD_HEIGHT + 2.5*ROW_HEIGHT
SHOOTER_X = GRID_LEFT_OFFSET + FIELD_WIDTH // 2
#Preview
PREVIEW_Y = GRID_TOP_OFFSET + FIELD_HEIGHT + 2.5*ROW_HEIGHT
PREVIEW_X = GRID_LEFT_OFFSET + COL_WIDTH*0.5