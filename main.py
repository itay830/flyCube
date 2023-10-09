from sys import exit
from random import randint
import pygame

pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.NOFRAME)
gameActive = 0

instructionsFont = pygame.font.SysFont("comicsansms", WIDTH // 100 * 3, True, False)
instructions = instructionsFont.render("press 'space' to shoot and start, 'esc' to exit".upper(), False, 0x000000)
instructions2 = instructionsFont.render("left mouse click to jump (right to shoot)".upper(), False, 0x000000)
dev = instructionsFont.render("made by: itay shinderman".upper(), False, 0x000000)

with open("bestScore.txt", 'r') as f:
    bestScore = int(f.read())
score = 0
scoreFont = pygame.font.SysFont("comicsansms", WIDTH // 100 * 10, False, False)
bestScoreTxt = scoreFont.render(f"BEST SCORE: {bestScore}", False, 0x000000)

pause = False
pauseSurf = pygame.surface.Surface((WIDTH, HEIGHT))
pauseSurf.set_alpha(175)
pauseFont = pygame.font.SysFont("comicsansms", WIDTH // 100 * 20, False, False)
pauseTxt = pauseFont.render("PAUSE", False, 0x676767)
pauseRect = pauseTxt.get_rect(center=(WIDTH/2, HEIGHT/2))

wallHitSound = pygame.mixer.Sound('recources/WallHitSound.ogg')
plusScoreSound = pygame.mixer.Sound('recources/plusScore.ogg')
jumpSound = pygame.mixer.Sound('recources/jumpSound.ogg')
doorHitSound = pygame.mixer.Sound('recources/doorHit.ogg')
shootHitSound = pygame.mixer.Sound('recources/shoot.ogg')
shootHitSound.set_volume(0.3)
pygame.mixer.music.load('recources/bgMusic.ogg')
pygame.mixer.music.set_volume(.4)
pygame.mixer.music.play(-1)


def defeat():
    global bestScoreTxt, gameActive
    if score > bestScore:
        with open("bestScore.txt", 'w') as file:
            file.write(str(score))
        bestScoreTxt = scoreFont.render(f"BEST SCORE: {score}", False, 0x000000)
    gameActive = False
    pygame.time.set_timer(makeTube, 0)
    pygame.time.set_timer(makeCircle, 0)


class Player:
    def __init__(self, pos):
        # Cube
        self.surf = pygame.surface.Surface((15, 15))
        self.surf.fill(0xffffff)
        self.rect = self.surf.get_rect(center=pos)
        self.gravity = 0

    def fall(self):
        if not pause:
            self.rect.y += self.gravity
            self.gravity += 0.5

    def jump(self):
        self.gravity = -10
        jumpSound.play()

    def draw(self):
        screen.blit(self.surf, self.rect)

    def update(self):
        self.fall()
        self.draw()


bird = Player((50, HEIGHT / 2))

tubes = []
tubeSpeed = 5
delay = 100


class Tube:
    def __init__(self, height, starty, tubedelay):
        self.destroyed = False
        # Cube:
        self.height = height
        if self.height > 1:
            self.surf = pygame.surface.Surface((50, self.height))
        else:
            self.surf = pygame.surface.Surface((50, 1))
        self.surf.fill(0xffffff)

        if starty == 0:
            self.rect = self.surf.get_rect(topleft=(randint(WIDTH, WIDTH + tubedelay - (score*5 % 100)), starty))
            height = HEIGHT - height - randint(125, 250 - (score % 100))
            if randint(0, 100) < score:
                doors.append(Door((self.rect.bottomleft[0] + self.rect.width - 20, self.rect.bottomleft[1]), HEIGHT))
            tubes.append(Tube(height, HEIGHT, self.rect.topleft[0]))
        else:
            self.rect = self.surf.get_rect(bottomleft=(tubedelay, starty))

        coins.append(Coin([randint(WIDTH, WIDTH + 200), randint(100, HEIGHT - 100)]))
        coins.append(Coin([randint(WIDTH, WIDTH + 200), randint(100, HEIGHT - 100)]))

    def draw(self):
        screen.blit(self.surf, self.rect)

    def move(self):
        if not pause:
            self.rect.x -= tubeSpeed

    def collisions(self):
        if self.rect.right < 0:
            # delLst.append(index)
            return True

        if self.rect.collidepoint(bird.rect.center):
            defeat()

        for subBulletIndex, subBullet in enumerate(bullets):
            if subBullet.rect.colliderect(self.rect):
                bullets.pop(subBulletIndex)
                wallHitSound.play()

    def update(self):
        self.draw()
        self.move()
        return self.collisions()


coins = []


class Coin:
    def __init__(self, pos):
        self.destroyed = False
        self.surf = pygame.surface.Surface((10, 10))
        self.surf.fill(0xFFFF00)
        self.rect = self.surf.get_rect(center=pos)
        self.speed = randint(-5, -1)

    def update(self):
        if not pause:
            self.rect.x += self.speed
        screen.blit(self.surf, self.rect)


circles = []


class Circle:
    def __init__(self, pos, sradius):
        self.destroyed = False
        self.pos = pos
        self.sradius = sradius
        self.eradius = randint(self.sradius + 50, self.sradius + 200)
        self.radius = sradius
        self.sizer = 1

        self.surf = pygame.surface.Surface((self.eradius * 2, self.eradius * 2))
        self.surf.set_colorkey((0, 0, 0))
        self.surf.set_alpha(randint(10, 50))

    def update(self):
        if self.radius > self.eradius or self.radius < self.sradius:
            self.sizer *= -1
        self.radius += self.sizer
        if not pause:
            self.pos[0] -= 5

        self.surf.fill((0, 0, 0))
        pygame.draw.circle(self.surf, (0, score % 255 + 1, 0), (self.eradius, self.eradius), self.radius)
        screen.blit(self.surf, self.pos)


bullets = []


class Bullet:
    def __init__(self, pos):
        self.destroyed = False
        self.pos = pos
        self.speed = 8
        self.surf = pygame.Surface((20, 10))
        self.surf.set_colorkey((0, 0, 0))
        pygame.draw.ellipse(self.surf, (255, 0, 0), (0, 0, 20, 10))
        self.rect = self.surf.get_rect(center=pos)

    def draw(self):
        screen.blit(self.surf, self.rect)

    def move(self):
        if not pause:
            self.rect.x += self.speed
            self.speed = self.speed - self.speed / 175

    def collisions(self):
        if self.rect.x > WIDTH:
            return True

    def update(self) -> bool:
        self.move()
        self.draw()
        return self.collisions()

    @staticmethod
    def shoot_bullet():
        bullets.append(Bullet(bird.rect.center))
        shootHitSound.play()


layers = ((255, 0, 0), (125, 0, 0), (25, 0, 0), (0, 0, 45))
doors = []


class Door:
    def __init__(self, pos, height):
        self.destroyed = False
        self.pos = pos
        self.surf = pygame.Surface((20, height))
        self.layers = layers[0:randint(1, len(layers)-1)]
        self.layerLevel = len(self.layers) - 1
        self.surf.fill(self.layers[self.layerLevel])
        self.rect = self.surf.get_rect(topleft=self.pos)

    def draw(self):
        screen.blit(self.surf, self.rect)

    def collision(self):
        global bullets
        if self.rect.collidepoint(bird.rect.center):
            defeat()

        for subBullet in bullets:
            if subBullet.rect.colliderect(self.rect):
                subBullet.destroyed = True
                doorHitSound.play()
                if self.hit():
                    door.destroyed = True
        bullets = [subBullet for subBullet in bullets if not subBullet.destroyed]

        if self.rect.right < 0:
            return True
        else:
            return False

    def move(self):
        if not pause:
            self.rect.x -= tubeSpeed

    def hit(self):
        self.layerLevel -= 1
        if self.layerLevel >= 0:
            self.surf.fill(self.layers[self.layerLevel])
            return False
        else:
            return True

    def update(self):
        self.move()
        self.draw()
        return self.collision()


makeTube = pygame.USEREVENT + 1
makeCircle = pygame.USEREVENT + 2

clock = pygame.time.Clock()
while 1:
    clock.tick(60)
    for eve in pygame.event.get():
        if eve.type == pygame.QUIT:
            pygame.quit()
            exit()
        if eve.type == pygame.KEYDOWN:
            if eve.key == pygame.K_ESCAPE:
                pygame.quit()
                exit()

            if eve.key == pygame.K_p:
                if pause:
                    pygame.time.set_timer(makeTube, 1500)
                    pygame.time.set_timer(makeCircle, 1500)
                    pause = False
                else:
                    pygame.time.set_timer(makeTube, 0)
                    pygame.time.set_timer(makeCircle, 0)
                    pause = True

        if eve.type == pygame.KEYUP:
            if eve.key == pygame.K_SPACE:
                if not gameActive:
                    score = 0
                    bird.gravity = 0
                    coins = []
                    tubes = []
                    doors = []
                    bullets = []
                    tubeSpeed = 5
                    bird.rect.y = HEIGHT / 2
                    pygame.time.set_timer(makeTube, 1500)
                    pygame.time.set_timer(makeCircle, 1500)
                    pause = False
                    gameActive = True
                else:
                    if not pause:
                        Bullet.shoot_bullet()

        if eve.type == pygame.MOUSEBUTTONDOWN and not pause and gameActive:
            if pygame.mouse.get_pressed()[0]:
                bird.jump()

            if pygame.mouse.get_pressed()[2]:
                Bullet.shoot_bullet()

        if eve.type == makeTube:
            tubes.append(Tube(randint(75, HEIGHT - 225), 0, delay))

        if eve.type == makeCircle:
            circles.append(Circle([randint(WIDTH, WIDTH + 400 - score % 401), randint(-300, HEIGHT)], randint(0, 100)))

    if gameActive:
        screen.fill((0, 0, 0))

        for door in doors:
            if door.update():
                door.destroyed = True

        for index, bullet in enumerate(bullets):
            if bullet.update():
                bullets.pop(index)

        for index, coin in enumerate(coins):
            coin.update()
            if coin.rect.colliderect(bird.rect):
                score += 1
                tubeSpeed += 0.1
                coin.destroyed = True
                plusScoreSound.play()

            if coin.rect.right < -50:
                coin.destroyed = True

        for index, circle in enumerate(circles):
            circle.update()
            if circle.pos[0] < -1000:
                circles.pop(index)

        bird.update()
        for tube in tubes:
            if tube.update():
                tube.destroyed = True

        if bird.rect.bottom < 0 or bird.rect.top > HEIGHT:
            defeat()

        if pause:
            screen.blit(pauseSurf, (0, 0))
            screen.blit(pauseTxt, pauseRect)

        bullets = [bullet for bullet in bullets if not bullet.destroyed]
        doors = [door for door in doors if not door.destroyed]
        tubes = [tube for tube in tubes if not tube.destroyed]
        coins = [coin for coin in coins if not coin.destroyed]
        circles = [circle for circle in circles if not circle.destroyed]
    else:
        screen.fill(0x676767)
        screen.blit(instructions, (10, 90))
        screen.blit(instructions2, (10, 130))
        screen.blit(dev, (10, 170))
        screen.blit(bestScoreTxt, (10, HEIGHT-200))

    # Score:
    scoreTxt = scoreFont.render(str(int(score)), False, 0x436960)
    scoreRect = scoreTxt.get_rect(center=(WIDTH / 2, 50))
    screen.blit(scoreTxt, scoreRect)

    pygame.display.update()
