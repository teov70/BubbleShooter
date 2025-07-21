# main.py
import pygame
import random
from config import *
from game_logic import *
from game_view import *

class Game:
    def __init__(self): 
        pygame.init()
        self.clock = pygame.time.Clock()
        icon = pygame.image.load("assets/sprites/bubble_icon.png")
        pygame.display.set_icon(icon)
        pygame.display.set_caption("Aero Bubble Shooter")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.bg_img = pygame.image.load("assets/sprites/frutiger_aero1.png").convert()
        self.bg_img = pygame.transform.scale(self.bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.popup_assets = load_popup_surfaces()
        self.widget_assets = load_widget_surfaces()
        init_audio()
        self.fonts = {"text": pygame.font.Font("assets/Arcade.ttf", 27),
                      "score": pygame.font.Font("assets/Arcade.ttf", 52)}

        #________________Game Over Popup_________________
        self.popup_img = self.popup_assets["popup"]
        self.buttons = {
            "yes":Button(self.popup_assets["yes"], self.popup_assets["yes_hover"], (POP_X, POP_Y)),
            "quit":Button(self.popup_assets["quit"], self.popup_assets["quit_hover"], (POP_X, POP_Y)),
            "cross":Button(self.popup_assets["cross"], self.popup_assets["cross_hover"], (POP_X, POP_Y)),
        }

        #________________Widget_________________
        self.widget_img = self.widget_assets["widget"]

        self.running = True
        self.restart_game()

    #___________________ helpers ____________________
    def restart_game(self):
        """Reset full game state: self.grid, shooter, preview, counters."""
        self.grid = BubbleGrid()
        self.grid.populate_random_rows()
        self.bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(SHOOTER_X, SHOOTER_Y))
        self.next_bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(PREVIEW_X, PREVIEW_Y))
        self.bubble_ready = True
        self.game_over = False

    def should_shoot(self, mouse_pos, click_frame):
        return (click_frame and self.bubble_ready and self.bubble.velocity.length_squared() == 0 and
                GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
                GRID_TOP_OFFSET  <= mouse_pos[1] <= GRID_TOP_OFFSET  + FIELD_HEIGHT)

    def run(self):
        while self.running:
            click_frame = False
            click_pos = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_frame = True
                    click_pos = event.pos

            # 2. INPUT SNAPSHOT _________________________________________
            mouse_pos = pygame.mouse.get_pos()
            mouse_lmb = pygame.mouse.get_pressed()[0]

            if not self.game_over:
                # Shoot self.bubble
                if self.should_shoot(mouse_pos, click_frame):
                    self.bubble.velocity = compute_velocity(self.bubble.pos, mouse_pos, PROJECTILE_SPEED)
                    self.bubble_ready = False

                # Move active self.bubble
                if self.bubble is not None:
                    self.bubble.move(self.clock.get_time() / 1000, self.grid)

                    # snap to cell when it stops and add it to self.grid
                    if self.bubble.velocity.length_squared() == 0 and not self.bubble_ready:
                        row, col   = self.grid.get_cell_for_position(*self.bubble.pos)
                        snap_cell  = self.grid.get_snap_cell(row, col, self.bubble.pos)
                        if snap_cell is None:
                            self.game_over = True
                        else:
                            self.bubble.pos = self.grid.get_position_for_cell(*snap_cell)
                            self.grid.add_bubble(self.bubble)

                            # match-3 detection → enqueue pops (floaters handled inside self.grid)
                            match_chain = self.grid.get_connected_same_color(*snap_cell)
                            self.game_over = not self.grid.destroy_bubbles(match_chain)

                        self.bubble = None
                        self.bubble_ready = False

                # animate popping & floaters
                self.grid.update(pygame.time.get_ticks())

                # spawn a new shooter when ready
                if self.bubble is None and not self.bubble_ready:
                    self.bubble = self.next_bubble
                    self.bubble.pos = pygame.Vector2(SHOOTER_X, SHOOTER_Y)
                    self.next_bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                                        pos=(PREVIEW_X, PREVIEW_Y))
                    self.bubble_ready = True

            else:
                # Update buttons
                for btn in self.buttons.values():
                    btn.update(mouse_pos, mouse_lmb)

                # React to clicks
                if self.buttons["yes"].is_clicked():
                    self.restart_game()
                elif  self.buttons["quit"].is_clicked() or self.buttons["cross"].is_clicked():
                    self.running = False

            # _________ drawing _________
            self.screen.blit(self.bg_img, (0, 0))
            self.screen.blit(self.widget_img, (WIDGET_X, WIDGET_Y))
            draw_game_field(self.screen)
            draw_bubble_bar(self.screen)
            self.grid.draw(self.screen)

            if self.bubble is not None:
                self.bubble.draw(self.screen)
                self.next_bubble.draw(self.screen)

            remaining_shots = max(0, self.grid.non_clearing_threshold - self.grid.non_clearing_count)
            draw_warning_bubbles(self.screen, remaining_shots, (PREVIEW_X, PREVIEW_Y), Bubble)
            draw_score(self.screen, self.grid.score,  self.fonts)

            if self.game_over:
                self.screen.blit(self.popup_img, (POP_X, POP_Y))
                for btn in self.buttons.values():
                    btn.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
