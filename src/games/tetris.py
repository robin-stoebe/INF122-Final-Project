import pygame
import random
from typing import List, Tuple

from src.engines.player import Player
from src.engines.game import Game

# Define Tetris constants
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
        self.orientation = 0 # 0,1,2,3

    def get_block_positions(self) -> List[Tuple[int, int]]:
        """Returns the positions of the blocks for this piece."""
        return [(self.x + dx, self.y + dy) for (dx, dy) in self.blocks]

    def move(self, dx: int, dy: int):
        """Moves the piece."""
        self.x += dx
        self.y += dy

    def rotate(self):
        new_blocks = [(-dy, dx) for dx, dy in self.blocks]  # Simulate rotation
        if all(0 <= self.x + dx < BOARD_WIDTH and 0 <= self.y + dy < BOARD_HEIGHT for dx, dy in new_blocks):
            self.blocks = new_blocks  # Apply rotation only if all positions are valid

class TetrisGame(Game):
    """Tetris game without GameEngine."""
    def __init__(self, player1: Player, player2: Player):
        super().__init__(BOARD_WIDTH, BOARD_HEIGHT, player1, player2, {
            "line_clear_1": 100,
            "line_clear_2": 300,
            "line_clear_3": 600,
            "line_clear_4": 1000
        })
        pygame.init()
        self.running = True
        self.active_piece = None
        self.spawn_piece()
        self.last_drop_time = pygame.time.get_ticks()
        self.drop_interval = 1000  # 1 second per drop

    def spawn_piece(self):
        """Spawns a new piece at the top of the board. Ends the game if there's no space."""
        shape = random.choice(list(TETROMINO_SHAPES.keys()))
        new_piece = TetrisPiece(shape, BOARD_WIDTH // 2 - 2, 0)

        # Check if the spawn position is already occupied (means game over)
        if any(self.board.grid[by][bx] is not None for bx, by in new_piece.get_block_positions()):
            self.running = False  # Stop the game
            print(f"Game Over! Final Score: {self.scoring_system.get_score()}")
            return  # Stop spawning the piece

        self.active_piece = new_piece  # Only spawn if the board is not full

    def update_board(self):
        """Handles piece movement and clearing full rows."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_drop_time >= self.drop_interval:
            self.last_drop_time = current_time

            self.active_piece.y += 1  # Move piece down

            # If the piece collides, lock it and spawn a new piece
            if any(by >= BOARD_HEIGHT or self.board.grid[by][bx] for bx, by in self.active_piece.get_block_positions()):
                self.lock_piece(self.active_piece)
                self.spawn_piece()  

    def clear_lines(self):
        """Removes full rows and shifts the board down in a single step."""
        cleared_rows = sum(all(cell is not None for cell in row) for row in self.board.grid)
        self.board.grid = [[None] * BOARD_WIDTH] * cleared_rows + [row for row in self.board.grid if not all(cell is not None for cell in row)]
        
        if cleared_rows:
            self.scoring_system.add_score(f"line_clear_{cleared_rows}", 1)


    def check_collision(self, piece: TetrisPiece) -> bool:
        """Checks if the piece collides with another block or boundary."""
        for (bx, by) in piece.get_block_positions():
            if bx < 0 or bx >= BOARD_WIDTH or by >= BOARD_HEIGHT:
                return True  # Board boundary collision
            if by >= 0 and self.board.grid[by][bx] is not None:
                return True  # Collision with another tile
        return False

    def is_game_over(self):
        """Ends the game and prints final score."""
        if any(cell is not None for cell in self.board.grid[0]):  # Check if top row is filled
            print(f"Game Over! Final Score: {self.scoring_system.get_score()}")
            self.running = False
            return True
        return False

    def lock_piece(self, piece: TetrisPiece):
        """Locks the piece and checks for game over."""
        for (bx, by) in piece.get_block_positions():
            if by < 0:
                self.is_game_over()
                return

            self.board.grid[by][bx] = piece.shape

        self.clear_lines()
        self.spawn_piece()

    def move_piece(self, dx: int, rotate=False):
        """Moves the active piece left, right, or rotates it."""
        if rotate:
            self.active_piece.rotate()
        else:
            self.active_piece.x += dx
            if self.check_collision(self.active_piece):  # Undo move if invalid
                self.active_piece.x -= dx

    def hard_drop(self):
        """Drops the active piece instantly to the lowest available row."""
        while not any(by >= BOARD_HEIGHT or self.board.grid[by][bx] for bx, by in self.active_piece.get_block_positions()):
            self.active_piece.y += 1  # Keep moving down until collision

        self.active_piece.y -= 1  # Undo last move to stay within bounds

        self.lock_piece(self.active_piece)  # Lock piece into the board
        self.spawn_piece()  # Spawn new piece

    def handle_player_input(self, event):
        """Handles movement and rotation using a cleaner function."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_piece(-1)  # Move left
            elif event.key == pygame.K_RIGHT:
                self.move_piece(1)  # Move right
            elif event.key == pygame.K_UP:
                self.move_piece(0, rotate=True)  # Rotate
            elif event.key == pygame.K_SPACE:
                self.hard_drop()  # Hard drop

    def render(self, screen):
        """Draws the Tetris board and active piece."""
        screen.fill((0, 0, 0))  # Clear screen with black

        # Draw locked tiles
        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                tile = self.board.grid[y][x]
                if tile:
                    pygame.draw.rect(screen, SHAPE_COLORS[tile],
                        pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # Draw active piece
        if self.active_piece:
            color = SHAPE_COLORS[self.active_piece.shape]
            for (bx, by) in self.active_piece.get_block_positions():
                pygame.draw.rect(screen, color,
                    pygame.Rect(bx * BLOCK_SIZE, by * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
                
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.scoring_system.get_score()}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if not self.running:
            game_over_text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(game_over_text, (BOARD_WIDTH * BLOCK_SIZE // 2 - 60, BOARD_HEIGHT * BLOCK_SIZE // 2))

        pygame.display.flip()  # Refresh screen

def main():
    player1, player2 = None, None
    game = TetrisGame(player1, player2)
    pygame.init()
    screen = pygame.display.set_mode((BOARD_WIDTH * BLOCK_SIZE, BOARD_HEIGHT * BLOCK_SIZE))
    clock = pygame.time.Clock()
    game.run_game_loop(screen, clock, FPS)

if __name__ == "__main__":
    main()
