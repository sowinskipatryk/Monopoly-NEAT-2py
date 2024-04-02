from neuro_evolution.genotype import Genotype, VertexInfo, EdgeInfo
from neuro_evolution.phenotype import Phenotype, Vertex
from neuro_evolution.mutation import Mutation


class NetworkFactory:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    @staticmethod
    def create_base_genotype(inputs, outputs):
        network = Genotype()

        for i in range(inputs):
            network.add_vertex(VertexInfo.EType.INPUT, i)

        for i in range(outputs):
            network.add_vertex(VertexInfo.EType.OUTPUT, i + inputs)

        network.add_edge(0, inputs, 0.0, True, 0)

        return network

    @staticmethod
    def register_base_markings(inputs, outputs):
        for i in range(inputs):
            for j in range(outputs):
                input_node = i
                output_node = j + inputs
                info = EdgeInfo(input_node, output_node, 0.0, True)
                Mutation().register_marking(info)

    @staticmethod
    def create_base_recurrent():
        network = Genotype()
        node_num = 0

        for i in range(1):
            network.add_vertex(VertexInfo.EType.INPUT, node_num)
            node_num += 1

        for i in range(1):
            network.add_vertex(VertexInfo.EType.OUTPUT, node_num)
            node_num += 1

        network.add_edge(0, 1, 0.0, True, 0)
        network.add_edge(1, 0, 0.0, True, 1)

        physicals = Phenotype()
        physicals.inscribe_genotype(network)
        physicals.process_graph()

        return network

    @staticmethod
    def create_buggy_network():
        network = Genotype()
        node_num = 0

        for i in range(2):
            network.add_vertex(VertexInfo.EType.INPUT, node_num)
            node_num += 1

        for i in range(1):
            network.add_vertex(VertexInfo.EType.OUTPUT, node_num)
            node_num += 1

        for i in range(2):
            network.add_vertex(VertexInfo.EType.HIDDEN, node_num)
            node_num += 1

        network.add_edge(0, 2, 0.0, True, 0)
        network.add_edge(1, 2, 0.0, True, 1)
        network.add_edge(1, 3, 0.0, True, 2)
        network.add_edge(3, 2, 0.0, True, 3)

        physicals = Phenotype()
        physicals.inscribe_genotype(network)
        physicals.process_graph()

        return network

    @staticmethod
    def create_base_phenotype(inputs, outputs):
        network = Phenotype()

        for i in range(inputs):
            network.add_vertex(Vertex.EType.INPUT, i)

        for i in range(outputs):
            network.add_vertex(Vertex.EType.OUTPUT, i + inputs)

        for i in range(inputs):
            for j in range(outputs):
                input_node = i
                output_node = j + inputs
                network.add_edge(input_node, output_node, 0.0, True)

        return network
