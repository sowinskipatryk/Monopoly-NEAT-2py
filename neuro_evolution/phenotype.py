import math


class Vertex:
    class EType:
        INPUT = 0
        HIDDEN = 1
        OUTPUT = 2

    def __init__(self, t, i):
        self.type = t
        self.index = i
        self.incoming = []
        self.value = 0.0


class Edge:
    class EType:
        FORWARD = 0
        RECURRENT = 1

    def __init__(self, s, d, w, e):
        self.type = self.EType.FORWARD
        self.source = s
        self.destination = d
        self.weight = w
        self.enabled = e
        self.signal = 0.0


class Phenotype:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.vertices_inputs = []
        self.vertices_outputs = []
        self.score = 0

    def inscribe_genotype(self, code):
        self.vertices.clear()
        self.edges.clear()

        for v in code.vertices:
            self.add_vertex(v.type, v.index)

        for e in code.edges:
            self.add_edge(e.source, e.destination, e.weight, e.enabled)

    def add_vertex(self, type_, index):
        v = Vertex(type_, index)
        self.vertices.append(v)

    def add_edge(self, source, destination, weight, enabled):
        e = Edge(source, destination, weight, enabled)
        self.edges.append(e)
        self.vertices[e.destination].incoming.append(e)

    def process_graph(self):
        for vertex in self.vertices:
            if vertex.type == Vertex.EType.INPUT:
                self.vertices_inputs.append(vertex)
            elif vertex.type == Vertex.EType.OUTPUT:
                self.vertices_outputs.append(vertex)

    def reset_graph(self):
        for vertex in self.vertices:
            vertex.value = 0.0

    def propagate(self, X):
        repeats = 10

        for _ in range(repeats):
            for i, vertex in enumerate(self.vertices_inputs):
                vertex.value = X[i]

            for vertex in self.vertices:
                if vertex.type == Vertex.EType.OUTPUT:
                    continue

                for edge in vertex.incoming:
                    vertex.value += self.vertices[edge.source].value * edge.weight * (1.0 if edge.enabled else 0.0)

                if vertex.incoming:
                    vertex.value = self.sigmoid(vertex.value)

            Y = [0.0] * len(self.vertices_outputs)
            for vertex in self.vertices_outputs:
                for edge in vertex.incoming:
                    vertex.value += self.vertices[edge.source].value * edge.weight * (1.0 if edge.enabled else 0.0)

                if vertex.incoming:
                    vertex.value = self.sigmoid(vertex.value)
                    Y.append(vertex.value)

            if _ == repeats - 1:
                return Y

        return []

    @staticmethod
    def sigmoid(x):
        return 1.0 / (1.0 + math.exp(-1.0 * x))
