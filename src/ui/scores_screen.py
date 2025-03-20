import pygame
from .base_screen import BaseScreen
from .button import Button

class scoresScreen(BaseScreen):
    def __init__(self, screen_manager, engine):
        super().__init__(screen_manager)
        self.game_engine = engine
        # self.player = self.game_engine.player
        # self.scores = self.game_engine.scores

        # BUTTONS
        self.buttons = [
            Button(500, 600, 200, 70, "Back", self.button_font, (200, 40, 40), (220, 70, 70), self.go_back),
        ]

    def draw(self):
        self.screen.fill((191, 88, 171))  # Background Color

        # Draw Title
        title_text = self.title_font.render("High Scores", True, (25, 169, 252))
        self.screen.blit(title_text, (self.WIDTH // 2 - title_text.get_width() // 2, 100))

        # Display name and score(s) THIS IS FOR ONE PLAYER ONLY
        #player1 = self.game_engine.player1
        #p1_text_str = f"{player1.name}: {player1.score}"
        #score_font = pygame.font.Font(None, 40)
        #p1_text = score_font.render(p1_text_str, True, (255, 255, 255))
        #self.screen.blit(p1_text, (self.WIDTH // 2 - p1_text.get_width() // 2, 250))

        profiles = self.game_engine.profile_manager.profiles
        score_font = pygame.font.Font(None, 40)
        y_offset = 300  # starting y-position for scores

        for name, data in profiles.items():
            score_text = score_font.render(f"{name}: {data['score']}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.WIDTH // 2 - score_text.get_width() // 2, y_offset))
            y_offset += 40

        # Draw Button
        for button in self.buttons:
            button.draw(self.screen)
        pygame.display.flip()
    
    def run(self):
        self.running = True
        pygame.display.set_caption("High Scores")
        while self.running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for button in self.buttons:
                    button.check_click(event)
    
    def go_back(self):
        """Return to Main Menu screen"""
        self.running = False
        self.screen_manager.set_screen("main_menu")