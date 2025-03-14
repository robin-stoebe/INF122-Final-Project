import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action
    
    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)

        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        text_rect.y += 5   # Offset for text centering due to font
        screen.blit(text_surf, text_rect)
    
    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            if self.action:
                self.action()