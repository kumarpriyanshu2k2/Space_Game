import pygame
import os
import random


pygame.font.init()


## Parent Screen

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

## Objects


# Ships

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers

RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))

## Background

BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Ship:
    COOLDOWN = 60

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_image = None
        self.laser_image = None
        self.lasers = []
        self.cool_down_counter = 0

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        self.cooldown()
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_image)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def draw(self, window):
        window.blit(self.ship_image, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_height(self):
        return self.ship_image.get_height()

    def get_width(self):
        return self.ship_image.get_width()


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_image, self.laser_image = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_image)

    def move(self, vel):
        self.y += vel


class PLAYER(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.score = 0
        self.ship_image = YELLOW_SPACE_SHIP
        self.laser_image = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_image)
        self.max_health = self.health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        obj.health -= 10
                        objs.remove(obj)
                        self.lasers.remove(laser)
                        self.score += 1

    def move(self, keys, vel):
        if keys[pygame.K_a] and self.x - vel > 0:
            self.x -= vel
        if keys[pygame.K_d] and self.x + vel + self.ship_image.get_width() < WIDTH:
            self.x += vel
        if keys[pygame.K_w] and self.y - vel > 0:
            self.y -= vel
        if keys[pygame.K_s] and self.y + vel + self.ship_image.get_height() < HEIGHT - 20:
            self.y += vel
        if keys[pygame.K_SPACE]:
            self.shoot()

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        self.score_board(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_image.get_height() + 10, self.ship_image.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0),
                         (self.x, self.y + self.ship_image.get_height() + 10,
                          self.ship_image.get_width() * (self.health / self.max_health), 10))

    def score_board(self, window):
        score_font = pygame.font.SysFont("arial", 30)
        title_label = score_font.render(f"SCORE: {self.score}", 1, (255, 255, 255))
        window.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 10))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(obj, self)


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 120
    level = 0
    lives = 5
    enemies = []
    wave_length = 5
    lost = False
    enemy_vel = 1
    laser_vel = 8
    player_vel = 10
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("arial", 50)
    lost_font = pygame.font.SysFont("arial", 50)
    lost_count = 0
    player = PLAYER(300, 630)

    def redraw_window():
        WIN.blit(BG, (0, 0))
        lives_label = main_font.render(f"lives : {lives}", 1, (255, 255, 255))
        level_label = main_font.render(f"level : {level}", 1, (255, 255, 255))
        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        player.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)
        player.draw(WIN)
        if lost:
            lost_label = lost_font.render("You lost!!", 1, (255, 255, 255))
            WIN.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
        pygame.display.update()

    while run:
        clock.tick(FPS)
        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                lost_count += 1
                continue
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(100, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "green", "blue"]))
                enemies.append(enemy)
        redraw_window()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        keys = pygame.key.get_pressed()
        player.move(keys, player_vel)
        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            if random.randrange(0, 4 * 60) == 1:
                enemy.shoot()
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
        player.move_lasers(-laser_vel, enemies)


def main_menue():
    title_font = pygame.font.SysFont("arial", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Click to begin ...", 1, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menue()
