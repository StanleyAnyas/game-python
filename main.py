import pygame #type: ignore
import sys
import random
import pygame_widgets #type: ignore
from pygame_widgets.button import Button #type: ignore

pygame.mixer.init()
pygame.init()
jump_sound = pygame.mixer.Sound("./sounds/jump.wav")
click_sound = pygame.mixer.Sound("./sounds/click.wav")
bullet_sound = pygame.mixer.Sound("./sounds/explosion.wav")
kill_sound = pygame.mixer.Sound("./sounds/kill.wav")
enemy_missed_sound = pygame.mixer.Sound("./sounds/powerUp.wav")
game_lost_sound = pygame.mixer.Sound("./sounds/explosion.wav")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
VIOLA = (42, 31, 89)
LIFE_BOSS = 5
POINT_PLAYER = 5
player_points = POINT_PLAYER

font_path = "./fonts/Press_Start_2P/PressStart2P-Regular.ttf"
font = pygame.font.Font(font_path, 24)
font_play = pygame.font.SysFont("Segoe UI Emoji", 16)  
text = font.render("Press START", True, (255, 255, 255))
player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
game_lost_text = font.render("GAME OVER", True, (WHITE))

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Giochiamo")

clock = pygame.time.Clock()

player_img = pygame.image.load("./image/player.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))
player = player_img.get_rect()
player.center = (400, 500)

enemy_image = pygame.image.load("./image/enemy.png").convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (60, 60))
enemy_image = pygame.transform.rotate(enemy_image, 180)
enemy = enemy_image.get_rect()

boss_image = pygame.image.load("./image/boss.png").convert_alpha()
boss_image = pygame.transform.scale(boss_image, (70, 70))
boss_image = pygame.transform.rotate(boss_image, 180)
bossy = boss_image.get_rect()

explosion_sheet = pygame.image.load("./image/boom.png").convert_alpha()
FRAME_WIDTH = 128
FRAME_HEIGHT = 145
COLUMNS = 8
ROWS = 7

explosion_frames = []

for row in range(ROWS):
    for col in range(COLUMNS):
        frame = explosion_sheet.subsurface((col * FRAME_WIDTH, row * FRAME_HEIGHT, FRAME_WIDTH, FRAME_HEIGHT))
        explosion_frames.append(frame)
explosion_frames.reverse()
explosion_frames_to_use = []
for idx, frame in enumerate(explosion_frames):
    if idx < 7:
        explosion_frames_to_use.append(frame)
        # pygame.image.save(frame, f"./explosion_frame_{idx}.png")

explosions = pygame.sprite.Group()
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 4 
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= self.animation_speed:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.index]


while True:
    velocity = 5
    enemies = []
    enemy_speed = 0.5

    bullets = []
    bullet_speed = 5
    bullet_width, bullet_height = 3, 7

    started = False
    running = False
    game_lost = False
    def change_settings():
        global started, running, game_lost, player_points, player_point_text
        player_points = POINT_PLAYER
        player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
        started = False
        running = False
        game_lost = False
    
    font_play2 = pygame.font.Font(font_path, 20)
    button = Button(
        screen,
        300,
        300, 
        155,
        50,
        text="Restart",
        font=font_play2,
        margin=5, 
        inactivityColour=(200, 50, 0),
        hoverColour=(150, 0, 0),
        pressedColor=(0, 200, 20),
        radius=5,
        onClick=lambda: change_settings() 
    )
    start = 0

    # starting bullet: 20
    # you have a limit of bullet but you get more when you kill an enemy (10)
    # when you kill a type of enemy you have a special bullet that you get when you kill a type of enemy
    # fix when the boss is not killed to continue bring out enemies
    stars = []
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(1, 3)
        stars.append([x, y, radius])
    while not started:
        screen.fill(BLACK)

        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star[2])
            star[1] += 1
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = 0
        screen.blit(text, (270, 260))
        pygame.display.update()

        for event in pygame.event.get():
            # print("hereee")
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    click_sound.play()
                    started = True
                    running = True
                    game_lost = False
                    # break

        # time.sleep(30)
        clock.tick(60)
        
    last_position = 0
   
        
    boss_life = LIFE_BOSS
    boss_to_come_out = False
    enemy_killed = 0
    boss_spawned = False
    boss_velocity = 3
    boss_move_timer = 0
    boss_move_interval = 60

    while running:
        screen.fill(BLACK)

        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star[2])
            star[1] += 1
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = 0
        
        if player_points == 0:
            game_lost_sound.play()
            # print("game lost")
            running = False
            game_lost = True
        # screen.fill(WHITE)
        screen.blit(player_img, player)
        screen.blit(player_point_text, (40, 30))

        if len(enemies) < 5 and not boss_to_come_out:
            if enemy_killed > 10: # rimetti a 20
                # print("boss to come out")
                enemies = []
                boss_to_come_out = True
                if not boss_spawned:
                    # print("spawn boss")
                    boss_spawned = True
                    enemies_create = pygame.Rect(350, 100, 50, 50)
                    enemies.append(enemies_create)
                
            else:
                # print(f"enemy killed {enemy_killed}")
                boss_to_come_out = False 
                random_position = random.randint(0, WIDTH - 50)
                enemies_create = pygame.Rect(random_position, 100, 50, 50)
                enemies.append(enemies_create)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:  
                if event.key == pygame.K_SPACE:
                    bullet_sound.play()
                    bullet = pygame.Rect(player.centerx - bullet_width // 2, player.top, bullet_width, bullet_height)
                    bullets.append(bullet)
                    bullets.append(bullet)
                    
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x > 0:
            jump_sound.play()
            player.x -= velocity
        if keys[pygame.K_RIGHT] and player.x < WIDTH - player.width:
            jump_sound.play()
            player.x += velocity
        
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            for enemy in enemies:
                if bullet.colliderect(enemy) and not boss_to_come_out:
                    enemy_killed +=1
                    if bullet in bullets:
                        bullets.remove(bullet)
                    enemies.remove(enemy)
                    # for x in explosion_frames_to_use:   
                    explosion = Explosion(enemy.centerx, enemy.centery, explosion_frames_to_use)
                    explosions.add(explosion)
                    kill_sound.play()
                    enemy.y = 100
                elif bullet.colliderect(enemy) and boss_to_come_out:
                    bullets.remove(bullet)
                    kill_sound.play()
                    # print(f"boss life {boss_life}")
                    if boss_life < 1:
                        enemies.remove(enemy)
                        explosion = Explosion(enemy.centerx, enemy.centery, explosion_frames_to_use)
                        explosions.add(explosion)
                        boss_to_come_out = False
                        boss_spawned = False
                        enemy_killed = 0
                        boss_life = LIFE_BOSS
                        player_points += 1
                        player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
                        screen.blit(player_point_text, (40, 30))
                        break
                    else:
                        boss_life -=1
                
            if bullet.y < 0:
                bullets.remove(bullet)
        for enemy in enemies:
            if boss_to_come_out:
                screen.blit(boss_image, enemy)
                enemy.y += enemy_speed
                boss_move_timer += 2
                if boss_move_timer >= boss_move_interval:
                    enemy.x = random.randint(0, WIDTH - enemy.width)
                    boss_move_timer = 0
            else:
                screen.blit(enemy_image, enemy)
                enemy.y += enemy_speed
            
            if enemy.y > player.y:
                if boss_to_come_out:
                    boss_to_come_out = False
                    boss_spawned = False
                    enemy_killed = 0
                    boss_life = LIFE_BOSS
                    enemy_missed_sound.play()
                    enemies.remove(enemy)
                else:
                    player_points -= 1
                    player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
                    screen.blit(player_point_text, (40, 30))
                    enemy_missed_sound.play()
                    enemies.remove(enemy)
                    
        explosions.update()
        explosions.draw(screen)
        
        for bullet in bullets:
            pygame.draw.rect(screen, RED, bullet)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        clock.tick(60)

    while game_lost is True:
        screen.fill(BLACK)
        for star in stars:
            pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), star[2])
            star[1] += 1
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = 0
        screen.blit(game_lost_text, (270, 260))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame_widgets.update(events)
        button.listen(events)
        button.draw()
        pygame.display.update()
        clock.tick(60)