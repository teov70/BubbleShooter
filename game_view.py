# game_view.py
import pygame
from config import *
import random

_POPUP_SURFACES = None

pygame.mixer.init()
#pygame.mixer.music.load("assets/sounds/frutigeraeromusic.ogg")
pygame.mixer.music.load("assets/sounds/lotus_waters.ogg")
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

def draw_score(screen, score):
        text_font = pygame.font.Font("assets/Arcade.ttf", 26)
        score_font = pygame.font.Font("assets/Arcade.ttf", 50)
        text_surf = text_font.render(f"Score", True, (255, 255, 255))
        score_surf = score_font.render(f"{score}", True, (255, 255, 255))
        screen.blit(text_surf, (417, 708))
        screen.blit(score_surf, (487, 695))

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

def load_popup_surfaces():
    global _POPUP_SURFACES
    if _POPUP_SURFACES is None:
        _POPUP_SURFACES = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in GAME_OVER_ASSETS
        }
    return _POPUP_SURFACES

# ── popup geometry (337×220 popup in 1000×800 screen) ──────
POP_W, POP_H = 337, 220
SCREEN_W, SCREEN_H = 1000, 800
POP_X = (SCREEN_W - POP_W) // 2          # 331
POP_Y = (SCREEN_H - POP_H) // 2          # 290

yes_rect   = pygame.Rect(POP_X + 114, POP_Y + 162, 103, 37)
quit_rect  = pygame.Rect(POP_X + 222, POP_Y + 162, 97, 37)
cross_rect = pygame.Rect(POP_X + 271, POP_Y +   1,  58, 28)

# ── draw helpers ───────────────────────────────────────────
def draw_game_over_popup(screen):
    surf = load_popup_surfaces()
    pos = (POP_X, POP_Y)
    screen.blit(surf["popup"], pos)
    screen.blit(surf["yes"],   pos)
    screen.blit(surf["quit"],  pos)
    screen.blit(surf["cross"], pos)

def debug_draw_hitboxes(screen):
    brd = 2
    pygame.draw.rect(screen, (0, 0, 0), yes_rect,   brd, border_radius=4)
    pygame.draw.rect(screen, (0, 0, 0), quit_rect,  brd, border_radius=4)
    pygame.draw.rect(screen, (0, 0, 0), cross_rect, brd, border_radius=4)



class Button:
    def __init__(self, image_idle, image_hover, pos):
        self.image_idle = image_idle
        self.image_hover = image_hover
        self.pos = pos
        self.rect = self.image_idle.get_rect(topleft=pos)
        self.mask = pygame.mask.from_surface(self.image_idle)
        self.hovered = False
        self.was_pressed = False  # Prevent repeated triggering

    def update(self, mouse_pos, mouse_pressed):
        local_x = mouse_pos[0] - self.pos[0]
        local_y = mouse_pos[1] - self.pos[1]

        if 0 <= local_x < self.rect.width and 0 <= local_y < self.rect.height:
            self.hovered = self.mask.get_at((local_x, local_y)) == 1
        else:
            self.hovered = False

        # Click detection (only once per press)
        if self.hovered and mouse_pressed[0]:  # Left click
            if not self.was_pressed and self.action:
                self.action()
            self.was_pressed = True
        elif not mouse_pressed[0]:
            self.was_pressed = False

    def draw(self, surface):
        if self.hovered:
            surface.blit(self.image_hover, self.pos)
        else:
            surface.blit(self.image_idle, self.pos)