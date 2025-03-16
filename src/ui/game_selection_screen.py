import pygame
import os
from .button import Button

class GameSelectionScreen:
    def __init__(self, screen_manager, engine):
        self.screen_manager = screen_manager
        self.game_engine = engine
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Select a Game")

        # FONTS
        font_path_Starborn = os.path.join("assets", "fonts", "Starborn.ttf")    # Construct path to font file
        if os.path.exists(font_path_Starborn):
            self.title_font = pygame.font.Font(font_path_Starborn, 100)
        else:
            print("Font not found; using default font.")

        font_path_Straw_Milky = os.path.join("assets", "fonts", "Straw Milky.otf")
        if os.path.exists(font_path_Straw_Milky):
            self.button_font = pygame.font.Font(font_path_Straw_Milky, 30)
        else:
            print("Font not found; using default font.")

        # Buttons for Suika, Tetris, and Back
        self.buttons = [
            Button(450, 350, 300, 70, "Suika", self.button_font, (10, 120, 200), (50, 150, 220), self.game_engine.runSuika),
            Button(450, 450, 300, 70, "Tetris", self.button_font, (200, 140, 3), (220, 160, 30), self.game_engine.runTetris),
            Button(450, 550, 300, 70, "Back", self.button_font, (200, 40, 40), (220, 70, 70), self.go_back),
        ]
        self.running = False

    def draw(self):
        self.screen.fill((191, 88, 171))  # Background Color

        # Draw Title
        title_text = self.title_font.render("Select a Game", True, (25, 169, 252))
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, 150))

        # Draw Buttons
        for button in self.buttons:
            button.draw(self.screen)

        pygame.display.flip()

    def run(self):
        self.running = True
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for button in self.buttons:
                    button.check_click(event)

        return
    
    def go_back(self):
        """Return to Main Menu screen"""
        self.screen_manager.set_screen("main_menu")