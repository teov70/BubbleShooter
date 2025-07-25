# game_view.py
import pygame
from config import *
import random

_BUBBLE_SURFACES = None
_POPUP_SURFACES = None
_WIDGET_SURFACES = None
_cached_field_surf = None
_cached_bar_surf = None

def draw_game_field(screen):
    global _cached_field_surf
    if _cached_field_surf is None:
        _cached_field_surf = pygame.Surface((FIELD_DRAW_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(_cached_field_surf, FIELD_COLOR, _cached_field_surf.get_rect(), border_radius=20)
    screen.blit(_cached_field_surf, (GRID_LEFT_OFFSET, GRID_TOP_OFFSET))

def draw_bubble(screen, bubble):
    surf = load_bubble_surfaces(BUBBLE_COLOR_PAIRS)[bubble.color]
    screen.blit(surf, surf.get_rect(center=bubble.pos))

def draw_bubble_grid(screen, grid):
    """Iterate grid and draw every occupied cell."""
    for row in grid.bubbles:
        for bubble in row:
            if bubble:
                draw_bubble(screen, bubble)

def draw_score(screen, score, fonts):
        text_surf = fonts["text"].render(f"Score", True, (255, 255, 255))
        score_surf = fonts["score"].render(f"{score}", True, (255, 255, 255))
        screen.blit(text_surf, (430, 720))
        screen.blit(score_surf, (430, 687))

def draw_bubble_bar(screen):
    global _cached_bar_surf
    if _cached_bar_surf is None:
        _cached_bar_surf = pygame.Surface((COL_WIDTH*9.2, ROW_HEIGHT*1.3), pygame.SRCALPHA)
        pygame.draw.rect(_cached_bar_surf, BAR_COLOR, _cached_bar_surf.get_rect(), border_radius=45)
    screen.blit(_cached_bar_surf, (GRID_LEFT_OFFSET-4, GRID_TOP_OFFSET + FIELD_HEIGHT + 1.9*ROW_HEIGHT))

def draw_warning_bubbles(screen, remaining: int, preview_pos: tuple[int, int], bubble_cls):
    """Draw bubbles that signal the next row addition."""
    bubble_spacing = 40
    base_x = preview_pos[0] + 40
    y = preview_pos[1]

    for i in range(remaining-1):
        x = base_x + i * bubble_spacing
        gray = bubble_cls(color=GRAY, pos=(x, y))
        draw_bubble(screen, gray)

def load_bubble_surfaces(color_pairs):
    global _BUBBLE_SURFACES
    if _BUBBLE_SURFACES is None:
        _BUBBLE_SURFACES = {
            color: pygame.image.load(f"assets/sprites/bubble_{name}.png").convert_alpha()
            for color, name in color_pairs
        }
    return _BUBBLE_SURFACES

def load_popup_surfaces():
    global _POPUP_SURFACES
    if _POPUP_SURFACES is None:
        _POPUP_SURFACES = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in GAME_OVER_ASSETS
        }
    return _POPUP_SURFACES

def load_widget_surfaces():
    global _WIDGET_SURFACES
    if _WIDGET_SURFACES is None:
        _WIDGET_SURFACES = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in WIDGET_ASSETS
        }
    return _WIDGET_SURFACES


#__________________Butoon Class______________________________
class Button:
    __slots__ = ("pos", "rect", "mask",
                 "_idle", "_hover",
                 "_hovered", "_clicked", "_prev_pressed")

    def __init__(self, idle: pygame.Surface,
                       hover: pygame.Surface,
                       pos: tuple[int, int]):
        self._idle  = idle.convert_alpha()
        self._hover = hover.convert_alpha()
        self.pos    = pygame.Vector2(pos)

        self.rect   = self._idle.get_rect(topleft=pos)
        self.mask   = pygame.mask.from_surface(self._idle)

        self._hovered       = False
        self._clicked       = False
        self._prev_pressed  = False

    # ----------------------------------------------------------
    def update(self, mouse_pos, mouse_pressed_lmb: bool) -> None:
        """Call once per frame before querying hovered / clicked."""
        lx = mouse_pos[0] - self.rect.x
        ly = mouse_pos[1] - self.rect.y
        inside = (0 <= lx < self.rect.w) and (0 <= ly < self.rect.h)
        self._hovered = inside and self.mask.get_at((lx, ly))

        now_pressed  = self._hovered and mouse_pressed_lmb
        self._clicked = now_pressed and not self._prev_pressed
        self._prev_pressed = now_pressed

    def draw(self, target: pygame.Surface) -> None:
        target.blit(self._hover if self._hovered else self._idle, self.pos)

    # ----------------------------------------------------------
    def is_hovered(self) -> bool: return self._hovered
    def is_clicked(self) -> bool: return self._clicked

#__________________DEBUG______________________
def draw_mouse_coords(screen, pos, font, DEBUG = False):
    if not DEBUG: return
    txt = font.render(f"x:{pos[0]}  y:{pos[1]}", True, (0, 0, 0))
    screen.blit(txt, (10, 10))      # top-left corner