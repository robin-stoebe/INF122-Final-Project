import sys
import numpy as np
import pygame
import pymunk
import random
from src.engines.game import Game
from src.engines.board import Board
from src.engines.player import Player


pygame.init()
rng = np.random.default_rng()

# Constants
SIZE = WIDTH, HEIGHT = np.array([570, 770])
PAD = (24, 160)
A = (PAD[0], PAD[1])
B = (PAD[0], HEIGHT - PAD[0])
C = (WIDTH - PAD[0], HEIGHT - PAD[0])
D = (WIDTH - PAD[0], PAD[1])
BG_COLOR = (250, 240, 148)
W_COLOR = (250, 190, 58)
COLORS = [
    (245, 0, 0),
    (250, 100, 100),
    (150, 20, 250),
    (250, 210, 10),
    (250, 150, 0),
    (245, 0, 0),
    (250, 250, 100),
    (255, 180, 180),
    (255, 255, 0),
    (100, 235, 10),
    (0, 185, 0),
]
FPS = 240
RADII = [17, 25, 32, 38, 50, 63, 75, 87, 100, 115, 135]
THICKNESS = 14
DENSITY = 0.001
ELASTICITY = 0.1
IMPULSE = 10000
GRAVITY = 2000
DAMPING = 0.8
NEXT_DELAY = FPS
BIAS = 0.00001
POINTS = [1, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66]
shape_to_particle = dict()


class Particle:
    def __init__(self, pos, n, space, mapper):
        self.n = n % 11
        self.radius = RADII[self.n]
        self.body = pymunk.Body(body_type=pymunk.Body.DYNAMIC)
        self.body.position = tuple(pos)
        self.shape = pymunk.Circle(body=self.body, radius=self.radius)
        self.shape.density = DENSITY
        self.shape.elasticity = ELASTICITY
        self.shape.collision_type = 1
        self.shape.friction = 0.2
        self.has_collided = False
        mapper[self.shape] = self
        print(f"part {self.shape.friction=}")

        space.add(self.body, self.shape)
        self.alive = True
        print(f"Particle {id(self)} created {self.shape.elasticity}")

    def draw(self, screen):
        if self.alive:
            c1 = np.array(COLORS[self.n])
            c2 = (c1 * 0.8).astype(int)
            pygame.draw.circle(screen, tuple(c2), self.body.position, self.radius)
            pygame.draw.circle(screen, tuple(c1), self.body.position, self.radius * 0.9)

    def kill(self, space):
        space.remove(self.body, self.shape)
        self.alive = False
        print(f"Particle {id(self)} killed")

    @property
    def pos(self):
        return np.array(self.body.position)


class PreParticle:
    def __init__(self, x, n):
        self.n = n % 11
        self.radius = RADII[self.n]
        self.x = x
        print(f"PreParticle {id(self)} created")

    def draw(self, screen):
        c1 = np.array(COLORS[self.n])
        c2 = (c1 * 0.8).astype(int)
        pygame.draw.circle(screen, tuple(c2), (self.x, PAD[1] // 2), self.radius)
        pygame.draw.circle(screen, tuple(c1), (self.x, PAD[1] // 2), self.radius * 0.9)

    def set_x(self, x):
        lim = PAD[0] + self.radius + THICKNESS // 2
        self.x = np.clip(x, lim, WIDTH - lim)

    def release(self, space, mapper):
        return Particle((self.x, PAD[1] // 2), self.n, space, mapper)


class Wall:
    thickness = THICKNESS

    def __init__(self, a, b, space):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, a, b, self.thickness // 2)
        self.shape.friction = 10
        space.add(self.body, self.shape)
        print(f"wall {self.shape.friction=}")

    def draw(self, screen):
        pygame.draw.line(screen, W_COLOR, self.shape.a, self.shape.b, self.thickness)


def resolve_collision(p1, p2, space, particles, mapper):
    if p1.n == p2.n:
        distance = np.linalg.norm(p1.pos - p2.pos)
        if distance < 2 * p1.radius:
            p1.kill(space)
            p2.kill(space)
            pn = Particle(np.mean([p1.pos, p2.pos], axis=0), p1.n+1, space, mapper)
            for p in particles:
                if p.alive:
                    vector = p.pos - pn.pos
                    distance = np.linalg.norm(vector)
                    if distance < pn.radius + p.radius:
                        impulse = IMPULSE * vector / (distance ** 2)
                        p.body.apply_impulse_at_local_point(tuple(impulse))
                        print(f"{impulse=} was applied to {id(p)}")
            return pn
    return None


class SuikaGame(Game):
    """Suika Game using TMGE"""
    def __init__(self, player1, player2):
        super().__init__(WIDTH, HEIGHT, player1, player2, scoring_rules={"merge": 1})
        pygame.init()

        self.running = True
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.space.damping = DAMPING
        self.space.collision_bias = BIAS

        # Ensure the board is the original Suika size
        self.board_width = WIDTH
        self.board_height = HEIGHT

        # Create game walls with  dimensions
        self.walls = [
            Wall(A, B, self.space),
            Wall(B, C, self.space),
            Wall(C, D, self.space)
        ]

        # Game data structures
        self.shape_to_particle = {}
        self.particles = []
        self.wait_for_next = 0
        self.next_particle = PreParticle(WIDTH // 2, rng.integers(0, 5))  # ✅ Preview piece follows mouse

        # Collision Handler
        handler = self.space.add_collision_handler(1, 1)
        handler.begin = self.collide
        handler.data["particles"] = self.particles
        handler.data["mapper"] = self.shape_to_particle

    def collide(self, arbiter, space, data):
        """Handles particle merging logic upon collision."""
        sh1, sh2 = arbiter.shapes
        p1, p2 = self.shape_to_particle[sh1], self.shape_to_particle[sh2]

        if p1.n == p2.n:  # Only merge if the particles are the same
            p1.kill(space)
            p2.kill(space)

            # Create a new merged particle at collision location
            merged_particle = Particle(np.mean([p1.pos, p2.pos], axis=0), p1.n + 1, space, self.shape_to_particle)
            self.particles.append(merged_particle)

            # Update score
            self.scoring_system.add_score("merge", POINTS[p1.n])

    def update_board(self):
        """Handles physics updates and checks for new particle spawning."""
        self.space.step(1 / FPS)

        if self.wait_for_next > 1:
            self.wait_for_next -= 1
        elif self.wait_for_next == 1:
            self.next_particle = PreParticle(self.next_particle.x, rng.integers(0, 5))
            self.wait_for_next -= 1

    def is_game_over(self):
        """Ends the game immediately if a particle overflows."""
        for p in self.particles:
            if p.pos[1] < PAD[1] and p.has_collided:  # Check if a particle collides at the top
                print(f"Game Over! Final Score: {self.scoring_system.get_score()}")
                self.running = False
                return True
        return False

    def handle_player_input(self, event):
        """Handles movement of the next particle and releasing it."""
        if event.type == pygame.MOUSEMOTION:
            self.next_particle.set_x(event.pos[0])  # Move preview piece with mouse

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                move_amount = -10 if event.key == pygame.K_LEFT else 10
                self.next_particle.set_x(self.next_particle.x + move_amount)  # Allow arrow keys to move preview piece

            elif event.key in [pygame.K_RETURN, pygame.K_SPACE] and self.wait_for_next == 0:
                # Release the particle and start countdown for the next one
                self.particles.append(self.next_particle.release(self.space, self.shape_to_particle))
                self.wait_for_next = NEXT_DELAY

        if event.type == pygame.MOUSEBUTTONDOWN and self.wait_for_next == 0:
            self.particles.append(self.next_particle.release(self.space, self.shape_to_particle))
            self.wait_for_next = NEXT_DELAY  # Allow mouse click to release piece

    def render(self, screen):
        """Draws all game elements on screen with the correct original board size."""
        screen.fill(BG_COLOR)

        # Draw game walls
        for wall in self.walls:
            wall.draw(screen)

        # Draw all particles
        for p in self.particles:
            p.draw(screen)

        # Draw next particle preview at mouse position
        if self.wait_for_next == 0:
            self.next_particle.draw(screen)

        # Display Score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.scoring_system.get_score()}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        pygame.display.flip()


def main():
    game = SuikaGame(None, None)
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    game.run_game_loop(screen, clock, FPS)

if __name__ == "__main__":
    main()