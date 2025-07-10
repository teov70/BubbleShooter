# game_logic.py
import pygame
from config import *
import random as rand

class Bubble:
    def __init__(self, color, pos, velocity=pygame.Vector2(0, 0), radius=BUBBLE_RADIUS):
        self.color = color
        self.radius = radius
        self.pos = pygame.Vector2(pos)       # Accepts tuple or Vector2
        self.velocity = pygame.Vector2(velocity)
        self.cell = None
        self.neighbors = {
            "left": None, "right": None,
            "top_left": None, "top_right": None,
            "bottom_left": None, "bottom_right": None,
        }

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def check_collision_with_neighbors(self, grid):
        row, col = grid.get_cell_for_position(*self.pos)
        collision_radius_sq = (2 * (self.radius-2)) ** 2

        candidates = [(row, col)]

        neighbors = grid.get_neighbor_coords(row, col)
        for _, n_row, n_col in neighbors:
            candidates.append((n_row, n_col))

        for r, c in candidates:
            if not (0 <= r < grid.rows and 0 <= c < grid.cols):
                continue
            other = grid.bubbles[r][c]
            if other is None:
                continue
            if (self.pos - other.pos).length_squared() <= collision_radius_sq:
                return True

        return False

    def move(self, delta_time, grid):
        self.pos += self.velocity * delta_time

        if self.check_collision_with_neighbors(grid):
            self.velocity = pygame.Vector2(0, 0)
            return

        if self.pos.x - self.radius <= GRID_LEFT_OFFSET or self.pos.x + self.radius >= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH:
            self.velocity.x *= -1
            # Clamp position inside the screen so it doesn't stick outside
            self.pos.x = max(self.radius + GRID_LEFT_OFFSET, min(GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH - self.radius, self.pos.x))

        if self.pos.y - self.radius <= GRID_TOP_OFFSET:
            self.velocity = pygame.Vector2(0, 0)
            self.pos.y = GRID_TOP_OFFSET + self.radius

class BubbleGrid:
    def __init__(self, cols=GRID_COLS, rows=GRID_ROWS):
        self.rows = rows
        self.cols = cols
        self.bubbles = [[None] * self.cols for _ in range(self.rows)]

        self.pop_queue: list[Bubble] = []   # bubbles waiting to pop
        self.pop_interval = 100             # ms between pops
        self.next_pop_time = 0              # timestamp of next pop
        self.pending_floater_check = False  # run floater DFS when chain gone

    def draw(self, screen):
        for row in self.bubbles:
            for bubble in row:
                if bubble is not None:
                    bubble.draw(screen)

    def remove_bubble(self, bubble):
        if not bubble.cell:
            print("⚠️ Tried to remove bubble without valid cell")
            return
        row, col = bubble.cell
        self.bubbles[row][col] = None
        bubble.cell = None

    def destroy_bubbles(self, match_chain: list[tuple[int, int]]):
        if len(match_chain) < 3:
            return

        for row, col in match_chain:
            bubble = self.bubbles[row][col]
            if bubble:
                self.pop_queue.append(bubble)

        self.next_pop_time = pygame.time.get_ticks() + self.pop_interval
        self.pending_floater_check = True

    def get_cell_for_position(self, x, y) -> tuple[int, int]:
        row = int((y - GRID_TOP_OFFSET) // ROW_HEIGHT)
        if row % 2 == 0:
            col = int((x - GRID_LEFT_OFFSET) // COL_WIDTH)
        else:
            col = int((x - GRID_LEFT_OFFSET - COL_WIDTH // 2) // COL_WIDTH)
        return row, col
    
    def get_position_for_cell(self, row: int, col: int) -> pygame.Vector2:
        y = GRID_TOP_OFFSET + (row + 0.5) * ROW_HEIGHT
        if row % 2 == 0:
            x = GRID_LEFT_OFFSET + (col + 0.5) * COL_WIDTH
        else:
            x = GRID_LEFT_OFFSET + (col + 1) * COL_WIDTH
        return pygame.Vector2(x, y)
    
    def populate_random_rows(self, num_rows=9, colors=BUBBLE_COLORS):
        for row in range(num_rows):
            for col in range(self.cols):
                pos = self.get_position_for_cell(row, col)
                color = rand.choice(colors)
                bubble = Bubble(color, pos)
                self.add_bubble(bubble)
    
    def get_neighbor_coords(self, row, col):
        if row % 2 == 0:
            directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
            names = ["top_left", "top_right", "left", "right", "bottom_left", "bottom_right"]
        else:
            directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
            names = ["top_left", "top_right", "left", "right", "bottom_left", "bottom_right"]

        result = []
        for (dr, dc), name in zip(directions, names):
            n_row, n_col = row + dr, col + dc
            if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                result.append((name, n_row, n_col))
        return result
    
    def find_closest_valid_cell(self, target_pos, candidate_cells):
        closest_cell = None
        min_dist_sq = float('inf')

        for row, col in candidate_cells:
            if not (0 <= row < self.rows and 0 <= col < self.cols):
                continue
            if self.bubbles[row][col] is not None:
                continue

            cell_pos = self.get_position_for_cell(row, col)
            dist_sq = (target_pos - cell_pos).length_squared()

            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                closest_cell = (row, col)

        return closest_cell
    
    def get_snap_cell(self, row: int, col: int, target_pos: pygame.Vector2) -> tuple[int, int] | None:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return None  # bubble stopped outside grid → game over

        if self.bubbles[row][col] is None:
            return (row, col)

        neighbors = [(r, c) for _, r, c in self.get_neighbor_coords(row, col)]
        return self.find_closest_valid_cell(target_pos, neighbors)
    
    def snap_bubble_to_grid(self, bubble, hit_row=None, hit_col=None):
        if hit_row is not None and hit_col is not None:    
            neighbors = []
            for _, row, col in self.get_neighbor_coords(hit_row, hit_col):
                neighbors.append((row, col))

            closest_cell = self.find_closest_valid_cell(bubble.pos, neighbors)
            if closest_cell is None:
                print(f"⚠️ No valid cell found for bubble at {bubble.pos}")
                return False #Game Over
            
        else:
            closest_cell = self.get_cell_for_position(*bubble.pos)
            if not (0 <= closest_cell[0] < self.rows and 0 <= closest_cell[1] < self.cols):
                return False  # Out-of-bounds = game over or invalid

        bubble.pos = self.get_position_for_cell(*closest_cell)
        self.add_bubble(bubble)
        return True

    def add_bubble(self, bubble):
        row, col = self.get_cell_for_position(*bubble.pos)

        if not (0 <= row < self.rows and 0 <= col < self.cols):
            print(f"⚠️ Ignoring out-of-bounds snap at row={row}, col={col}")
            return
        if 0 <= col < self.cols and 0 <= row < self.rows:
            bubble.pos = self.get_position_for_cell(row, col)
            bubble.cell = (row, col)
            self.bubbles[row][col] = bubble

        neighbors = self.get_neighbor_coords(row, col)
        for direction, n_row, n_col in neighbors:
            neighbor = self.bubbles[n_row][n_col]
            if neighbor:
                bubble.neighbors[direction] = neighbor
                reverse_direction = {
                    "left": "right",
                    "right": "left",
                    "top_left": "bottom_right",
                    "top_right": "bottom_left",
                    "bottom_left": "top_right",
                    "bottom_right": "top_left"
                }[direction]
                neighbor.neighbors[reverse_direction] = bubble

        print(f"Added bubble at ({row}, {col})")
        for k, v in bubble.neighbors.items():
            if v:
                print(f" - {k}: neighbor exists")

    def get_connected_same_color(self, start_row, start_col):
        """Recursive function using DFS to find all connected bubbles of the same color."""
        visited = set()
        result = []

        def dfs(row, col, target_color):
            if (row, col) in visited:
                return
            visited.add((row, col))

            bubble = self.bubbles[row][col]
            if not bubble or bubble.color != target_color:
                return

            result.append((row, col))

            for _, n_row, n_col in self.get_neighbor_coords(row, col):
                if 0 <= n_row < self.rows and 0 <= n_col < self.cols:
                    dfs(n_row, n_col, target_color)

        start_bubble = self.bubbles[start_row][start_col]
        if start_bubble:
            dfs(start_row, start_col, start_bubble.color)

        return result
    
    def enqueue_floating_bubbles(self):
        """Find bubbles not connected to the top row and enqueue them for destruction."""
        visited: set[tuple[int, int]] = set()

        # mark all bubbles reachable from the top row
        def dfs(row, col):
            if (row, col) in visited:
                return
            visited.add((row, col))
            for _, r2, c2 in self.get_neighbor_coords(row, col):
                if self.bubbles[r2][c2]:
                    dfs(r2, c2)

        # start DFS from every occupied top-row cell
        for col in range(self.cols):
            if self.bubbles[0][col]:
                dfs(0, col)

        # enqueue floaters (scan bottom-up for nicer effect)
        for r in reversed(range(self.rows)):
            for c in range(self.cols):
                bub = self.bubbles[r][c]
                if bub and (r, c) not in visited:
                    self.pop_queue.append(bub)

    def update(self, now):
        # pop animation
        while self.pop_queue and now >= self.next_pop_time:
            bubble = self.pop_queue.pop(0)
            self.remove_bubble(bubble)
            self.next_pop_time += self.pop_interval

        # when chain finished and floaters still pending
        if self.pending_floater_check and not self.pop_queue:
            self.enqueue_floating_bubbles()
            self.pending_floater_check = False
            if self.pop_queue:                 # floaters found
                self.next_pop_time = now + self.pop_interval

def compute_velocity(start_pos, target_pos, speed):
    direction = pygame.Vector2(target_pos) - pygame.Vector2(start_pos)
    if direction.length() == 0:
        return pygame.Vector2(0, 0)
    return direction.normalize() * speed