import sys
from src.games.tetris import TetrisGame
from src.games.suika import SuikaGame
from src.engines.board import Board
from src.engines.player import Player
# import pygame
# import pymunk


class GameEngine:
    def __init__(self):
        self.games = []
        self.timer = 0
        # self.games: list[game] = []
        # self.ui = UI() // UI class not yet implemented

    def startGame(self):
        print("Game Engine: Starting game...")
        selected_game = self.selectGame()
        if selected_game:
            selected_game.initialize_board()
            selected_game.gameLoop()
        else:
            print("No game started.")

    def loadGame(self, filename: str):
        print(f"Loading game from {filename}...")
        # Stub
        pass

    def saveGame(self, filename: str):
        print(f"Saving current game to {filename}...")
        # Stub
        pass

    def selectGame(self):
        print("Selecting which game to play...")

        if not self.games:
            print("No games available.")
            return None
        
        # Display the list of games
        print("Select a game to play:") 

        for i, game in enumerate(self.games):
            print(f"{i}: {type(game).__name__}")
        
        while True:
            choice_str = input("Enter the number of the game you want to play: ")
            try:
                choice = int(choice_str)
                if 0 <= choice < len(self.games):
                    return self.games[choice]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid integer.")

    def run(self):
        # self.ui.init() // not yet implemented 
        self.startGame()

    def __repr__(self):
        return f"GameEngine(games={len(self.games)})"
    
if __name__ == "__main__":
    engine = GameEngine()

    p1 = Player("Ava")
    p2 = Player("Bob")

    tetris_board = Board(10, 20)
    tetris_game = TetrisGame(tetris_board, p1, p2)
    engine.games.append(tetris_game)

    engine.run()