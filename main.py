# main.py
import pygame
from config import *
from game_logic import *
from game_view import *
import random

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

bubble = Bubble(
    color=random.choice(BUBBLE_COLORS),
    pos=(SHOOTER_X, SHOOTER_Y)
)

grid = BubbleGrid()
bubble_ready = True  # This means: shooter bubble is available

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BG_COLOR)
    draw_game_field(screen)
    grid.draw(screen)

    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and bubble.velocity.length_squared() == 0 and bubble_ready:
        mouse_pos = pygame.mouse.get_pos()
        # Check if the mouse is within the game field
        if (GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
            GRID_TOP_OFFSET <= mouse_pos[1] <= GRID_TOP_OFFSET + FIELD_HEIGHT):
            # Compute the velocity towards the mouse position
            bubble.velocity = compute_velocity(bubble.pos, mouse_pos, PROJECTILE_SPEED)
            bubble_ready = False

    if bubble is not None:
        bubble.move(clock.get_time() / 1000, grid)  # Move bubble based on delta time
        bubble.draw(screen)

        if bubble.velocity.length_squared() == 0 and not bubble_ready:
            row, col = grid.get_cell_for_position(*bubble.pos)
            snap_cell = grid.get_snap_cell(row, col, bubble.pos)
            if snap_cell is None:
                print("❌ Game Over - no valid snap position")
                running = False
                bubble = None
                bubble_ready = False
                continue

            bubble.pos = grid.get_position_for_cell(*snap_cell)
            grid.add_bubble(bubble)
            bubble = None
            bubble_ready = False

    if bubble is None and not bubble_ready:
        bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(SHOOTER_X, SHOOTER_Y))
        bubble_ready = True

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()