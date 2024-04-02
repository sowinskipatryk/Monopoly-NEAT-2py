from typing import List

from monopoly.board import Board


class Analytics:
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.bids: List[int] = [0] * 40
        self.money: List[int] = [0] * 40
        self.average: List[float] = [0.0] * 40
        self.price: List[float] = [0.0] * 40

        self.trades: List[int] = [0] * 40
        self.exchanges: List[int] = [0] * 40

        self.wins: List[int] = [0] * 40
        self.max: int = 0
        self.min: int = 0
        self.ratio: List[float] = [0.0] * 40

    def make_bid(self, index, bid):
        self.bids[index] += 1
        self.money[index] += bid
        self.average[index] = self.money[index] / self.bids[index]
        self.price[index] = self.average[index] / Board.COSTS[index]

    def made_trade(self, index):
        self.trades[index] += 1

    def mark_win(self, index):
        self.wins[index] += 1

        if self.max < self.wins[index]:
            self.max = self.wins[index]

        temp_min = float('inf')

        for i in range(40):
            if self.wins[i] != 0 and self.wins[i] < temp_min:
                temp_min = self.wins[i]
        self.ratio[index] = (self.wins[index] - temp_min) / (self.max - temp_min)
