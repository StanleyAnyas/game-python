import pygame #type: ignore
import sys
import time

pygame.mixer.init()
pygame.init()

font_path = "./fonts/Press_Start_2P/PressStart2P-Regular.ttf"
font = pygame.font.Font(font_path, 24)  
text = font.render("Press START", True, (0, 0, 0))

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Giochiamo")


WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
clock = pygame.time.Clock()

player = pygame.Rect(340, 350, 50, 50)
velocity = 5

started = False
running = False
start = 0
while not started:
    start += 1
    print(f"start {start}")
    screen.fill(WHITE)
    screen.blit(text, (250, 260))
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                # break
                started = True 
                running = True
                break
    clock.tick(0) 
run = 0
while running:
    screen.fill(WHITE)
    run += 1
    print(f"running {run}") 
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: 
        if player.x != 0:
            player.x -= velocity; 
    if keys[pygame.K_RIGHT]: 
        if player.x != WIDTH - 50:
            player.x += velocity; 
    if keys[pygame.K_UP]: 
        if player.y != 0:
            player.y -= velocity;
    if keys[pygame.K_DOWN]: 
        if player.y != HEIGHT - 50:
            player.y += velocity; 
    
    pygame.draw.rect(screen, BLUE, player)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
