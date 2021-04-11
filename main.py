import random
import math
import copy
from pygame import *
import pygame
from pygame.display import set_caption
from pygame.mixer import fadeout
import pygame.sprite
from settings import *
from assets import *


class Animation(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int) -> None:

        super().__init__()

        self.image = TITLE_ANIMATION[0]
        self.counter = 0

        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)

    def update(self):

        self.counter += 1

        if self.counter >= 180:

            self.counter = 0

        temp = self.rect.center

        self.image = TITLE_ANIMATION[self.counter]

        self.rect = self.image.get_rect()

        self.rect.center = temp


class PowerUp(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int) -> None:

        super().__init__()

        self.image = pygame.Surface((10, 10))
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)

    def update(self) -> None:

        self.rect.y += 2

        if self.rect.colliderect(paddle):
            self.on_caught()
            powerups.remove(self)
            self.kill()

        if self.rect.y > HEIGHT - 50:
            sprites.add(Explosion("BLOCK_EXPLOSION_IMAGES",
                                  self.rect.centerx, self.rect.centery))
            powerups.remove(self)
            self.kill()

    def on_caught(self) -> None:
        pass


class SizePoweruUp(PowerUp):

    def __init__(self, x: int, y: int) -> None:

        super().__init__(x, y)

        self.image.fill(GREEN)

    def on_caught(self) -> None:

        if paddle.width < 400:
            paddle.width += 10


class MagnetPowerUp(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        self.image.fill(CYAN)

    def on_caught(self):
        paddle.magnet = 1200


class FirePowerUp(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        self.image.fill(CYAN)

    def on_caught(self):
        paddle.fires += 5

        if paddle.fires > 30:
            paddle.fires = 30


class x3PowerUp(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        self.image.fill(BLUE)

    def on_caught(self):
        for i in range(2):
            new_ball = Ball(paddle.rect.centerx, paddle.rect.y - 5)
            new_ball.moving = True
            new_ball.velocity.x = (-1) ** i
            balls.add(new_ball)


class BallPowerUp(PowerUp):

    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)

        self.image.fill(YELLOW)

    def on_caught(self):
        for ball in balls:
            ball.fire = 1200


class Explosion(pygame.sprite.Sprite):

    def __init__(self, image_sequence: str, x: int, y: int) -> None:

        super().__init__()

        # Counter for animation frames
        self.counter = 0

        # Image
        self.image_sequence = image_sequence
        self.UB = len(self.image_sequence)
        self.image = globals()[self.image_sequence][0]
        self.image.set_colorkey(BLACK)

        # Positioning
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)

    def update(self) -> None:

        if self.counter < self.UB:

            # Update the frame
            self.image = globals()[self.image_sequence][self.counter]

            # Increment the image counter
            self.counter += 1

            # Positioning
            temp = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = temp

        else:
            # End the animation
            self.kill()


class FireExplosion(Explosion):

    def __init__(self, x: int, y: int):

        super().__init__("FIRE_EXPLOSION_IMAGES", x, y)

    def update(self):

        super().update()

        for block in pygame.sprite.spritecollide(self, blocks, dokill=False):

            block.destroy()


class Ball(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int) -> None:

        super().__init__()

        # Image
        self.image = BALL_IMAGE
        self.image.set_colorkey(BLACK)

        # Positioning
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # Initially balls is not moving
        self.moving = False
        self.offset = x - paddle.rect.centerx

        # 2-D Vector for velocity
        self.velocity = Vector2(0, -BALL_SPEED)

        # fire powerup
        self.fire = 0

    def update(self) -> None:

        if self.moving == False:
            self.rect.center = Vector2(
                paddle.rect.centerx + self.offset, paddle.rect.y - 9)
        else:
            self.rect = self.rect.move(self.velocity)

            # Collision with Paddle
            if pygame.sprite.collide_rect(self, paddle):

                offset = self.rect.centerx - paddle.rect.centerx

                self.velocity.x = BALL_SPEED * \
                    math.sin(2 * offset / paddle.width)
                self.velocity.y = - \
                    math.sqrt(abs(BALL_SPEED ** 2 - self.velocity.x ** 2))

                if paddle.magnet > 0:
                    self.offset = self.rect.centerx - paddle.rect.centerx
                    self.moving = False

            # Collision with Target
            block = pygame.sprite.spritecollideany(self, blocks)
            if block:
                if self.fire > 0:
                    sprites.add(FireExplosion(
                        self.rect.centerx, self.rect.centery))
                else:
                    block.destroy()

                if self.isCollidingHorizontally(block):
                    self.velocity.x *= -1

                else:
                    self.velocity.y *= -1

            # Collision with Walls
            wall = pygame.sprite.spritecollideany(self, walls)
            if wall:
                if wall.side == "top":
                    self.velocity.y *= -1
                else:
                    self.velocity.x *= -1

            # Ball missed
            if self.rect.y > paddle.rect.bottom:
                sprites.add(Explosion("BLOCK_EXPLOSION_IMAGES",
                                      self.rect.centerx, self.rect.centery))
                balls.remove(self)
                self.kill()

        # Fire powerup timedown
        if self.fire > 0:
            self.fire -= 1
            pygame.draw.circle(screen, get_random_color(),
                               self.rect.center, 10, 2)

    def duplicate(self) -> pygame.sprite.Sprite:
        new_sprite = copy.copy(self)
        new_sprite.rect = self.rect.copy()
        return new_sprite

    def isCollidingHorizontally(self, block: pygame.sprite.Sprite) -> bool:
        return (
            self.rect.collidepoint(block.rect.x - 9, block.rect.centery) or
            self.rect.collidepoint(block.rect.x - 9, block.rect.centery + 9) or
            self.rect.collidepoint(block.rect.x - 9, block.rect.centery - 9) or
            self.rect.collidepoint(block.rect.right + 9, block.rect.centery) or
            self.rect.collidepoint(block.rect.right + 9, block.rect.centery + 9) or
            self.rect.collidepoint(block.rect.right + 9,
                                   block.rect.centery - 9)
        )


class Wall(pygame.sprite.Sprite):

    def __init__(self, side: str) -> None:

        super().__init__()

        self.side = side
        if side == "top":
            self.image = pygame.Surface((1366, 12))
        else:
            self.image = pygame.Surface((12, 768))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        if side == "right":
            self.rect.topleft = Vector2(WIDTH - 12, 0)
        else:
            self.rect.topleft = Vector2(0, 0)


class Fire(pygame.sprite.Sprite):

    def __init__(self, x: int, y: int) -> None:

        super().__init__()
        self.image = pygame.Surface((2, 10))
        self.image.fill(RED)
        self.image.set_colorkey(BLACK)

        self.rect = self.image.get_rect()
        self.rect.center = Vector2(x, y)

    def update(self):

        self.rect.centery -= 5

        block = pygame.sprite.spritecollideany(self, blocks)

        if block:
            sprites.remove(self)
            self.kill()
            sprites.add(FireExplosion(self.rect.centerx, self.rect.y))

        if self.rect.y < 0:
            sprites.remove(self)
            self.kill()


class Paddle(pygame.sprite.Sprite):

    def __init__(self) -> None:

        super().__init__()

        self.width = 80

        self.image = pygame.transform.scale(PADDLE_IMAGES[0], (self.width, 16))

        self.image.fill(WHITE)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = Vector2(WIDTH / 2, HEIGHT - 100)

        self.counter = 0

        # magnet powerup
        self.magnet = 0

        # fire powerup
        self.fires = 0

    def update(self) -> None:

        if self.counter >= 36:
            self.counter = 0

        else:
            self.image = pygame.transform.scale(
                PADDLE_IMAGES[self.counter], (self.width, 16))
            self.image.set_colorkey(BLACK)
            self.counter += 1

            temp = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = temp

        if self.magnet > 0:
            self.magnet -= 1

    def get_smaller(self) -> None:
        if (self.width > 40):
            for i in range(paddle.width // 40):
                sprites.add(Explosion("PADDLE_EXPLOSION_IMAGES", paddle.rect.centerx - i * 20, paddle.rect.centery - 7),
                            Explosion("PADDLE_EXPLOSION_IMAGES", paddle.rect.centerx + i * 20, paddle.rect.centery - 7))
            self.width -= 40

        else:
            pygame.quit()

    def fire(self):

        sprites.add(Fire(self.rect.x, self.rect.y),
                    Fire(self.rect.right, self.rect.y))


class Target(pygame.sprite.Sprite):

    def __init__(self, image: pygame.Surface, life: int, x: int, y: int) -> None:

        super().__init__()

        self.image = image
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y
        self.life = life

    def destroy(self):

        pass


class Block(Target):

    def __init__(self, image: pygame.Surface, x: int, y: int) -> None:

        super().__init__(image, 1, x, y)

    def destroy(self):

        sprites.add(Explosion("BLOCK_EXPLOSION_IMAGES",
                              self.rect.centerx, self.rect.centery))
        blocks.remove(self)
        self.kill()


class Brick(Target):

    def __init__(self, x: int, y: int) -> None:

        super().__init__(BRICK_IMAGES[1], 2, x, y)

    def destroy(self):

        if self.life == 2:
            sprites.add(Explosion("PUFF_SMOKE_IMAGES",
                                  self.rect.centerx, self.rect.centery))
            self.life = 1
            self.image = BRICK_IMAGES[0]

        else:

            sprites.add(Explosion("BRICK_EXPLOSION_IMAGES",
                                  self.rect.centerx, self.rect.centery))
            powerups.add(random.choice([BallPowerUp(self.rect.centerx, self.rect.centery),
                                        x3PowerUp(self.rect.centerx,
                                                  self.rect.centery),
                                        SizePoweruUp(
                                            self.rect.centerx, self.rect.centery),
                                        MagnetPowerUp(
                                            self.rect.centerx, self.rect.centery),
                                        FirePowerUp(self.rect.centerx, self.rect.centery)]))
            blocks.remove(self)
            self.kill()


class Lava(Target):

    def __init__(self, x: int, y: int) -> None:

        self.counter = 0
        super().__init__(pygame.Surface((48, 24)), 1, x, y)

    def update(self) -> None:

        screen.blit(LAVA_IMAGES[self.counter], self.rect.topleft)
        self.counter += 1
        if self.counter == 17:
            self.counter = 0

    def destroy(self) -> None:

        sprites.add(FireExplosion(self.rect.centerx, self.rect.centery))
        blocks.remove(self)
        self.kill()


def display_splash_screen() -> None:

    title_animation.update()
    title_animation.draw(screen)


def load_sprites() -> None:

    # Sprites Group
    global sprites
    sprites = pygame.sprite.Group()

    # Walls
    global walls
    walls = pygame.sprite.Group()
    for side in ("top", "left", "right"):
        walls.add(Wall(side))

    # Paddle
    global paddle
    paddle = Paddle()
    sprites.add(paddle)

    # Balls
    global balls
    balls = pygame.sprite.Group()
    balls.add(Ball(paddle.rect.centerx, paddle.rect.y - 12))

    # Blocks
    global blocks
    blocks = pygame.sprite.Group()

    # Powerup Sprites
    global powerups
    powerups = pygame.sprite.Group()


def next_level() -> None:
    global level
    level += 1
    with open("levels\\{}.txt".format(level)) as file:
        rows = file.readlines()
        for i in range(len(rows)):
            for j in range(len(rows[i])):
                char = rows[i][j]
                index = ord(char) - ord("a")
                if index in range(25):
                    blocks.add(
                        Block(BLOCK_IMAGES[index], 48 * j + 12, 24 * i + 12))
                elif char == "1":
                    blocks.add(Brick(48 * j + 12, 24 * i + 12))
                elif char == "2":
                    blocks.add(Lava(48 * j + 12, 24 * i + 12))


def __main__() -> None:

    # Initialize pygame
    pygame.init()

    # Screen
    global screen
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, 64)

    # Title
    pygame.display.set_caption("Breakout!")

    # Clock
    clock = pygame.time.Clock()

    # Title Animations
    global title_animation
    title_animation = pygame.sprite.GroupSingle()
    title_animation.add(Animation(WIDTH / 2, 200))

    # Level
    global level
    level = 0

    load_sprites()

    # Game Loop
    global running
    running = True

    global game_started
    game_started = False

    global fadeout
    global alpha
    black_screen = pygame.Surface((WIDTH, HEIGHT)).convert()
    black_screen.fill(BLACK)
    fadeout = False
    alpha = 0

    while running:

        screen.blit(BACKGROUND_IMAGE, (0, 0))

        if not game_started:

            display_splash_screen()

        elif fadeout:
            black_screen.set_alpha(alpha)
            screen.blit(black_screen, (0, 0))

            alpha += 4
            if alpha > 255:
                fadeout = False
                alpha = 0
                load_sprites()
                next_level()

        else:

            if len(blocks) == 0:
                fadeout = True

            # If all balls are lost, respawn 1 and shorten the paddle
            if len(balls) == 0:
                paddle.get_smaller()
                paddle.update()
                new_ball = Ball(paddle.rect.centerx, paddle.rect.y - 5)
                balls.add(new_ball)

            # Update sprites
            sprites.update()
            powerups.update()
            balls.update()
            walls.update()
            blocks.update()

            # Draw/Render sprites

            # The left and right curvatures of the paddle
            screen.blit(PADDLE_LEFT, (paddle.rect.x - 4, paddle.rect.y))
            screen.blit(PADDLE_RIGHT, (paddle.rect.right - 8, paddle.rect.y))

            # Progress bars for powerups
            if paddle.magnet:
                pygame.draw.rect(screen, WHITE, pygame.Rect(
                    10, HEIGHT - 20, 302, 10), 1)
                pygame.draw.rect(screen, CYAN, pygame.Rect(
                    12, HEIGHT - 18, paddle.magnet // 4, 6))

            if paddle.fires:
                pygame.draw.rect(screen, WHITE, pygame.Rect(
                    CENTER[0] - 150, HEIGHT - 20, 302, 10), 1)
                for i in range(paddle.fires):
                    pygame.draw.rect(screen, RED, pygame.Rect(
                        CENTER[0] - 148 + i * 10, HEIGHT - 18, 8, 6))

            # The sprites
            walls.draw(screen)
            blocks.draw(screen)
            sprites.draw(screen)
            balls.draw(screen)
            powerups.draw(screen)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEMOTION:
                paddle.rect.centerx = pygame.mouse.get_pos()[0]
                if paddle.rect.x < 0:
                    paddle.rect.x = 0
                elif paddle.rect.right > WIDTH:
                    paddle.rect.right = WIDTH

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_started:
                    game_started = True
                    fadeout = True
                else:
                    for ball in balls:
                        ball.moving = True
                    if paddle.fires > 0:
                        paddle.fire()
                        paddle.fires -= 1

        # Flip the screen
        pygame.display.flip()

        # Clock Tick
        clock.tick(FPS)

    # Quit Game
    pygame.quit()


if __name__ == "__main__":

    __main__()
