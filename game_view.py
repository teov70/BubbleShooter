# game_view.py
import pygame
from config import *
import random

pygame.mixer.init()
pop_sounds = [pygame.mixer.Sound(path) for path in POP_SOUND_PATHS]
for s in pop_sounds:
    s.set_volume(0.5)
plop_sound = pygame.mixer.Sound(PLOP_SOUND_PATH)
plop_sound.set_volume(1)

def play_pop_sound():
    random.choice(pop_sounds).play()

def play_plop_sound():
    plop_sound.play()

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