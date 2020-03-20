import random
import math
import pygame
import main
import QLearning as Q
import constant as C
import main

#Tunable parameters
PopulationSize = 10								#Number of chromosomes.
NumIterations = 10  							#Number of generations.
SimulationLength = 1000                         #Number of frames to simulate
MutationPct = 0.45								#Liklihood of mutation.
Replacement = True								#Multiple recombination.
Kickstart = True								#Start with unique rows.
Elitism = True									#Better parents persist.
Resets = True									#Allow reset when stale.
StaleFactor = 0.05								#Staleness before reset.
statespace = len(C.results)**len(C.sensors)

def random_chromosome():
    return [random.randint(1,(len(C.actions)))-1 for i in range(statespace)]

def updateAction(player, chromosome):
    return C.actions[chromosome[C.state.index(player.state)]]

def average_fitness(fitness_scores):
    total_fitness = 0
    for each in range(PopulationSize):
        total_fitness += fitness_scores[each]
    return total_fitness/PopulationSize

def selection_chance(fitness_scores, chromosome, remaining):
    this_fitness = fitness_scores[chromosome]
    fit_sum = 0
    for each in range(remaining):
        fit_sum += fitness_scores[each]
    if fit_sum == 0: return 0
    else: return this_fitness/fit_sum

def select(fitness_scores, remaining, blacklist):
    r = random.random()
    lower = upper = 0
    #TODO: surround this in an infinite loop so that it cant ever not find a parent to select
    for chromosome in range(remaining):
        lower = upper
        upper += selection_chance(fitness_scores, chromosome, remaining)
        if r > lower and r < upper and chromosome != blacklist: return chromosome
    return -1

def select_pair(population, fitness_scores, remaining):
    p1 = select(fitness_scores, remaining, -1)
    if p1 == -1: p1 = 0
    p2 = p1
    while p2 == p1: p2 = select(fitness_scores, remaining-1, p1)
    if p2 == -1:
        if p1 == 0: p2 = 1
        else: p2 = 0
    if Replacement: return [population[max(p1, p2)], population[min(p1, p2)]]
    else: return [population.pop(max(p1, p2)), population.pop(min(p1, p2))], population

def breed(population, fitness_scores):
    newPopulation = []
    newFitnessScores = []
    remaining = PopulationSize
    while remaining > 0:
        if Replacement: p = select_pair(population, fitness_scores, PopulationSize)
        else: p, population = select_pair(population, fitness_scores, remaining)
        p1 = p[0]
        p2 = p[1]
        r = random.randrange(1, statespace)
        c1 = p1[:r]+p2[r:]
        c2 = p2[:r]+p1[r:]
        if random.random() < MutationPct:
            g1 = random.randrange(statespace)
            g2 = random.randrange(statespace)
            c1[g1], c1[g2] = c1[g2], c1[g1]
        if random.random() < MutationPct:
            g1 = random.randrange(statespace)
            g2 = random.randrange(statespace)
            c2[g1], c2[g2] = c2[g2], c2[g1]
        if Elitism:
            p1score = fitness_scores[population.index(p[0])]
            p2score = fitness_scores[population.index(p[1])]
            c1score = main.simulate(main.newGameContainer(), c1)
            c2score = main.simulate(main.newGameContainer(), c2)
            contenderscores = [p1score, p2score, c1score, c2score]
            contenders = [p1, p2, c1, c2]
            m1 = contenderscores.index(max(contenderscores))
            newFitnessScores.append(contenderscores[m1])
            newPopulation.append(contenders.pop(m1))
            del contenderscores[m1]
            m2 = contenderscores.index(max(contenderscores))
            newFitnessScores.append(contenderscores[m2])
            newPopulation.append(contenders.pop(m2))
        else:
            newPopulation.append(c1)
            newPopulation.append(c2)
        remaining -= 2
        print("remaining: ",remaining)
    return newPopulation, newFitnessScores

def best_solution(fitness_scores):
    return fitness_scores.index(max(fitness_scores))




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
#
#def main():
#     #these three variables are placeholders
#    maxFitness = (timeStepCount *asteroidPoints * asteroidAmount)
#    maxIterations = 500
#    iterations = 0
#    population = [random_chromosome() for _ in range(100)]
#    while not maxFitness in [fitness(chrom) for chrom in population]:
#        population = genetic_algorithm(iterations, maxIterations, population, fitness)
#        iterations += 1


#if __name__ == "__main__":
#    main()
