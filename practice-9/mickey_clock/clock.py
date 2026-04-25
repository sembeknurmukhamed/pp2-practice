import pygame
import sys
import datetime
import os
pygame.init()

SIZE = 800
screen = pygame.display.set_mode((SIZE, SIZE))
fps_clock = pygame.time.Clock()
 
clock_face = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\DUIK5642.PNG")
hour_img = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\SWRA0740.PNG")
minute_img = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\XKSJ9149.PNG")
second_img = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\GJNQ3302.PNG")
 
def scale(surf): return pygame.transform.scale(surf, (SIZE, SIZE))
clock_face = scale(clock_face)
hour_img   = scale(hour_img)
minute_img = scale(minute_img)
second_img = scale(second_img)
 
HOUR_NATURAL   = 270
MINUTE_NATURAL = 57
SECOND_NATURAL = 225 
 
CENTER = (SIZE // 2, SIZE // 2)
 
def rotate_hand(img, target_angle_cw, natural_angle_cw):
   """Поворачивает руку так, чтобы она указывала на target_angle_cw."""
   rotation = -(target_angle_cw - natural_angle_cw)
   rotated  = pygame.transform.rotate(img, rotation)
   rect     = rotated.get_rect(center=CENTER)
   return rotated, rect
 
def get_time_angles():
   now = datetime.datetime.now()   # ← убрать markdown-форматирование
   h  = now.hour % 12
   m  = now.minute
   s  = now.second
   ms = now.microsecond / 1_000_000

   second_angle = (s + ms) * 6
   minute_angle = m * 6 + s * 0.1
   hour_angle   = h * 30 + m * 0.5
   return hour_angle, minute_angle, second_angle
 
while True:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         pygame.quit()
         sys.exit()
      if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
         pygame.quit()
         sys.exit()
 
   hour_angle, minute_angle, second_angle = get_time_angles()
 
   screen.blit(clock_face, (0, 0))
 
   h_surf, h_rect = rotate_hand(hour_img, hour_angle, HOUR_NATURAL)
   screen.blit(h_surf, h_rect)
 
   m_surf, m_rect = rotate_hand(minute_img, minute_angle, MINUTE_NATURAL)
   screen.blit(m_surf, m_rect)
 
   s_surf, s_rect = rotate_hand(second_img, second_angle, SECOND_NATURAL)
   screen.blit(s_surf, s_rect)
 
   pygame.display.flip()
   fps_clock.tick(60)
 
