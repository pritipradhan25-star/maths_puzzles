import math
import pygame
import asyncio

pygame.init()
screen = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Math Riddle Game")

font = pygame.font.SysFont("arial", 28)
num_font = pygame.font.SysFont("arial", 34, bold=True)
big_font = pygame.font.SysFont("arial", 40)
level_font = pygame.font.SysFont("arial", 36, bold=True)
answer_font = pygame.font.SysFont("arial", 32)
clock = pygame.time.Clock()

BG = (45, 27, 78)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
GREEN = (80, 220, 100)
RED = (240, 80, 80)

CX, CY = 600, 330          # puzzle ka center (upar wala hissa)

# ---------------- LEVELS ----------------
levels = [
    # 1. plus: upar, daayein, neeche, baayein, beech
    {"type": "cross", "numbers": [4, 7, 6, 3, None], "answer": "20"},
    # 2. spoke: sabse upar se ghadi ki disha mein
    {"type": "spoke", "numbers": [8, None, 14, 4, 11, 10, 5, 15], "answer": "9"},
    # 3. pyramid: upar se neeche, har row left se right
    {"type": "pyramid", "numbers": [None, 9, 9, 6, 3, 6, 8, 3, 4, 6], "answer": "9"},
    # 4. star: sabse upar wale kone se ghadi ki disha mein
    {"type": "star", "numbers": [6, 10, 18, 34, 66, None], "answer": "130"},
    # 5. text: jaisi lines likhi hain waisi hi dikhengi
    {"type": "text", "lines": ["m - n = 4", "m² - n² = 40", "m + n = ?"], "answer": "10"},
    # 6. circle: top ke daayein hisse se ghadi ki disha mein
    {"type": "circle", "numbers": [10, 1, 6, 5, None, 3, 7, 4], "answer": "8"},
]

# ---------------- GAME KI STATE ----------------
current_level = 0
score = 0
user_text = ""
message = ""
message_color = WHITE
game_over = False


# ---------------- HELPER FUNCTIONS ----------------
def draw_center_text(text, fnt, color, y):
    img = fnt.render(text, True, color)
    screen.blit(img, img.get_rect(center=(CX, y)))


def point_on_circle(angle, r):
    # angle upar se ghadi ki disha mein (degree), r = center se doori
    a = math.radians(angle)
    return (CX + r * math.sin(a), CY - r * math.cos(a))


def draw_box(value, x, y, w=100, h=90):
    rect = pygame.Rect(0, 0, w, h)
    rect.center = (x, y)
    pygame.draw.rect(screen, BG, rect)
    if value is None:
        text, color = "?", GOLD
    else:
        text, color = str(value), WHITE
    pygame.draw.rect(screen, color, rect, 3)
    img = num_font.render(text, True, color)
    screen.blit(img, img.get_rect(center=rect.center))


# ---------------- SHAPES ----------------
def draw_cross(numbers):
    spots = [(0, -170), (170, 0), (0, 170), (-170, 0), (0, 0)]
    for dx, dy in spots[:4]:
        pygame.draw.line(screen, WHITE, (CX, CY), (CX + dx, CY + dy), 3)
    for i in range(5):
        dx, dy = spots[i]
        draw_box(numbers[i], CX + dx, CY + dy)


def draw_spokes(numbers):
    for i in range(4):
        x1, y1 = point_on_circle(i * 45, 170)
        x2, y2 = point_on_circle(i * 45 + 180, 170)
        pygame.draw.line(screen, WHITE, (x1, y1), (x2, y2), 3)
    for i, value in enumerate(numbers):
        x, y = point_on_circle(45 * i, 170)
        draw_box(value, x, y)


def draw_pyramid(numbers):
    index = 0
    for row in range(4):
        for j in range(row + 1):
            x = CX + (j - row / 2) * 120
            y = 150 + row * 100
            draw_box(numbers[index], x, y)
            index += 1


def draw_star(numbers):
    teal = (0, 230, 190)
    up = [point_on_circle(a, 220) for a in (0, 120, 240)]
    down = [point_on_circle(a, 220) for a in (60, 180, 300)]
    pygame.draw.polygon(screen, teal, up, 5)
    pygame.draw.polygon(screen, teal, down, 5)
    for i, value in enumerate(numbers):
        x, y = point_on_circle(60 * i, 150)
        text = "?" if value is None else str(value)
        img = num_font.render(text, True, (255, 165, 0))
        screen.blit(img, img.get_rect(center=(x, y)))


def draw_lines(lines):
    board = pygame.Rect(0, 0, 520, 320)
    board.center = (CX, CY)
    pygame.draw.rect(screen, (40, 45, 50), board, border_radius=12)
    pygame.draw.rect(screen, (140, 100, 60), board, 6, border_radius=12)
    top = CY - (len(lines) - 1) * 30
    for i, line in enumerate(lines):
        color = GOLD if "?" in line else WHITE
        img = big_font.render(line, True, color)
        screen.blit(img, img.get_rect(center=(CX, top + i * 60)))


def draw_circle(numbers):
    line_color = (30, 50, 120)
    pygame.draw.circle(screen, WHITE, (CX, CY), 170)
    pygame.draw.circle(screen, line_color, (CX, CY), 170, 3)
    for k in range(4):
        x1, y1 = point_on_circle(k * 45, 170)
        x2, y2 = point_on_circle(k * 45 + 180, 170)
        pygame.draw.line(screen, line_color, (x1, y1), (x2, y2), 3)
    for i, value in enumerate(numbers):
        x, y = point_on_circle(22.5 + 45 * i, 115)
        if value is None:
            text, color = "??", (220, 30, 30)
        else:
            text, color = str(value), (0, 150, 220)
        img = num_font.render(text, True, color)
        screen.blit(img, img.get_rect(center=(x, y)))


def draw_puzzle(level):
    if level["type"] == "cross":
        draw_cross(level["numbers"])
    elif level["type"] == "spoke":
        draw_spokes(level["numbers"])
    elif level["type"] == "pyramid":
        draw_pyramid(level["numbers"])
    elif level["type"] == "star":
        draw_star(level["numbers"])
    elif level["type"] == "text":
        draw_lines(level["lines"])
    elif level["type"] == "circle":
        draw_circle(level["numbers"])



# ---------------- MAIN LOOP ----------------

async def main():
    global current_level, score, user_text
    global message, message_color, game_over

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and not game_over:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if user_text == levels[current_level]["answer"]:
                        score += 10
                        current_level += 1

                        if current_level == len(levels):
                            game_over = True
                    else:
                        message = "Wrong! Try again."
                        message_color = RED

                    user_text = ""

                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]

                elif event.unicode.isdigit() and len(user_text) < 6:
                    user_text += event.unicode

        screen.fill(BG)

        if not game_over:
            draw_center_text(
                f"Level: {current_level + 1} / {len(levels)}   |   Score: {score}",
                level_font, GOLD, 45
            )

            draw_puzzle(levels[current_level])

            answer_rect = pygame.Rect(0, 0, 500, 70)
            answer_rect.center = (CX, 650)
            pygame.draw.rect(screen, WHITE, answer_rect, 3)

            draw_center_text("Answer: " + user_text, answer_font, WHITE, 650)
            draw_center_text(message, font, message_color, 725)

        else:
            draw_center_text("Congratulations! You won!", big_font, GREEN, 300)
            draw_center_text(f"Final Score: {score}", big_font, GOLD, 380)

        pygame.display.flip()

        await asyncio.sleep(1 / 30)

    pygame.quit()


asyncio.run(main())
