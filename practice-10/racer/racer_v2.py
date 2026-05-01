import pygame, sys
from pygame.locals import *
import random, time
pygame.init()

# [MATERIALS PATH]
green_car = r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\CarGreenFront.png"
red_car = r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\CarRedFront.png"
coin_frames_paths = [
   r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\KBGU4713.PNG",   # 0deg
   r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\DRGF5324.PNG",   # 45deg
   r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\FURF8350.PNG",   # 90deg
   r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\GXNF9041.PNG",   # 135deg
]

# [FPS]
FPS = 60
clock = pygame.time.Clock()

# [COLORS]
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)

# [SOME VARIABLES]
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
SPEED = 5
SCORE = 0

# [FONTS]
font_small = pygame.font.SysFont("Verdana", 20)
font = pygame.font.SysFont("Verdana", 30)
game_over = font.render("Game Over", True, BLACK)

# [BACKGROUND ROAD]
background = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\pixel_art_road_green_land.png")
bg_y = 0
bg_h = background.get_height()

# [SCREEN]
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill(WHITE)
pygame.display.set_caption("Racer")

# [COLLECTING MUSIC TRIGGER]
pygame.mixer.music.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\pp_2\practice-10\racer\materials\coin_recieved.mp3")
pygame.mixer.music.set_volume(0.1)

# [ENEMY]
class Enemy(pygame.sprite.Sprite):
   def __init__(self):
      super().__init__()
      self.image = pygame.image.load(red_car)
      self.rect = self.image.get_rect()
      self.rect.center = (random.randint(90, SCREEN_WIDTH-90), 0)

   def move(self):
      global SCORE
      self.rect.move_ip(0, SPEED)
      if (self.rect.bottom > 690):
         SCORE += 1
         self.rect.top = 0
         self.rect.center = (random.randint(90, 310), -240)

# [COIN]
class Coin(pygame.sprite.Sprite):
   def __init__(self):
      super().__init__()
      # Загружаем все кадры анимации
      self.frames = [pygame.image.load(p) for p in coin_frames_paths]
      self.frame_index = 0
      self.animation_speed = 7   # смена кадра каждые N тиков
      self.animation_timer = 0
      self.image = self.frames[self.frame_index]
      self.rect = self.image.get_rect()
      self.rect.center = (random.randint(90, SCREEN_WIDTH - 90), 0)

   def respawn(self):
      self.rect.center = (random.randint(90, SCREEN_WIDTH - 90), -60)

   def move(self):
      self.rect.move_ip(0, SPEED)

      # Анимация — листаем кадры
      self.animation_timer += 1
      if self.animation_timer >= self.animation_speed:
         self.animation_timer = 0
         self.frame_index = (self.frame_index + 1) % len(self.frames)
         self.image = self.frames[self.frame_index]

      # Монета ушла за экран — респавн без очков
      if self.rect.top > SCREEN_HEIGHT:
         self.respawn()

# [PLAYER]
class Player(pygame.sprite.Sprite):
   def __init__(self):
      super().__init__()
      self.image = pygame.image.load(green_car)
      self.rect = self.image.get_rect()
      self.rect.center = (160, 520)

   def move(self):
      pressed = pygame.key.get_pressed()
      if self.rect.left > 70:
         if pressed[K_LEFT]:
            self.rect.move_ip(-5, 0)
      if self.rect.right < SCREEN_WIDTH - 70:
         if pressed[K_RIGHT]:
            self.rect.move_ip(5, 0)

P1 = Player()
E1 = Enemy()
C1 = Coin()

# [SPRITES GROUP]
enemies = pygame.sprite.Group()
enemies.add(E1)
coins = pygame.sprite.Group()
coins.add(C1)
all_sprites = pygame.sprite.Group()
all_sprites.add(P1)
all_sprites.add(E1)
all_sprites.add(C1)

# [USER EVENT — скорость растёт каждую секунду]
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 1000)

# [GAME LOOP]
while True:
   for event in pygame.event.get():
      if event.type == INC_SPEED:
         SPEED += 0.05
      if event.type == QUIT:
         pygame.quit()
         sys.exit()

   # Бесконечная дорога
   bg_y += SPEED
   if bg_y >= bg_h:
      bg_y = 0

   screen.blit(background, (0, bg_y))
   screen.blit(background, (0, bg_y - bg_h))

   # Счёт
   scores = font_small.render(f"Coins: {SCORE}", True, BLACK)
   screen.blit(scores, (10, 10))

   # Двигаем и рисуем спрайты
   for entity in all_sprites:
      entity.move()
      screen.blit(entity.image, entity.rect)

   # Проверка сбора монеты
   collected = pygame.sprite.spritecollideany(P1, coins)
   if collected:
      pygame.mixer.music.play()
      SCORE += 1
      collected.respawn()
   
   # Проверка на столкновение
   if pygame.sprite.spritecollideany(P1, enemies):
      screen.fill(RED)
      screen.blit(game_over, (110, 250))
      pygame.display.update()
      for entity in all_sprites:
         entity.kill()
      time.sleep(1)
      pygame.quit()
      sys.exit()

   pygame.display.update()
   clock.tick(FPS)
