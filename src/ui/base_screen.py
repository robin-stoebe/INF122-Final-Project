import pygame
import os
from abc import ABC, abstractmethod

class BaseScreen(ABC):
    """Abstract base class for all screens in the game."""

    def __init__(self, screen_manager):
        pygame.init()
        self.screen_manager = screen_manager
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((1200, 800))
        self.running = False

        # FONTS
        self.title_font = self.load_font("Starborn.ttf", 100)
        self.button_font = self.load_font("Straw Milky.otf", 30)
        self.default_font = pygame.font.Font(None, 30)
    

    def load_font(self, file_name, size):
        """Load a font from the given path and size."""
        font_path = os.path.join("assets", "fonts", file_name)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)
        else:
            print(f"Font not found at {font_path}; using default font.")
            return pygame.font.Font(None, size)

    @abstractmethod
    def draw(self):
        """Abstract method to draw the screen. Each screen must have its own drawing method."""
        pass

    @abstractmethod
    def run(self):
        """Abstract method to run the screen. Each screen must have its own event loop."""
        pass