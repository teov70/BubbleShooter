# main.py
import pygame
import random
from config import *
from game_logic import *
from game_view import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img = pygame.image.load("assets/sprites/frutiger_aero1.png").convert()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()


# ─────────────────── helpers ────────────────────
def restart_game() -> None:
    """Reset full game state: grid, shooter, preview, counters."""
    global grid, bubble, next_bubble, bubble_ready, game_over
    grid = BubbleGrid()
    grid.populate_random_rows()

    bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                    pos=(SHOOTER_X, SHOOTER_Y))
    next_bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                         pos=(PREVIEW_X, PREVIEW_Y))
    bubble_ready = True
    game_over = False


# ─────────────────── initial state ──────────────
restart_game()
running = True

# ─────────────────── main loop ──────────────────
while running:
    # ───────── event handling ─────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over:
            # Only handle popup clicks
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if yes_rect.collidepoint(event.pos):
                    restart_game()
                elif quit_rect.collidepoint(event.pos) or cross_rect.collidepoint(event.pos):
                    running = False
            continue  # skip normal gameplay events

        # Gameplay events (only when not game_over)
        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            and bubble.velocity.length_squared() == 0 and bubble_ready):
            mouse_pos = pygame.mouse.get_pos()
            if (GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
                GRID_TOP_OFFSET  <= mouse_pos[1] <= GRID_TOP_OFFSET  + FIELD_HEIGHT):
                bubble.velocity = compute_velocity(bubble.pos, mouse_pos, PROJECTILE_SPEED)
                bubble_ready = False

    # ───────── update logic (only if not paused) ─────────
    dt  = clock.get_time() / 1000
    now = pygame.time.get_ticks()

    if not game_over:
        # move active projectile
        if bubble is not None:
            bubble.move(dt, grid)

            # snap when it stops
            if bubble.velocity.length_squared() == 0 and not bubble_ready:
                row, col   = grid.get_cell_for_position(*bubble.pos)
                snap_cell  = grid.get_snap_cell(row, col, bubble.pos)
                if snap_cell is None:
                    game_over = True
                else:
                    bubble.pos = grid.get_position_for_cell(*snap_cell)
                    grid.add_bubble(bubble)

                    # match-3 detection → enqueue pops (floaters handled inside grid)
                    match_chain = grid.get_connected_same_color(*snap_cell)
                    game_over = not grid.destroy_bubbles(match_chain)

                bubble = None
                bubble_ready = False

        # animate popping & floaters
        grid.update(now)

        # spawn a new shooter when ready
        if bubble is None and not bubble_ready:
            bubble = next_bubble
            bubble.pos = pygame.Vector2(SHOOTER_X, SHOOTER_Y)
            next_bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                                 pos=(PREVIEW_X, PREVIEW_Y))
            bubble_ready = True

    # ───────── drawing ─────────
    screen.blit(bg_img, (0, 0))
    draw_game_field(screen)
    draw_bubble_bar(screen)
    grid.draw(screen)

    if bubble is not None:
        bubble.draw(screen)
        next_bubble.draw(screen)

    remaining_shots = max(0, grid.non_clearing_threshold - grid.non_clearing_count)
    draw_warning_bubbles(screen, remaining_shots, (PREVIEW_X, PREVIEW_Y), Bubble)

    font = pygame.font.SysFont("Consolas", 30)
    score_surf = font.render(f"Score:{grid.score}", True, (255, 255, 255))
    screen.blit(score_surf, (730, 280))

    if game_over:
        draw_game_over_popup(screen)
        #debug_draw_hitboxes(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
