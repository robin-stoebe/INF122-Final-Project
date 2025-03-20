import sys
import numpy as np
import pygame
import pymunk
import random
from src.engines.game import Game
from src.engines.board import Board
from src.engines.player import Player
from src.engines.scoring_system import ScoringSystem


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
GRAVITY = 6000
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


def resolve_collision(p1, p2, space, particles, mapper, game):
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
            if game.current_turn == 1:
                game.scoring_p2.add_score("merge", POINTS[p2.n])
                print(f"Player 2 Score: {game.scoring_p2.get_score()}")
            else:
                game.scoring_p1.add_score("merge", POINTS[p1.n])
                print(f"Player 1 Score: {game.scoring_p1.get_score()}")
            return pn
        

    return None

def collide(arbiter, space, data):
    """Handles collisions between particles of the same type."""
    sh1, sh2 = arbiter.shapes
    mapper = data["mapper"]

    if sh1 not in mapper or sh2 not in mapper:
        return True  # Ignore collision if shapes are missing from mapping

    p1, p2 = mapper[sh1], mapper[sh2]

    if p1.n != p2.n:
        return True  # Do nothing if they are different sizes

    # Merge particles
    merged_particle = resolve_collision(p1, p2, space, data["particles"], mapper, data["game"])

    if merged_particle:
        data["particles"].append(merged_particle)

    return False


class SuikaGame(Game):
    """Suika Game using TMGE"""
    def __init__(self, player1, player2, two_player=True):
        super().__init__(WIDTH, HEIGHT, player1, player2, scoring_rules={"merge": 1})
        pygame.init()

        self.running = True
        self.space = pymunk.Space()
        self.space.gravity = (0, GRAVITY)
        self.space.damping = DAMPING
        self.space.collision_bias = BIAS
        self.two_player = two_player  
        self.scoring_p1 = ScoringSystem(scoring_rules={"merge": 1}) 
        self.scoring_p2 = ScoringSystem(scoring_rules={"merge": 1})

        # Track which player's turn it is
        self.current_turn = 1  # Player 1 starts first

        # Create game walls
        self.walls_p1 = [
            Wall(A, B, self.space),  # Left border
            Wall(B, C, self.space),  # Bottom border
            Wall(C, D, self.space)   # Right border
        ]

        if self.two_player:
            self.walls_p2 = [
                Wall((A[0] + WIDTH, A[1]), (B[0] + WIDTH, B[1]), self.space), 
                Wall((B[0] + WIDTH, B[1]), (C[0] + WIDTH, C[1]), self.space), 
                Wall((C[0] + WIDTH, C[1]), (D[0] + WIDTH, D[1]), self.space)   
            ]
            # Add a center wall to separate players
            center_x = WIDTH
            self.walls_p1.append(Wall((center_x, PAD[1]), (center_x, HEIGHT - PAD[0]), self.space))
            self.walls_p2.append(Wall((center_x, PAD[1]), (center_x, HEIGHT - PAD[0]), self.space))

        # Separate lists for particles
        self.shape_to_particle = {}
        self.particles_p1 = []
        self.particles_p2 = []
        self.wait_for_next = 0

        # Only one preview piece is needed
        self.next_particle = PreParticle(WIDTH // 4, rng.integers(0, 5))

        # Attach collision handler AFTER defining shape_to_particle
        handler = self.space.add_collision_handler(1, 1)
        handler.begin = collide  # Correct function reference
        handler.data["mapper"] = self.shape_to_particle
        handler.data["particles"] = self.particles_p1
        if self.two_player:
            handler.data["particles"] += self.particles_p2
        handler.data["game"] = self


    def update_board(self):
        """Handles physics updates and checks for new particle spawning."""
        self.space.step(1 / FPS)  # Update physics simulation

        if self.wait_for_next > 1:
            self.wait_for_next -= 1
        elif self.wait_for_next == 1:
            # Only spawn a new preview piece if it is None
            if self.next_particle is None:
                if self.current_turn == 1:
                    self.next_particle = PreParticle(WIDTH // 4, rng.integers(0, 5))  # Player 1's preview
                else:
                    self.next_particle = PreParticle(WIDTH + WIDTH // 4, rng.integers(0, 5))  # Player 2's preview

            self.wait_for_next -= 1  # Reset delay

        if self.is_game_over():
            self.running = False  # Stop the game loop when one player loses

    def is_game_over(self):
        """Ends the game immediately if a particle overflows."""
        for p in self.particles_p1:
            if p.pos[1] < PAD[1] and p.has_collided:  # Check if Player 1 loses
                print(f"Game Over for Player 1! Final Score: {self.scoring_system.get_score()}")
                self.running = False
                return True

        if self.two_player:
            for p in self.particles_p2:
                if p.pos[1] < PAD[1] and p.has_collided:  # Check if Player 2 loses
                    print(f"Game Over for Player 2! Final Score: {self.scoring_system.get_score()}")
                    self.running = False
                    return True

        return False  # No player has lost yet

    def handle_player_input(self, event):
        """Handles mouse-based input for turn-based dropping of pieces."""

        if event.type == pygame.MOUSEMOTION and self.next_particle:
            mouse_x, _ = event.pos

            if self.current_turn == 1:
                # Player 1's preview orb moves inside their board
                self.next_particle.set_x(np.clip(mouse_x, PAD[0], WIDTH - PAD[0]))
            elif self.current_turn == 2:
                # Player 2's preview orb moves inside their board
                self.next_particle.set_x(np.clip(mouse_x - WIDTH, PAD[0], WIDTH - PAD[0]))  
                self.next_particle.x += WIDTH

        if event.type == pygame.MOUSEBUTTONDOWN and self.wait_for_next == 0 and self.next_particle:
            if self.current_turn == 1:
                # Drop Player 1's piece inside left board
                self.particles_p1.append(self.next_particle.release(self.space, self.shape_to_particle))
            else:
                # Drop Player 2's piece inside right board
                self.particles_p2.append(self.next_particle.release(self.space, self.shape_to_particle))


            self.wait_for_next = NEXT_DELAY  # Add delay before next piece spawns
            self.next_particle = None  # 🚀 Prevent immediate preview spawning

            # Switch player AFTER dropping
            self.current_turn = 1 if self.current_turn == 2 else 2

            # Ensure the next particle is spawned in the correct location
            if self.current_turn == 1:
                self.next_particle = PreParticle(WIDTH // 4, rng.integers(0, 5))  # Player 1's side
            else:
                self.next_particle = PreParticle(WIDTH + (WIDTH // 4), rng.integers(0, 5))  # Player 2's side

    def render(self, screen):
        """Draws all game elements on screen with the correct original board size."""
        screen.fill(BG_COLOR)

        # Draw walls
        for wall in self.walls_p1:
            wall.draw(screen)
        if self.two_player:
            for wall in self.walls_p2:
                wall.draw(screen)

        # Draw Player 1's particles
        for p in self.particles_p1:
            p.draw(screen)
        # Draw Player 2's particles
        for p in self.particles_p2:
            p.draw(screen)

        # Only draw the preview for the active player IF IT EXISTS
        if self.next_particle:
            self.next_particle.draw(screen)

        font = pygame.font.SysFont("monospace", 32)
        label_p1 = font.render(f"Player 1 Score: {self.scoring_p1.get_score()}", 1, (0, 0, 0))
        label_p2 = font.render(f"Player 2 Score: {self.scoring_p2.get_score()}", 1, (0, 0, 0))

        screen.blit(label_p1, (10, 10))  # Player 1's score in top-left
        if self.two_player:
            screen.blit(label_p2, (WIDTH + 10, 10))  # Player 2's score in top-right

        pygame.display.flip()

    # RUN "python -m src.engines.game_engine" to run the game - Wilson
# def main():
#     two_player = True
#     suika_game = SuikaGame(Player("Bob"), Player("Ava"), two_player=two_player)
#     SIZE = (WIDTH * 2 if two_player else WIDTH, HEIGHT)
#     screen = pygame.display.set_mode(SIZE)
#     suika_game.run_game_loop(screen, pygame.time.Clock(), 60)

# if __name__ == "__main__":
#     main()