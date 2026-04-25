import pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()
done = False
x, y = 200, 200

while not done:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         done = True

   screen.fill((255, 255, 255))

   pressed = pygame.key.get_pressed()
   if pressed[pygame.K_UP]:    y -= 20
   if pressed[pygame.K_DOWN]:  y += 20
   if pressed[pygame.K_LEFT]:  x -= 20
   if pressed[pygame.K_RIGHT]: x += 20

   # Не выходить за границы
   x = max(25, min(375, x))
   y = max(25, min(375, y))

   pygame.draw.circle(screen, (133, 13, 17), (x, y), 25)
   pygame.display.flip()
   clock.tick(30)
