import random
import math
from typing import List

from neuro_evolution.crossover import Crossover
from neuro_evolution.genotype import Genotype
from neuro_evolution.mutation import Mutation
from neuro_evolution.network_factory import NetworkFactory
from neuro_evolution.phenotype import Phenotype


class Species:
    def __init__(self):
        self.members: List[Genotype] = []
        self.topFitness: float = 0.0
        self.staleness: int = 0
        self.fitnessSum: float = 0.0

    def breed(self):
        roll = random.random()
        if roll < Crossover.CROSSOVER_CHANCE and len(self.members) > 1:
            s1 = random.randint(0, len(self.members) - 1)
            s2 = random.randint(0, len(self.members) - 2)
            if s2 >= s1:
                s2 += 1
            if s1 > s2:
                s1, s2 = s2, s1
            child = Crossover.instance.produce_offspring(self.members[s1], self.members[s2])
            Mutation.instance.mutate_all(child)
            selection = random.randint(0, len(self.members) - 1)
            return child
        else:
            selection = random.randint(0, len(self.members) - 1)
            child = self.members[selection].clone()
            Mutation.instance.mutate_all(child)
            return child

    def sort_members(self):
        self.members.sort(key=lambda x: x.adjustedFitness, reverse=True)

    def cull_to_portion(self, portion):
        if len(self.members) <= 1:
            return
        remaining = math.ceil(len(self.members) * portion)
        del self.members[remaining:]

    def cull_to_one(self):
        if len(self.members) <= 1:
            return
        del self.members[1:]

    def calculate_adjusted_fitness_sum(self):
        self.fitnessSum = sum(member.adjustedFitness for member in self.members)


class Population:
    instance = None

    def __init__(self):
        self.GENERATION = 0
        self.POPULATION_SIZE = 256
        self.INPUTS = 126
        self.OUTPUTS = 7
        self.MAX_STALENESS = 15
        self.PORTION = 0.2
        self.species = []
        self.genetics = []
        self.population = []

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def generate_base_population(self, size, inputs, outputs):
        self.POPULATION_SIZE = size
        self.INPUTS = inputs
        self.OUTPUTS = outputs
        for _ in range(self.POPULATION_SIZE):
            genotype = NetworkFactory().create_base_genotype(inputs, outputs)
            self.genetics.append(genotype)
            self.add_to_species(genotype)
        NetworkFactory().register_base_markings(inputs, outputs)
        for genotype in self.genetics:
            Mutation.instance.mutate_all(genotype)
        self.inscribe_population()

    def new_generation(self):
        self.calculate_adjusted_fitness()
        for i, s in enumerate(self.species):
            s.sort_members()
            s.cull_to_portion(self.PORTION)
            if len(s.members) <= 1:
                del self.species[i]
        self.update_staleness()
        fitness_sum = sum(s.fitnessSum for s in self.species)
        children = []
        for s in self.species:
            build = int(self.POPULATION_SIZE * (s.fitnessSum / fitness_sum)) - 1
            for _ in range(build):
                child = s.breed()
                children.append(child)
        while self.POPULATION_SIZE > len(self.species) + len(children):
            child = random.choice(self.species).breed()
            children.append(child)
        for s in self.species:
            s.cull_to_one()
        for child in children:
            self.add_to_species(child)
        self.genetics.clear()
        for s in self.species:
            self.genetics.extend(s.members)
        self.inscribe_population()
        self.GENERATION += 1

    def calculate_adjusted_fitness(self):
        for s in self.species:
            for member in s.members:
                member.adjustedFitness = member.fitness / len(s.members)

    def update_staleness(self):
        for s in self.species:
            if len(self.species) == 1:
                return
            top = s.members[0].fitness
            if s.topFitness < top:
                s.topFitness = top
                s.staleness = 0
            else:
                s.staleness += 1
            if s.staleness >= self.MAX_STALENESS:
                self.species.remove(s)

    def inscribe_population(self):
        self.population.clear()
        for genotype in self.genetics:
            genotype.fitness = 0.0
            genotype.adjustedFitness = 0.0
            physical = Phenotype()
            physical.inscribe_genotype(genotype)
            physical.process_graph()
            self.population.append(physical)

    def add_to_species(self, genotype):
        if not self.species:
            new_species = Species()
            new_species.members.append(genotype)
            self.species.append(new_species)
        else:
            found = False
            for s in self.species:
                distance = Crossover.instance.speciation_distance(s.members[0], genotype)
                if distance < Crossover.DISTANCE:
                    s.members.append(genotype)
                    found = True
                    break
            if not found:
                new_species = Species()
                new_species.members.append(genotype)
                self.species.append(new_species)

    @staticmethod
    def sort_genotype_by_fitness(a, b):
        if a.fitness > b.fitness:
            return -1
        elif a.fitness == b.fitness:
            return 0
        return 1
