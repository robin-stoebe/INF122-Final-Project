from abc import ABC, abstractmethod
from board import Board

class Game(ABC):
    """Abstract base class"""
    
    def __init__(self, players):
        self.board = Board()
        self.players = players

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