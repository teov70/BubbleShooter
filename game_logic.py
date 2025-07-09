import pygame
from config import *

class Bubble:
    def __init__(self, color, pos, velocity=pygame.Vector2(0, 0), radius=BUBBLE_RADIUS):
        self.color = color
        self.radius = radius
        self.pos = pygame.Vector2(pos)       # Accepts tuple or Vector2
        self.velocity = pygame.Vector2(velocity)
        self.neighbors = {
            "left": None,
            "right": None,
            "top_left": None,
            "top_right": None,
            "bottom_left": None,
            "bottom_right": None,
        }


    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def move(self, delta_time):
        self.pos += self.velocity * delta_time

        if self.pos.x - self.radius <= GRID_LEFT_OFFSET or self.pos.x + self.radius >= GRID_LEFT_OFFSET + FIELD_WIDTH:
            self.velocity.x *= -1
            # Clamp position inside the screen so it doesn't stick outside
            self.pos.x = max(self.radius + GRID_LEFT_OFFSET, min(GRID_LEFT_OFFSET + FIELD_WIDTH - self.radius, self.pos.x))

        if self.pos.y - self.radius <= GRID_TOP_OFFSET:
            self.velocity = pygame.Vector2(0, 0)
            self.pos.y = GRID_TOP_OFFSET + self.radius

class BubbleGrid:
    def __init__(self, cols=GRID_COLS, rows=GRID_ROWS):
        self.cols = cols
        self.rows = rows
        self.bubbles = [[None] * self.cols for _ in range(self.rows)]

    def get_cell_for_position(self, x, y) -> tuple[int, int]:
        row = int((y - GRID_TOP_OFFSET)// ROW_HEIGHT)
        if row%2 == 0:
            col = int((x - GRID_LEFT_OFFSET) // COL_WIDTH)
        else:
            col = int((x - GRID_LEFT_OFFSET - COL_WIDTH // 2) // COL_WIDTH)

        return row, col
    
    def get_position_for_cell(self, row: int, col: int) -> pygame.Vector2:
        y = GRID_TOP_OFFSET + (row + 0.5) * ROW_HEIGHT
        if row % 2 == 0:
            x = GRID_LEFT_OFFSET + (col + 0.5) * COL_WIDTH
        else:
            x = GRID_LEFT_OFFSET + (col + 1) * COL_WIDTH + COL_WIDTH // 2
        return pygame.Vector2(x, y)

    def add_bubble(self, bubble):
        row, col = self.get_cell_for_position(*bubble.pos)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            bubble.pos = self.get_position_for_cell(row, col)
            self.bubbles[row][col] = bubble

    def draw(self, screen):
        for row in self.bubbles:
            for bubble in row:
                if bubble is not None:
                    bubble.draw(screen)

def compute_velocity(start_pos, target_pos, speed):
    direction = pygame.Vector2(target_pos) - pygame.Vector2(start_pos)
    if direction.length() == 0:
        return pygame.Vector2(0, 0)
    return direction.normalize() * speed