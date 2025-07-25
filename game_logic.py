# game_logic.py
import pygame
from config import *
from game_view import *
import random as rand

BUBBLE_SURFACES: dict = {}

class Bubble:
    def __init__(self, color, pos, velocity=pygame.Vector2(0, 0), radius=BUBBLE_RADIUS):
        self.color = color
        self.radius = radius
        self.pos = pygame.Vector2(pos)       # Accepts tuple or Vector2
        self.velocity = pygame.Vector2(velocity)
        self.cell = None
        self.neighbors = {direction : None for direction in DIRECTIONS}
       
    def draw(self, screen):
        global BUBBLE_SURFACES
        if not BUBBLE_SURFACES:
            BUBBLE_SURFACES = load_bubble_surfaces(BUBBLE_COLOR_PAIRS)

        img = BUBBLE_SURFACES[self.color]
        rect = img.get_rect(center=self.pos)
        screen.blit(img, rect)

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
    
    def first_colliding_cell(self, grid):
        row, col = grid.get_cell_for_position(*self.pos)
        for _, r, c in grid.get_neighbor_coords(row, col):
            other = grid.bubbles[r][c]
            if other and (self.pos - other.pos).length_squared() <= (2*(self.radius-2))**2:
                return r, c
        return row, col   

    def move(self, delta_time, grid):
        self.pos += self.velocity * delta_time

        if self.check_collision_with_neighbors(grid):
            self.pos -= self.velocity * delta_time
            self.velocity = pygame.Vector2(0, 0)
            self.hit_cell = self.first_colliding_cell(grid)
            return

        if self.pos.x - self.radius <= GRID_LEFT_OFFSET or self.pos.x + self.radius >= GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH:
            self.velocity.x *= -1
            # Clamp position inside the screen so it doesn't stick outside
            self.pos.x = max(self.radius + GRID_LEFT_OFFSET, min(GRID_LEFT_OFFSET + FIELD_DRAW_WIDTH - self.radius, self.pos.x))

        if self.pos.y - self.radius <= GRID_TOP_OFFSET:
            self.velocity = pygame.Vector2(0, 0)
            self.pos.y = GRID_TOP_OFFSET + ROW_HEIGHT//2

class BubbleGrid:
    def __init__(self, audio, cols=GRID_COLS, rows=GRID_ROWS):
        self.audio = audio
        self.rows = rows
        self.cols = cols
        self.bubbles = [[None] * self.cols for _ in range(self.rows)]

        self.pop_queue: list[Bubble] = []   # bubbles waiting to pop
        self.pop_interval = 100             # ms between pops
        self.next_pop_time = 0              # timestamp of next pop
        self.pending_floater_check = False  # run floater DFS when chain gone
        self.non_clearing_count = 0      # shots since last auto-row
        self.non_clearing_threshold  = 6
        self.score = 0      # total points
        self._floaters_scoring = False   # flag: next enqueue_floating_bubbles gives points
        self.row_offset = False

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

        for direction, neighbor in bubble.neighbors.items():
            if neighbor:
                neighbor.neighbors[REVERSE_DIR[direction]] = None
        bubble.neighbors = {k: None for k in bubble.neighbors}
        self.bubbles[row][col] = None
        bubble.cell = None

    def destroy_bubbles(self, match_chain: list[tuple[int, int]]):
        if len(match_chain) < 3:
            self.audio.play_plop()
            return self.register_non_clearing_shot()
        
        n = len(match_chain)
        # chain scoring: 30 for first 3, then 20, 40, 80, ...
        if n == 3:
            chain_pts = 30
        else:
            chain_pts = 30 + 20 * ((2 ** (n - 3)) - 1)
        self.score += chain_pts

        for row, col in match_chain:
            bubble = self.bubbles[row][col]
            if bubble:
                self.pop_queue.append(bubble)

        self.next_pop_time = pygame.time.get_ticks() + self.pop_interval
        self.pending_floater_check = True
        self._floaters_scoring = True
        return True
    
    def is_flush_left(self, row: int) -> bool:
        return (row % 2 == 0) != self.row_offset

    def get_cell_for_position(self, x, y) -> tuple[int, int]:
        row = int((y - GRID_TOP_OFFSET) // ROW_HEIGHT)
        if self.is_flush_left(row):
            col = int((x - GRID_LEFT_OFFSET) // COL_WIDTH)
        else:
            col = int((x - GRID_LEFT_OFFSET - COL_WIDTH // 2) // COL_WIDTH)
        col = max(0, min(self.cols - 1, col))
        return row, col
    
    def get_position_for_cell(self, row: int, col: int) -> pygame.Vector2:
        y = GRID_TOP_OFFSET + (row + 0.5) * ROW_HEIGHT
        if self.is_flush_left(row):
            x = GRID_LEFT_OFFSET + (col + 0.5) * COL_WIDTH
        else:
            x = GRID_LEFT_OFFSET + (col + 1) * COL_WIDTH
        return pygame.Vector2(x, y)
    
    def populate_random_rows(self, num_rows=STARTING_ROWS, colors=BUBBLE_COLORS):
        for row in range(num_rows):
            for col in range(self.cols):
                pos = self.get_position_for_cell(row, col)
                color = rand.choice(colors)
                bubble = Bubble(color, pos)
                self.add_bubble(bubble)
    
    def get_neighbor_coords(self, row, col):
        if self.is_flush_left(row):
            dir_vectors = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
        else:
            dir_vectors = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
            
        result = []
        for (dr, dc), name in zip(dir_vectors, DIRECTIONS):
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
    
    def snap_bubble_to_grid(self, bubble, hit_row=None, hit_col=None):
        if hit_row is None or hit_col is None:
            anchor_row, anchor_col = self.get_cell_for_position(*bubble.pos)
        else:
            anchor_row, anchor_col = hit_row, hit_col

        if not (0 <= anchor_row < self.rows and 0 <= anchor_col < self.cols):
            return None
        
        candidates = [(anchor_row, anchor_col)]
        candidates += [(r, c) for _, r, c
                    in self.get_neighbor_coords(anchor_row, anchor_col)]
        
        self._debug_snap_info(anchor_row, anchor_col, bubble.pos)

        target = self.find_closest_valid_cell(bubble.pos, candidates)
        if target is None:
            return None

        bubble.pos = self.get_position_for_cell(*target)
        self.add_bubble(bubble)
        return target

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
                reverse_dir = REVERSE_DIR[direction]
                neighbor.neighbors[reverse_dir] = bubble
        DEBUG = False
        if DEBUG:
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
                    if self._floaters_scoring:
                        self.score += 100
                    self.pop_queue.append(bub)
        self._floaters_scoring = False

    def add_row_to_top(self):
        for col in range(self.cols):
            if self.bubbles[self.rows-1][col] is not None:
                return False
        # Shift all existing rows down by 1
        for row in reversed(range(self.rows - 1)):
            for col in range(self.cols):
                self.bubbles[row + 1][col] = self.bubbles[row][col]
                if self.bubbles[row + 1][col]:
                    self.bubbles[row + 1][col].cell = (row + 1, col)
        
        # Insert a new random row at the top (row 0)
        for col in range(self.cols):
            color = rand.choice(BUBBLE_COLORS)
            new_bubble = Bubble(color, pos = self.get_position_for_cell(0, col))
            self.bubbles[0][col] = new_bubble

        # After insertion, relink neighbors
        self.row_offset = not self.row_offset
        self.update_all_bubbles()
        return True
    
    def register_non_clearing_shot(self) -> bool:
        """Increments count; adds row if threshold reached.
        Lowers threshold after each addition, cycles back to 6 after hitting 2.
        Returns False if row addition causes game over."""
        self.non_clearing_count += 1

        if self.non_clearing_count >= self.non_clearing_threshold:
            self.non_clearing_count = 0

            if not self.add_row_to_top():
                return False  # game over due to overflow

            # cycle threshold down to 2, then reset back to 6
            if self.non_clearing_threshold > 2:
                self.non_clearing_threshold -= 1
            else:
                self.non_clearing_threshold = 6

        return True

    def update(self, now):
        # pop animation and pop sound
        while self.pop_queue and now >= self.next_pop_time:
            bubble = self.pop_queue.pop(0)
            self.remove_bubble(bubble)
            self.audio.play_pop()
            self.next_pop_time += self.pop_interval

        # when chain finished and floaters still pending
        if self.pending_floater_check and not self.pop_queue:
            self.enqueue_floating_bubbles()
            self.pending_floater_check = False
            if self.pop_queue:                 # floaters found
                self.next_pop_time = now + self.pop_interval

    def update_all_bubbles(self):
        for row in range(self.rows):
            for col in range(self.cols):
                bubble = self.bubbles[row][col]
                if bubble:
                    bubble.cell = (row, col)
                    bubble.pos = self.get_position_for_cell(row, col)
                    bubble.neighbors = {k: None for k in bubble.neighbors}
                    neighbors = self.get_neighbor_coords(row, col)
                    for direction, n_row, n_col in neighbors:
                        neighbor = self.bubbles[n_row][n_col]
                        if neighbor:
                            bubble.neighbors[direction] = neighbor

    def _debug_snap_info(self, anchor_row, anchor_col,
                         bubble_pos, DEBUG_SNAP = False):
        """Console dump of neighbour cells and centre-to-centre distance."""
        if not DEBUG_SNAP:
            return

        print(f"\n[DBG] anchor ({anchor_row},{anchor_col})"
            f"  bubble-stop @ {bubble_pos}")

        for name, r, c in self.get_neighbor_coords(anchor_row, anchor_col):
            centre = self.get_position_for_cell(r, c)
            dist   = (centre - bubble_pos).length()
            occ    = "OCC" if self.bubbles[r][c] else "   "
            print(f"  {name:<13} cell=({r:2},{c:2})  {occ}  dist={dist:6.1f}")

def compute_velocity(start_pos, target_pos, speed):
    direction = pygame.Vector2(target_pos) - pygame.Vector2(start_pos)
    if direction.length() == 0:
        return pygame.Vector2(0, 0)
    return direction.normalize() * speed