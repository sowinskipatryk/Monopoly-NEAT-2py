import random

from typing import List

from neuro_evolution.phenotype import Phenotype
from neuro_evolution.genotype import Genotype
from monopoly.neural_player import NeuralPlayer


class RNG:
    instance = None

    def __init__(self):
        self.gen = random.Random()

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def shuffle_card_entries(self, cards):
        shuffle = []
        while cards:
            r = self.gen.randint(0, len(cards) - 1)
            shuffle.append(cards.pop(r))
        return shuffle

    def shuffle_neural_players(self, players: List[NeuralPlayer]) -> List[NeuralPlayer]:
        container: List[NeuralPlayer] = list(players)
        shuffle: List[NeuralPlayer] = []
        while container:
            r = self.gen.randint(0, len(container) - 1)
            shuffle.append(container.pop(r))
        return shuffle

    def shuffle_phenotypes(self, phenotypes: List[Phenotype]) -> List[Phenotype]:
        shuffle: List[Phenotype] = []
        while phenotypes:
            r: int = self.gen.randint(0, len(phenotypes) - 1)
            shuffle.append(phenotypes.pop(r))
        return shuffle

    def double_shuffle(self, phen: List[Phenotype], gene: List[Genotype], op: List[Phenotype], og: List[Genotype]) -> None:
        for i in range(len(phen)):
            r: int = self.gen.randint(0, len(phen) - 1)
            op.append(phen.pop(r))
            og.append(gene.pop(r))
