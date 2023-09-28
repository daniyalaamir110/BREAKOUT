from random import choice

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

WIDTH = 1366
HEIGHT = 768
CENTER = WIDTH / 2, HEIGHT / 2

BALL_SPEED = 6
PADDLE_WIDTH = 80
PADDLE_HEIGHT = 16

FPS = 60


def get_random_color() -> tuple:
    return choice([BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, WHITE])
