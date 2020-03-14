import pygame
import math

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLACK = (0, 0, 0, 0)
MAXSPEED = 10
THRUST = 0.2
DECAY = 0.1

class Player:
    x = 100
    y = 100
    rotation = 0
    speed = 1
    direction = 0
    lives = 3
    IMAGE = "player.png"

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        speed = 1
        direction = 0

class Projectile:
    x = 100
    y = 100
    rotation = 0
    velocity = 15
    lifespan = WINDOW_WIDTH

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        velocity = 15
        lifespan = WINDOW_WIDTH

class Asteroid:
    x = 50
    y = 50
    rotation = 90.0
    velocity = 1
    scale = 3 #lower by 1 each time hit and split into more asteroids, if at 1, dies when hit

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        velocity = 1

def main():
    pygame.init()

    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

    pygame.display.set_caption("Asteroids Genetic Algorithm")

    player = Player(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 0)
    ship = pygame.image.load(player.IMAGE)
    ship = pygame.transform.rotate(ship, -90)
    ship = pygame.transform.scale(ship, (20, 20))

    thrustvectors = []

    projectiles = []
    firing = False

    timer =  pygame.time.Clock()

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.rotation += 5
        if keys[pygame.K_RIGHT]:
            player.rotation -= 5
        if keys[pygame.K_UP]:
            if player.speed <= MAXSPEED: player.speed += THRUST
            thrustvectors.append([player.speed, player.rotation])

        #if keys[pygame.K_DOWN]:
            #if player.speed >= 1: player.speed -= 0.5
        if keys[pygame.K_SPACE]:
            if not firing: projectiles.append(fireProjectile(player, ship))
            firing = True
        if not keys[pygame.K_SPACE]:
            firing = False

        win.fill(BLACK)

        drawProjectiles(projectiles, win)
        updateDirection(player, thrustvectors)
        updatePosition(player)
        drawPlayer(player, ship, win)
        decayThrust(thrustvectors)

        pygame.display.update()
        timer.tick(60)

    pygame.quit()

def fireProjectile(player, ship):
    x = player.x + ship.get_rect().centerx
    y = player. y + ship.get_rect().centery
    fire = Projectile(x, y, player.rotation)
    return fire

#calculate and draw projectiles
def drawProjectiles(projectiles, win):
    for each in projectiles:
        each.x += math.cos(math.radians(each.rotation))*each.velocity
        each.y -= math.sin(math.radians(each.rotation))*each.velocity
        if each.y > WINDOW_HEIGHT: each.y -= WINDOW_HEIGHT
        if each.y < 0: each.y += WINDOW_HEIGHT
        if each.x > WINDOW_WIDTH: each.x -= WINDOW_WIDTH
        if each.x < 0: each.x += WINDOW_WIDTH
        pygame.draw.rect(win, (255, 255, 255), (each.x-1, each.y-1, 3, 3))
        each.lifespan -= each.velocity
    for each in projectiles:
        if each.lifespan <= 0: projectiles.remove(each)

#calculate new ship direction
def updateDirection(player, thrustvectors):
    thrustlimit = 0
    thrusttotal = 0
    thrustdirection = 0
    directions = []
    directiontotal = 0
    for each in thrustvectors:
        thrusttotal += each[0]
    for each in range(len(thrustvectors)):
        directions.append(thrustvectors[each][1] * thrustvectors[each][0] / thrusttotal)
        if thrustvectors[each][0] > thrustlimit: thrustlimit = thrustvectors[each][0]
    for each in directions:
        thrustdirection += each
    if thrusttotal > 0:
        player.direction = thrustdirection
    else: player.direction = player.rotation
    player.speed = thrustlimit

#calculate new ship position.
def updatePosition(player):
    angle = math.radians(player.direction)
    xcomp = math.cos(angle)
    ycomp = math.sin(angle)
    player.x += xcomp*player.speed
    player.y -= ycomp*player.speed

#draw player
def drawPlayer(player, ship, win):
    rotatedShip = pygame.transform.rotate(ship, player.rotation)
    if player.y > WINDOW_HEIGHT: player.y -= WINDOW_HEIGHT
    if player.y < 0: player.y += WINDOW_HEIGHT
    if player.x > WINDOW_WIDTH: player.x -= WINDOW_WIDTH
    if player.x < 0: player.x += WINDOW_WIDTH
    newship = rotatedShip.get_rect(center = ship.get_rect(topleft = (player.x, player.y)).center)
    win.blit(rotatedShip, newship.topleft)

#decay speed and prune vectors
def decayThrust(thrustvectors):
    for each in thrustvectors:
        each[0] -= DECAY
    for each in thrustvectors:
        if each[0] < 0.5: thrustvectors.remove(each)

if __name__ == '__main__':
    main()
