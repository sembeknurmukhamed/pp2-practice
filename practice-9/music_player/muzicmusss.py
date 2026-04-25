import pygame

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((600, 400))
done = False

newspaper = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\Ripped-Newspaper-Artistic-Design-Inspiration-PNG.png")
newspaper.set_alpha(40)

vynil = pygame.image.load(r"C:\Users\tacoc\OneDrive\Рабочий стол\Gramophone_Vinyl_LP_Record_PNG_Transparent_Clip_Art_Image.png")
vynil = pygame.transform.scale(vynil, (500, 500)).convert_alpha()

vynil_lowalpha = pygame.transform.scale(vynil, (670, 670)).convert_alpha()
vynil_lowalpha.set_alpha(128)

vynil_avralpha = pygame.transform.scale(vynil, (570, 570)).convert_alpha()
vynil_avralpha.set_alpha(156)

VINYL_CENTER = (0, 0)

songs = [
   r"C:\Users\tacoc\OneDrive\Рабочий стол\Frank Ocean - White Ferrari.mp3",
   r"C:\Users\tacoc\OneDrive\Рабочий стол\Frank Ocean - Nights.mp3",
   r"C:\Users\tacoc\OneDrive\Рабочий стол\Frank Ocean - Crack Rock.mp3"
]
song_labels    = ["Frank Ocean - White Ferrari", "Frank Ocean - Nights", "Frank Ocean - Crack Rock"]
song_positions = [(340, 40), (335, 80), (320, 120)]
song_lines_y   = [35, 75, 115]

try:
   from mutagen.mp3 import MP3
   durations = [MP3(s).info.length * 1000 for s in songs]
except:
   durations = [230000, 306000, 175000]

current_song = 0

MUSIC_END = pygame.USEREVENT + 1
pygame.mixer.music.set_endevent(MUSIC_END)

# Ручной счётчик времени
is_playing      = False
paused_pos      = 0    # сохранённая позиция в мс
paused_offset   = 0    # сколько мс уже проиграло до текущего play()
play_start_tick = 0    # pygame.time.get_ticks() в момент запуска
manual_stop     = False

def get_pos_ms():
   # Текущая позиция в мс
   if is_playing:
      return paused_offset + (pygame.time.get_ticks() - play_start_tick)
   else:
      return paused_pos

def play_song(index):
   global is_playing, paused_pos, paused_offset, play_start_tick
   pygame.mixer.music.load(songs[index])
   pygame.mixer.music.play()
   is_playing      = True
   paused_pos      = 0
   paused_offset   = 0
   play_start_tick = pygame.time.get_ticks()

def do_pause():
   # Ставит на паузу и запоминает позицию
   global is_playing, paused_pos
   paused_pos = get_pos_ms()
   pygame.mixer.music.pause()
   is_playing = False

def do_unpause():
   # Снимает с паузы и продолжает счёт времени
   global is_playing, paused_offset, play_start_tick
   paused_offset   = paused_pos
   play_start_tick = pygame.time.get_ticks()
   pygame.mixer.music.unpause()
   is_playing = True

def format_time(ms):
   s = max(0, int(ms / 1000))
   return f"{s // 60:02}:{s % 60:02}"

# Шрифты
timer_font        = pygame.font.SysFont("timesnewroman", 14, 1)
font              = pygame.font.SysFont("timesnewroman", 12, 1)
songs_font        = pygame.font.SysFont("timesnewroman", 15, 1)
songs_font_active = pygame.font.SysFont("timesnewroman", 19, 1)

play_b = font.render("Play [P]",  True, (69, 66, 3))
stop_b = font.render("Stop [S]",  True, (69, 66, 3))
back_b = font.render("Back [B]",  True, (69, 66, 3))
next_b = font.render("Next [N]",  True, (69, 66, 3))
quit_b = font.render("Quit [Q]",  True, (69, 66, 3))

angle1 = angle2 = angle3 = 0
SLIDER_MIN = 24
clock = pygame.time.Clock()

while not done:
   for event in pygame.event.get():
      if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
         done = True

      if event.type == MUSIC_END:
         if not manual_stop:
            current_song = (current_song + 1) % len(songs)
            play_song(current_song)
         manual_stop = False

      if event.type == pygame.KEYDOWN:

         # [P]
         if event.key == pygame.K_p:
            if is_playing:
               do_pause()
            else:
               if paused_pos > 0:
                  do_unpause()   # продолжить с места паузы
               else:
                  play_song(current_song)  # начать заново

         # [S] с сохранением позиции
         elif event.key == pygame.K_s:
            if is_playing:
               do_pause()
            # если уже на паузе — ничего не делаем

         # [N]
         elif event.key == pygame.K_n:
            manual_stop = True
            current_song = (current_song + 1) % len(songs)
            play_song(current_song)

         # [B]
         elif event.key == pygame.K_b:
            manual_stop = True
            current_song = (current_song - 1) % len(songs)
            play_song(current_song)

   # Позиция и ползунок
   pos_ms   = get_pos_ms()
   duration = durations[current_song]
   progress = min(pos_ms / duration, 1.0) if duration > 0 else 0
   slider_point_x = int(SLIDER_MIN + progress * 550)
   slider_line_x  = slider_point_x - SLIDER_MIN

   # Отрисовка
   screen.fill((212, 202, 23))
   screen.blit(newspaper, (-25, 50))

   timer = timer_font.render(format_time(pos_ms), True, (69, 66, 3))
   screen.blit(timer, (535, 340))

   screen.blit(play_b, (24,  375))
   screen.blit(stop_b, (72,  375))
   screen.blit(back_b, (122, 375))
   screen.blit(next_b, (174, 375))
   screen.blit(quit_b, (228, 375))

   for i, (label, pos, line_y) in enumerate(zip(song_labels, song_positions, song_lines_y)):
      f = songs_font_active if (i == current_song and is_playing) else songs_font
      screen.blit(f.render(label, True, (69, 66, 3)), pos)
      pygame.draw.line(screen, (69, 66, 3), (pos[0], line_y), (600, line_y))

   rotated_v3 = pygame.transform.rotate(vynil_lowalpha, angle3)
   screen.blit(rotated_v3, rotated_v3.get_rect(center=VINYL_CENTER))

   rotated_v2 = pygame.transform.rotate(vynil_avralpha, angle2)
   screen.blit(rotated_v2, rotated_v2.get_rect(center=VINYL_CENTER))

   rotated_v1 = pygame.transform.rotate(vynil, angle1)
   screen.blit(rotated_v1, rotated_v1.get_rect(center=VINYL_CENTER))

   if is_playing:
      angle1 = (angle1 - 0.4) % 360
      angle2 = (angle2 - 0.2) % 360
      angle3 = (angle3 - 0.1) % 360

   pygame.draw.rect(screen, (168, 163, 56), pygame.Rect(24, 360, 550, 5))
   pygame.draw.rect(screen, (69, 66, 3),   pygame.Rect(24, 360, slider_line_x, 5))
   pygame.draw.circle(screen, (69, 66, 3), (slider_point_x, 362), 5)

   pygame.display.flip()
   clock.tick(30)