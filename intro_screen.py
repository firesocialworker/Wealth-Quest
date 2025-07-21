import pygame
import sys

WIDTH, HEIGHT = 800, 600

# Initialize pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Wealth Quest Intro")

# Colors (16-bit style palette)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Load a pixel-style font
font = pygame.font.Font(None, 72)  # Default font scaled up

text = font.render("Wealth Quest", True, WHITE)
text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

