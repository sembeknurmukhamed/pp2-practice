import pygame
import sys
import random
from pygame.locals import *

pygame.init()

# [ПУТИ К РЕСУРСАМ]
# Все картинки берутся из папки materials рядом со скриптом
import os
BASE = os.path.join(os.path.dirname(__file__), "materials")

bg_glade  = os.path.join(BASE, "glade.jpg")
bg_bush   = os.path.join(BASE, "snake_background.png")

# Спрайты змейки (SPRITE_* ниже)
snake_sprites = [
    os.path.join(BASE, "snakehead.png"),   # голова
    os.path.join(BASE, "snakebody.png"),   # прямое тело
    os.path.join(BASE, "snakeside1.png"),  # поворот право/вверх вниз/лево
    os.path.join(BASE, "snakeside2.png"),  # поворот лево/вверх вниз/право
    os.path.join(BASE, "snakeside3.png"),  # поворот право/вниз вверх/лево
    os.path.join(BASE, "snakeside4.png"),  # поворот лево/вниз вверх/право
    os.path.join(BASE, "snaketale.png"),   # хвост 
]

# Кадры анимации яблока
apple_frames = [
    os.path.join(BASE, "XLYI5953.PNG"),
    os.path.join(BASE, "MAWA5410.PNG"),
    os.path.join(BASE, "JVYL6650.PNG"),
    os.path.join(BASE, "LVLP4508.PNG"),
    os.path.join(BASE, "NBUN0214.PNG"),
]

# [НАСТРОЙКИ]
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 400
TILE          = 20          # размер клетки в пикселях
COLS          = SCREEN_WIDTH  // TILE   # 20 колонок
ROWS          = SCREEN_HEIGHT // TILE   # 20 строк

FPS_BASE      = 10           # начальная скорость (кадров/сек логики)
SPEED_STEP    = 1           # +1 кадр/сек за каждый уровень
FOOD_PER_LVL  = 4           # еды до следующего уровня

# [НАПРАВЛЕНИЯ] — вектор (dx, dy) в клетках
RIGHT = ( 1,  0)
LEFT  = (-1,  0)
UP    = ( 0, -1)
DOWN  = ( 0,  1)

# [ЦВЕТА]
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)
RED    = (200, 30, 30)

# [ЭКРАН И ШРИФТ]
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake")

font_big   = pygame.font.SysFont("Verdana", 22, bold=True)
font_small = pygame.font.SysFont("Verdana", 14)
clock      = pygame.time.Clock()

# [ЗАГРУЗКА И МАСШТАБИРОВАНИЕ ФОНОВ]
background      = pygame.transform.scale(pygame.image.load(bg_glade), (SCREEN_WIDTH, SCREEN_HEIGHT))

# [ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ] — поворот спрайта
def rot_img(surf, angle):
    """Возвращает повёрнутую на angle градусов копию изображения."""
    return pygame.transform.rotate(surf, angle)

# [КЛАСС ЯБЛОКА]
class Apple:
    """Анимированная еда для змейки."""

    ANIM_SPEED = 7  # тиков между кадрами анимации
    LIFETIME = 300

    def __init__(self):
        # Загружаем все кадры и масштабируем под клетку
        self.frames = [
            pygame.transform.scale(pygame.image.load(p), (TILE, TILE))
            for p in apple_frames
        ]
        self.frame_idx   = 0
        self.anim_timer  = 0
        self.grid_pos    = (0, 0)   # позиция в клетках (col, row)
        self.rect        = pygame.Rect(0, 0, TILE, TILE)

        self.value = 10
        self.timer = 0
    
    @property
    def image(self):
        return self.frames[self.frame_idx]

    def respawn(self, occupied: list):
        """Случайная позиция вне стен и вне тела змейки."""
        free = [
            (c, r)
            for c in range(1, COLS - 1)
            for r in range(1, ROWS - 1)
            if (c, r) not in occupied
        ]
        self.grid_pos = random.choice(free) if free else (COLS // 2, ROWS // 2)
        self.rect.topleft = (self.grid_pos[0] * TILE, self.grid_pos[1] * TILE)
        
        self.value = random.choices([10, 30, 50], weights=[70, 20, 10])[0]
        self.timer = 0

    def update(self):
        """Прокрутка анимации."""
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer  = 0
            self.frame_idx   = (self.frame_idx + 1) % len(self.frames)

        self.timer += 1

    def is_expired(self):
        return self.timer > self.LIFETIME

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        
    #     txt = font_small.render(str(self.value), True, YELLOW)
    #     surface.blit(txt, self.rect.topleft)

# [КЛАСС ЗМЕЙКИ]
class Snake:
    """
    Змейка на сетке.
    body — список (col, row), body[0] — голова, body[-1] — хвост.
    """

    def __init__(self):
        # Загружаем исходные спрайты (все смотрят «вправо»)
        self.raw = [
            pygame.transform.scale(pygame.image.load(p), (TILE, TILE))
            for p in snake_sprites
        ]
        self.reset()

    # индексы в self.raw
    HEAD  = 0
    BODY  = 1
    S1    = 2   # поворот право/вверх вниз/лево
    S2    = 3   # поворот лево/вверх вниз/право
    S3    = 4   # поворот право/вниз вверх/лево
    S4    = 5   # поворот лево/вниз вверх/право
    TAIL  = 6

    def reset(self):
        # Сброс к начальному состоянию (3 клетки по центру)
        cx, cy = COLS // 2, ROWS // 2
        # Начальное тело: [голова, средняя, хвост]
        self.body      = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = RIGHT          # текущее направление
        self.next_dir  = RIGHT          # следующее (из очереди ввода)
        self.grew      = False          # флаг роста на следующем шаге

    # ввод
    def handle_key(self, key):
        # Запоминаем желаемое направление (нельзя разворот на 180°)
        mapping = {
            K_RIGHT: RIGHT, K_d: RIGHT,
            K_LEFT:  LEFT,  K_a: LEFT,
            K_UP:    UP,    K_w: UP,
            K_DOWN:  DOWN,  K_s: DOWN,
        }
        new = mapping.get(key)
        if new is None:
            return
        # Запрещаем разворот: если сумма dx даёт 0 и dy даёт 0 — это 180°
        if (new[0] + self.direction[0] != 0 or new[1] + self.direction[1] != 0):
            self.next_dir = new

    # шаг движения
    def move(self):
        # Перемещает змейку на одну клетку в текущем направлении
        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy  = self.direction
        new_head = (hx + dx, hy + dy)

        self.body.insert(0, new_head)

        # Если snake съела еду - не удаляем хвост (рост)
        if self.grew:
            self.grew = False
        else:
            self.body.pop()

    def grow(self):
        #Помечаем, что на следующем шаге хвост не убирается
        self.grew = True

    # проверка столкновений
    def hits_wall(self) -> bool:
        # True, если голова вышла за границы поля
        hx, hy = self.body[0]
        return not (0 <= hx < COLS and 0 <= hy < ROWS)

    def hits_self(self) -> bool:
        # True, если голова столкнулась с собственным телом
        return self.body[0] in self.body[1:]

    def is_dead(self) -> bool:
        return self.hits_wall() or self.hits_self()

    # рендер
    def _choose_segment(self, idx: int):
        # Возвращает правильный (повёрнутый) спрайт для сегмента body[idx].
        raw = self.raw

        # ГОЛОВА
        if idx == 0:
            angle_map = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: -90}
            return rot_img(raw[self.HEAD], angle_map[self.direction])

        # ХВОСТ
        if idx == len(self.body) - 1:
            # Направление от предыдущего к хвосту
            px, py = self.body[idx - 1]
            tx, ty = self.body[idx]
            d = (tx - px, ty - py)
            angle_map = {RIGHT: 0, LEFT: 180, UP: 90, DOWN: -90}
            return rot_img(raw[self.TAIL], angle_map.get(d, 0))

        # ТЕЛО (средние сегменты) 
        prev = self.body[idx - 1]
        curr = self.body[idx]
        nxt  = self.body[idx + 1]

        # Вектор «откуда пришли» и «куда идём»
        from_d = (curr[0] - prev[0], curr[1] - prev[1])  # направление от prev к curr
        to_d   = (nxt[0]  - curr[0], nxt[1]  - curr[1])  # направление от curr к next

        # Если оба вектора коллинеарны - прямое тело
        if from_d == to_d:
            if from_d in (RIGHT, LEFT):
                return rot_img(raw[self.BODY], 0)
            else:
                return rot_img(raw[self.BODY], 90)

        # Поворот - выбираем нужный corner-спрайт
        pair = (from_d, to_d)
        if pair in ((RIGHT, DOWN), (UP, LEFT)):
            return rot_img(raw[self.S2], 0)
        if pair in ((RIGHT, UP), (DOWN, LEFT)):
            return rot_img(raw[self.S3], 90)
        if pair in ((LEFT, DOWN), (UP, RIGHT)):
            return rot_img(raw[self.S3], -90)
        if pair in ((LEFT, UP), (DOWN, RIGHT)):
            return rot_img(raw[self.S2], 180)

        # Запасной вариант
        return rot_img(raw[self.BODY], 0)

    def draw(self, surface):
        for i, (col, row) in enumerate(self.body):
            sprite = self._choose_segment(i)
            surface.blit(sprite, (col * TILE, row * TILE))

# [HUD]
def draw_hud(surface, score, level):
    # Рисует счёт и уровень в левом верхнем углу с обводкой
    texts = [
        font_big.render(f"Score: {score}", True, YELLOW),
        font_small.render(f"Level: {level}", True, WHITE),
    ]
    shadow_off = 1
    for i, txt in enumerate(texts):
        # тень
        shadow = pygame.Surface(txt.get_size(), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 0))
        y = 6 + i * 22
        surface.blit(font_big.render(f"Score: {score}", True, BLACK) if i == 0
                     else font_small.render(f"Level: {level}", True, BLACK),
                     (6 + shadow_off, y + shadow_off))
        surface.blit(txt, (6, y))

# [ЭКРАН GAME OVER]
def show_game_over(surface, score):
    # Блокирующий экран Game Over; возвращает True — играть снова, False — выход
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    lines = [
        font_big.render("GAME OVER",           True, RED),
        font_big.render(f"Score: {score}",     True, YELLOW),
        font_small.render("R — снова  /  Q — выйти", True, WHITE),
    ]
    total_h = sum(l.get_height() + 8 for l in lines)
    y = (SCREEN_HEIGHT - total_h) // 2
    for line in lines:
        x = (SCREEN_WIDTH - line.get_width()) // 2
        surface.blit(line, (x, y))
        y += line.get_height() + 8

    pygame.display.update()

    while True:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                pygame.quit(); sys.exit()
            if ev.type == KEYDOWN:
                if ev.key == K_r:
                    return True
                if ev.key in (K_q, K_ESCAPE):
                    return False

# [ГЛАВНЫЙ ИГРОВОЙ ЦИКЛ]
def main():
    snake = Snake()
    apple = Apple()
    apple.respawn(snake.body)

    score        = 0
    level        = 1
    food_count   = 0          # сколько еды съедено на текущем уровне
    logic_fps    = FPS_BASE   # тиков логики в секунду

    # Таймер логики — движение змейки не привязано к FPS рендера
    LOGIC_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(LOGIC_EVENT, 1000 // logic_fps)

    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == KEYDOWN:
                snake.handle_key(event.key)
                if event.key == K_ESCAPE:
                    pygame.quit(); sys.exit()

            # Тик логики: движение и проверка столкновений
            if event.type == LOGIC_EVENT:
                snake.move()

                # Столкновение со стеной / собой
                if snake.is_dead():
                    pygame.time.set_timer(LOGIC_EVENT, 0)   # останавливаем таймер
                    # Рисуем последний кадр перед паузой
                    screen.blit(background, (0, 0))
                    snake.draw(screen)
                    apple.draw(screen)
                    draw_hud(screen, score, level)
                    pygame.display.update()
                    pygame.time.wait(300)

                    play_again = show_game_over(screen, score)
                    if play_again:
                        # Полный сброс
                        snake.reset()
                        apple.respawn(snake.body)
                        score      = 0
                        level      = 1
                        food_count = 0
                        logic_fps  = FPS_BASE
                        pygame.time.set_timer(LOGIC_EVENT, 1000 // logic_fps)
                    else:
                        pygame.quit(); sys.exit()
                    continue

                # Поедание яблока
                if snake.body[0] == apple.grid_pos:
                    snake.grow()
                    score += apple.value
                    food_count += 1

                    # Повышение уровня
                    if food_count >= FOOD_PER_LVL:
                        level      += 1
                        food_count  = 0
                        logic_fps   = FPS_BASE + (level - 1) * SPEED_STEP
                        # Обновляем интервал таймера
                        pygame.time.set_timer(LOGIC_EVENT, 1000 // logic_fps)

                    apple.respawn(snake.body)

        # Обновление анимации яблока
        apple.update()

        if apple.is_expired():
         apple.respawn(snake.body)

        # Рендер
        screen.blit(background, (0, 0))          # зелёная трава

        snake.draw(screen)
        apple.draw(screen)
        draw_hud(screen, score, level)

        pygame.display.update()
        clock.tick(60)   # рендер всегда 60 FPS, логика - через USEREVENT


if __name__ == "__main__":
    main()
