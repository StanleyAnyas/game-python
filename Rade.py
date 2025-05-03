import pygame
import sys
import random
import pygame_widgets
from pygame_widgets.button import Button 
from pygame_widgets.dropdown import Dropdown 
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
pygame.mixer.init()
pygame.init()
jump_sound = pygame.mixer.Sound(resource_path("sounds/jump.wav"))
click_sound = pygame.mixer.Sound(resource_path("sounds/click.wav"))
bullet_sound = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))
kill_sound = pygame.mixer.Sound(resource_path("sounds/kill.wav"))
enemy_missed_sound = pygame.mixer.Sound(resource_path("sounds/powerUp.wav"))
game_lost_sound = pygame.mixer.Sound(resource_path("sounds/explosion.wav"))

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
VIOLA = (42, 31, 89)
LIFE_BOSS = 5
POINT_PLAYER = 5
player_points = POINT_PLAYER

font_path = resource_path("fonts/Press_Start_2P/PressStart2P-Regular.ttf")
font = pygame.font.Font(font_path, 24)
font_play = pygame.font.SysFont("Segoe UI Emoji", 16)  
text = font.render("Press Space key", True, WHITE)
level = font.render("Level: ", True, WHITE)
player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
game_lost_text = font.render("GAME OVER", True, (WHITE))

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rade Invaders")

clock = pygame.time.Clock()

player_img = pygame.image.load(resource_path("image/player.png")).convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 50))
player = player_img.get_rect()
player.center = (400, 500)

enemy_image = pygame.image.load(resource_path("image/enemy.png")).convert_alpha()
enemy_image = pygame.transform.scale(enemy_image, (60, 60))
enemy_image = pygame.transform.rotate(enemy_image, 180)
enemy = enemy_image.get_rect()

boss_image = pygame.image.load(resource_path("image/boss.png")).convert_alpha()
boss_image = pygame.transform.scale(boss_image, (70, 70))
boss_image = pygame.transform.rotate(boss_image, 180)
bossy = boss_image.get_rect()

explosion_sheet = pygame.image.load(resource_path("image/boom.png")).convert_alpha()
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
dropdown = Dropdown(
            screen, 
            410, # this is the X
            305, # this is the Y
            100, # this is the width
            30, # this is the height
            name='Select level',
            choices=[
                'Easy',
                'Medium',
                'Hard',
            ],
            borderRadius=3, 
            colour=pygame.Color('grey'), 
            values=[1, 2, 3], 
            direction='down', 
            textHAlign='left'
        )
while True:
    total_kill = 0
    boss_kill = 0
    total_score = 0
    
    velocity = 5
    enemies = []
    enemy_speed = 0.5

    bullets = []
    bullet_speed = 5
    bullet_width, bullet_height = 3, 7

    boss_bullets = []
    boss_bullet_speed = 5
    boss_bullet_width, boss_bullet_height = 3, 7
    
    started = False
    running = False
    game_lost = False

    difficulty = 1
    
    def change_settings():
        global started, running, game_lost, player_points, player_point_text, button, dropdown
        player_points = POINT_PLAYER
        player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
        started = False
        running = False
        game_lost = False
        button.hide()
        dropdown.show()
        
    def setup_game(difficulty, number_of_enemy, number_of_kill_before_boss, increase_enemy_by):
        player_points_in_func = 5
        match difficulty:
            case 1:
                number_of_enemy = 5
                number_of_kill_before_boss = 15
                increase_enemy_by = 0.2
                player_points_in_func = 5
            case 2:
                number_of_enemy = 7
                number_of_kill_before_boss = 25
                increase_enemy_by = 0.4
                player_points_in_func = 10
            case 3:
                number_of_enemy = 9
                number_of_kill_before_boss = 32
                increase_enemy_by = 0.65
                player_points_in_func = 20
            case _: 
                number_of_enemy = 5
                number_of_kill_before_boss = 15
                increase_enemy_by = 0.2
                player_points_in_func = 5
        return number_of_enemy, number_of_kill_before_boss, increase_enemy_by, player_points_in_func
    start = 0

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
        screen.blit(level, (270, 310))
        events = pygame.event.get()
        # Button.set_visible(False)
        # print(dropdown.getSelected())
        if button:
            button.hide()
        # button.hide()
        pygame_widgets.update(events)
        pygame.display.update()
        
        for event in events:
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
                    
                    number_of_enemy = 5
                    number_of_kill_before_boss = 15
                    increase_enemy_by = 0.2
                    difficulty = dropdown.getSelected()
                    # print(difficulty)
                    number_of_enemy, number_of_kill_before_boss, increase_enemy_by, player_points = setup_game(difficulty, number_of_enemy, number_of_kill_before_boss, increase_enemy_by)
                    
                    player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
                            # break
        # pygame_widgets.update(events)
        # pygame.display.update()
        # time.sleep(30)
        clock.tick(60)
        
    last_position = 0
   
    boss_life = LIFE_BOSS
    boss_to_come_out_with_bullet = False
    boss_to_come_out = False
    enemy_killed = 0
    boss_spawned = False
    boss_velocity = 3
    boss_move_timer = 0
    boss_move_interval = 60
    
        # print(difficulty)
    

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
            running = False
            game_lost = True
        # screen.fill(WHITE)
        screen.blit(player_img, player)
        screen.blit(player_point_text, (40, 30))

        if len(enemies) < number_of_enemy and not boss_to_come_out:
            if enemy_killed > number_of_kill_before_boss: # rimetti a 20
                # print("boss to come out")
                enemies = []
                boss_to_come_out = True
                # print(boss_to_come_out_with_bullet)
                if not boss_spawned:
                    boss_spawned = True
                    enemies_create = pygame.Rect(350, 100, 50, 50)
                    enemies.append(enemies_create)
                    
            else:
                # print(f"enemy killed {enemy_kille}")
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
                    # print(total_kill)
                    enemy_killed +=1
                    total_kill +=1
                    if total_kill % 50 == 0:
                        enemy_speed += increase_enemy_by 
                    if total_kill % 10 == 0:
                        # print("qui")
                        boss_to_come_out_with_bullet = True
                        # print(f"total kill {total_kill}")
                        # print(f"enemy speed {enemy_speed}")
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
                        boss_kill += 1
                        player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
                        screen.blit(player_point_text, (40, 30))
                        break
                    else:
                        boss_life -= 1
                
            if bullet.y < 0:
                bullets.remove(bullet)
                
        for bullet in boss_bullets[:]:
            bullet.y += boss_bullet_speed
            print(bullet.y)
            if bullet.colliderect(player):
                print("player touched")
                # player_points -= 1
                player_point_text = font_play.render(f"❤️ {player_points}", True, (0, 0, 0), WHITE)
                screen.blit(player_point_text, (40, 30))
                
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
        display_total_kill = font.render(f"You killed: {str(total_kill)}", True, (WHITE))
        display_boss_kill = font.render(f"Boss killed: {str(boss_kill)}", True, (WHITE))
        display_score = font.render(f"Total score: {str(total_kill + (boss_kill * 2))}", True, (WHITE))
        screen.blit(display_total_kill, (270, 380))
        screen.blit(display_boss_kill, (270, 420))
        screen.blit(display_score, (270, 460))

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        dropdown.hide()
        button.show()
        pygame_widgets.update(events)
        # print(events)
        # print(pygame_widgets)
        button.listen(events)
        button.draw()
        pygame.display.update()
        clock.tick(60)
        
# and after 300 kill and enemy will come out and will have a possibilty to shoot the player