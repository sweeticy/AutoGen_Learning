# filename: pong_game.py
import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 15
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 60

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")
clock = pygame.time.Clock()

# Game objects
player1 = pygame.Rect(50, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
player2 = pygame.Rect(WIDTH - 50 - PADDLE_WIDTH, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

# Game variables
player1_speed = 0
player2_speed = 0
ball_speed_x = 7 * random.choice((1, -1))
ball_speed_y = 7 * random.choice((1, -1))
player1_score = 0
player2_score = 0
font = pygame.font.Font(None, 36)

def reset_ball():
    ball.center = (WIDTH//2, HEIGHT//2)
    global ball_speed_x, ball_speed_y
    ball_speed_x = 7 * random.choice((1, -1))
    ball_speed_y = 7 * random.choice((1, -1))

def ball_animation():
    global ball_speed_x, ball_speed_y, player1_score, player2_score
    
    # Ball movement
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    
    # Ball collision with top and bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_speed_y *= -1
    
    # Ball collision with paddles
    if ball.colliderect(player1) or ball.colliderect(player2):
        ball_speed_x *= -1
    
    # Score points
    if ball.left <= 0:
        player2_score += 1
        reset_ball()
    if ball.right >= WIDTH:
        player1_score += 1
        reset_ball()

def paddle_animation():
    # Player 1 movement
    player1.y += player1_speed
    if player1.top <= 0:
        player1.top = 0
    if player1.bottom >= HEIGHT:
        player1.bottom = HEIGHT
    
    # Player 2 movement
    player2.y += player2_speed
    if player2.top <= 0:
        player2.top = 0
    if player2.bottom >= HEIGHT:
        player2.bottom = HEIGHT

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Player controls
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player1_speed = -7
            if event.key == pygame.K_s:
                player1_speed = 7
            if event.key == pygame.K_UP:
                player2_speed = -7
            if event.key == pygame.K_DOWN:
                player2_speed = 7
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_s:
                player1_speed = 0
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                player2_speed = 0
    
    # Game logic
    ball_animation()
    paddle_animation()
    
    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, player1)
    pygame.draw.rect(screen, WHITE, player2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))
    
    # Score display
    player1_text = font.render(f"{player1_score}", True, WHITE)
    player2_text = font.render(f"{player2_score}", True, WHITE)
    screen.blit(player1_text, (WIDTH//4, 20))
    screen.blit(player2_text, (3*WIDTH//4, 20))
    
    # Update the display
    pygame.display.flip()
    clock.tick(FPS)