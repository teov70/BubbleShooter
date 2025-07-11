# game_view.py
import pygame
from config import *
import random

pygame.mixer.init()
pygame.mixer.music.load("assets/sounds/frutigeraeromusic.ogg")
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(loops=-1)
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

def draw_bubble_bar(screen):
    """Draw a translucent rounded-corner rectangle for bubble bar."""
    # 1. make an SRCALPHA surface the size of the field
    bar_surf = pygame.Surface((COL_WIDTH*9.2, ROW_HEIGHT*1.3), pygame.SRCALPHA)

    # 2. draw the rounded rectangle onto that surface
    pygame.draw.rect(
        bar_surf,
        BAR_COLOR,
        bar_surf.get_rect(),
        border_radius=45
    )

    # 3. blit the translucent surface onto the main screen
    screen.blit(bar_surf, (GRID_LEFT_OFFSET-4, GRID_TOP_OFFSET + FIELD_HEIGHT + 1.9*ROW_HEIGHT))

def draw_warning_bubbles(screen, remaining: int, preview_pos: tuple[int, int], bubble_cls):
    """Draw a bubbles that signal the next row addition."""
    bubble_spacing = 40
    base_x = preview_pos[0] + 40
    y = preview_pos[1]

    for i in range(remaining-1):
        x = base_x + i * bubble_spacing
        gray = bubble_cls(color=GRAY, pos=(x, y))
        gray.draw(screen)