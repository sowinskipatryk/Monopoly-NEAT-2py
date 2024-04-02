import os

from typing import List

from analytics import Analytics
from rng import RNG
from tournament import Tournament
from neuro_evolution.network_factory import NetworkFactory
from neuro_evolution.crossover import Crossover
from neuro_evolution.mutation import Mutation, Marking
from neuro_evolution.population import Population, Species
from neuro_evolution.genotype import Genotype, VertexInfo


class Program:
    DELIM_MAIN = ';'
    DELIM_COMMA = ','

    @staticmethod
    def main():
        path = "C:\\Users\\brad\\Desktop\\monopoly_population.txt"

        Analytics()

        RNG()

        NetworkFactory()

        Mutation()
        Crossover()
        Population()

        tournament = Tournament()

        if os.path.exists(path):
            Program.load_state(path, tournament)
        else:
            tournament.initialise()

        for i in range(1000):
            tournament.execute_tournament()
            Population.instance.new_generation()
            Program.save_state(path, tournament)

    @staticmethod
    def save_state(target, tournament):
        print("SAVING POPULATION")

        build = ""
        build2 = ""

        build += str(Population.instance.GENERATION)
        build += Program.DELIM_MAIN
        build += str(tournament.champion_score)
        build += Program.DELIM_MAIN

        markings = 0

        for mutation in Mutation.instance.historical:
            build += str(mutation.order)
            build += Program.DELIM_COMMA

            build += str(mutation.source)
            build += Program.DELIM_COMMA

            build += str(mutation.destination)

            build += Program.DELIM_COMMA

            markings += 1

        net_build: List[str] = []
        net_count: int = -1
        gene_count: int = 0

        build += Program.DELIM_MAIN

        for species in Population.instance.species:
            net_build.append("")
            net_count += 1

            net_build[net_count] += str(species.top_fitness)
            net_build[net_count] += Program.DELIM_COMMA
            net_build[net_count] += str(species.staleness)

            net_build[net_count] += "&"

            for member in species.members:
                net_build.append("")
                net_count += 1
                gene_count += 1

                print(f"{gene_count}/{len(Population.instance.genetics)}")

                for vertex in member.vertices:
                    net_build[net_count] += str(vertex.index)
                    net_build[net_count] += Program.DELIM_COMMA
                    net_build[net_count] += str(vertex.type.value)
                    net_build[net_count] += Program.DELIM_COMMA

                net_build[net_count] += '#'

                for edge in member.edges:
                    net_build[net_count] += str(edge.source)
                    net_build[net_count] += Program.DELIM_COMMA
                    net_build[net_count] += str(edge.destination)
                    net_build[net_count] += Program.DELIM_COMMA
                    net_build[net_count] += str(edge.weight)
                    net_build[net_count] += Program.DELIM_COMMA
                    net_build[net_count] += str(edge.enabled)
                    net_build[net_count] += Program.DELIM_COMMA
                    net_build[net_count] += str(edge.innovation)
                    net_build[net_count] += Program.DELIM_COMMA

                if member != species.members[-1]:
                    net_build[net_count] += "n"

            if species != Population.instance.species[-1]:
                net_build[net_count] += "&"

        build2 += Program.DELIM_MAIN

        with open(target, "w") as file:
            file.write(build)

            for b in net_build:
                file.write(b)

            file.write(build2)

        print(f"{markings} MARKINGS")

    @staticmethod
    def load_state(location, tournament):
        with open(location, "r") as file:
            load = file.read()

        parts = load.split(Program.DELIM_MAIN)

        gen = int(parts[0])
        score = float(parts[1])

        Population.instance.generation = gen
        tournament.champion_score = score

        marking_string = parts[2]
        marking_parts = marking_string.split(Program.DELIM_COMMA)

        for i in range(0, len(marking_parts), 3):
            order = int(marking_parts[i])
            source = int(marking_parts[i + 1])
            destination = int(marking_parts[i + 2])

            mutation = Marking()
            mutation.order = order
            mutation.source = source
            mutation.destination = destination

            Mutation.instance.historical.append(mutation)

        network_string = parts[3]
        species_parts = network_string.split('&')

        for x in range(0, len(species_parts), 2):
            first_parts = species_parts[x].split(Program.DELIM_COMMA)
            Population.instance.species.append(Species())
            Population.instance.species[-1].top_fitness = float(first_parts[0])
            Population.instance.species[-1].staleness = int(first_parts[1])

            network_parts = species_parts[x + 1].split('n')

            for i in range(len(network_parts)):
                genotype = Genotype()

                network = network_parts[i]
                nparts = network.split('#')

                verts = nparts[0].split(',')
                for j in range(0, len(verts) - 1, 2):
                    index = int(verts[j])
                    type_ = getattr(VertexInfo.EType, verts[j + 1])
                    genotype.add_vertex(type_, index)

                edges = nparts[1].split(',')
                for j in range(0, len(edges) - 1, 5):
                    source = int(edges[j])
                    destination = int(edges[j + 1])
                    weight = float(edges[j + 2])
                    enabled = bool(edges[j + 3])
                    innovation = int(edges[j + 4])

                    genotype.add_edge(source, destination, weight, enabled, innovation)

                Population.instance.species[-1].members.append(genotype)
                Population.instance.genetics.append(genotype)

        Population.instance.inscribe_population()


if __name__ == "__main__":
    Program.main()
