import random
import math
import pygame
import main
import QLearning as Q
import constant as C

#Tunable parameters
PopulationSize = 40								#Number of chromosomes.
NumIterations = 10000  							#Number of generations.
MutationPct = 0.45								#Liklihood of mutation.
Replacement = False								#Multiple recombination.
Kickstart = True								#Start with unique rows.
Elitism = True									#Better parents persist.
Resets = True									#Allow reset when stale.
StaleFactor = 0.05								#Staleness before reset.
BOARDSIZE = 8									#Boardsize for n-queens.

def random_chromosome():
    statespace = len(C.results)**len(C.sensors)
    return [random.randint(1,(len(C.actions)))-1 for i in range(statespace)]

def updateAction(player, chromosome):
    action = C.actions[chromosome[C.state.index(player.state)]]

#calculate the fitness of a chromosome
def fitness(chromosome):
    return int(maxFitness - score())

#our probability is just defined by the ratio of a chromosomes fitness compared to our maximum fitness threshold
def probability(chromosome, maxFitness):
    return fitness(chromosome)/ maxFitness
#randomly pick nodes within a certain range.
def random_pick(population, probabilities):
    population_with_probability = zip(population, probabilities)
    total = sum(w for c, w in population_with_probability)
    r = random.uniform(0,total)
    upto = 0
    for c, w in zip(population, probabilities):
        if upto + w >= r:
            return c
        upto += w
    assert False, "Error, something went wrong......"
#combine the first trait of the x "genome" with the y "genome"
def reproduce(x,y):
    n = len(x)
    c = random.randint(0, n-1)
    return x[0:c] + y[c:n]
#randomly changes an aspect about an unfortunate child node
def mutate(x):
    n = len(x)
    c = random.randint(0, n-1)
    m = random.randint(1,n)
    x[c] = m
    return x
#this is where the actual magic happens, all the functions above were helper functions for this
# we set our mutation here and this is where we modify our population
def genetic_algorithm(iterations, maxIterations, population, fitness):
    iterations += 1
    mutation_probability = 0.055
    new_population = []
    probabilities = [probability(n, fitness) for n in population]
    #after we find our probabilities for our nodes, then start to select their attributes to reproduce with
    for i in range(len(population)):
        x = random_pick(population, probabilities)
        y = random_pick(population, probabilities)
        child = reproduce(x,y)
        #if our mutation is greater than our randomly generated number, mutate a part of the child
        if random.random() < mutation_probability:
            child = mutate(child)
        print_chromosome(child)
        #add this new child to the generation
        new_population.append(child)
        #we found our solution child! Or we reached our limit
        if fitness(child) == maxFitness: break
        if iterations == maxIterations: break
    return new_population
#prints individual information about a chromosome
def print_chromosome(chrom):
    print("Chromosome = {}, Fitness = {}".format(str(chrom), fitness(chrom)))

def main():
     #these three variables are placeholders
    maxFitness = (timeStepCount *asteroidPoints * asteroidAmount)
    maxIterations = 500
    iterations = 0
    population = [random_chromosome() for _ in range(100)]
    while not maxFitness in [fitness(chrom) for chrom in population]:
        population = genetic_algorithm(iterations, maxIterations, population, fitness)
        iterations += 1


if __name__ == "__main__":
    main()
