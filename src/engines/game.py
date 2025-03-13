from abc import ABC, abstractmethod
from src.engines.board import Board
from src.engines.player import Player

class Game(ABC):
    """Abstract base class"""
    
    def __init__(self, board: Board, player1: Player, player2: Player):
        self.board = board
        self.player1 = player1
        self.player2 = player2

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