import pygame
import os
from src.engines.profile_manager import ProfileManager
from src.engines.player import Player
from .base_screen import BaseScreen

class LoginScreen(BaseScreen):
    def __init__(self, screen_manager, game_engine):
        super().__init__(screen_manager)
        self.game_engine = game_engine
        self.profile_manager = ProfileManager()
        pygame.display.set_caption("Login")
        self.font = pygame.font.Font(None, 50)

        # Text Input (for two players)
        self.input_box1 = pygame.Rect(400, 300, 400, 50)
        self.input_box2 = pygame.Rect(400, 400, 400, 50)

        self.active1 = False
        self.active2 = False
        self.text1 = ''
        self.text2 = ''

        # Colors
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color1 = self.color_inactive
        self.color2 = self.color_inactive


    def draw(self):
        self.screen.fill((30, 30, 30))
        # Draw prompt

        prompt1 = self.font.render("Enter Player 1 username:", True, (255, 255, 255))
        self.screen.blit(prompt1, (400, 250))
        prompt2 = self.font.render("Enter Player 2 username:", True, (255, 255, 255))
        self.screen.blit(prompt2, (400, 350))

        # Render text input for player 1
        txt_surface1 = self.font.render(self.text1, True, self.color1)
        width1 = max(400, txt_surface1.get_width() + 10)
        self.input_box1.w = width1
        self.screen.blit(txt_surface1, (self.input_box1.x + 5, self.input_box1.y + 5))
        pygame.draw.rect(self.screen, self.color1, self.input_box1, 2)

        # Same for player 2
        txt_surface2 = self.font.render(self.text2, True, self.color2)
        width2 = max(400, txt_surface2.get_width() + 10)
        self.input_box2.w = width2
        self.screen.blit(txt_surface2, (self.input_box2.x + 5, self.input_box2.y + 5))
        pygame.draw.rect(self.screen, self.color2, self.input_box2, 2)

        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Toggle activation if input box is clicked
                    # Now we should check which box was clicked
                    if self.input_box1.collidepoint(event.pos):
                        self.active1 = True
                        self.active2 = False
                    elif self.input_box2.collidepoint(event.pos):
                        self.active2 = True
                        self.active1 = False
                    else:
                        self.active1 = False
                        self.active2 = False

                    self.color1 = self.color_active if self.active1 else self.color_inactive
                    self.color2 = self.color_active if self.active2 else self.color_inactive

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # If Enter is pressed and BOTH fields are filled, create player profiles
                        if self.text1.strip() and self.text2.strip():
                            username1 = self.text1.strip()
                            username2 = self.text2.strip()

                            # Load profiles and create Player instances
                            profile1 = self.profile_manager.get_profile(username1)
                            profile2 = self.profile_manager.get_profile(username2)
                            
                            player1 = Player(username1)
                            player1.score = profile1.get("score", 0)
                            player2 = Player(username2)
                            player2.score = profile2.get("score", 0)
                            
                            # Sets player profiles
                            self.game_engine.set_player(player1, player2, self.profile_manager)
                            
                            # Switch to the main menu after login
                            self.screen_manager.set_screen("main_menu")
                            running = False

                    else:
                        if self.active1:
                            if event.key == pygame.K_BACKSPACE:
                                self.text1 = self.text1[:-1]
                            else:
                                self.text1 += event.unicode

                        elif self.active2:
                            if event.key == pygame.K_BACKSPACE:
                                self.text2 = self.text2[:-1]
                            else:
                                self.text2 += event.unicode

            self.draw()
            clock.tick(30)