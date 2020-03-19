
#Genetic algorithm


#Q-learning

#Game
WINDOW_WIDTH = 1280                                                             #
WINDOW_HEIGHT = 920
BLACK = (0, 0, 0)                                                               #
WHITE = (255, 255, 255)                                                         #
MAXSPEED = 10                                                                   #
THRUST = 2.5                                                                    #Thrust vector increase per input.
DECAY = 0.05                                                                    #Thrust vector decay per frame.
VECTORCOUNT = 30                                                                #Number of thrust vectors
BREAKPOINTS = [0, 100, 50, 20]                                                  #Points awarded for breaking each size.
DEATHPOINTS = -1000                                                             #Points deducted for getting hit.
RESPAWNTIME = 6000                                                              #Invulnerability time in milliseconds.
ASTEROIDSCALE = 30                                                              #
PLAYERSIZE = 20                                                                 #
FPS = 60                                                                        #
SENSORCOUNT = 8                                                                 #Ship sensors, limited by Q.sensors[].
#SENSORRANGE = constant.WINDOW_HEIGHT/2
SENSORRANGE = WINDOW_HEIGHT/2                                                  #
FRAMES_PER_ACTION = 6                                                           #
QTRAINING = True                                                               #Toggle for Q-Learning.
SAVEQMATRIX = False                                                              #Toggle for output of Q-Matrix.
DRAW_SENSORS = False                                                             #
DISPLAY_GAME = True
