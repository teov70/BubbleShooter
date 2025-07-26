# game_view.py
import pygame
from config import *
from audio import AudioManager

#GameUI class
class GameUI:
    def __init__(self, screen, audio: AudioManager):
        """Load/create/set up UI assets."""
        self.screen = screen
        self.audio = audio

        self.bg_img = pygame.image.load("assets/sprites/frutiger_aero1.png").convert()
        self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.field_surf = pygame.Surface((FIELD_DRAW_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect( self.field_surf, FIELD_COLOR,  self.field_surf.get_rect(), border_radius=20)
        self.bar_surf = pygame.Surface((COL_WIDTH*9.2, ROW_HEIGHT*1.3), pygame.SRCALPHA)
        pygame.draw.rect(self.bar_surf, BAR_COLOR, self.bar_surf.get_rect(), border_radius=45)

        self.bubble_surfaces = {
            color: pygame.image.load(f"assets/sprites/bubble_{name}.png").convert_alpha()
            for color, name in BUBBLE_COLOR_PAIRS
            }
        
        self.popup_assets = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in GAME_OVER_ASSETS
            }
        
        self.widget_assets = {
            key: pygame.image.load(path).convert_alpha()
            for key, path in WIDGET_ASSETS
            }

        self.fonts = {
            "text": pygame.font.Font("assets/Arcade.ttf", 27),
            "score": pygame.font.Font("assets/Arcade.ttf", 52),
            "debug": pygame.font.Font(None, 24)
        }


        self._init_popup_buttons()
        self._init_widget_buttons()

    def _init_popup_buttons(self):
        self.popup_img = self.popup_assets["popup"]
        self.popup_buttons = {
            "yes": Button(self.popup_assets["yes"], self.popup_assets["yes_hover"], (POP_X, POP_Y)),
            "quit": Button(self.popup_assets["quit"], self.popup_assets["quit_hover"], (POP_X, POP_Y)),
            "cross": Button(self.popup_assets["cross"], self.popup_assets["cross_hover"], (POP_X, POP_Y)),
        }

    def _init_widget_buttons(self):
        self.widget_img = self.widget_assets["widget"]
        self.widget_buttons = {
            "previous": Button(self.widget_assets["previous"], self.widget_assets["previous_hover"], (WIDGET_X, WIDGET_Y)),
            "next": Button(self.widget_assets["next"], self.widget_assets["next_hover"], (WIDGET_X, WIDGET_Y)),
            "play": Button(self.widget_assets["play"], self.widget_assets["play_hover"], (WIDGET_X, WIDGET_Y)),
            "pause": Button(self.widget_assets["pause"], self.widget_assets["pause_hover"], (WIDGET_X, WIDGET_Y)),
            "replay": Button(self.widget_assets["replay"], self.widget_assets["replay_hover"], (WIDGET_X, WIDGET_Y)),
            "replay1": Button(self.widget_assets["replay1"], self.widget_assets["replay1_hover"], (WIDGET_X, WIDGET_Y)),
        }

    def draw_bubble(self, bubble):
        """Blit a single bubble sprite at its current position."""
        surf = self.bubble_surfaces[bubble.color]
        self.screen.blit(surf, surf.get_rect(center=bubble.pos))

    def draw_bubble_grid(self, grid):
        """Iterate through the grid and draw every occupied cell."""
        for row in grid.bubbles:
            for bubble in row:
                if bubble:
                    self.draw_bubble(bubble)

    def draw_game_field(self):
        self.screen.blit( self.field_surf, (GRID_LEFT_OFFSET, GRID_TOP_OFFSET))

    def draw_bubble_bar(self):
        self.screen.blit(self.bar_surf, (GRID_LEFT_OFFSET-4, GRID_TOP_OFFSET + FIELD_HEIGHT + 1.9*ROW_HEIGHT))

    def draw_warning_bubbles(self, warning_bubble, remaining: int):
        """Draw gray bubbles that indicate shots remaining before a new row."""
        bubble_spacing = 40
        x0, y = warning_bubble.pos
        original_pos = warning_bubble.pos

        for i in range(remaining):
            warning_bubble.pos = (x0 + i * bubble_spacing, y)
            self.draw_bubble(warning_bubble)

        warning_bubble.pos = original_pos

    def draw_score(self, score):
            text_surf = self.fonts["text"].render(f"Score", True, (255, 255, 255))
            score_surf = self.fonts["score"].render(f"{score}", True, (255, 255, 255))
            self.screen.blit(text_surf, (430, 720))
            self.screen.blit(score_surf, (430, 687))

    def update_buttons(self, mouse_pos, mouse_lmb, game_over):
        """Update hover/click states for visible buttons."""
        if game_over:
            for btn in self.popup_buttons.values():
                btn.update(mouse_pos, mouse_lmb)
        self.widget_buttons["previous"].update(mouse_pos, mouse_lmb)
        self.widget_buttons["next"].update(mouse_pos, mouse_lmb)

        active_play_pause = "play" if self.audio.is_paused() else "pause"
        self.widget_buttons[active_play_pause].update(mouse_pos, mouse_lmb)

        active_replay = "replay" if self.audio.loop else "replay1"
        self.widget_buttons[active_replay].update(mouse_pos, mouse_lmb)

    def draw_ui(self, grid, bubble, next_bubble, warning_bubble, remaining_shots, mouse_pos, game_over, DEBUG=False):
        """Compose and draw the entire UI frame."""
        self.screen.blit(self.bg_img, (0, 0))
        self.screen.blit(self.widget_img, (WIDGET_X, WIDGET_Y))

        self.draw_game_field()
        self.draw_bubble_bar()
        self.draw_bubble_grid(grid)

        if bubble:
            self.draw_bubble(bubble)
            self.draw_bubble(next_bubble)

        self.widget_buttons["previous"].draw(self.screen)
        self.widget_buttons["next"].draw(self.screen)

        toggle = self.widget_buttons["play"] if self.audio.is_paused() else self.widget_buttons["pause"]
        toggle.draw(self.screen)

        replay = self.widget_buttons["replay"] if self.audio.loop else self.widget_buttons["replay1"]
        replay.draw(self.screen)

        self.draw_warning_bubbles(warning_bubble, remaining_shots)
        self.draw_score(grid.score)

        if game_over:
            self.screen.blit(self.popup_img, (POP_X, POP_Y))
            for btn in self.popup_buttons.values():
                btn.draw(self.screen)

        if DEBUG:
            coords = self.fonts["debug"].render(str(mouse_pos), True, (0, 0, 0))
            self.screen.blit(coords, (0, 0))

# Button class
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

    def update(self, mouse_pos, mouse_pressed_lmb: bool) -> None:
        """Refresh hover and click flags based on current mouse position and button press."""
        lx = mouse_pos[0] - self.rect.x
        ly = mouse_pos[1] - self.rect.y
        inside = (0 <= lx < self.rect.w) and (0 <= ly < self.rect.h)
        self._hovered = inside and self.mask.get_at((lx, ly))

        now_pressed  = self._hovered and mouse_pressed_lmb
        self._clicked = now_pressed and not self._prev_pressed
        self._prev_pressed = now_pressed

    def draw(self, target: pygame.Surface) -> None:
        """Blit the button’s hover or idle image onto the target surface."""
        target.blit(self._hover if self._hovered else self._idle, self.pos)

    def is_hovered(self) -> bool: return self._hovered
    def is_clicked(self) -> bool: return self._clicked