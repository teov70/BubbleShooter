# game_view.py
import pygame
from config import *

def draw_game_field(screen):
    """Draw the rounded-corner play field as a translucent rectangle."""
    # 1. make an SRCALPHA surface the size of the field
    field_surf = pygame.Surface((FIELD_DRAW_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)

    # 2. draw the rounded rectangle onto that surface
    pygame.draw.rect(
        field_surf,
        FIELD_COLOR,                       # RGBA with alpha component
        field_surf.get_rect(),
        border_radius=20
    )

    # 3. blit the translucent surface onto the main screen
    screen.blit(field_surf, (GRID_LEFT_OFFSET, GRID_TOP_OFFSET))