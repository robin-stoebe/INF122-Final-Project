import pygame
import random
from typing import List, Tuple, Optional

from src.engines.player import Player
from src.engines.game import Game
from src.engines.board import Board

# Tetris constants
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

class TetrisPiece:
    """Represents a single falling Tetrimino with shape, position, and orientation."""
    def __init__(self, shape: str, x: int, y: int):
        self.shape = shape
        self.blocks = TETROMINO_SHAPES[shape]
        self.x = x
        self.y = y

    def get_block_positions(self) -> List[Tuple[int, int]]:
        """Returns the positions of the blocks for this piece."""
        return [(self.x + dx, self.y + dy) for (dx, dy) in self.blocks]

    def move(self, dx: int, dy: int):
        """Moves the piece."""
        self.x += dx
        self.y += dy

    def rotate(self):
        new_blocks = [(-dy, dx) for (dx, dy) in self.blocks]
        self.blocks = new_blocks


class TetrisGame(Game):
    def __init__(self, player1: Player, player2: Player):
        super().__init__(BOARD_WIDTH, BOARD_HEIGHT, player1, player2, {
            "line_clear_1": 100,
            "line_clear_2": 300,
            "line_clear_3": 600,
            "line_clear_4": 1000
        })

        # Create two separate boards for the two players:
        self.board1 = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.board2 = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

        # Create two active pieces
        self.active_piece1: Optional[TetrisPiece] = None
        self.active_piece2: Optional[TetrisPiece] = None

        # Gravity timers
        self.drop_timer1 = 0.0
        self.drop_timer2 = 0.0
        self.drop_interval1 = DROP_INTERVAL
        self.drop_interval2 = DROP_INTERVAL

        # Game states
        self.game_over1 = False
        self.game_over2 = False

        # pygame.init()
        self.screen_width = BOARD_WIDTH * BLOCK_SIZE * 2 + 60
        self.screen_height = BOARD_HEIGHT * BLOCK_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Two-Player Tetris")

        # Spawn initial pieces
        self.spawn_piece1()
        self.spawn_piece2()

    def update_board(self):
        dt = 1.0 / 60.0  # If you prefer a fixed step; or measure real dt from clock
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

    def is_game_over(self) -> bool:
        return (self.game_over1 and self.game_over2) or (not self.running)

    def handle_player_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Player 1
            if not self.game_over1 and self.active_piece1:
                self._handle_player1_keys(event.key)
            # Player 2
            if not self.game_over2 and self.active_piece2:
                self._handle_player2_keys(event.key)

    def render(self, screen):
        self.screen.fill((0, 0, 0))  # Black background

        # Draw board1
        self._draw_board(self.board1, offset_x=0, offset_y=0)
        # Draw board2
        self._draw_board(self.board2, offset_x=(BOARD_WIDTH * BLOCK_SIZE + 60), offset_y=0)

        # Draw active pieces
        if self.active_piece1 and not self.game_over1:
            self._draw_piece(self.active_piece1, offset_x=0)
        if self.active_piece2 and not self.game_over2:
            self._draw_piece(self.active_piece2, offset_x=(BOARD_WIDTH * BLOCK_SIZE + 60))

        # Display each player's name and score
        font = pygame.font.Font(None, 30)
        p1_text = font.render(f"{self.player1.name} Score: {self.player1.score}", True, (255, 255, 255))
        p2_text = font.render(f"{self.player2.name} Score: {self.player2.score}", True, (255, 255, 255))
        self.screen.blit(p1_text, (10, 10))
        self.screen.blit(p2_text, (BOARD_WIDTH * BLOCK_SIZE + 70, 10))

        # If game over for a player, show message
        if self.game_over1:
            over_text = font.render("GAME OVER!", True, (255, 0, 0))
            self.screen.blit(over_text, (50, self.screen_height // 2 - 20))
        if self.game_over2:
            over_text = font.render("GAME OVER!", True, (255, 0, 0))
            self.screen.blit(over_text, ((BOARD_WIDTH * BLOCK_SIZE + 110), self.screen_height // 2 - 20))

        pygame.display.flip()

    def _handle_player1_keys(self, key):
        # Move left
        if key == pygame.K_a:
            self.active_piece1.x -= 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.x += 1
        # Move right
        elif key == pygame.K_d:
            self.active_piece1.x += 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.x -= 1
        # Rotate
        elif key == pygame.K_w:
            old_blocks = list(self.active_piece1.blocks)
            self.active_piece1.rotate()
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.blocks = old_blocks
        # Soft drop
        elif key == pygame.K_s:
            self.active_piece1.y += 1
            if self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.y -= 1
                self.lock_piece(self.active_piece1, self.board1, player=1)
        # Hard drop
        elif key == pygame.K_SPACE:
            while not self.check_collision(self.active_piece1, self.board1):
                self.active_piece1.y += 1
            self.active_piece1.y -= 1
            self.lock_piece(self.active_piece1, self.board1, player=1)

    def _handle_player2_keys(self, key):
        # Move left
        if key == pygame.K_LEFT:
            self.active_piece2.x -= 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.x += 1
        # Move right
        elif key == pygame.K_RIGHT:
            self.active_piece2.x += 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.x -= 1
        # Rotate
        elif key == pygame.K_UP:
            old_blocks = list(self.active_piece2.blocks)
            self.active_piece2.rotate()
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.blocks = old_blocks
        # Soft drop
        elif key == pygame.K_DOWN:
            self.active_piece2.y += 1
            if self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.y -= 1
                self.lock_piece(self.active_piece2, self.board2, player=2)
        # Hard drop
        elif key == pygame.K_RCTRL:
            while not self.check_collision(self.active_piece2, self.board2):
                self.active_piece2.y += 1
            self.active_piece2.y -= 1
            self.lock_piece(self.active_piece2, self.board2, player=2)

    def spawn_piece1(self):
        shape = random.choice(list(TETROMINO_SHAPES.keys()))
        self.active_piece1 = TetrisPiece(shape, BOARD_WIDTH // 2 - 2, 0)

    def spawn_piece2(self):
        shape = random.choice(list(TETROMINO_SHAPES.keys()))
        self.active_piece2 = TetrisPiece(shape, BOARD_WIDTH // 2 - 2, 0)

    def check_collision(self, piece: TetrisPiece, board_array) -> bool:
        for (bx, by) in piece.get_block_positions():
            if bx < 0 or bx >= BOARD_WIDTH or by < 0 or by >= BOARD_HEIGHT:
                return True
            if board_array[by][bx] is not None:
                return True
        return False

    def lock_piece(self, piece: TetrisPiece, board_array, player: int):
        """Locks the piece and checks for game over."""
        for (bx, by) in piece.get_block_positions():
            board_array[by][bx] = piece.shape
        self.clear_lines(board_array, player)

        if player == 1:
            self.spawn_piece1()
            # Check immediate collision => game over for P1
            if self.check_collision(self.active_piece1, self.board1):
                self.game_over1 = True
        else:
            self.spawn_piece2()
            if self.check_collision(self.active_piece2, self.board2):
                self.game_over2 = True

    def clear_lines(self, board_array, player: int):
        lines_cleared = 0
        for row in range(BOARD_HEIGHT):
            if all(board_array[row][col] is not None for col in range(BOARD_WIDTH)):
                lines_cleared += 1
                # shift everything above down
                for r in range(row, 0, -1):
                    board_array[r] = board_array[r - 1][:]
                board_array[0] = [None for _ in range(BOARD_WIDTH)]

        # Add scoring via player objects
        if lines_cleared > 0:
            points = lines_cleared * 100
            if player == 1:
                self.player1.updateScore(points)
            else:
                self.player2.updateScore(points)
    def _draw_board(self, board_array, offset_x: int, offset_y: int):
        """Draw locked tiles + optional grid lines."""
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                shape = board_array[y][x]
                if shape is not None:
                    color = SHAPE_COLORS.get(shape, (200, 200, 200))
                    rect = pygame.Rect(offset_x + x * BLOCK_SIZE,
                                       offset_y + y * BLOCK_SIZE,
                                       BLOCK_SIZE, BLOCK_SIZE)
                    pygame.draw.rect(self.screen, color, rect)

        # Grid lines
        for row in range(BOARD_HEIGHT + 1):
            pygame.draw.line(
                self.screen, (80, 80, 80),
                (offset_x, offset_y + row * BLOCK_SIZE),
                (offset_x + BOARD_WIDTH * BLOCK_SIZE, offset_y + row * BLOCK_SIZE),
                width=1
            )
        for col in range(BOARD_WIDTH + 1):
            pygame.draw.line(
                self.screen, (80, 80, 80),
                (offset_x + col * BLOCK_SIZE, offset_y),
                (offset_x + col * BLOCK_SIZE, offset_y + BOARD_HEIGHT * BLOCK_SIZE),
                width=1
            )

    def _draw_piece(self, piece: TetrisPiece, offset_x: int):
        """Draw the active piece."""
        color = SHAPE_COLORS.get(piece.shape, (200, 200, 200))
        for (bx, by) in piece.get_block_positions():
            rx = offset_x + bx * BLOCK_SIZE
            ry = by * BLOCK_SIZE
            rect = pygame.Rect(rx, ry, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            # Outline
            pygame.draw.rect(self.screen, (50, 50, 50), rect, 1)

if __name__ == "__main__":
    p1 = Player("Alice")
    p2 = Player("Bob")
    game = TetrisGame(p1, p2)
    screen = pygame.display.set_mode((BOARD_WIDTH * BLOCK_SIZE * 2 + 60, BOARD_HEIGHT * BLOCK_SIZE))
    clock = pygame.time.Clock()
    game.run_game_loop(screen, clock, FPS)
