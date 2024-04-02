import threading
from typing import Optional, List

from analytics import Analytics
from monopoly.board import Board
from network_adapter import NetworkAdapter
from neuro_evolution.population import Population
from rng import RNG
from neuro_evolution.genotype import Genotype
from neuro_evolution.phenotype import Phenotype


class Tournament:
    TOURNAMENT_SIZE: int = 256
    ROUND_SIZE: int = 2000  # 2000
    WORKERS: int = 20  # 20
    BATCH_SIZE: int = 20  # 20
    INPUTS: int = 126
    OUTPUTS: int = 9

    def __init__(self):
        self.champion: Optional[Genotype] = None
        self.champion_score = 0.0
        self.contestants: List[Phenotype] = []
        self.contestants_g: List[Genotype] = []
        self.lock = threading.Lock()

    def initialise(self):
        Population.instance.generate_base_population(self.TOURNAMENT_SIZE, self.INPUTS, self.OUTPUTS)

    def execute_tournament(self):
        print("TOURNAMENT #" + str(Population.instance.GENERATION))
        self.contestants.clear()
        self.contestants_g.clear()

        for i in range(self.TOURNAMENT_SIZE):
            Population.instance.genetics[i].bracket = 0
            Population.instance.population[i].score = 0.0
            self.contestants.append(Population.instance.population[i])
            self.contestants_g.append(Population.instance.genetics[i])

        while len(self.contestants) > 1:
            self.execute_tournament_round()

        for i in range(self.TOURNAMENT_SIZE):
            top = 0.0 if self.champion is None else self.champion.bracket
            diff = self.contestants_g[i].bracket - top
            self.contestants_g[i].fitness = self.champion_score + diff * 5

        self.champion = self.contestants_g[0]
        self.champion_score = self.contestants_g[0].fitness

    def execute_tournament_round(self):
        print("ROUND SIZE " + str(len(self.contestants)))
        cs: List[Phenotype] = []
        cs_g: List[Genotype] = []
        RNG.instance.double_shuffle(self.contestants, self.contestants_g, cs, cs_g)
        for i in range(self.TOURNAMENT_SIZE):
            Population.instance.population[i].score = 0.0
        self.contestants = cs
        self.contestants_g = cs_g

        for i in range(0, len(self.contestants), 4):
            played = 0
            print("BRACKET (" + str(i // 4) + ")")
            while played < self.ROUND_SIZE:
                print("Initialised Workers")
                workers = []
                for _ in range(self.WORKERS):
                    worker = threading.Thread(target=self.play_game_thread, args=(i,))
                    worker.start()
                    workers.append(worker)
                for worker in workers:
                    worker.join()
                played += self.WORKERS * self.BATCH_SIZE
                for c in range(40):
                    print("index:", c, ", {:.3f}".format(Analytics.instance.ratio[c]))
            mi: int = 0
            ms: float = self.contestants[i].score
            for j in range(1, 4):
                if ms < self.contestants[i + j].score:
                    mi = j
                    ms = self.contestants[i + j].score
            for j in range(4):
                if j == mi:
                    self.contestants_g[i + j].bracket += 1
                    continue
                self.contestants[i + j] = None
        self.contestants = [contestant for contestant in self.contestants if contestant is not None]
        self.contestants_g = [contestant_g for contestant_g in self.contestants_g if contestant_g is not None]

    def play_game_thread(self, i):
        for _ in range(self.BATCH_SIZE):
            adapter = NetworkAdapter()
            board = Board(adapter)
            for j in range(4):
                board.players[j].network = self.contestants[i + j]
                board.players[j].adapter = adapter
            board.players = RNG.instance.shuffle_neural_players(board.players)
            outcome = Board.EOutcome.ONGOING
            while outcome == Board.EOutcome.ONGOING:
                outcome = board.step()
            if outcome == Board.EOutcome.WIN1:
                with self.lock:
                    board.players[0].network.score += 1.0
                for b in board.players[0].items:
                    with self.lock:
                        Analytics.instance.mark_win(b)
            elif outcome == Board.EOutcome.WIN2:
                with self.lock:
                    board.players[1].network.score += 1.0
                for b in board.players[1].items:
                    with self.lock:
                        Analytics.instance.mark_win(b)
            elif outcome == Board.EOutcome.WIN3:
                with self.lock:
                    board.players[2].network.score += 1.0
                for b in board.players[2].items:
                    with self.lock:
                        Analytics.instance.mark_win(b)
            elif outcome == Board.EOutcome.WIN4:
                with self.lock:
                    board.players[3].network.score += 1.0
                for b in board.players[3].items:
                    with self.lock:
                        Analytics.instance.mark_win(b)
            elif outcome == Board.EOutcome.DRAW:
                for player in board.players:
                    with self.lock:
                        player.network.score += 0.25
