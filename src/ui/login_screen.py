import pygame
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
        # Text Input
        self.input_box = pygame.Rect(400, 300, 400, 50)
        self.active = False
        self.text = ''
        # Colors
        self.color_inactive = pygame.Color('lightskyblue3')
        self.color_active = pygame.Color('dodgerblue2')
        self.color = self.color_inactive


    def draw(self):
        self.screen.fill((30, 30, 30))
        # Draw prompt
        prompt = self.font.render("Enter username:", True, (255, 255, 255))
        self.screen.blit(prompt, (400, 250))
        # Render text input
        txt_surface = self.font.render(self.text, True, self.color)
        width = max(400, txt_surface.get_width() + 10)
        self.input_box.w = width
        self.screen.blit(txt_surface, (self.input_box.x + 5, self.input_box.y + 5))
        pygame.draw.rect(self.screen, self.color, self.input_box, 2)
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
                    if self.input_box.collidepoint(event.pos):
                        self.active = not self.active
                    else:
                        self.active = False
                    self.color = self.color_active if self.active else self.color_inactive
                if event.type == pygame.KEYDOWN:
                    if self.active:
                        if event.key == pygame.K_RETURN:
                            username = self.text.strip()
                            if username:
                                # Load profile and create a Player instance
                                profile = self.profile_manager.get_profile(username)
                                player = Player(username)
                                player.score = profile.get("score", 0)
                                self.game_engine.set_player(player, self.profile_manager)
                                # Switch to the main menu after login
                                self.screen_manager.set_screen("main_menu")
                                running = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.text = self.text[:-1]
                        else:
                            self.text += event.unicode
            self.draw()
            clock.tick(30)