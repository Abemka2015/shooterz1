from pygame import *
from random import randint
import time as t_time

# Initialize Pygame
font.init()
mixer.init()

# --- Constants and Assets ---
# Fonts
font1 = font.SysFont('Arial', 80)
win = font1.render('YOU WIN!', True, (255, 255, 255))
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
font2 = font.SysFont('Arial', 36)

# Sounds
mixer.music.load('space.ogg')
mixer.music.play()
fire_sound = mixer.Sound('fire.ogg')
explosion_sound = mixer.Sound('explosion.wav')  # Add explosion sound

# Images
img_back = "galaxy.jpg"
img_bullet = "bullet.png"
img_hero = "rocket.png"
img_enemy = "ufo.png"
img_explosion = ["explosion1.png", "explosion2.png", "explosion3.png", "explosion4.png", "explosion5.png"] # Add explosion images

# Game Variables
score = 0
goal = 10
lost = 0
max_lost = 3

# Window settings
win_width = 700
win_height = 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter")
background = transform.scale(image.load(img_back), (win_width, win_height))

# --- Classes ---
class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        sprite.Sprite.__init__(self)
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        bullet = Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15)
        bullets.add(bullet)

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            lost += 1

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

class Timer():
    def __init__(self, sec):
        self.sec = sec
        self.start_time = t_time.time()
        self.end = self.start_time + sec
    
    def is_running(self):
        return t_time.time() < self.end
    
    def is_end(self):
        return t_time.time() >= self.end
    
    def reset(self):
        self.end = t_time.time() + self.sec

class Explosion(GameSprite):
    def __init__(self, x, y, images):
        super().__init__(images[0], x, y, 80, 80, 0)
        self.images = [transform.scale(image.load(img), (80, 80)) for img in images]
        self.frame = 0
        self.timer = Timer(0.1) # change frame every 0.1 sec

    def update(self):
        if self.timer.is_end():
            self.timer.reset()
            self.frame += 1
            if self.frame >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame]

# --- Sprite Groups ---
ship = Player(img_hero, 5, win_height - 100, 80, 100, 10)
monsters = sprite.Group()
for i in range(1, 6):
    monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
    monsters.add(monster)
bullets = sprite.Group()
explosions = sprite.Group() # add explosions group

# --- Game Loop ---
finish = False
run = True
while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                fire_sound.play()
                ship.fire()

    if not finish:
        window.blit(background, (0, 0))

        text = font2.render("Счет: " + str(score), 1, (255, 255, 255))
        window.blit(text, (10, 20))
        text_lose = font2.render("Пропущено: " + str(lost), 1, (255, 255, 255))
        window.blit(text_lose, (10, 50))

        ship.update()
        monsters.update()
        bullets.update()
        explosions.update() # update explosions

        ship.reset()
        monsters.draw(window)
        bullets.draw(window)
        explosions.draw(window) # draw explosions

        collides = sprite.groupcollide(monsters, bullets, True, True)
        for c in collides:
            score += 1
            explosion_sound.play() # play explosion sound
            explosion = Explosion(c.rect.x, c.rect.y, img_explosion) # create explosion
            explosions.add(explosion)
            monster = Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, randint(1, 5))
            monsters.add(monster)

        if sprite.spritecollide(ship, monsters, False) or lost >= max_lost:
            finish = True
            window.blit(lose, (200, 200))

        if score >= goal:
            finish = True
            window.blit(win, (200, 200))

        display.update()
    time.delay(50)
