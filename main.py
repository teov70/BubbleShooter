# main.py
import pygame
import random
from config import *
from game_logic import Bubble, BubbleGrid, compute_velocity
from game_view import GameUI
from audio import AudioManager

class Game:
    def __init__(self):
        """Initialize Pygame, audio, UI layer, and first game state."""
        pygame.init()
        self.clock = pygame.time.Clock()
        icon = pygame.image.load("assets/sprites/bubble_icon.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Aero Bubble Shooter")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.audio = AudioManager()
        self.ui = GameUI(self.screen, self.audio)
        self.running = True
        self.restart_game()

    def restart_game(self):
        """Reset full game state: grid, shooter, preview, counters."""
        self.grid = BubbleGrid(audio=self.audio)
        self.grid.populate_random_rows()
        self.bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(SHOOTER_X, SHOOTER_Y))
        self.next_bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(PREVIEW_X, PREVIEW_Y))
        self.warning_bubble = Bubble(color=GRAY, pos=(PREVIEW_X + 40, PREVIEW_Y))
        self.bubble_ready = True
        self.game_over = False

    def should_shoot(self, mouse_pos, click_frame):
        """Return True when a left-click is valid for firing the bubble."""
        return (click_frame and self.bubble_ready and self.bubble.velocity.length_squared() == 0 and
                GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
                GRID_TOP_OFFSET  <= mouse_pos[1] <= GRID_TOP_OFFSET  + FIELD_HEIGHT and not self.grid.pop_queue)

    def run(self):
        """Execute the event loop, update logic, and delegate all rendering."""
        while self.running:
            click_frame = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_frame = True
                elif event.type == self.audio.NEXT_EVENT:
                    if self.audio.loop:
                        self.audio.replay()
                    else: 
                        self.audio.next()

            # 2. INPUT SNAPSHOT _________________________________________
            mouse_pos = pygame.mouse.get_pos()
            mouse_lmb = pygame.mouse.get_pressed()[0]
            self.ui.update_buttons(mouse_pos, mouse_lmb, self.game_over)
            if not self.game_over:
                # Shoot bubble
                if self.should_shoot(mouse_pos, click_frame):
                    self.bubble.velocity = compute_velocity(self.bubble.pos, mouse_pos, PROJECTILE_SPEED)
                    self.bubble_ready = False

                # Move active bubble
                if self.bubble is not None:
                    self.bubble.move(self.clock.get_time() / 1000, self.grid)

                    # snap to cell when it stops and add it to grid
                    if self.bubble.velocity.length_squared() == 0 and not self.bubble_ready:
                        hit_r, hit_c = getattr(self.bubble, "hit_cell", (None, None))
                        placed_cell = self.grid.snap_bubble_to_grid(self.bubble, hit_r, hit_c)
                        if placed_cell is None:
                            self.game_over = True
                        else:
                            # match-3 detection → enqueue pops (floaters handled inside grid)
                            match_chain = self.grid.get_connected_same_color(*placed_cell)
                            self.game_over = not self.grid.destroy_bubbles(match_chain)

                        if hasattr(self.bubble, "hit_cell"):
                            delattr(self.bubble, "hit_cell")

                        self.bubble = None
                        self.bubble_ready = False

                # Update grid state
                self.grid.update(pygame.time.get_ticks())

                # spawn a new shooter when ready
                if self.bubble is None and not self.bubble_ready:
                    self.bubble = self.next_bubble
                    self.bubble.pos = pygame.Vector2(SHOOTER_X, SHOOTER_Y)
                    self.next_bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                                        pos=(PREVIEW_X, PREVIEW_Y))
                    self.bubble_ready = True
            
            else:
                # React to clicks
                if self.ui.popup_buttons["yes"].is_clicked():
                    self.audio.play_click()
                    self.restart_game()
                elif  self.ui.popup_buttons["quit"].is_clicked() or self.ui.popup_buttons["cross"].is_clicked():
                    self.audio.play_click()
                    self.running = False

            if self.ui.widget_buttons["playpause"].is_clicked():
                self.audio.play_click()
                self.audio.toggle()

            elif self.ui.widget_buttons["replay"].is_clicked():
                self.audio.play_click()
                self.audio.toggle_loop()

            elif self.ui.widget_buttons["next"].is_clicked():
                self.audio.play_click()
                self.audio.next()

            elif self.ui.widget_buttons["previous"].is_clicked():
                self.audio.play_click()
                self.audio.previous()

            elif self.ui.widget_buttons["restart"].is_clicked():
                self.audio.play_click()
                self.restart_game()

            # _________ drawing _________
            self.ui.draw_ui(self.grid, self.bubble, self.next_bubble, self.warning_bubble, mouse_pos, self.game_over)

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
