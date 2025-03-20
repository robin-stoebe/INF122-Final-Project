import sys
from src.games.tetris import TetrisGame
from src.games.suika import SuikaGame
from src.engines.player import Player
from src.engines.profile_manager import ProfileManager
import pygame
# import pymunk
import numpy as np
# from src.engines.game import Game


class GameEngine:
    def __init__(self, screen_manager):
        self.games = []
        self.timer = 0
        self.screen_manager = screen_manager
        self.profile_manager = ProfileManager()
        self.player1 = Player()
        self.player2 = Player()

    def loadScores(self):
        """Load a player's scores from a file"""
        print(f"Loading scores...")
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

    # works with ui > login_screen.py
    def set_player(self, player1, player2, profile_manager):
        """Store logged in player's data."""
        self.player1 = player1
        self.player2 = player2
        self.profile_manager = profile_manager

    def runSuika(self):
        """Run instance of Suika after selecting Suika button"""
        print("Running Suika")
        suika_game = SuikaGame(self.player1, self.player2, two_player=True)
        SIZE = WIDTH, HEIGHT = np.array([570, 770])
        SIZE = (WIDTH * 2 if True else WIDTH, HEIGHT)
        screen = pygame.display.set_mode(SIZE)
        suika_game.run_game_loop(screen, pygame.time.Clock(), 60)

        self.player1.score = suika_game.scoring_p1.get_score()
        self.player2.score = suika_game.scoring_p2.get_score()
        self.profile_manager.update_profile_score(self.player1.name, self.player1.score)
        self.profile_manager.update_profile_score(self.player2.name, self.player2.score)
        self.profile_manager.save_profiles()


    def runTetris(self):
        """Run instance of Tetris after selecting Suika button"""
        print("Running Tetris")
        tetris_game = TetrisGame(self.player1, self.player2)
        screen = pygame.display.set_mode((tetris_game.board.width * 30 * 2 + 60, tetris_game.board.height * 30))
        clock = pygame.time.Clock()
        tetris_game.run_game_loop(screen, clock, 60)

        self.player1.score = tetris_game.player1.score  # Assuming the game updated these
        self.player2.score = tetris_game.player2.score
        self.profile_manager.update_profile_score(self.player1.name, self.player1.score)
        self.profile_manager.update_profile_score(self.player2.name, self.player2.score)
        self.profile_manager.save_profiles()
        print(self.player1.score)
        print(self.player2.score)
        print(self.profile_manager.profiles)

        pygame.display.set_mode((1200, 800))
        self.screen_manager.set_screen("main_menu")


    def __repr__(self):
        return f"GameEngine(games={len(self.games)})"