import random

from neuro_evolution.genotype import VertexInfo, EdgeInfo


class Marking:
    def __init__(self):
        self.order = 0
        self.source = 0
        self.destination = 0


class Mutation:
    instance = None

    def __init__(self):
        self.MUTATE_LINK = 0.2
        self.MUTATE_NODE = 0.1
        self.MUTATE_ENABLE = 0.6
        self.MUTATE_DISABLE = 0.2
        self.MUTATE_WEIGHT = 2.0
        self.PETRUB_CHANCE = 0.9
        self.SHIFT_STEP = 0.1
        self.historical = []

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def register_marking(self, info):
        for marking in self.historical:
            if marking.source == info.source and marking.destination == info.destination:
                return marking.order

        creation = Marking()
        creation.order = len(self.historical)
        creation.source = info.source
        creation.destination = info.destination

        self.historical.append(creation)

        return len(self.historical) - 1

    def mutate_all(self, genotype):
        for _ in range(int(self.MUTATE_WEIGHT)):
            self.mutate_weight(genotype)
        for _ in range(int(self.MUTATE_LINK)):
            self.mutate_link(genotype)
        for _ in range(int(self.MUTATE_NODE)):
            self.mutate_node(genotype)
        for _ in range(int(self.MUTATE_DISABLE)):
            self.mutate_disable(genotype)
        for _ in range(int(self.MUTATE_ENABLE)):
            self.mutate_enable(genotype)

    def mutate_link(self, genotype):
        vertex_count = len(genotype.vertices)
        edge_count = len(genotype.edges)
        potential = []

        for i in range(vertex_count):
            for j in range(vertex_count):
                source = genotype.vertices[i].index
                destination = genotype.vertices[j].index
                t1 = genotype.vertices[i].type
                t2 = genotype.vertices[j].type

                if t1 == VertexInfo.EType.OUTPUT or t2 == VertexInfo.EType.INPUT:
                    continue

                if source == destination:
                    continue

                search = False

                for k in range(edge_count):
                    edge = genotype.edges[k]
                    if edge.source == source and edge.destination == destination:
                        search = True
                        break

                if not search:
                    weight = random.random() * 4.0 - 2.0
                    creation = EdgeInfo(source, destination, weight, True)
                    potential.append(creation)

        if not potential:
            return

        selection = random.randint(0, len(potential) - 1)
        mutation = potential[selection]
        mutation.innovation = self.register_marking(mutation)

        genotype.add_edge(mutation.source, mutation.destination, mutation.weight, mutation.enabled, mutation.innovation)

    def mutate_node(self, genotype):
        edge_count = len(genotype.edges)
        selection = random.randint(0, edge_count - 1)
        edge = genotype.edges[selection]

        if not edge.enabled:
            return

        edge.enabled = False
        vertex_new = genotype.vertices[-1].index + 1
        vertex = VertexInfo(VertexInfo.EType.HIDDEN, vertex_new)
        first = EdgeInfo(edge.source, vertex_new, 1.0, True)
        second = EdgeInfo(vertex_new, edge.destination, edge.weight, True)
        first.innovation = self.register_marking(first)
        second.innovation = self.register_marking(second)
        genotype.add_vertex(vertex.type, vertex.index)
        genotype.add_edge(first.source, first.destination, first.weight, first.enabled, first.innovation)
        genotype.add_edge(second.source, second.destination, second.weight, second.enabled, second.innovation)

    @staticmethod
    def mutate_enable(genotype):
        candidates = [edge for edge in genotype.edges if not edge.enabled]
        if not candidates:
            return
        selection = random.randint(0, len(candidates) - 1)
        edge = candidates[selection]
        edge.enabled = True

    @staticmethod
    def mutate_disable(genotype):
        candidates = [edge for edge in genotype.edges if edge.enabled]
        if not candidates:
            return
        selection = random.randint(0, len(candidates) - 1)
        edge = candidates[selection]
        edge.enabled = False

    def mutate_weight(self, genotype):
        selection = random.randint(0, len(genotype.edges) - 1)
        edge = genotype.edges[selection]
        roll = random.random()

        if roll < self.PETRUB_CHANCE:
            self.mutate_weight_shift(edge, self.SHIFT_STEP)
        else:
            self.mutate_weight_random(edge)

    @staticmethod
    def mutate_weight_shift(edge, step):
        scalar = random.random() * step - step * 0.5
        edge.weight += scalar

    @staticmethod
    def mutate_weight_random(edge):
        value = random.random() * 4.0 - 2.0
        edge.weight = value
