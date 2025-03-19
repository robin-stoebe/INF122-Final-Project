import pygame
import os
from .base_screen import BaseScreen
from .button import Button

class GameSelectionScreen(BaseScreen):
    def __init__(self, screen_manager, engine):
        super().__init__(screen_manager)
        self.game_engine = engine
        pygame.display.set_caption("Select a Game")

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