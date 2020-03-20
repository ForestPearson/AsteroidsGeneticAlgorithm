import pygame
import math
import random
import QLearning as Q
import GA
import os.path
import constant as C

MODE = 1                                                                        #0 = Player control, 1 = Q-Learning, 2 = GA

class Player:
    x = 100
    y = 100
    rotation = 0
    speed = 0
    direction = 0
    lives = 3
    IMAGE = "player.png"
    hit = False
    respawning = C.RESPAWNTIME
    state = ('None', 'None', 'None', 'None', 'None', 'None', 'None', 'None')
    score = 0
    thrustvectors = []
    firing = False

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.rotation = rotation
        speed = 0
        direction = 0
        for each in range(C.VECTORCOUNT):
            self.thrustvectors.append([0, 0])

class Projectile:
    x = 100
    y = 100
    direction = 0
    speed = 15
    lifespan = C.WINDOW_WIDTH/2

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        speed = 15
        lifespan = C.WINDOW_WIDTH/2

class Asteroid:
    x = 50
    y = 50
    direction = 90.0
    speed = 1
    IMAGE = "asteroid.png"
    scale = 3 #lower by 1 each time hit and split into more asteroids, if at 1, dies when hit
    sprite = pygame.image.load(IMAGE)
    dead = False

    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        speed = 1

def main():
    Default= 0
    QLearning = 1
    Genetic = 2

    C.initialize()

    #Initialize pygame and window surface.
    pygame.init()
    win = pygame.display.set_mode((C.WINDOW_WIDTH, C.WINDOW_HEIGHT))
    pygame.display.set_caption("Asteroids Genetic Algorithm")
    timer =  pygame.time.Clock()

    #Initialize Q-Learning.
    if MODE == QLearning:
        QTRAINING = True
        Q.Q_Matrix = Q.initialize()
        actiontimer = 0
        action = 0
        currentaction = 0
        oldstateval = 0
        oldscore = 0
        prevQscore = 0

    #Initialize level one asteroids ().
    LEVEL = 1
    asteroids = []
    asteroids = generateAsteroids(asteroids, LEVEL)

    #Initialize scoreboard.
    SCORE = 0
    if C.DISPLAY_GAME:
        font = pygame.font.Font('Vector_Battle.ttf', 24)
        font.set_bold(True)
        show_score = font.render('SCORE: 0', True, C.WHITE, C.BLACK)
        scoreboard = show_score.get_rect()
        scoreboard.center = (150, 50)

    #Initialize player sprite.
    player = Player(C.WINDOW_WIDTH/2, C.WINDOW_HEIGHT/2, 0)
    if C.DISPLAY_GAME:
        ship = pygame.image.load(player.IMAGE)
        ship = pygame.transform.rotate(ship, -90)
        ship = pygame.transform.scale(ship, (C.PLAYERSIZE, C.PLAYERSIZE))

    #Initialize state display.
        show_state = font.render('State: '+' '.join(player.state), True, C.WHITE, C.BLACK)
        statedisplay = show_state.get_rect()
        statedisplay.center = (535, 150)

    #Initialize projectiles.
    projectiles = []

    #Initialize timers.
    respawntime = 0

    run = True

    if MODE == Genetic:
        population = [GA.random_chromosome() for _ in range(GA.PopulationSize)]
        fitness_scores = [0 for i in range(GA.PopulationSize)]
        for each in range(len(population)):
            fitness_scores[each] = simulate(newGameContainer(), population[each])
            print(fitness_scores[each])
        average = GA.average_fitness(fitness_scores)
        print("avg fitness: "+str(average))

        i = 0
        while i < GA.NumIterations:
            i += 1
            population, fitness_scores = GA.breed(population, fitness_scores)
            average = GA.average_fitness(fitness_scores)
            print("avg-fitness: "+str(average))
        best_chromosome = population[GA.best_solution(fitness_scores)]

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        #If using Q-Learning, train the Q-Matrix when the action timer runs out.
        if MODE == QLearning:
            actiontimer += 1
            if actiontimer == C.FRAMES_PER_ACTION:
                actiontimer = 0
                reward = SCORE - oldscore
                oldscore = SCORE
                nextbest = Q.Q_Matrix[C.state.index(player.state)][Q.greedy_choice(player.state)]
                Q.Q_Matrix[oldstateval][action] = prevQscore + C.stepsize*(reward + C.discount*nextbest - prevQscore)
                oldstateval = C.state.index(player.state)
                action = Q.choose_action(player.state)
                prevQscore = Q.Q_Matrix[oldstateval][action]
                currentaction = C.actions[action]

        if MODE == Genetic:
            action = GA.updateAction(player, best_chromosome)
            executeAction(player, projectiles, action)

        #Choose an action, based on current key press or Q-Learning decision.
        keys = pygame.key.get_pressed()
        if (MODE == QLearning and currentaction == 'Left') or keys[pygame.K_LEFT]:
            player.rotation += 5
        if (MODE == QLearning and currentaction == 'Right') or keys[pygame.K_RIGHT]:
            player.rotation -= 5
        if (MODE == QLearning and currentaction == 'Thrust') or keys[pygame.K_UP]:
            if player.speed <= C.MAXSPEED: player.speed += C.THRUST
            del player.thrustvectors[0]
            player.thrustvectors.append([player.speed, player.rotation])
        if (MODE == QLearning and currentaction == 'Shoot') or keys[pygame.K_SPACE]:
            if not player.firing: projectiles.append(fireProjectile(player))
            player.firing = True
        if MODE == QLearning:
            if currentaction != 'Shoot': player.firing = False
        else:
             if not keys[pygame.K_SPACE]: player.firing = False

        #Update player, asteroids, projectiles, SCORE, LEVEL and state.
        rays = sense(player, asteroids)
        projectiles = detectProjectileColision(asteroids, projectiles)
        SCORE += updateScore(player, asteroids)
        player.score = SCORE
        updatePlayer(player)
        LEVEL = updateAsteroids(asteroids, LEVEL)
        updateProjectiles(projectiles)

        #Draw the game.
        if C.DISPLAY_GAME: drawGame(player, ship, asteroids, projectiles, scoreboard, SCORE, statedisplay, rays, font, win)

        timer.tick(C.FPS)

    if MODE != 2: pygame.quit()
    if C.SAVEQMATRIX: saveQmatrix(Q.Q_Matrix)

def drawGame(player, ship, asteroids, projectiles, scoreboard, SCORE, statedisplay, rays, font, win):
    win.fill(C.BLACK)
    drawPlayer(player, ship, win)
    drawAsteroids(asteroids, win)
    drawProjectiles(projectiles, win)
    displayState(player.state, font, statedisplay, win)
    displayScore(SCORE, font, scoreboard, win)
    if C.DRAW_SENSORS: drawSensors(rays, win)
    pygame.display.update()

def simulate(game, CHROMOSOME):
    player = game[0]
    asteroids = game[1]
    projectiles = game[2]
    LEVEL = game[3]
    SCORE = game[4]
    steps = game[5]
    action = 0
    for step in range(steps):
        sense(player, asteroids)
        action = GA.updateAction(player, CHROMOSOME)
        player = executeAction(player, projectiles, action)
        projectiles = detectProjectileColision(asteroids, projectiles)
        SCORE += updateScore(player, asteroids)
        if SCORE < 0: SCORE = 0
        player.score = SCORE
        updatePlayer(player)
        LEVEL = updateAsteroids(asteroids, LEVEL)
        updateProjectiles(projectiles)
    return SCORE

def executeAction(player, projectiles, action):
    if action == 'Left':
        player.rotation += 5
    if action == 'Right':
        player.rotation -= 5
    if action == 'Thrust':
        if player.speed <= C.MAXSPEED: player.speed += C.THRUST
        del player.thrustvectors[0]
        player.thrustvectors.append([player.speed, player.rotation])
    if action == 'Shoot':
        if not player.firing: projectiles.append(fireProjectile(player))
        player.firing = True
    if action != 'Shoot': player.firing = False
    return player

def newGameContainer():
    player = Player(C.WINDOW_WIDTH/2, C.WINDOW_HEIGHT/2, 0)
    LEVEL = 1
    asteroids = []
    asteroids = generateAsteroids(asteroids, LEVEL)
    projectiles = []
    SCORE = 0
    game = [player, asteroids, projectiles, LEVEL, SCORE, GA.SimulationLength]
    return game

#Generate a projectile in the direction the player is facing.
def fireProjectile(player):
    x = player.x + C.PLAYERSIZE/2
    y = player. y + C.PLAYERSIZE/2
    fire = Projectile(x, y, player.rotation)
    return fire

def wrap(object):
    if object.y > C.WINDOW_HEIGHT: object.y -= C.WINDOW_HEIGHT
    if object.y < 0: object.y += C.WINDOW_HEIGHT
    if object.x > C.WINDOW_WIDTH: object.x -= C.WINDOW_WIDTH
    if object.x < 0: object.x += C.WINDOW_WIDTH
    return object

def updatePosition(object):
    object.x += math.cos(math.radians(object.direction))*object.speed
    object.y -= math.sin(math.radians(object.direction))*object.speed
    wrap(object)

#Calculate position and lifespan of projectiles based on velocity, wrapping as necessary.
def updateProjectiles(projectiles):
    for projectile in projectiles:
        updatePosition(projectile)
        projectile.lifespan -= projectile.speed
        if projectile.lifespan <= 0: projectiles.remove(projectile)

#Draw projectiles to screen.
def drawProjectiles(projectiles, win):
    for each in projectiles:
        pygame.draw.rect(win, (255, 255, 255), (each.x-1, each.y-1, 3, 3))

#Calculate player velocity using thrust vectors.
def updateDirection(player, thrustvectors):
    xcomps = []
    ycomps = []
    for each in range(len(thrustvectors)):
        xcomps.append(math.cos(math.radians(thrustvectors[each][1]))*thrustvectors[each][0])
        ycomps.append(math.sin(math.radians(thrustvectors[each][1]))*thrustvectors[each][0])
    xavg = sum(xcomps)/len(thrustvectors)
    yavg = sum(ycomps)/len(thrustvectors)
    player.speed = math.sqrt(xavg**2 + yavg**2)
    player.direction = math.degrees(math.atan2(yavg/C.MAXSPEED,xavg/C.MAXSPEED))

#Calculate new ship position using velocity, wrapping as necessary.
def updatePlayer(player):
    updateDirection(player, player.thrustvectors)
    decayThrust(player.thrustvectors)
    updatePosition(player)
    if player.hit:
        player.hit = False
        player.x = C.WINDOW_WIDTH/2
        player.y = C.WINDOW_HEIGHT/2
        player.respawning = C.RESPAWNTIME
    if player.respawning > 0:
        player.respawning -= C.FPS

#Draw player to screen.
def drawPlayer(player, ship, win):
    rotatedShip = pygame.transform.rotate(ship, player.rotation)
    newship = rotatedShip.get_rect(center = ship.get_rect(topleft = (player.x, player.y)).center)
    if player.respawning % 500 < 250:
        win.blit(rotatedShip, newship.topleft)

#Decay each thrust vector.
def decayThrust(thrustvectors):
    for each in thrustvectors:
        if each[0] >= C.DECAY: each[0] -= C.DECAY

#Generate some random asteroids based on current level.
def generateAsteroids(asteroids, LEVEL):
    INITIAL_DENSITY = 3
    for each in range(LEVEL + INITIAL_DENSITY):
        newasteroid = Asteroid(random.random()*C.WINDOW_WIDTH, random.random()*C.WINDOW_HEIGHT, random.random()*360)
        asteroids.append(newasteroid)
        asteroids[each].sprite = pygame.image.load(asteroids[each].IMAGE)
        asteroids[each].sprite = pygame.transform.scale(asteroids[each].sprite, (3*C.ASTEROIDSCALE, 3*C.ASTEROIDSCALE))
    return asteroids

#Calculate new position of each asteroid, wrapping as necessary.
def updateAsteroids(asteroids, LEVEL):
    if len(asteroids) == 0:
        LEVEL += 1
        asteroids = generateAsteroids(asteroids, LEVEL)
    for asteroid in asteroids:
        updatePosition(asteroid)
    return LEVEL

#Draw asteroids to screen.
def drawAsteroids(asteroids, win):
    for each in asteroids:
        win.blit(each.sprite,( each.x, each.y))

#Detect whether the player has hit any asteroids.
def detectPlayerColision(asteroids, player):
    if not player.hit and not player.respawning:
        for asteroid in asteroids:
            diameter = asteroid.scale*C.ASTEROIDSCALE
            if player.x >= asteroid.x and player.y >= asteroid.y and player.x <= asteroid.x + diameter and player.y <= asteroid.y + diameter:
                player.hit = True
                return C.DEATHPOINTS
    return 0

#Detect whether any projectiles have hit any asteroids.
def detectProjectileColision(asteroids, projectiles):
    for asteroid in asteroids:
        for bullet in projectiles:
            diameter = asteroid.scale*C.ASTEROIDSCALE
            if bullet.x >= asteroid.x and bullet.y >= asteroid.y and bullet.x <= asteroid.x + diameter and bullet.y <= asteroid.y + diameter:
                asteroid.dead = True
                projectiles.remove(bullet)
    return projectiles

#Split any dead asteroids into smaller ones and remove them.
def splitAsteroids(asteroids):
    score = 0
    for each in asteroids:
        if each.dead == True:
            score += C.BREAKPOINTS[each.scale]
            if each.scale > 1:
                newAsteroid1 = Asteroid(each.x, each.y, random.random()*360)
                newAsteroid2 = Asteroid(each.x, each.y, random.random()*360)
                newAsteroid1.scale = newAsteroid2.scale = each.scale - 1
                newAsteroid1.speed = newAsteroid2.speed = each.speed + 1
                newAsteroid1.sprite = newAsteroid2.sprite = pygame.transform.scale(newAsteroid2.sprite, (newAsteroid2.scale*C.ASTEROIDSCALE, newAsteroid2.scale*C.ASTEROIDSCALE))
                asteroids.append(newAsteroid1)
                asteroids.append(newAsteroid2)
            asteroids.remove(each)
    return score

def updateScore(player, asteroids):
    return detectPlayerColision(asteroids, player) + splitAsteroids(asteroids)

def displayScore(SCORE, font, scoreboard, win):
    show_score = font.render('SCORE: '+str(SCORE), True, C.WHITE, C.BLACK)
    win.blit(show_score, scoreboard)

def displayState(state, font, statedisplay, win):
    show_state = font.render('State: '+' '.join(state), True, C.WHITE, C.BLACK)
    win.blit(show_state, statedisplay)

#Determine whether two lines (lists of two points x and y) intersect.
#Credit: https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
def lines_intersect(l1, l2):
    p1 = x = 0
    p2 = y = 1
    def ccw(A, B, C):
        return (C[y] - A[y]) * (B[x] - A[x]) > (B[y] - A[y]) * (C[x] - A[x])
    return ccw(l1[p1], l2[p1], l2[p2]) != ccw(l1[p2], l2[p1], l2[p2]) and ccw(l1[p1], l1[p2], l2[p1]) != ccw(l1[p1], l1[p2], l2[p2])

#Update player state by checking whether rays from the player intersect any asteroids and if so, what size.
def sense(player, asteroids):
    angle = player.rotation
    x = 0
    y = 1
    ship = [player.x+C.PLAYERSIZE/2, player.y+C.PLAYERSIZE/2]
    result = []
    rays = []
    for sensor in range(C.SENSORCOUNT):
        edge = [ship[x] + math.cos(math.radians(angle))*C.SENSORRANGE,
                ship[y] - math.sin(math.radians(angle))*C.SENSORRANGE]
        ray = [ship, edge]
        rays.append(ray)
        result.append('None')
        for asteroid in asteroids:
            diameter = asteroid.scale*C.ASTEROIDSCALE
            UL = [asteroid.x, asteroid.y]
            UR = [asteroid.x + diameter, asteroid.y]
            LL = [asteroid.x, asteroid.y + diameter]
            LR = [asteroid.x + diameter, asteroid.y + diameter]
            if lines_intersect(ray, [UL, UR]) or lines_intersect(ray, [UR, LR]) or lines_intersect(ray, [LL, LR]) or lines_intersect(ray, [UL, LL]):
                #result[sensor] = (C.results[asteroid.scale])
                result[sensor] = C.results[1]
        angle += 360/C.SENSORCOUNT
    player.state = tuple(result)
    return rays

def drawSensors(rays, win):
    for ray in rays:
        pygame.draw.line(win, (255, 255, 255), ray[0], ray[1], 3)

#Save Q-Matrix to a .csv file. First column: state #, columns 2-5: Q-Scores for actions in Q.actions[]
#TODO: Fix file naming so that it doesn't keey outputting to test0
def saveQmatrix(Q_Matrix):
    name = "empty"
    t = 0
    while name == "empty":
        if not os.path.exists(os.getcwd()+"test"+str(t)+".csv"): name = "test"+str(t)+".csv"
    output = open(name, "w")
    print("Q Matrix data saved to"+name)

    for state in range(len(Q_Matrix)):
        output.write(str(state)+',')
        for action in range(len(Q_Matrix[state])):
            output.write(str(Q_Matrix[state][action])+',')
        output.write('\n')
    output.close()

if __name__ == '__main__':
    main()
