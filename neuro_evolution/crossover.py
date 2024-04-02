import random
from neuro_evolution.genotype import Genotype, VertexInfo


class Crossover:
    instance = None

    CROSSOVER_CHANCE = 0.75

    C1 = 1.0
    C2 = 1.0
    C3 = 0.4
    DISTANCE = 1.0

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def produce_offspring(self, first, second):
        copy_first = first.edges.copy()
        copy_second = second.edges.copy()

        match_first = []
        match_second = []
        disjoint_first = []
        disjoint_second = []
        excess_first = []
        excess_second = []

        genes_first = len(first.edges)
        genes_second = len(second.edges)

        invmax_first = first.edges[-1].innovation
        invmax_second = second.edges[-1].innovation

        invmin = min(invmax_first, invmax_second)

        for i in range(genes_first):
            for j in range(genes_second):
                info_first = copy_first[i]
                info_second = copy_second[j]

                if info_first.innovation == info_second.innovation:
                    match_first.append(info_first)
                    match_second.append(info_second)

                    copy_first.remove(info_first)
                    copy_second.remove(info_second)

                    genes_first -= 1
                    genes_second -= 1
                    break

        for info in copy_first:
            if info.innovation > invmin:
                excess_first.append(info)
            else:
                disjoint_first.append(info)

        for info in copy_second:
            if info.innovation > invmin:
                excess_second.append(info)
            else:
                disjoint_second.append(info)

        child = Genotype()

        matching = len(match_first)

        for i in range(matching):
            roll = random.randint(0, 1)
            if roll == 0 or not match_second[i].enabled:
                child.add_edge(match_first[i].source, match_first[i].destination, match_first[i].weight,
                               match_first[i].enabled, match_first[i].innovation)
            else:
                child.add_edge(match_second[i].source, match_second[i].destination, match_second[i].weight,
                               match_second[i].enabled, match_second[i].innovation)

        for info in disjoint_first:
            child.add_edge(info.source, info.destination, info.weight, info.enabled, info.innovation)

        for info in excess_first:
            child.add_edge(info.source, info.destination, info.weight, info.enabled, info.innovation)

        child.sort_edges()

        ends = []

        for vertex in first.vertices:
            if vertex.type == VertexInfo.EType.HIDDEN:
                break
            ends.append(vertex.index)
            child.add_vertex(vertex.type, vertex.index)

        self.add_unique_vertices(child, ends)

        child.sort_vertices()

        return child

    def add_unique_vertices(self, genotype, ends):
        unique = set()

        for info in genotype.edges:
            if info.source not in ends and info.source not in unique:
                unique.add(info.source)

            if info.destination not in ends and info.destination not in unique:
                unique.add(info.destination)

        for index in unique:
            genotype.add_vertex(VertexInfo.EType.HIDDEN, index)

    def speciation_distance(self, first, second):
        copy_first = first.edges.copy()
        copy_second = second.edges.copy()

        match_first = []
        match_second = []
        disjoint_first = []
        disjoint_second = []
        excess_first = []
        excess_second = []

        genes_first = len(first.edges)
        genes_second = len(second.edges)

        invmax_first = first.edges[-1].innovation
        invmax_second = second.edges[-1].innovation

        invmin = min(invmax_first, invmax_second)

        diff = 0.0

        for i in range(genes_first):
            for j in range(genes_second):
                info_first = copy_first[i]
                info_second = copy_second[j]

                if info_first.innovation == info_second.innovation:
                    weight_diff = abs(info_first.weight - info_second.weight)
                    diff += weight_diff

                    match_first.append(info_first)
                    match_second.append(info_second)

                    copy_first.remove(info_first)
                    copy_second.remove(info_second)

                    genes_first -= 1
                    genes_second -= 1
                    break

        for info in copy_first:
            if info.innovation > invmin:
                excess_first.append(info)
            else:
                disjoint_first.append(info)

        for info in copy_second:
            if info.innovation > invmin:
                excess_second.append(info)
            else:
                disjoint_second.append(info)

        match = len(match_first)
        disjoint = len(disjoint_first) + len(disjoint_second)
        excess = len(excess_first) + len(excess_second)

        n = max(len(first.edges), len(second.edges))

        E = excess / n
        D = disjoint / n
        W = diff / match if match > 0 else 0

        return E * self.C1 + D * self.C2 + W * self.C3
