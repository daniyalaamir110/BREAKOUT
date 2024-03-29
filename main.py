import pygame, math, random, settings, assets
from os import path


class Animation(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        # Image and positioning
        self.image = assets.TITLE_ANIMATION[0]
        self.counter = 0
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Vector2(x, y)

    def update(self):
        # Animation loop
        self.counter += 1
        if self.counter >= 180:
            self.counter = 0
        temp = self.rect.center
        self.image = assets.TITLE_ANIMATION[self.counter]
        self.rect = self.image.get_rect()
        self.rect.center = temp


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        # Image and positioning
        self.image = pygame.Surface((10, 10))
        self.image.fill(settings.BLACK)
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Vector2(x, y)

    def update(self) -> None:
        # Trigger powerup pick
        self.rect.y += 2
        if self.rect.colliderect(paddle):
            self.on_caught()
            powerups.remove(self)
            self.kill()

        # Powerup missed
        if self.rect.y > settings.HEIGHT - 50:
            sprites.add(
                Explosion(
                    "BLOCK_EXPLOSION_IMAGES", self.rect.centerx, self.rect.centery
                )
            )
            powerups.remove(self)
            self.kill()

    def on_caught(self) -> None:
        pass


class SizePoweruUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.fill(settings.GREEN)

    def on_caught(self) -> None:
        if paddle.width < 400:
            paddle.width += 10


class MagnetPowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.fill(settings.CYAN)

    def on_caught(self):
        paddle.magnet = 1200


class FirePowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.fill(settings.RED)

    def on_caught(self):
        paddle.fires += 5
        if paddle.fires > 30:
            paddle.fires = 30


class x3PowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.fill(settings.BLUE)

    def on_caught(self):
        for i in range(2):
            new_ball = Ball(paddle.rect.centerx, paddle.rect.y - 5)
            new_ball.moving = True
            new_ball.velocity.x = (-1) ** i
            balls.add(new_ball)


class BallPowerUp(PowerUp):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
        self.image.fill(settings.YELLOW)

    def on_caught(self):
        for ball in balls:
            ball.fire = 1200


class Explosion(pygame.sprite.Sprite):
    def __init__(self, image_sequence: str, x: int, y: int) -> None:
        super().__init__()

        # Counter for animation frames
        self.counter = 0

        # Image and positioning
        self.image_sequence = image_sequence
        self.UB = len(self.image_sequence)
        self.image = assets.get_globals()[self.image_sequence][0]
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Vector2(x, y)

    def update(self) -> None:
        if self.counter < self.UB:
            # Update the frame
            self.image = assets.get_globals()[self.image_sequence][self.counter]

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

        # Image and positioning
        self.image = assets.BALL_IMAGE
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = x, y

        # Initially ball is not moving
        self.moving = False
        self.offset = x - paddle.rect.centerx

        # 2-D Vector for velocity
        self.velocity = pygame.Vector2(0, -settings.BALL_SPEED)

        # fire powerup
        self.fire = 0

    def update(self) -> None:
        if self.moving == False:
            self.rect.center = pygame.Vector2(
                paddle.rect.centerx + self.offset, paddle.rect.y - 9
            )
        else:
            self.rect = self.rect.move(self.velocity)

            # Collision with Paddle
            if pygame.sprite.collide_rect(self, paddle):
                offset = self.rect.centerx - paddle.rect.centerx
                self.velocity.x = settings.BALL_SPEED * math.sin(
                    2 * offset / paddle.width
                )
                self.velocity.y = -math.sqrt(
                    abs(settings.BALL_SPEED**2 - self.velocity.x**2)
                )
                if paddle.magnet > 0:
                    self.offset = self.rect.centerx - paddle.rect.centerx
                    self.moving = False

            # Collision with Target
            block = pygame.sprite.spritecollideany(self, blocks)
            if block:
                if self.fire > 0:
                    sprites.add(FireExplosion(self.rect.centerx, self.rect.centery))
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
                sprites.add(
                    Explosion(
                        "BLOCK_EXPLOSION_IMAGES", self.rect.centerx, self.rect.centery
                    )
                )
                balls.remove(self)
                self.kill()

        # Fire powerup timedown
        if self.fire > 0:
            self.fire -= 1
            pygame.draw.circle(
                screen, settings.get_random_color(), self.rect.center, 10, 2
            )

    def isCollidingHorizontally(self, block: pygame.sprite.Sprite) -> bool:
        return (
            self.rect.collidepoint(block.rect.x - 9, block.rect.centery)
            or self.rect.collidepoint(block.rect.x - 9, block.rect.centery + 9)
            or self.rect.collidepoint(block.rect.x - 9, block.rect.centery - 9)
            or self.rect.collidepoint(block.rect.right + 9, block.rect.centery)
            or self.rect.collidepoint(block.rect.right + 9, block.rect.centery + 9)
            or self.rect.collidepoint(block.rect.right + 9, block.rect.centery - 9)
        )


class Wall(pygame.sprite.Sprite):
    def __init__(self, side: str) -> None:
        super().__init__()

        # Image and positioning
        self.side = side
        if side == "top":
            self.image = pygame.Surface((1366, 12))
        else:
            self.image = assets.WALL_IMAGE
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        if side == "right":
            self.rect.topleft = pygame.Vector2(settings.WIDTH - 12, 0)
        else:
            self.rect.topleft = pygame.Vector2(0, 0)


class Fire(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()

        # Image and positioning
        self.image = pygame.Surface((2, 10))
        self.image.fill(settings.RED)
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Vector2(x, y)

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

        # Image and positioning
        self.width = settings.PADDLE_WIDTH
        self.image = pygame.transform.scale(
            assets.PADDLE_IMAGES[0], (self.width, settings.PADDLE_HEIGHT)
        )
        self.image.fill(settings.WHITE)
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = pygame.Vector2(settings.WIDTH / 2, settings.HEIGHT - 100)

        # Animation frame counter
        self.counter = 0

        # Powerups
        self.magnet = 0
        self.fires = 0

    def update(self) -> None:
        # Animation loop
        if self.counter >= 36:
            self.counter = 0
        else:
            self.image = pygame.transform.scale(
                assets.PADDLE_IMAGES[self.counter], (self.width, 16)
            )
            self.image.set_colorkey(settings.BLACK)
            self.counter += 1
            temp = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = temp

        if self.magnet > 0:
            self.magnet -= 1

    def get_smaller(self) -> None:
        if self.width > 40:
            for i in range(paddle.width // 40):
                sprites.add(
                    Explosion(
                        "PADDLE_EXPLOSION_IMAGES",
                        paddle.rect.centerx - i * 20,
                        paddle.rect.centery - 7,
                    ),
                    Explosion(
                        "PADDLE_EXPLOSION_IMAGES",
                        paddle.rect.centerx + i * 20,
                        paddle.rect.centery - 7,
                    ),
                )
            self.width -= 40
        else:
            pygame.quit()

    def fire(self):
        sprites.add(Fire(self.rect.x, self.rect.y), Fire(self.rect.right, self.rect.y))


class Target(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, life: int, x: int, y: int) -> None:
        super().__init__()

        # Image and positioning
        self.image = image
        self.image.set_colorkey(settings.BLACK)
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y
        self.life = life

    def destroy(self):
        pass


class Block(Target):
    def __init__(self, image: pygame.Surface, x: int, y: int) -> None:
        super().__init__(image, 1, x, y)

    def destroy(self):
        sprites.add(
            Explosion("BLOCK_EXPLOSION_IMAGES", self.rect.centerx, self.rect.centery)
        )
        blocks.remove(self)
        self.kill()

        global score
        score += 10


class Brick(Target):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(assets.BRICK_IMAGES[1], 2, x, y)

    def destroy(self):
        if self.life == 2:
            sprites.add(
                Explosion("PUFF_SMOKE_IMAGES", self.rect.centerx, self.rect.centery)
            )
            self.life = 1
            self.image = assets.BRICK_IMAGES[0]

            global score
            score += 5
        else:
            sprites.add(
                Explosion(
                    "BRICK_EXPLOSION_IMAGES", self.rect.centerx, self.rect.centery
                )
            )
            powerups.add(
                random.choice(
                    [
                        BallPowerUp(self.rect.centerx, self.rect.centery),
                        x3PowerUp(self.rect.centerx, self.rect.centery),
                        SizePoweruUp(self.rect.centerx, self.rect.centery),
                        MagnetPowerUp(self.rect.centerx, self.rect.centery),
                        FirePowerUp(self.rect.centerx, self.rect.centery),
                    ]
                )
            )
            blocks.remove(self)
            self.kill()
            score += 50


class Lava(Target):
    def __init__(self, x: int, y: int) -> None:
        self.counter = 0
        super().__init__(pygame.Surface((48, 24)), 1, x, y)

    def update(self) -> None:
        screen.blit(assets.LAVA_IMAGES[self.counter], self.rect.topleft)
        self.counter += 1
        if self.counter == 17:
            self.counter = 0

    def destroy(self) -> None:
        sprites.add(FireExplosion(self.rect.centerx, self.rect.centery))
        blocks.remove(self)
        self.kill()
        global score
        score += 100


class LevelText(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # Image and positioning
        self.image = font.render("Level {}".format(level), True, settings.WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.top = 0, settings.HEIGHT
        self.distance = math.sqrt(settings.WIDTH**2 + settings.HEIGHT**2)
        self.displacement = 0
        self.velocity = pygame.Vector2()
        sprites.add(self)

    def update(self):
        self.displacement = math.sqrt(self.rect.centerx**2 + self.rect.centery**2)
        self.offset = abs(self.displacement - self.distance / 2)
        self.velocity.x = self.offset * 16 / 60 + 1
        self.velocity.y = -(self.offset * 9 / 60 + 1)
        if self.velocity.x < 1:
            self.velocity.x = 1
        if self.velocity.y > -1:
            self.velocity.y = -1
        self.rect = self.rect.move(self.velocity)
        if self.rect.bottom < 0:
            self.kill()
            sprites.remove(self)


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
    try:
        with open(path.join("assets", "levels", f"{level}.txt")) as file:
            rows = file.readlines()
            for i in range(len(rows)):
                for j in range(len(rows[i])):
                    char = rows[i][j]
                    index = ord(char) - ord("a")
                    if index in range(25):
                        blocks.add(
                            Block(assets.BLOCK_IMAGES[index], 48 * j + 12, 24 * i + 12)
                        )
                    elif char == "1":
                        blocks.add(Brick(48 * j + 12, 24 * i + 12))
                    elif char == "2":
                        blocks.add(Lava(48 * j + 12, 24 * i + 12))
    except:
        level = 0
        next_level()
    LevelText()


def __main__() -> None:
    # Initialize pygame
    pygame.init()

    # Screen
    global screen
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT), 64)

    # Title
    pygame.display.set_caption("Breakout!")

    # Font
    global font
    font = pygame.font.Font(path.join("assets", "ToThePointRegular.ttf"), 100)

    # 'Click to Continue'
    continue_text = font.render("CLICK TO CONTINUE", True, settings.WHITE)
    continue_rect = continue_text.get_rect()
    continue_rect.center = pygame.Vector2(settings.CENTER[0], settings.HEIGHT - 300)

    # Level
    global level
    level = 0

    # Score Rect
    global score
    score = 0
    score_text = font.render(str(score), True, settings.WHITE)
    score_rect = pygame.Rect(24, 0, 400, 100)

    # Clock
    clock = pygame.time.Clock()

    # Title Animations
    global title_animation
    title_animation = pygame.sprite.GroupSingle()
    title_animation.add(Animation(settings.WIDTH / 2, 200))

    load_sprites()

    # Game Loop
    global running
    running = True

    global game_started
    game_started = False

    global fadeout, alpha
    black_screen = pygame.Surface((settings.WIDTH, settings.HEIGHT)).convert()
    black_screen.fill(settings.BLACK)
    fadeout = False
    alpha = 0

    while running:
        screen.blit(assets.BACKGROUND_IMAGE, (0, 0))
        if not game_started:
            display_splash_screen()
            screen.blit(continue_text, continue_rect)
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

            # The score
            score_text = font.render(str(score), True, settings.WHITE)

            # Update sprites
            sprites.update()
            powerups.update()
            balls.update()
            walls.update()
            blocks.update()

            # Draw/Render sprites
            # The left and right curvatures of the paddle
            screen.blit(assets.PADDLE_LEFT, (paddle.rect.x - 4, paddle.rect.y))
            screen.blit(assets.PADDLE_RIGHT, (paddle.rect.right - 8, paddle.rect.y))

            # Progress bars for powerups
            if paddle.magnet:
                pygame.draw.rect(
                    screen,
                    settings.WHITE,
                    pygame.Rect(10, settings.HEIGHT - 20, 302, 10),
                    1,
                )
                pygame.draw.rect(
                    screen,
                    settings.CYAN,
                    pygame.Rect(12, settings.HEIGHT - 18, paddle.magnet // 4, 6),
                )

            if paddle.fires:
                pygame.draw.rect(
                    screen,
                    settings.WHITE,
                    pygame.Rect(
                        settings.CENTER[0] - 150, settings.HEIGHT - 20, 302, 10
                    ),
                    1,
                )
                for i in range(paddle.fires):
                    pygame.draw.rect(
                        screen,
                        settings.RED,
                        pygame.Rect(
                            settings.CENTER[0] - 148 + i * 10,
                            settings.HEIGHT - 18,
                            8,
                            6,
                        ),
                    )

            # The sprites
            walls.draw(screen)
            blocks.draw(screen)
            sprites.draw(screen)
            balls.draw(screen)
            powerups.draw(screen)
            screen.blit(score_text, score_rect)

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
                elif paddle.rect.right > settings.WIDTH:
                    paddle.rect.right = settings.WIDTH
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
        clock.tick(settings.FPS)

    # Quit Game
    pygame.quit()


if __name__ == "__main__":
    __main__()
