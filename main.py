import pygame
import math
import random
import QLearning as Q

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 920
BLACK = (0, 0, 0, 0)
WHITE = (255, 255, 255)
MAXSPEED = 10
THRUST = 2.5
DECAY = 0.05
VECTORCOUNT = 30
BREAKPOINTS = [0, 100, 50, 20]
DEATHPOINTS = -1000
RESPAWNTIME = 6000
ASTEROIDSCALE = 30
PLAYERSIZE = 20
FPS = 60
SENSORCOUNT = 8
SENSORRANGE = WINDOW_HEIGHT/2
FRAMES_PER_ACTION = 30

class Player:
    x = 100
    y = 100
    rotation = 0
    speed = 0
    direction = 0
    lives = 3
    IMAGE = "player.png"
    hit = False
    respawning = RESPAWNTIME
    state = ('None', 'None', 'None', 'None', 'None', 'None', 'None', 'None')
    score = 0

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        speed = 0
        direction = 0

class Projectile:
    x = 100
    y = 100
    rotation = 0
    velocity = 15
    lifespan = WINDOW_WIDTH/2

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        velocity = 15
        lifespan = WINDOW_WIDTH/2

class Asteroid:
    x = 50
    y = 50
    rotation = 90.0
    velocity = 1
    IMAGE = "asteroid.png"
    scale = 3 #lower by 1 each time hit and split into more asteroids, if at 1, dies when hit
    sprite = pygame.image.load(IMAGE)
    dead = False

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        velocity = 1

def main():
    pygame.init()
    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Asteroids Genetic Algorithm")

    Q.Q_Matrix = Q.initialize()

    SCORE = 0
    font = pygame.font.Font('Vector_Battle.ttf', 24)
    font.set_bold(True)
    show_score = font.render('SCORE: 0', True, WHITE, BLACK)
    scoreboard = show_score.get_rect()
    scoreboard.center = (150, 50)

    LEVEL = 4
    asteroids = []
    asteroids = generateAsteroids(asteroids, LEVEL)

    player = Player(WINDOW_WIDTH/2, WINDOW_HEIGHT/2, 0)
    ship = pygame.image.load(player.IMAGE)
    ship = pygame.transform.rotate(ship, -90)
    ship = pygame.transform.scale(ship, (PLAYERSIZE, PLAYERSIZE))

    #temporary
    show_state = font.render('State: '+' '.join(player.state), True, WHITE, BLACK)
    statedisplay = show_state.get_rect()
    statedisplay.center = (535, 150)

    thrustvectors = []
    for each in range(VECTORCOUNT):
        thrustvectors.append([0, 0])

    projectiles = []
    firing = False

    respawntime = 0

    timer =  pygame.time.Clock()
    actiontimer = 0
    currentaction = 'None'

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        actiontimer += 1
        if actiontimer == FRAMES_PER_ACTION:
            actiontimer = 0
            currentaction = Q.actions[Q.choose_action(player.state)]

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or currentaction == 'Left':
            player.rotation += 5
        if keys[pygame.K_RIGHT] or currentaction == 'Right':
            player.rotation -= 5
        if keys[pygame.K_UP] or currentaction == 'Thrust':
            if player.speed <= MAXSPEED: player.speed += THRUST
            del thrustvectors[0]
            thrustvectors.append([player.speed, player.rotation])
        if keys[pygame.K_SPACE] or currentaction == 'Shoot':
            if not firing: projectiles.append(fireProjectile(player, ship))
            firing = True
        if not keys[pygame.K_SPACE]:
            firing = False

        win.fill(BLACK)

        #if level cleared, go to next level
        if len(asteroids) == 0:
            LEVEL += 1
            asteroids = generateAsteroids(asteroids, LEVEL)

        #detect collisions and update score
        SCORE += detectPlayerColision(asteroids, player)
        projectiles = detectProjectileColision(asteroids, projectiles)
        SCORE += splitAsteroids(asteroids)
        show_score = font.render('SCORE: '+str(SCORE), True, WHITE, BLACK)
        win.blit(show_score, scoreboard)
        player.score = SCORE

        #respawn if needed
        if player.hit:
            player.hit = False
            player.respawning = RESPAWNTIME
        if player.respawning > 0:
             player.respawning -= FPS

        sense(player, asteroids, win)
        show_state = font.render('State: '+' '.join(player.state), True, WHITE, BLACK)
        win.blit(show_state, statedisplay)

        drawAsteroids(asteroids, win)
        drawProjectiles(projectiles, win)
        if len(thrustvectors) > 0: updateDirection(player, thrustvectors)
        updatePosition(player)
        drawPlayer(player, ship, win)
        decayThrust(thrustvectors)

        pygame.display.update()
        timer.tick(FPS)

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
    xcomps = []
    ycomps = []
    for each in range(len(thrustvectors)):
        xcomps.append(math.cos(math.radians(thrustvectors[each][1]))*thrustvectors[each][0])
        ycomps.append(math.sin(math.radians(thrustvectors[each][1]))*thrustvectors[each][0])
    xavg = sum(xcomps)/len(thrustvectors)
    yavg = sum(ycomps)/len(thrustvectors)
    player.speed = math.sqrt(xavg**2 + yavg**2)
    player.direction = math.degrees(math.atan2(yavg/MAXSPEED,xavg/MAXSPEED))


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
    if player.respawning % 500 < 250:
        win.blit(rotatedShip, newship.topleft)

#decay speed
def decayThrust(thrustvectors):
    for each in thrustvectors:
        if each[0] >= DECAY: each[0] -= DECAY

def generateAsteroids(asteroids, LEVEL):
    for each in range(LEVEL):
        newasteroid = Asteroid(random.random()*WINDOW_WIDTH, random.random()*WINDOW_HEIGHT, random.random()*360)
        asteroids.append(newasteroid)
        asteroids[each].sprite = pygame.image.load(asteroids[each].IMAGE)
        asteroids[each].sprite = pygame.transform.scale(asteroids[each].sprite, (3*ASTEROIDSCALE, 3*ASTEROIDSCALE))
    return asteroids

def drawAsteroids(asteroids, win):
    for each in asteroids:
        each.x += math.cos(math.radians(each.rotation))*each.velocity
        each.y -= math.sin(math.radians(each.rotation))*each.velocity
        if each.y > WINDOW_HEIGHT: each.y -= WINDOW_HEIGHT
        if each.y < 0: each.y += WINDOW_HEIGHT
        if each.x > WINDOW_WIDTH: each.x -= WINDOW_WIDTH
        if each.x < 0: each.x += WINDOW_WIDTH
        win.blit(each.sprite,( each.x, each.y))

def detectPlayerColision(asteroids, player):
    if not player.hit and not player.respawning:
        for asteroid in asteroids:
            diameter = asteroid.scale*ASTEROIDSCALE
            if player.x >= asteroid.x and player.y >= asteroid.y and player.x <= asteroid.x + diameter and player.y <= asteroid.y + diameter:
                player.hit = True
                player.x = WINDOW_WIDTH/2
                player.y = WINDOW_HEIGHT/2
                return DEATHPOINTS
    return 0


def detectProjectileColision(asteroids, projectiles):
    for asteroid in asteroids:
        for bullet in projectiles:
            diameter = asteroid.scale*ASTEROIDSCALE
            if bullet.x >= asteroid.x and bullet.y >= asteroid.y and bullet.x <= asteroid.x + diameter and bullet.y <= asteroid.y + diameter:
                asteroid.dead = True
                projectiles.remove(bullet)
    return projectiles

def splitAsteroids(asteroids):
    score = 0
    for each in asteroids:
        if each.dead == True:
            score += BREAKPOINTS[each.scale]
            if each.scale > 1:
                newAsteroid1 = Asteroid(each.x, each.y, random.random()*360)
                newAsteroid2 = Asteroid(each.x, each.y, random.random()*360)
                newAsteroid1.scale = each.scale - 1
                newAsteroid2.scale = each.scale - 1
                newAsteroid1.velocity = each.velocity + 1
                newAsteroid2.velocity = each.velocity + 1
                newAsteroid1.sprite = pygame.transform.scale(newAsteroid1.sprite, (newAsteroid1.scale*ASTEROIDSCALE, newAsteroid1.scale*ASTEROIDSCALE))
                newAsteroid2.sprite = pygame.transform.scale(newAsteroid2.sprite, (newAsteroid2.scale*ASTEROIDSCALE, newAsteroid2.scale*ASTEROIDSCALE))
                asteroids.append(newAsteroid1)
                asteroids.append(newAsteroid2)
            asteroids.remove(each)
    return score

def lines_intersect(l1, l2):
    p1 = 0
    p2 = 1
    x = 0
    y = 1

    def ccw(A, B, C):
        return (C[y] - A[y]) * (B[x] - A[x]) > (B[y] - A[y]) * (C[x] - A[x])

    return ccw(l1[p1], l2[p1], l2[p2]) != ccw(l1[p2], l2[p1], l2[p2]) and ccw(l1[p1], l1[p2], l2[p1]) != ccw(l1[p1], l1[p2], l2[p2])

def sense(player, asteroids, win):
    angle = 90
    x = 0
    y = 1
    ship = [player.x+PLAYERSIZE/2, player.y+PLAYERSIZE/2]
    result = []
    for sensor in range(SENSORCOUNT):
        edge = [ship[x] + math.cos(math.radians(angle))*SENSORRANGE,
                ship[y] - math.sin(math.radians(angle))*SENSORRANGE]
        ray = [ship, edge]
        pygame.draw.line(win, (255, 255, 255), ship, edge, 3)
        result.append('None')
        for asteroid in asteroids:
            diameter = asteroid.scale*ASTEROIDSCALE
            UL = [asteroid.x, asteroid.y]
            UR = [asteroid.x + diameter, asteroid.y]
            LL = [asteroid.x, asteroid.y + diameter]
            LR = [asteroid.x + diameter, asteroid.y + diameter]

            if lines_intersect(ray, [UL, UR]) or lines_intersect(ray, [UR, LR]) or lines_intersect(ray, [LL, LR]) or lines_intersect(ray, [UL, LL]):
                result[sensor] = (Q.results[asteroid.scale])

        angle += 360/SENSORCOUNT
    player.state = tuple(result)


if __name__ == '__main__':
    main()
