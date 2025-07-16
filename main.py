# main.py
import pygame
import random
from config import *
from game_logic import *
from game_view import *

pygame.init()

icon = pygame.image.load("assets/sprites/bubble_icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Aero Bubble Shooter")

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
bg_img = pygame.image.load("assets/sprites/frutiger_aero1.png").convert()
bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

#________________Game Over Popup_________________
popup_assets = load_popup_surfaces()
popup_pos = (POP_X, POP_Y)

popup_img = popup_assets["popup"]
yes_btn = Button(popup_assets["yes"], popup_assets["yes_hover"], popup_pos)
quit_btn = Button(popup_assets["quit"], popup_assets["quit_hover"], popup_pos)
cross_btn = Button(popup_assets["cross"], popup_assets["cross_hover"], popup_pos)

buttons = (yes_btn, quit_btn, cross_btn)

#________________Widget_________________
widget_assets = load_widget_surfaces()
widget_pos = (WIDGET_X, WIDGET_Y)

widget_img = widget_assets["widget"]

#___________________ helpers ____________________
def restart_game() -> None:
    """Reset full game state: grid, shooter, preview, counters."""
    global grid, bubble, next_bubble, bubble_ready, game_over
    grid = BubbleGrid()
    grid.populate_random_rows()
    bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(SHOOTER_X, SHOOTER_Y))
    next_bubble = Bubble(color=random.choice(BUBBLE_COLORS), pos=(PREVIEW_X, PREVIEW_Y))
    bubble_ready = True
    game_over = False

# ___________________ initial state ______________
restart_game()
running = True

# ___________________ main loop __________________
while running:
    # _________ event handling _________
    click_frame = False
    click_pos = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click_frame = True
            click_pos = event.pos

    # 2. INPUT SNAPSHOT _________________________________________
    mouse_pos = pygame.mouse.get_pos()
    mouse_lmb = pygame.mouse.get_pressed()[0]

    if not game_over:
        # Shoot bubble
        if (click_frame and bubble_ready and bubble.velocity.length_squared() == 0 and
            GRID_LEFT_OFFSET <= mouse_pos[0] <= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH and
            GRID_TOP_OFFSET  <= mouse_pos[1] <= GRID_TOP_OFFSET  + FIELD_HEIGHT):
            bubble.velocity = compute_velocity(bubble.pos, mouse_pos, PROJECTILE_SPEED)
            bubble_ready = False

        # Move active bubble
        if bubble is not None:
            bubble.move(clock.get_time() / 1000, grid)

            # snap to cell when it stops and add it to grid
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
        grid.update(pygame.time.get_ticks())

        # spawn a new shooter when ready
        if bubble is None and not bubble_ready:
            bubble = next_bubble
            bubble.pos = pygame.Vector2(SHOOTER_X, SHOOTER_Y)
            next_bubble = Bubble(color=random.choice(BUBBLE_COLORS),
                                 pos=(PREVIEW_X, PREVIEW_Y))
            bubble_ready = True

    else:
        # Update buttons
        for b in buttons:
            b.update(mouse_pos, mouse_lmb)

        # React to clicks
        if yes_btn.is_clicked():
            restart_game()
        elif quit_btn.is_clicked() or cross_btn.is_clicked():
            running = False

    # _________ drawing _________
    screen.blit(bg_img, (0, 0))
    screen.blit(widget_img, widget_pos)
    draw_game_field(screen)
    draw_bubble_bar(screen)
    grid.draw(screen)

    if bubble is not None:
        bubble.draw(screen)
        next_bubble.draw(screen)

    remaining_shots = max(0, grid.non_clearing_threshold - grid.non_clearing_count)
    draw_warning_bubbles(screen, remaining_shots, (PREVIEW_X, PREVIEW_Y), Bubble)
    draw_score(screen, grid.score)

    if game_over:
        screen.blit(popup_img, popup_pos)
        for btn in buttons:
            btn.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
