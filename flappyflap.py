import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Create the screen object
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird')

# Define constants
GRAVITY = 0.25
BIRD_FLAP_STRENGTH = -6
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Load images
BIRD_IMG = pygame.Surface((34, 24), pygame.SRCALPHA)
pygame.draw.polygon(BIRD_IMG, (255, 255, 0), [(0, 12), (17, 0), (34, 12), (17, 24)])
PIPE_IMG = pygame.Surface((52, SCREEN_HEIGHT), pygame.SRCALPHA)
PIPE_IMG.fill((0, 255, 0))
BASE_IMG = pygame.Surface((SCREEN_WIDTH, 100))
BASE_IMG.fill((222, 216, 149))
BACKGROUND_COLOR = (135, 206, 235)

# Define fonts
FONT = pygame.font.SysFont('Arial', 32, bold=True)

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = BIRD_IMG
        self.rect = self.image.get_rect(center=(50, SCREEN_HEIGHT // 2))
        self.velocity = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)

        # Prevent bird from going off-screen
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity = 0

    def flap(self):
        self.velocity = BIRD_FLAP_STRENGTH

class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, x, y):
        super().__init__()
        self.image = PIPE_IMG
        self.rect = self.image.get_rect()
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = (x, y - PIPE_GAP // 2)
        else:
            self.rect.topleft = (x, y + PIPE_GAP // 2)

    def update(self):
        self.rect.x -= 2
        if self.rect.right < 0:
            self.kill()

def check_collision(bird, pipes):
    return pygame.sprite.spritecollideany(bird, pipes)

def display_score(screen, score):
    score_surface = FONT.render(f'Score: {score}', True, (255, 255, 255))
    screen.blit(score_surface, (10, 10))

def game_over_screen(screen, score):
    screen.fill(BACKGROUND_COLOR)
    game_over_surface = FONT.render('Game Over!', True, (255, 0, 0))
    score_surface = FONT.render(f'Final Score: {score}', True, (255, 255, 255))
    screen.blit(game_over_surface, (SCREEN_WIDTH // 2 - game_over_surface.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(score_surface, (SCREEN_WIDTH // 2 - score_surface.get_width() // 2, SCREEN_HEIGHT // 2))
    pygame.display.flip()
    pygame.time.wait(2000)

def main():
    clock = pygame.time.Clock()
    bird = Bird()
    bird_group = pygame.sprite.GroupSingle(bird)
    pipe_group = pygame.sprite.Group()

    SPWANPIPE = pygame.USEREVENT
    pygame.time.set_timer(SPWANPIPE, PIPE_FREQUENCY)

    score = 0
    running = True
    while running:
        clock.tick(120)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == SPWANPIPE:
                pipe_height = random.randint(100, SCREEN_HEIGHT - 200)
                top_pipe = Pipe(True, SCREEN_WIDTH, pipe_height)
                bottom_pipe = Pipe(False, SCREEN_WIDTH, pipe_height)
                pipe_group.add(top_pipe)
                pipe_group.add(bottom_pipe)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.flap()

        # Update
        bird_group.update()
        pipe_group.update()

        # Collision
        if check_collision(bird, pipe_group) or bird.rect.bottom >= SCREEN_HEIGHT - 100:
            game_over_screen(SCREEN, score)
            main()

        # Scoring
        for pipe in pipe_group:
            if pipe.rect.centerx == bird.rect.centerx and pipe.rect.bottom >= SCREEN_HEIGHT:
                score += 0.5  # Increment score when passing each bottom pipe

        # Draw
        SCREEN.fill(BACKGROUND_COLOR)
        bird_group.draw(SCREEN)
        pipe_group.draw(SCREEN)
        SCREEN.blit(BASE_IMG, (0, SCREEN_HEIGHT - 100))
        display_score(SCREEN, int(score))
        pygame.display.update()

if __name__ == '__main__':
    main()
