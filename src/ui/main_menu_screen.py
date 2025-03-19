import pygame
import os
from .base_screen import BaseScreen
from .button import Button

class MainMenu(BaseScreen):
    def __init__(self, screen_manager, game_engine):
        super().__init__(screen_manager)
        self.game_engine = game_engine

        # BUTTONS
        self.buttons = [
            Button(450, 400, 300, 70, "Start Game", self.button_font, (10, 120, 200), (50, 150, 220), self.game_engine.selectGame),
            Button(450, 500, 300, 70, "Load Game", self.button_font, (200, 140, 3), (220, 160, 30), self.game_engine.loadGame),
            Button(450, 600, 300, 70, "Exit Game", self.button_font, (200, 40, 40), (220, 70, 70), self.exit_game),
        ]

    
    def draw(self):
        self.screen.fill((191, 88, 171))  # Background Color

        # Draw Title
        title_text = self.title_font.render("TMGE Arcade", True, (25, 169, 252))
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, 150))

        # Draw buttons
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

    def exit_game(self):
        """Terminate Application"""
        print("Exiting Game...")
        pygame.quit()
        exit()