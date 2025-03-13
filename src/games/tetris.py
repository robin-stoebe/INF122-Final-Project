import pygame
import random
import sys
from typing import List, Tuple, Optional

from src.engines.game import Game
from src.engines.player import Player
from src.engines.board import Board  # Optionally used if you want to unify boards

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_SIZE = 30
FPS = 60
DROP_INTERVAL = 0.5   # seconds per gravity drop

TETROMINO_SHAPES = {
    'I': [(0, 1), (1, 1), (2, 1), (3, 1)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T': [(0, 1), (1, 1), (2, 1), (1, 0)],
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],
    'J': [(0, 0), (0, 1), (1, 1), (2, 1)],
    'L': [(2, 0), (0, 1), (1, 1), (2, 1)]
}

SHAPE_COLORS = {
    'I': (0, 255, 255),
    'O': (255, 255, 0),
    'T': (128, 0, 128),
    'S': (0, 255, 0),
    'Z': (255, 0, 0),
    'J': (0, 0, 255),
    'L': (255, 165, 0)
}

# TETRIS PIECE CLASS
class TetrisPiece:
    """Represents a single falling Tetrimino with shape, position, and orientation."""
    def __init__(self, shape: str, x: int, y: int):
        self.shape = shape
        self.blocks = TETROMINO_SHAPES[shape]
        self.x = x
        self.y = y
        self.orientation = 0  # 0,1,2,3

    def get_block_positions(self) -> List[Tuple[int, int]]:
        """Returns a list of (x, y) positions on the board for each block."""
        rotated = self._rotate_blocks(self.blocks, self.orientation)
        return [(self.x + dx, self.y + dy) for (dx, dy) in rotated]

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    def rotate(self):
        """Rotate piece clockwise by 90° (simple approach, no wall kicks)."""
        self.orientation = (self.orientation + 1) % 4

    def _rotate_blocks(self, blocks, orientation: int) -> List[Tuple[int, int]]:
        """Rotate coordinates in 90° increments."""
        if orientation == 0:
            return blocks
        elif orientation == 1:
            # (x, y) -> (y, -x)
            return [(b[1], -b[0]) for b in blocks]
        elif orientation == 2:
            # (x, y) -> (-x, -y)
            return [(-b[0], -b[1]) for b in blocks]
        elif orientation == 3:
            # (x, y) -> (-y, x)
            return [(-b[1], b[0]) for b in blocks]
        return blocks

class TetrisGame(Game):
    """
    A real-time Tetris game with two separate boards side-by-side in a single Pygame window.
    Player 1 uses WASD (and space to hard drop), Player 2 uses arrow keys (and RCtrl to hard drop).
    """

    def __init__(self, board: Board, player1: Player, player2: Player):
        super().__init__(board, player1, player2)
        pygame.init()
        self.clock = pygame.time.Clock()

        # Each board is 2D array: board[y][x] = shape or None
        self.board1 = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.board2 = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        # Window width is 2 boards + a small gap
        self.screen_width = BOARD_WIDTH * BLOCK_SIZE * 2 + 60
        self.screen_height = BOARD_HEIGHT * BLOCK_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Two-Player Tetris")

        # Game states
        self.game_over1 = False
        self.game_over2 = False
        self.running = True

        # Active pieces
        self.active_piece1: Optional[TetrisPiece] = None
        self.active_piece2: Optional[TetrisPiece] = None

        # Drop timers
        self.drop_timer1 = 0.0
        self.drop_timer2 = 0.0
        self.drop_interval1 = DROP_INTERVAL
        self.drop_interval2 = DROP_INTERVAL

    def initialize_board(self):
        self.spawn_piece1()
        self.spawn_piece2()

    def update_board(self):
        dt = self.clock.tick(FPS) / 1000.0
        # Player 1 gravity
        if not self.game_over1 and self.active_piece1:
            self.drop_timer1 += dt
            if self.drop_timer1 >= self.drop_interval1:
                self.drop_timer1 = 0.0
                self.active_piece1.y += 1
                if self.check_collision(self.active_piece1, self.board1):
                    self.active_piece1.y -= 1
                    self.lock_piece(self.active_piece1, self.board1, player=1)

        # Player 2 gravity
        if not self.game_over2 and self.active_piece2:
            self.drop_timer2 += dt
            if self.drop_timer2 >= self.drop_interval2:
                self.drop_timer2 = 0.0
                self.active_piece2.y += 1
                if self.check_collision(self.active_piece2, self.board2):
                    self.active_piece2.y -= 1
                    self.lock_piece(self.active_piece2, self.board2, player=2)

        # If both players are game over, end the match
        if self.game_over1 and self.game_over2:
            self.running = False

        self.render()

    def check_win_condition(self):
        """Check if both players are done or if the game was closed."""
        return (self.game_over1 and self.game_over2) or (not self.running)

    def handle_player_input(self, player, action):
        if player == 1 and not self.game_over1 and self.active_piece1:
            self._handle_player1_action(action)
        elif player == 2 and not self.game_over2 and self.active_piece2:
            self._handle_player2_action(action)

    def gameLoop(self):
        while not self.check_win_condition():
            self.handle_events()
            self.update_board()  # includes gravity & rendering

        pygame.quit()

    # Real-time event handling
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                # Player 1
                if not self.game_over1 and self.active_piece1:
                    self._handle_player1_keys(event.key)
                # Player 2
                if not self.game_over2 and self.active_piece2:
                    self._handle_player2_keys(event.key)

    def _handle_player1_keys(self, key):
        if key == pygame.K_a:  # left
            self.active_piece1.x -= 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.x += 1
        elif key == pygame.K_d:  # right
            self.active_piece1.x += 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.x -= 1
        elif key == pygame.K_w:  # rotate
            old_orientation = self.active_piece1.orientation
            self.active_piece1.rotate()
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.orientation = old_orientation
        elif key == pygame.K_s:  # soft drop
            self.active_piece1.y += 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.y -= 1
                self.lock_piece(self.active_piece1, self.board1, player=1)
        elif key == pygame.K_SPACE:  # hard drop
            while not self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.y += 1
            self.active_piece1.y -= 1
            self.lock_piece(self.active_piece1, self.board1, player=1)

    def _handle_player2_keys(self, key):
        if key == pygame.K_LEFT:
            self.active_piece2.x -= 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.x += 1
        elif key == pygame.K_RIGHT:
            self.active_piece2.x += 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.x -= 1
        elif key == pygame.K_UP:
            old_orientation = self.active_piece2.orientation
            self.active_piece2.rotate()
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.orientation = old_orientation
        elif key == pygame.K_DOWN:
            self.active_piece2.y += 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.y -= 1
                self.lock_piece(self.active_piece2, self.board2, player=2)
        elif key == pygame.K_RCTRL:  # hard drop
            while not self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.y += 1
            self.active_piece2.y -= 1
            self.lock_piece(self.active_piece2, self.board2, player=2)

    # Collision / Lock / Clear
    def check_collision(self, piece: TetrisPiece, board: List[List[Optional[str]]]) -> bool:
        for (bx, by) in piece.get_block_positions():
            if bx < 0 or bx >= BOARD_WIDTH or by < 0 or by >= BOARD_HEIGHT:
                return True
            if board[by][bx] is not None:
                return True
        return False

    def lock_piece(self, piece: TetrisPiece, board: List[List[Optional[str]]], player: int):
        """Place piece into board array, clear lines, spawn new piece."""
        for (bx, by) in piece.get_block_positions():
            board[by][bx] = piece.shape
        self.clear_lines(board, player)

        if player == 1:
            self.spawn_piece1()
            if self.check_collision(self.active_piece1, self.board1):
                self.game_over1 = True
        else:
            self.spawn_piece2()
            if self.check_collision(self.active_piece2, self.board2):
                self.game_over2 = True

    def clear_lines(self, board: List[List[Optional[str]]], player: int):
        lines_cleared = 0
        for row in range(BOARD_HEIGHT):
            if all(board[row][col] is not None for col in range(BOARD_WIDTH)):
                lines_cleared += 1
                for r in range(row, 0, -1):
                    board[r] = board[r - 1][:]
                board[0] = [None for _ in range(BOARD_WIDTH)]

        # Update the parent player's score
        if lines_cleared > 0:
            points = lines_cleared * 100
            if player == 1:
                self.player1.updateScore(points)
            else:
                self.player2.updateScore(points)

    # SPAWN PIECES
    def spawn_piece1(self):
        shape = random.choice(list(TETROMINO_SHAPES.keys()))
        self.active_piece1 = TetrisPiece(shape, BOARD_WIDTH // 2 - 2, 0)

    def spawn_piece2(self):
        shape = random.choice(list(TETROMINO_SHAPES.keys()))
        self.active_piece2 = TetrisPiece(shape, BOARD_WIDTH // 2 - 2, 0)

    # RENDER
    def render(self):
        self.screen.fill((255, 255, 255))

        # Render board1
        self._draw_board(self.board1, offset_x=0, offset_y=0)
        # Render board2
        self._draw_board(self.board2, offset_x=(BOARD_WIDTH * BLOCK_SIZE + 60), offset_y=0)

        # Active pieces
        if self.active_piece1 and not self.game_over1:
            self._draw_piece(self.active_piece1, offset_x=0)
        if self.active_piece2 and not self.game_over2:
            self._draw_piece(self.active_piece2, offset_x=(BOARD_WIDTH * BLOCK_SIZE + 60))

        # Player names, scores, game over states
        self._draw_text(f"{self.player1.name} Score: {self.player1.score}", 20, 10, 10)
        self._draw_text(f"{self.player2.name} Score: {self.player2.score}",
                        20, BOARD_WIDTH * BLOCK_SIZE + 70, 10)

        if self.game_over1:
            self._draw_text("GAME OVER!", 40, 50, self.screen_height // 2 - 20)
        if self.game_over2:
            self._draw_text("GAME OVER!", 40,
                            BOARD_WIDTH * BLOCK_SIZE + 110, self.screen_height // 2 - 20)

        pygame.display.flip()

    def _draw_board(self, board: List[List[Optional[str]]], offset_x: int, offset_y: int):
        """Draw locked/placed tiles in the board + grid lines."""
        # Draw Tiles
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                shape = board[y][x]
                if shape is not None:
                    color = SHAPE_COLORS.get(shape, (200, 200, 200))
                    rect = pygame.Rect(
                        offset_x + x * BLOCK_SIZE,
                        offset_y + y * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                    pygame.draw.rect(self.screen, color, rect)

        # Draw Grid
        for row in range(BOARD_HEIGHT + 1):
            pygame.draw.line(
                self.screen,
                (80, 80, 80),
                (offset_x, offset_y + row * BLOCK_SIZE),
                (offset_x + BOARD_WIDTH * BLOCK_SIZE, offset_y + row * BLOCK_SIZE),
                width=1
            )
        for col in range(BOARD_WIDTH + 1):
            pygame.draw.line(
                self.screen,
                (80, 80, 80),
                (offset_x + col * BLOCK_SIZE, offset_y),
                (offset_x + col * BLOCK_SIZE, offset_y + BOARD_HEIGHT * BLOCK_SIZE),
                width=1
            )

    def _draw_piece(self, piece: TetrisPiece, offset_x: int):
        """Draw the active piece at its current position."""
        color = SHAPE_COLORS.get(piece.shape, (200, 200, 200))
        for (bx, by) in piece.get_block_positions():
            rx = offset_x + bx * BLOCK_SIZE
            ry = by * BLOCK_SIZE
            rect = pygame.Rect(rx, ry, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

    def _draw_text(self, text: str, size: int, x: int, y: int):
        font = pygame.font.SysFont("Arial", size, bold=True)
        surface = font.render(text, True, (0, 0, 0))
        self.screen.blit(surface, (x, y))

if __name__ == "__main__":
    from src.engines.player import Player
    from src.engines.board import Board

    p1 = Player("Alice")
    p2 = Player("Bob")
    dummy_board = Board(BOARD_WIDTH, BOARD_HEIGHT)

    game = TetrisGame(dummy_board, p1, p2)
    game.initialize_board()
    game.gameLoop()
    print("Tetris finished!")
    print(f"{p1.name} final score: {p1.score}")
    print(f"{p2.name} final score: {p2.score}")
