# main.py
import pygame
import random
from config import *
from game_logic import *
from game_view import *
from audio import AudioManager

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
        self.audio = AudioManager()

        self.fonts = {"text": pygame.font.Font("assets/Arcade.ttf", 27),
                      "score": pygame.font.Font("assets/Arcade.ttf", 52),
                      "debug": pygame.font.Font(None, 24)}

        #________________Popup_________________
        self.popup_img = self.popup_assets["popup"]
        self.popup_buttons = {
            "yes":Button(self.popup_assets["yes"], self.popup_assets["yes_hover"], (POP_X, POP_Y)),
            "quit":Button(self.popup_assets["quit"], self.popup_assets["quit_hover"], (POP_X, POP_Y)),
            "cross":Button(self.popup_assets["cross"], self.popup_assets["cross_hover"], (POP_X, POP_Y)),
        }

        #________________Widget_________________
        self.widget_img = self.widget_assets["widget"]
        self.widget_buttons = {
            "previous":Button(self.widget_assets["previous"], self.widget_assets["previous_hover"], (WIDGET_X, WIDGET_Y)),
            "next":Button(self.widget_assets["next"], self.widget_assets["next_hover"], (WIDGET_X, WIDGET_Y)),
            "play":Button(self.widget_assets["play"], self.widget_assets["play_hover"], (WIDGET_X, WIDGET_Y)),
            "pause":Button(self.widget_assets["pause"], self.widget_assets["pause_hover"], (WIDGET_X, WIDGET_Y)),
            "replay":Button(self.widget_assets["replay"], self.widget_assets["replay_hover"], (WIDGET_X, WIDGET_Y)),
            "replay1":Button(self.widget_assets["replay1"], self.widget_assets["replay1_hover"], (WIDGET_X, WIDGET_Y))
        }

        self.running = True
        self.restart_game()

    #___________________ helpers ____________________
    def restart_game(self):
        """Reset full game state: grid, shooter, preview, counters."""
        self.grid = BubbleGrid(audio=self.audio)
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
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    click_frame = True
                    click_pos = event.pos
                elif event.type == self.audio.NEXT_EVENT:
                    if self.audio.loop == 0:
                        self.audio.next()
                    else: 
                        self.audio.replay()

            # 2. INPUT SNAPSHOT _________________________________________
            mouse_pos = pygame.mouse.get_pos()
            mouse_lmb = pygame.mouse.get_pressed()[0]

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
                for btn in self.popup_buttons.values():
                    btn.update(mouse_pos, mouse_lmb)

                # React to clicks
                if self.popup_buttons["yes"].is_clicked():
                    self.audio.play_click()
                    self.restart_game()
                elif  self.popup_buttons["quit"].is_clicked() or self.popup_buttons["cross"].is_clicked():
                    self.audio.play_click()
                    self.running = False

            self.widget_buttons["previous"].update(mouse_pos, mouse_lmb)
            self.widget_buttons["next"].update(mouse_pos, mouse_lmb)
            toggle_btn = self.widget_buttons["play"] if self.audio.is_paused() \
                    else self.widget_buttons["pause"]
            toggle_btn.update(mouse_pos, mouse_lmb)

            toggle_replay = self.widget_buttons["replay"] if self.audio.loop == -1 \
                    else self.widget_buttons["replay1"]
            toggle_replay.update(mouse_pos, mouse_lmb)

            if click_frame and toggle_btn.is_clicked():
                self.audio.play_click()
                self.audio.toggle()

            elif click_frame and toggle_replay.is_clicked():
                self.audio.play_click()
                self.audio.toggle_loop()

            elif self.widget_buttons["next"].is_clicked():
                self.audio.play_click()
                self.audio.next()

            elif self.widget_buttons["previous"].is_clicked():
                self.audio.play_click()
                self.audio.previous()

            # _________ drawing _________
            self.screen.blit(self.bg_img, (0, 0))
            self.screen.blit(self.widget_img, (WIDGET_X, WIDGET_Y))
            draw_game_field(self.screen)
            self.grid.draw(self.screen)

            self.widget_buttons["previous"].draw(self.screen)
            self.widget_buttons["next"].draw(self.screen)
            toggle_btn.draw(self.screen)
            toggle_replay.draw(self.screen)

            draw_bubble_bar(self.screen)
            if self.bubble is not None:
                self.bubble.draw(self.screen)
                self.next_bubble.draw(self.screen)

            remaining_shots = max(0, self.grid.non_clearing_threshold - self.grid.non_clearing_count)
            draw_warning_bubbles(self.screen, remaining_shots, (PREVIEW_X, PREVIEW_Y), Bubble)
            draw_score(self.screen, self.grid.score,  self.fonts)

            if self.game_over:
                self.screen.blit(self.popup_img, (POP_X, POP_Y))
                for btn in self.popup_buttons.values():
                    btn.draw(self.screen)

            draw_mouse_coords(self.screen, mouse_pos, self.fonts["debug"])

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    Game().run()
