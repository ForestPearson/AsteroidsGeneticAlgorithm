import random, itertools

sensors = ['DN', 'NE', 'DE', 'SE', 'DS' , 'SW' , 'DW' , 'NW']
results = ['None', 'Small', 'Medium', 'Large']
actions = ['Left', 'Right', 'Thrust', 'Shoot']
episodes = 5000
lifespan = 200
stepsize = 0.2
discount = 0.9
takerisk = 0.1

Q_Matrix = []
Q = []

def initialize():
      for s in itertools.product(results, repeat = len(sensors)): Q.append(s)
      Q_Matrix = [[0 for a in range(len(actions))]for s in range(len(Q))]
      return Q_Matrix

def choose_action(state):
    if random.random() < takerisk: return random.choice(range(len(actions)))
    else: return greedy_choice(state)

def greedy_choice(state):
    #print(state)
    #print(Q.index(state))
    best = max(Q_Matrix[Q.index(state)])
    bests = [i for i, x in enumerate(Q_Matrix[Q.index(state)]) if x == best]
    return random.choice(bests)

def act(action, player):
    initscore = player.score
    finalscore = initscore
    #execute given action
    #TODO figure this stuff out
    if action == 'Left':
        player.position = ((player.position + MOVESPEED) * FRAMES_PER_ACTION) * moveVector
        updatePosition(player)
        drawPlayer(player, ship, win)
    if action == 'Right':
        player.position = ((player.position + MOVESPEED) * FRAMES_PER_ACTION) * moveVector
        updatePosition(player)
        drawPlayer(player, ship, win)
    if action == 'Thrust':
        player.position = ((player.position + MOVESPEED) * FRAMES_PER_ACTION) * moveVector
        updatePosition(player)
        drawPlayer(player,ship,win)
    if action == 'Shoot':
        drawPlayer(player, ship,win)
        fireProjectile(player, ship)
        drawProjectiles(projectiles, win)
        if(detectProjectileCollision(asteroids, projectiles)):
            finalscore += asteroidValue

def train(player, Q_Matrix):
    initstate = Q.index(player.state)
    action = choose_action(player.state)
    prev = Q_Matrix[initstate][action]
    reward = act(actions[action], player)
    nextbest = Q_Matrix[Q.index(player.state)][greedy_choice(player.state)]
    Q_Matrix[initstate][action] = prev + stepsize*(reward + discount*nextbest - prev)
    return Q_Matrix

def step(player):
    action = choose_action(player.state)
    reward = act(actions[action], player)
