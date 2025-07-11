# main.py
import pygame
from config import *
from game_logic import *
from game_view import *
import random

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img = pygame.image.load("assets/sprites/frutiger_aero.png").convert()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

bubble = Bubble(
    color=random.choice(BUBBLE_COLORS),
    pos=(SHOOTER_X, SHOOTER_Y)
)

grid = BubbleGrid()
grid.populate_random_rows()
bubble_ready = True  # This means: shooter bubble is available

running = True
while running:
    # ───────── event handling & shooting ─────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and
            bubble.velocity.length_squared() == 0 and bubble_ready):
            mouse_pos = pygame.mouse.get_pos()
            if (GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
                GRID_TOP_OFFSET  <= mouse_pos[1] <= GRID_TOP_OFFSET  + FIELD_HEIGHT):
                bubble.velocity = compute_velocity(bubble.pos, mouse_pos, PROJECTILE_SPEED)
                bubble_ready = False

    # ───────── update logic ─────────
    dt  = clock.get_time() / 1000
    now = pygame.time.get_ticks()

    # move active projectile
    if bubble is not None:
        bubble.move(dt, grid)

        # snap when it stops
        if bubble.velocity.length_squared() == 0 and not bubble_ready:
            row, col   = grid.get_cell_for_position(*bubble.pos)
            snap_cell  = grid.get_snap_cell(row, col, bubble.pos)
            if snap_cell is None:
                print("❌ Game Over - no valid snap position")
                running = False
            else:
                bubble.pos = grid.get_position_for_cell(*snap_cell)
                grid.add_bubble(bubble)

                # match-3 detection → enqueue pops (floaters handled inside grid)
                match_chain = grid.get_connected_same_color(*snap_cell)
                game_continue = grid.destroy_bubbles(match_chain)
                if not game_continue:
                    running = False


            bubble = None
            bubble_ready = False

    # animate popping & floaters
    grid.update(now)

    # spawn a new shooter when ready
    if bubble is None and not bubble_ready:
        bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                        pos=(SHOOTER_X, SHOOTER_Y))
        bubble_ready = True

    # ───────── drawing ─────────
    screen.blit(bg_img, (0, 0))
    draw_game_field(screen)
    grid.draw(screen)
    if bubble is not None:
        bubble.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()