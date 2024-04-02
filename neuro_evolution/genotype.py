class VertexInfo:
    class EType:
        INPUT = 0
        HIDDEN = 1
        OUTPUT = 2

    def __init__(self, t, i):
        self.type = t
        self.index = i


class EdgeInfo:
    def __init__(self, s, d, w, e):
        self.source = s
        self.destination = d
        self.weight = w
        self.enabled = e
        self.innovation = 0


class Genotype:
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.inputs = 0
        self.externals = 0
        self.bracket = 0
        self.fitness = 0.0
        self.adjustedFitness = 0.0

    def add_vertex(self, type, index):
        v = VertexInfo(type, index)
        self.vertices.append(v)

        if v.type != VertexInfo.EType.HIDDEN:
            self.externals += 1

        if v.type == VertexInfo.EType.INPUT:
            self.inputs += 1

    def add_edge(self, source, destination, weight, enabled, innovation=None):
        e = EdgeInfo(source, destination, weight, enabled)
        if innovation is not None:
            e.innovation = innovation
        self.edges.append(e)

    def clone(self):
        copy = Genotype()

        for v in self.vertices:
            copy.add_vertex(v.type, v.index)

        for e in self.edges:
            copy.add_edge(e.source, e.destination, e.weight, e.enabled, e.innovation)

        return copy

    def sort_topology(self):
        self.sort_vertices()
        self.sort_edges()

    def sort_vertices(self):
        self.vertices.sort(key=lambda v: v.index)

    def sort_edges(self):
        self.edges.sort(key=lambda e: e.innovation)
