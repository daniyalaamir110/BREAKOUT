from settings import *
import pygame
from os import path


def load_tileset(filename: str, width: int, height: int) -> list:
    # Load the tile map and get its dimensions
    image = pygame.image.load(filename)
    image_width, image_height = image.get_size()

    # Initialize the tileset as a list
    tileset = list()

    for tile_y in range(0, image_height // height):
        for tile_x in range(0, image_width // width):
            # Take out a tile from the tilemap: rect = (pos_x, pos_y, width, height)
            rect = (tile_x * width, tile_y * height, width, height)

            # Append the tile to the line
            tileset.append(image.subsurface(rect))

    return tileset


def load_images(folder: str, n: int, prefix: str = "") -> list:
    # Initialize the sequence of imgs as a list
    imgs = list()
    for i in range(n):
        # load the images one by one by using str.format()
        imgs.append(pygame.image.load(path.join(folder, f"{prefix}{i}.png")))

    return imgs


# =========================LOAD THE ASSETS=========================#

# Load Title animation
TITLE_ANIMATION = load_images(
    path.join("assets", "title_animation"),
    180,
    "4220108e60f146e7c576ae98600b1196dcXP12mFsrGfmBzD-",
)

# Load Backgroud Image
BACKGROUND_IMAGE = pygame.transform.scale(
    pygame.image.load(path.join("assets", "background.png")), (WIDTH, HEIGHT)
)

# Load Block Tile Set
BLOCK_IMAGES = load_tileset(
    path.join("assets", "tilesets", "block_tileset.png"), 48, 24
)
LAVA_IMAGES = load_tileset(path.join("assets", "tilesets", "lava.png"), 48, 24)

# Brick Images
BRICK_IMAGES = load_images(path.join("assets", "brick"), 2)

# Explosion Animation Sequence
BLOCK_EXPLOSION_IMAGES = load_images(path.join("assets", "explosion"), 24)
PADDLE_EXPLOSION_IMAGES = load_images(path.join("assets", "paddle_explosion"), 24)
PUFF_SMOKE_IMAGES = load_images(path.join("assets", "puff_smoke"), 32)
BRICK_EXPLOSION_IMAGES = load_images(path.join("assets", "brick_explosion"), 24)
FIRE_EXPLOSION_IMAGES = load_images(path.join("assets", "fire_explosion"), 32)

# Paddle Images
PADDLE_IMAGES = load_images(path.join("assets", "paddle", "middle_part"), 36)
PADDLE_LEFT = pygame.image.load(path.join("assets", "paddle", "left_part.png"))
PADDLE_RIGHT = pygame.image.load(path.join("assets", "paddle", "right_part.png"))

# Ball Image
BALL_IMAGE = pygame.image.load(path.join("assets", "ball.png"))

# Wall Image
WALL_IMAGE = pygame.image.load(path.join("assets", "wall.jpg"))


def get_globals() -> list:
    return globals()
