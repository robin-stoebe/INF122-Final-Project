from abc import ABC, abstractmethod
import pygame
from src.engines.board import Board
from src.engines.player import Player
from src.engines.scoring_system import ScoringSystem

class Game(ABC):
    """Base class for all games"""
    
    def __init__(self, width, height, player1: Player, player2: Player, scoring_rules=None):
        self.board = Board(width, height) # Games now call board size
        self.player1 = player1
        self.player2 = player2
        self.running = True

        self.scoring_system = ScoringSystem(scoring_rules if scoring_rules else {})

    @abstractmethod
    def update_board(self):
        """Each game defines its own board update logic."""
        raise NotImplementedError("Subclasses must implement update_board()")

    @abstractmethod
    def is_game_over(self):
        """Each game defines its own game-over condition."""
        raise NotImplementedError("Subclasses must implement is_game_over()")

    def run_game_loop(self, screen, clock, fps):
        """Universal game loop for all TMGE games."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle_player_input(event)  # Calls game-specific input handling

            self.update_board()  # Calls game-specific board update logic
            if self.is_game_over():
                self.running = False  # Stop if game-over condition is met

            self.render(screen)  # Calls game rendering
            clock.tick(fps)

        # pygame.quit()
        print(f"Game Over! Final Score: {self.scoring_system.get_score()}")

    @abstractmethod
    def handle_player_input(self, action):
        """Handle player input for movement or actions"""
        pass

    @abstractmethod
    def render(self):
        """Render the board"""
        self.board.display()