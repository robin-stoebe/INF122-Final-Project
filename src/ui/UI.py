import pygame
import time
import os
from .button import Button

class UI:
    def __init__(self, game_engine):
        pygame.init()
        self.game_engine = game_engine
        self.WIDTH, self.HEIGHT = 1200, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("TMGE Arcade")

        # FONTS
        font_path_Starborn = os.path.join("assets", "fonts", "Starborn.ttf")    # Construct path to font file
        if os.path.exists(font_path_Starborn):
            self.font = pygame.font.Font(font_path_Starborn, 100)
        else:
            print("Font not found; using default font.")
        font_path_Straw_Milky = os.path.join("assets", "fonts", "Straw Milky.otf")


        # BUTTONS
        self.button_font = pygame.font.Font(font_path_Straw_Milky, 30)
        self.buttons = [
            Button(450, 400, 300, 70, "Start Game", self.button_font, (10, 120, 200), (50, 150, 220), self.game_engine.selectGame),
            Button(450, 500, 300, 70, "Load Game", self.button_font, (200, 140, 3), (220, 160, 30), self.game_engine.loadGame),
            Button(450, 600, 300, 70, "Exit Game", self.button_font, (200, 40, 40), (220, 70, 70), self.exit_game),
        ]
        self.running = True

    
    def draw_menu(self):
        self.screen.fill((191, 88, 171))  # Background Color

        # TITLE TEXT
        title_text = self.font.render("TMGE Arcade", True, (25, 169, 252))
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, 150))

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
        
        pygame.display.flip()

    def run(self):
        while self.running:
            self.draw_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for button in self.buttons:
                    button.check_click(event)

    def exit_game(self):
        print("Exiting Game...")
        pygame.quit()
        exit()