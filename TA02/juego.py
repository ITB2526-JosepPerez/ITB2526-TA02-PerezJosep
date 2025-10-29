# python
"""
Tetris-like game using pygame.

Save as: `TA02/tetris_pygame.py`
Run: python3 TA02/tetris_pygame.py
Requires: pygame (pip install pygame)
"""

import os
import sys
import random
import time

try:
    import pygame
    from pygame import Rect
except Exception:
    print("This game requires pygame. Install with: pip install pygame")
    sys.exit(1)

# --- Configuration ---
CELL = 28
COLUMNS = 10
ROWS = 20
W = COLUMNS * CELL
H = ROWS * CELL
SIDE_PANEL = 180
WIN_W = W + SIDE_PANEL + 40
WIN_H = H + 40
FPS = 60

# Shapes defined in 4x4 blocks for easier rotation
SHAPES = {
    'I': [
        [[0,0,0,0],
         [1,1,1,1],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'J': [
        [[1,0,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'L': [
        [[0,0,1,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'O': [
        [[0,1,1,0],
         [0,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'S': [
        [[0,1,1,0],
         [1,1,0,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'T': [
        [[0,1,0,0],
         [1,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
    'Z': [
        [[1,1,0,0],
         [0,1,1,0],
         [0,0,0,0],
         [0,0,0,0]],
    ],
}

COLORS = {
    'I': (80, 200, 240),
    'J': (40, 80, 200),
    'L': (240, 160, 40),
    'O': (240, 220, 60),
    'S': (80, 220, 100),
    'T': (160, 60, 200),
    'Z': (220, 60, 60),
    0: (18, 18, 18),
    -1: (90, 90, 90)
}

# --- Utilities ---
def rotate_matrix(mat):
    return [list(row) for row in zip(*mat[::-1])]

def random_piece_kind():
    return random.choice(list(SHAPES.keys()))

# --- Classes (Board, Piece, Game) ---
class Piece:
    def __init__(self, kind=None):
        self.kind = kind or random_piece_kind()
        # start with base 4x4 matrix copy
        self.matrix = [row[:] for row in SHAPES[self.kind][0]]
        self.x = COLUMNS // 2 - 2  # grid coordinates (top-left of 4x4)
        self.y = -1  # start slightly above visible
        self.color = COLORS[self.kind]

    def cells(self):
        result = []
        for r, row in enumerate(self.matrix):
            for c, v in enumerate(row):
                if v:
                    result.append((self.x + c, self.y + r))
        return result

    def rotate(self):
        self.matrix = rotate_matrix(self.matrix)

    def clone_rotated(self):
        new = Piece(self.kind)
        new.matrix = rotate_matrix(self.matrix)
        new.x = self.x
        new.y = self.y
        new.color = self.color
        return new

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(COLUMNS)] for _ in range(ROWS)]

    def inside(self, x, y):
        return 0 <= x < COLUMNS and y < ROWS

    def cell(self, x, y):
        if y < 0:
            return 0
        return self.grid[y][x]

    def can_place(self, piece, ox=0, oy=0):
        for x, y in piece.cells():
            tx = x + ox
            ty = y + oy
            if ty < 0:
                continue
            if not self.inside(tx, ty):
                return False
            if self.grid[ty][tx]:
                return False
        return True

    def lock(self, piece):
        for x, y in piece.cells():
            if 0 <= y < ROWS and 0 <= x < COLUMNS:
                self.grid[y][x] = piece.kind
        lines = self.clear_lines()
        return lines

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        lines_cleared = ROWS - len(new_grid)
        for _ in range(lines_cleared):
            new_grid.insert(0, [0 for _ in range(COLUMNS)])
        self.grid = new_grid
        return lines_cleared

    def is_game_over(self):
        # any occupied cell in top row -> game over
        return any(self.grid[0])

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Tetris - Pygame")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 36, bold=True)

        self.board = Board()
        self.piece = Piece()
        self.next_piece = Piece()
        self.score = 0
        self.level = 1
        self.lines = 0
        self.drop_interval = 0.7  # seconds per step
        self.last_drop = time.time()
        self.game_over = False
        self.paused = False

    def spawn_piece(self):
        self.piece = self.next_piece
        self.next_piece = Piece()
        self.piece.x = COLUMNS // 2 - 2
        self.piece.y = -1
        if not self.board.can_place(self.piece):
            self.game_over = True

    def soft_drop(self):
        if self.board.can_place(self.piece, oy=1):
            self.piece.y += 1
            self.score += 1  # small soft-drop reward
            return True
        return False

    def hard_drop(self):
        dist = 0
        while self.board.can_place(self.piece, oy=1):
            self.piece.y += 1
            dist += 1
        self.score += dist * 2
        lines = self.board.lock(self.piece)
        self.on_lines_cleared(lines)
        self.spawn_piece()

    def rotate_piece(self):
        rotated = self.piece.clone_rotated()
        # simple wall-kick attempts
        kicks = [(0,0), (-1,0), (1,0), (-2,0), (2,0), (0,-1)]
        for dx, dy in kicks:
            rotated.x = self.piece.x + dx
            rotated.y = self.piece.y + dy
            if self.board.can_place(rotated):
                self.piece.matrix = rotated.matrix
                self.piece.x = rotated.x
                self.piece.y = rotated.y
                return

    def move_piece(self, dx):
        if self.board.can_place(self.piece, ox=dx):
            self.piece.x += dx

    def tick(self):
        if self.paused or self.game_over:
            return
        now = time.time()
        if now - self.last_drop >= self.drop_interval:
            self.last_drop = now
            if self.board.can_place(self.piece, oy=1):
                self.piece.y += 1
            else:
                lines = self.board.lock(self.piece)
                self.on_lines_cleared(lines)
                self.spawn_piece()

    def on_lines_cleared(self, lines):
        if lines == 0:
            return
        # scoring similar to classic tetris
        if lines == 1:
            self.score += 100
        elif lines == 2:
            self.score += 300
        elif lines == 3:
            self.score += 500
        elif lines >= 4:
            self.score += 800 * (lines - 3)
        self.lines += lines
        # level up every 10 lines
        self.level = 1 + self.lines // 10
        # speed increases slightly with level
        self.drop_interval = max(0.1, 0.7 - (self.level - 1) * 0.06)

    def draw_grid(self):
        # board background
        bx = 20
        by = 20
        pygame.draw.rect(self.screen, (10, 10, 10), Rect(bx-4, by-4, W+8, H+8))
        for r in range(ROWS):
            for c in range(COLUMNS):
                cell = self.board.grid[r][c]
                color = COLORS[cell] if cell else (30,30,30)
                rect = Rect(bx + c*CELL, by + r*CELL, CELL-1, CELL-1)
                pygame.draw.rect(self.screen, color, rect)
        # draw current piece
        for x, y in self.piece.cells():
            if y >= 0:
                rect = Rect(bx + x*CELL, by + y*CELL, CELL-1, CELL-1)
                pygame.draw.rect(self.screen, self.piece.color, rect)

        # grid lines
        for gx in range(COLUMNS+1):
            pygame.draw.line(self.screen, (15,15,15), (bx + gx*CELL, by), (bx + gx*CELL, by + H))
        for gy in range(ROWS+1):
            pygame.draw.line(self.screen, (15,15,15), (bx, by + gy*CELL), (bx + W, by + gy*CELL))

        # side panel
        sx = bx + W + 20
        sy = by
        pygame.draw.rect(self.screen, (22,22,22), Rect(sx, sy, SIDE_PANEL, H))
        # Next piece
        self.draw_next_piece(sx + 20, sy + 20)
        # score, level, lines
        self._draw_text(f"Score: {self.score}", sx + 20, sy + 160)
        self._draw_text(f"Level: {self.level}", sx + 20, sy + 190)
        self._draw_text(f"Lines: {self.lines}", sx + 20, sy + 220)

        # controls
        self._draw_text("Controls:", sx + 20, sy + 270)
        controls = ["Arrows: move", "Up/W: rotate", "Down: soft drop", "Space: hard drop", "P: pause", "Q: quit"]
        for i, t in enumerate(controls):
            self._draw_text(t, sx + 20, sy + 300 + i*22, size=18, color=(200,200,200))

        if self.paused:
            self._draw_centered("PAUSED")
        if self.game_over:
            self._draw_centered("GAME OVER")

    def draw_next_piece(self, x, y):
        self._draw_text("Next:", x, y - 24)
        for r, row in enumerate(self.next_piece.matrix):
            for c, v in enumerate(row):
                if v:
                    rect = Rect(x + c*CELL, y + r*CELL, CELL-2, CELL-2)
                    pygame.draw.rect(self.screen, self.next_piece.color, rect)

    def _draw_text(self, text, x, y, size=20, color=(230,230,230)):
        font = pygame.font.SysFont(None, size)
        surf = font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def _draw_centered(self, text):
        surf = self.big_font.render(text, True, (230,80,80))
        self.screen.blit(surf, ( (WIN_W - surf.get_width())//2, 30 ))

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.stop()
            elif ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_q, pygame.K_ESCAPE):
                    self.stop()
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    self.move_piece(-1)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    self.move_piece(1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    self.soft_drop()
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    self.rotate_piece()
                elif ev.key == pygame.K_SPACE:
                    self.hard_drop()
                elif ev.key == pygame.K_p:
                    self.paused = not self.paused

    def stop(self):
        pygame.quit()
        sys.exit(0)

    def run(self):
        # initial spawn
        self.spawn_piece()
        self.last_drop = time.time()
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.handle_events()
            self.tick()
            # draw
            self.screen.fill((8, 8, 12))
            self.draw_grid()
            pygame.display.flip()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
