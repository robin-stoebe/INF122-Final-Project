import pygame
from src.ui.screen_manager import ScreenManager
from src.ui.main_menu_screen import MainMenu
from src.ui.game_selection_screen import GameSelectionScreen
from src.ui.login_screen import LoginScreen
from src.ui.scores_screen import scoresScreen
from src.engines.game_engine import GameEngine

def main():
    pygame.init()
    screen_manager = ScreenManager()
    engine = GameEngine(screen_manager)

    # Create screens
    main_menu = MainMenu(screen_manager, engine)
    game_selection = GameSelectionScreen(screen_manager, engine)
    login_screen = LoginScreen(screen_manager, engine)
    scores = scoresScreen(screen_manager, engine)

    # Add screens to manager
    screen_manager.add_screen("main_menu", main_menu)
    screen_manager.add_screen("game_selection", game_selection)
    screen_manager.add_screen("login", login_screen)
    screen_manager.add_screen("scores", scores)

    screen_manager.set_screen("main_menu")
    screen_manager.run()

if __name__ == "__main__":
    main()