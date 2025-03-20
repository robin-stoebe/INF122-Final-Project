import sys
from src.games.tetris import TetrisGame
from src.games.suika import SuikaGame
from src.engines.board import Board
from src.engines.player import Player
from src.ui.main_menu_screen import MainMenu
from src.ui.screen_manager import ScreenManager
from src.ui.game_selection_screen import GameSelectionScreen
from src.ui.base_screen import BaseScreen
from src.ui.login_screen import LoginScreen
from src.ui.scores_screen import scoresScreen
import pygame
# import pymunk
import numpy as np
# from src.engines.game import Game


class GameEngine:
    def __init__(self, screen_manager):
        self.games = []
        self.timer = 0
        self.screen_manager = screen_manager

    def loadScores(self, filename: str):
        """Load a player's scores from a file"""
        print(f"Loading scores from {filename}...")
        self.screen_manager.set_screen("scores")

    def saveGame(self, filename: str):
        """Save the current game to a file"""
        print(f"Saving current game to {filename}...")
        # Stub
        pass

    def selectGame(self):
        """Switch to game selection screen"""
        print("Game Engine: Opening game selection menu...")
        self.screen_manager.set_screen("game_selection")

    # works with ui > login_screen.py and engines > player.py
    def set_player(self, player, profile_manager):
        """Store logged in player's data."""
        self.player = player
        self.profile_manager = profile_manager

    def runSuika(self):
        """Run instance of Suika after selecting Suika button"""
        print("Running Suika")
        suika_game = SuikaGame(Player("Bob"), Player("Ava"))
        SIZE = WIDTH, HEIGHT = np.array([570, 770])
        screen = pygame.display.set_mode(SIZE)
        suika_game.run_game_loop(screen, pygame.time.Clock(), 60)

    def runTetris(self):
        """Run instance of Tetris after selecting Suika button"""
        # FIX THIS; lock_piece() index error
        print("Running Tetris")
        tetris_game = TetrisGame(Player("Bob"), Player("Ava"))
        screen = pygame.display.set_mode((tetris_game.board.width * 30, tetris_game.board.height * 30))
        tetris_game.run_game_loop(screen, pygame.time.Clock(), 60)

    def run_game_loop(self, game):
        """Unified game loop for all games."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    game.handle_player_input(event)  # passes raw event to games to process
                    
            game.update_board()
            game.render()

    def __repr__(self):
        return f"GameEngine(games={len(self.games)})"
    
if __name__ == "__main__":
    screen_manager = ScreenManager()
    engine = GameEngine(screen_manager)

    # Create screens
    main_menu = MainMenu(screen_manager, engine)
    game_selection = GameSelectionScreen(screen_manager, engine)
    login_screen = LoginScreen(screen_manager, engine)
    scores = scoresScreen(screen_manager, engine)

    # Add screens to manager
    screen_manager.add_screen("login", login_screen)
    screen_manager.add_screen("main_menu", main_menu)
    screen_manager.add_screen("game_selection", game_selection)
    screen_manager.add_screen("scores", scores)
    
    # Start screen at main menu
    screen_manager.set_screen("login")
    screen_manager.run()