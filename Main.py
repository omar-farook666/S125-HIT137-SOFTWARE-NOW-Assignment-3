import random
import math
import pygame
from pygame import mixer

# Initialize the pygame
pygame.init()

# Create the screen
screen = pygame.display.set_mode((800, 600))

# Background
background = pygame.image.load("background.jpg")

# Background music
mixer.music.load("bg-1.mp3")
mixer.music.play(-1)


pygame.display.set_caption("S125 HIT137 SOFTWARE NOW - Assignment-3")
icon = pygame.image.load("cdu.jpg")
pygame.display.set_icon(icon)


score_value = 0
font = pygame.font.Font('Game Space Academy.otf', 40)
textX = 10
textY = 10


over_font = pygame.font.Font('Game Space Academy.otf', 64)



def show_score(x, y, score):
    score_text = font.render(f"Score: {score}", True, (255, 0, 0))
    screen.blit(score_text, (x, y))

def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(over_text, (200, 250))

def update_level(score):
    if score < 10:
        return 1, 0.3  
    elif score < 20:
        return 2, 0.5
    else:
        return 3, 0.7

def show_level(x, y, level):
    lvl_text = font.render(f"Level: {level}", True, (0, 255, 0))
    screen.blit(lvl_text, (x, y))

def you_win_text():
    win_text = over_font.render("YOU WIN!", True, (0, 255, 0))
    screen.blit(win_text, (200, 250))

def rect_collision(x1, y1, w1, h1, x2, y2, w2, h2):
    return (
        x1 < x2 + w2 and
        x1 + w1 > x2 and
        y1 < y2 + h2 and
        y1 + h1 > y2
    )

def distance_collision(obj1_x, obj1_y, obj2_x, obj2_y, threshold=27):
    distance = math.sqrt((math.pow(obj1_x - obj2_x, 2)) + (math.pow(obj1_y - obj2_y, 2)))
    return distance < threshold

# --- Game Classes ---

class Player:
    def __init__(self, x, y, image_path):
        self.img = pygame.image.load(image_path)
        self.x = x
        self.y = y
        self.x_change = 0
        self.y_change = 0
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def move(self):
        self.x += self.x_change
        
        if self.x <= 0:
            self.x = 0
        elif self.x >= 800 - self.width:
            self.x = 800 - self.width

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Bullet:
    def __init__(self, image_path, x, y):
        self.img = pygame.image.load(image_path)
        self.x = x
        self.y = y
        self.y_change = 2
        self.state = "ready"  
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def fire(self, screen):
        self.state = "fire"
        screen.blit(self.img, (self.x, self.y + 10))

    def move(self):
        if self.state == "fire":
            self.y -= self.y_change
            if self.y <= 0:
                self.y = 480
                self.state = "ready"

class Enemy:
    def __init__(self, x, y, image_path, speed):
        self.img = pygame.image.load(image_path)
        self.x = x
        self.y = y
        self.x_change = speed
        self.y_change = 30
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def move(self):
        self.x += self.x_change
        if self.x <= 0:
            self.x_change *= -1  
            self.y += self.y_change
        elif self.x >= 800 - self.width:
            self.x_change *= -1
            self.y += self.y_change

    def draw(self, screen):
        screen.blit(self.img, (self.x, self.y))

class Boss:
    def __init__(self, x, y, image_path, speed, health):
        self.img = pygame.transform.scale(pygame.image.load(image_path), (200, 200))
        self.x = x
        self.y = y
        self.x_change = speed
        self.y_change = 0
        self.health = health
        self.visible = False
        self.width = self.img.get_width()
        self.height = self.img.get_height()

    def move(self):
        self.x += self.x_change
        if self.x <= 0 or self.x >= 800 - self.width:
            self.x_change *= -1
            self.y += 30

    def draw(self, screen):
        if self.health > 0 and self.visible:
            screen.blit(self.img, (self.x, self.y))

    def take_damage(self):
        self.health -= 1
        explode_sound = mixer.Sound("explode.mp3")
        explode_sound.play()
        print(f"Boss hit! HP: {self.health}")

    def show_health(self, x, y):
        if self.visible and self.health > 0:
            health_text = font.render(f"Boss HP: {self.health}", True, (255, 255, 0))
            screen.blit(health_text, (x, y))


blast = pygame.image.load("explode.png")



player = Player(x=370, y=480, image_path="spaceship_hero.png")
bullet = Bullet(image_path="bullet.png", x=0, y=480)

enemies = []
num_of_enemies = 12
for _ in range(num_of_enemies):
    enemy_x = random.randint(0, 736)
    enemy_y = random.randint(20, 150)
    enemies.append(Enemy(x=enemy_x, y=enemy_y, image_path="alien2.png", speed=0.3))

boss = Boss(x=300, y=50, image_path="boss.gif", speed=0.5, health=10)

# --- Game Loop ---
running = True
game_state = "playing" 

while running:
    screen.fill((255, 0, 0))
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.x_change = -0.3
            if event.key == pygame.K_RIGHT:
                player.x_change = 0.3
            if event.key == pygame.K_SPACE:
                if bullet.state == "ready":
                    bullet_sound = mixer.Sound("blaster.wav")
                    bullet_sound.play()
                    bullet.x = player.x + (player.width / 2) - (bullet.width / 2) 
                    bullet.fire(screen)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                player.x_change = 0

    if game_state == "playing":
        player.move()
        player.draw(screen)
        bullet.move()
        if bullet.state == "fire":
            bullet.fire(screen) 

        level, enemy_speed = update_level(score_value)

        
        if score_value >= 25:
            boss.visible = True
            if boss.health > 0:
                boss.move()
                boss.draw(screen)
                boss.show_health(600, 10)

                
                if bullet.state == "fire":
                    if rect_collision(boss.x, boss.y, boss.width, boss.height, bullet.x, bullet.y, bullet.width, bullet.height):
                        bullet.y = 480
                        bullet.state = "ready"
                        boss.take_damage()
                        if boss.health <= 0:
                            game_state = "you_win"
                            mixer.music.stop() 

                
                if boss.y + boss.height > player.y:
                    game_state = "game_over"
                    mixer.music.stop() 

            else: 
                game_state = "you_win"
                mixer.music.stop() 

        
        if not boss.visible:
            for i, enemy in enumerate(enemies):
                
                if enemy.y > 440:
                    game_state = "game_over"
                    mixer.music.stop() 
                    break 

                enemy.x_change = enemy_speed if enemy.x_change > 0 else -enemy_speed
                enemy.move()
                enemy.draw(screen)

                
                if distance_collision(enemy.x, enemy.y, bullet.x, bullet.y):
                    screen.blit(blast, (enemy.x, enemy.y)) 
                    explode_sound = mixer.Sound("explode.mp3")
                    explode_sound.play()
                    bullet.y = 480
                    bullet.state = "ready"
                    score_value += 1
                    enemy.x = random.randint(0, 736)
                    enemy.y = random.randint(20, 150)

    
    if game_state == "game_over":
        game_over_text()
        player.y = 2000 
        for enemy in enemies:
            enemy.y = 2000 
    elif game_state == "you_win":
        you_win_text()
        player.y = 2000 
        for enemy in enemies:
            enemy.y = 2000 
        if boss.health <= 0: 
            boss.visible = False


    show_score(textX, textY, score_value)
    show_level(textX, textY + 40, level)

    pygame.display.update()