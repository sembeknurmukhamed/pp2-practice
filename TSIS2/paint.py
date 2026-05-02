import pygame
import sys
from datetime import datetime
from collections import deque

pygame.init()
clock = pygame.time.Clock()

# ── Размеры окна ──────────────────────────────────────────────────────────────
WIDTH, HEIGHT   = 1000, 650
TOOLBAR_WIDTH   = 150
PALETTE_HEIGHT  = 80

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

# ── Цвета UI ──────────────────────────────────────────────────────────────────
WHITE     = (255, 255, 255)
GRAY      = (230, 230, 230)
DARK_GRAY = (40,  40,  40)
BLUE      = (70,  130, 255)
GREEN     = (50,  180, 80)

# ── Палитра ───────────────────────────────────────────────────────────────────
palette_colors = [
    (0,0,0),   (255,255,255),(255,0,0),   (0,255,0),
    (0,0,255), (255,255,0),  (255,0,255), (0,255,255),
    (128,0,0), (0,128,0),   (0,0,128),   (128,128,0),
    (128,0,128),(0,128,128)
]

# ── Шрифты ────────────────────────────────────────────────────────────────────
font      = pygame.font.SysFont("Segoe UI", 13, bold=True)
text_font = pygame.font.SysFont("Segoe UI", 20)

# ── Состояние инструментов ────────────────────────────────────────────────────
current_color    = (0, 0, 0)
tool             = "brush"
brush_size       = 5          # текущий размер (1..50, меняется колёсиком)
size_preset      = "medium"   # "small" | "medium" | "large"

BRUSH_SIZES = {"small": 2, "medium": 5, "large": 10}
size_presets = ["small", "medium", "large"]

drawing         = False
start_pos       = None
prev_pos        = None        # предыдущая точка (для карандаша)
preview_surface = None

# ── Текстовый инструмент ──────────────────────────────────────────────────────
text_active  = False
text_pos     = None           # позиция на холсте (без смещения тулбара)
text_buffer  = ""
text_color   = (0, 0, 0)

# ── Уведомление о сохранении ──────────────────────────────────────────────────
save_msg      = ""
save_msg_time = 0

# ── Холст ─────────────────────────────────────────────────────────────────────
CANVAS_W = WIDTH - TOOLBAR_WIDTH
CANVAS_H = HEIGHT - PALETTE_HEIGHT
canvas = pygame.Surface((CANVAS_W, CANVAS_H))
canvas.fill(WHITE)

# ── Список инструментов ───────────────────────────────────────────────────────
tools = [
    "brush", "pencil", "line",
    "rectangle", "circle",
    "square", "right_triangle",
    "equilateral_triangle", "rhombus",
    "fill", "text", "eraser"
]

TOOL_NAMES = {
    "brush":                "Brush",
    "pencil":               "Pencil",
    "line":                 "Line",
    "rectangle":            "Rect",
    "circle":               "Circle",
    "square":               "Square",
    "right_triangle":       "Right Tri",
    "equilateral_triangle": "Equi Tri",
    "rhombus":              "Rhombus",
    "fill":                 "Fill",
    "text":                 "Text",
    "eraser":               "Eraser",
}

# ── Размеры кнопок тулбара ────────────────────────────────────────────────────
BTN_H   = 42
BTN_GAP = 50          # шаг между кнопками инструментов
BTN_TOP = 5


# ═════════════════════════════════════════════════════════════════════════════
# Вспомогательные функции рисования
# ═════════════════════════════════════════════════════════════════════════════
def draw_square(surface, color, start, end, thick=2):
    size = min(abs(end[0]-start[0]), abs(end[1]-start[1]))
    rect = pygame.Rect(start[0], start[1], size, size)
    pygame.draw.rect(surface, color, rect, thick)


def draw_right_triangle(surface, color, start, end, thick=2):
    pts = [start, (end[0], start[1]), end]
    pygame.draw.polygon(surface, color, pts, thick)


def draw_equilateral_triangle(surface, color, start, end, thick=2):
    w = end[0] - start[0]
    h = abs(w * (3**0.5) / 2)
    pts = [
        (start[0],         start[1] + h),
        (start[0] + w,     start[1] + h),
        (start[0] + w / 2, start[1])
    ]
    pygame.draw.polygon(surface, color, pts, thick)


def draw_rhombus(surface, color, start, end, thick=2):
    mx = (start[0] + end[0]) // 2
    my = (start[1] + end[1]) // 2
    pts = [
        (mx,       start[1]),
        (end[0],   my),
        (mx,       end[1]),
        (start[0], my)
    ]
    pygame.draw.polygon(surface, color, pts, thick)


def draw_shape_on(surface, shape, start, end, color, thick):
    """Рисует нужную фигуру на surface."""
    if shape == "rectangle":
        r = pygame.Rect(start, (end[0]-start[0], end[1]-start[1]))
        pygame.draw.rect(surface, color, r, thick)
    elif shape == "circle":
        dx, dy = end[0]-start[0], end[1]-start[1]
        radius = int((dx**2 + dy**2)**0.5)
        pygame.draw.circle(surface, color, start, radius, thick)
    elif shape == "line":
        pygame.draw.line(surface, color, start, end, thick)
    elif shape == "square":
        draw_square(surface, color, start, end, thick)
    elif shape == "right_triangle":
        draw_right_triangle(surface, color, start, end, thick)
    elif shape == "equilateral_triangle":
        draw_equilateral_triangle(surface, color, start, end, thick)
    elif shape == "rhombus":
        draw_rhombus(surface, color, start, end, thick)


# ═════════════════════════════════════════════════════════════════════════════
# Flood-fill (BFS итеративный, без рекурсии)
# ═════════════════════════════════════════════════════════════════════════════
def flood_fill(surface, sx, sy, fill_color):
    target = surface.get_at((sx, sy))[:3]
    fill3  = tuple(fill_color[:3])
    if target == fill3:
        return

    w, h    = surface.get_size()
    visited = bytearray(w * h)   # быстрее чем set()
    queue   = deque()
    queue.append((sx, sy))

    surface.lock()
    try:
        while queue:
            x, y = queue.popleft()
            idx  = y * w + x
            if visited[idx]:
                continue
            if surface.get_at((x, y))[:3] != target:
                continue
            visited[idx] = 1
            surface.set_at((x, y), fill_color)

            if x + 1 < w:  queue.append((x+1, y))
            if x - 1 >= 0: queue.append((x-1, y))
            if y + 1 < h:  queue.append((x, y+1))
            if y - 1 >= 0: queue.append((x, y-1))
    finally:
        surface.unlock()


# ═════════════════════════════════════════════════════════════════════════════
# Сохранение
# ═════════════════════════════════════════════════════════════════════════════
def save_canvas():
    global save_msg, save_msg_time
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    save_msg      = f"Saved: {filename}"
    save_msg_time = pygame.time.get_ticks()
    print(save_msg)


# ═════════════════════════════════════════════════════════════════════════════
# Отрисовка UI
# ═════════════════════════════════════════════════════════════════════════════
def draw_toolbar():
    pygame.draw.rect(screen, GRAY, (0, 0, TOOLBAR_WIDTH, HEIGHT))

    # Кнопки инструментов
    for i, t in enumerate(tools):
        y    = BTN_TOP + i * BTN_GAP
        rect = pygame.Rect(10, y, TOOLBAR_WIDTH - 20, BTN_H)
        col  = BLUE if t == tool else DARK_GRAY
        pygame.draw.rect(screen, col, rect, border_radius=8)
        lbl  = font.render(TOOL_NAMES[t], True, WHITE)
        screen.blit(lbl, (rect.x + 8, rect.y + 14))

    # Кнопки размера кисти
    size_section_y = BTN_TOP + len(tools) * BTN_GAP + 4
    lbl = font.render("Size (1/2/3):", True, DARK_GRAY)
    screen.blit(lbl, (8, size_section_y))

    btn_w = (TOOLBAR_WIDTH - 20) // 3
    for i, sname in enumerate(size_presets):
        bx   = 10 + i * btn_w
        by   = size_section_y + 18
        rect = pygame.Rect(bx, by, btn_w - 4, 26)
        col  = GREEN if sname == size_preset else DARK_GRAY
        pygame.draw.rect(screen, col, rect, border_radius=6)
        stxt = font.render(f"{i+1}", True, WHITE)
        screen.blit(stxt, (rect.centerx - stxt.get_width()//2, rect.y + 6))


def draw_palette():
    pygame.draw.rect(screen, GRAY,
                     (TOOLBAR_WIDTH, HEIGHT - PALETTE_HEIGHT, WIDTH, PALETTE_HEIGHT))
    for i, color in enumerate(palette_colors):
        x    = TOOLBAR_WIDTH + 10 + i * 60
        y    = HEIGHT - 60
        rect = pygame.Rect(x, y, 40, 40)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if color == current_color:
            pygame.draw.rect(screen, BLUE, rect, 3, border_radius=8)


def draw_info():
    txt = font.render(
        f"{TOOL_NAMES.get(tool, tool)}  |  size: {brush_size}px  |  Ctrl+S = save",
        True, DARK_GRAY
    )
    screen.blit(txt, (TOOLBAR_WIDTH + 10, 10))

    # Уведомление о сохранении (показываем 3 секунды)
    if save_msg and pygame.time.get_ticks() - save_msg_time < 3000:
        notif = font.render(save_msg, True, GREEN)
        screen.blit(notif, (TOOLBAR_WIDTH + 10, HEIGHT - PALETTE_HEIGHT - 22))


def draw_text_cursor():
    """Живой курсор при работе с текстовым инструментом."""
    if text_active and text_pos:
        preview = text_font.render(text_buffer + "|", True, text_color)
        screen.blit(preview, (text_pos[0] + TOOLBAR_WIDTH, text_pos[1]))


# ═════════════════════════════════════════════════════════════════════════════
# Вспомогательные: попадание в кнопки тулбара
# ═════════════════════════════════════════════════════════════════════════════
def toolbar_click(mx, my):
    """Обрабатывает клик внутри тулбара. Возвращает True если что-то нажали."""
    global tool, size_preset, brush_size, text_active, text_buffer

    # Кнопки инструментов
    for i, t in enumerate(tools):
        ty = BTN_TOP + i * BTN_GAP
        if ty <= my <= ty + BTN_H and 10 <= mx <= TOOLBAR_WIDTH - 10:
            tool = t
            text_active  = False
            text_buffer  = ""
            return True

    # Кнопки размера
    size_section_y = BTN_TOP + len(tools) * BTN_GAP + 4
    btn_w = (TOOLBAR_WIDTH - 20) // 3
    by0   = size_section_y + 18
    if by0 <= my <= by0 + 26:
        for i, sname in enumerate(size_presets):
            bx = 10 + i * btn_w
            if bx <= mx <= bx + btn_w - 4:
                size_preset = sname
                brush_size  = BRUSH_SIZES[sname]
                return True

    return False


# ═════════════════════════════════════════════════════════════════════════════
# ГЛАВНЫЙ ЦИКЛ
# ═════════════════════════════════════════════════════════════════════════════
while True:
    screen.fill((200, 200, 200))

    # Холст (или превью)
    screen.blit(preview_surface if preview_surface else canvas,
                (TOOLBAR_WIDTH, 0))

    draw_toolbar()
    draw_palette()
    draw_info()
    draw_text_cursor()

    for event in pygame.event.get():

        # ── Выход ────────────────────────────────────────────────────────────
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # ── Клавиатура ───────────────────────────────────────────────────────
        if event.type == pygame.KEYDOWN:

            # Горячие клавиши размера (1 / 2 / 3)
            if not text_active:
                if event.key == pygame.K_1:
                    size_preset = "small";  brush_size = BRUSH_SIZES["small"]
                elif event.key == pygame.K_2:
                    size_preset = "medium"; brush_size = BRUSH_SIZES["medium"]
                elif event.key == pygame.K_3:
                    size_preset = "large";  brush_size = BRUSH_SIZES["large"]

            # Ctrl+S → сохранение
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                save_canvas()

            # Текстовый ввод
            elif text_active:
                if event.key == pygame.K_RETURN:
                    if text_buffer:
                        rendered = text_font.render(text_buffer, True, text_color)
                        canvas.blit(rendered, text_pos)
                    text_active = False
                    text_buffer = ""
                    text_pos    = None
                elif event.key == pygame.K_ESCAPE:
                    text_active = False
                    text_buffer = ""
                    text_pos    = None
                elif event.key == pygame.K_BACKSPACE:
                    text_buffer = text_buffer[:-1]
                elif event.unicode and event.unicode.isprintable():
                    text_buffer += event.unicode

        # ── Нажатие мыши ─────────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if mx < TOOLBAR_WIDTH:
                toolbar_click(mx, my)

            elif my > HEIGHT - PALETTE_HEIGHT:
                # Палитра
                for i, color in enumerate(palette_colors):
                    px = TOOLBAR_WIDTH + 10 + i * 60
                    if px <= mx <= px + 40:
                        current_color = color

            else:
                # Холст
                cx, cy = mx - TOOLBAR_WIDTH, my

                if tool == "text":
                    text_active = True
                    text_pos    = (cx, cy)
                    text_color  = current_color
                    text_buffer = ""

                elif tool == "fill":
                    if 0 <= cx < CANVAS_W and 0 <= cy < CANVAS_H:
                        flood_fill(canvas, cx, cy, current_color)

                else:
                    drawing   = True
                    start_pos = (cx, cy)
                    prev_pos  = (cx, cy)

        # ── Отпуск мыши ──────────────────────────────────────────────────────
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing:
                mx, my = event.pos
                cx, cy = mx - TOOLBAR_WIDTH, my

                if tool in ("rectangle", "circle", "square",
                            "right_triangle", "equilateral_triangle",
                            "rhombus", "line"):
                    draw_shape_on(canvas, tool, start_pos, (cx, cy),
                                  current_color, brush_size)

            drawing         = False
            preview_surface = None
            prev_pos        = None

        # ── Движение мыши ────────────────────────────────────────────────────
        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos
            cx, cy = mx - TOOLBAR_WIDTH, my

            if tool == "brush":
                pygame.draw.circle(canvas, current_color, (cx, cy), brush_size)
                preview_surface = None

            elif tool == "pencil":
                if prev_pos:
                    pygame.draw.line(canvas, current_color,
                                     prev_pos, (cx, cy), brush_size)
                prev_pos        = (cx, cy)
                preview_surface = None

            elif tool == "eraser":
                pygame.draw.circle(canvas, WHITE, (cx, cy), brush_size + 5)
                preview_surface = None

            else:
                # Превью для линий и фигур
                preview_surface = canvas.copy()
                draw_shape_on(preview_surface, tool,
                              start_pos, (cx, cy),
                              current_color, brush_size)

        # ── Колёсико мыши (тонкая настройка размера) ─────────────────────────
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))
            # Синхронизируем подсветку кнопки
            if brush_size <= 3:
                size_preset = "small"
            elif brush_size <= 7:
                size_preset = "medium"
            else:
                size_preset = "large"

    pygame.display.flip()
    clock.tick(60)
