import pygame
from config import *

def draw_game_field(screen):
    field_rect = pygame.Rect(
        GRID_LEFT_OFFSET,
        GRID_TOP_OFFSET,
        FIELD_WIDTH,
        FIELD_HEIGHT
    )
    pygame.draw.rect(screen, FIELD_COLOR, field_rect, border_radius=20)