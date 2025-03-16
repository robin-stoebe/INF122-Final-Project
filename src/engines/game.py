from abc import ABC, abstractmethod
from src.engines.board import Board
from src.engines.player import Player
from src.engines.tile import Tile

class Game(ABC):
    """Base class for all games"""
    
    def __init__(self, width, height, player1: Player, player2: Player):
        self.board = Board(width, height) # Games now call board size
        self.player1 = player1
        self.player2 = player2

    def add_tile(self, symbol: str, color: tuple, x: int, y: int, tile_type="default"):
        """Places tile on the board at (x, y)"""
        if not self.board.check_collision(x, y):
            tile = Tile(symbol, color, tile_type)
            self.board.grid[y][x] = tile # Games handle tile logic

    def remove_tile(self, x: int, y: int):
        """Removes a tile from the board at (x, y)"""
        if 0 <= x < self.board.width and 0 <= y < self.board.height:
            self.board.grid[y][x] = None


    @abstractmethod
    def initialize_board(self):
        """Set up the initial state of the board."""
        pass

    @abstractmethod
    def update_board(self):
        """Update the board state per game rules."""
        pass

    @abstractmethod
    def check_win_condition(self):
        """Check if a player has won"""
        pass

    @abstractmethod
    def handle_player_input(self, player, action):
        """Handle player input for movement or actions"""
        pass

    def render(self):
        """Render the board (text-based for now)"""
        self.board.display()