import pygame
import time

def main():
    pygame.init()

    surface = pygame.display.set_mode((1200, 800))
    surface.fill((255, 255, 255))
    pygame.display.flip()
    time.sleep(5)
    pygame.quit



if __name__ == "__main__":
    main()