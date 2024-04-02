from enum import Enum
from typing import List


class Player:
    class EState(Enum):
        NORMAL = 1
        JAIL = 2
        RETIRED = 3

    class EBuyDecision(Enum):
        BUY = 1
        AUCTION = 2

    class EJailDecision(Enum):
        ROLL = 1
        PAY = 2
        CARD = 3

    class EDecision(Enum):
        YES = 1
        NO = 2

    def __init__(self):
        self.state = Player.EState.NORMAL
        self.position = 0
        self.funds = 1500
        self.jail = 0
        self.doub = 0
        self.card = 0
        self.items: List[int] = []

    def decide_buy(self, index):
        return Player.EBuyDecision.BUY

    def decide_jail(self):
        return Player.EJailDecision.ROLL

    def decide_mortgage(self, index):
        if self.funds < 0:
            return Player.EDecision.YES
        return Player.EDecision.NO

    def decide_advance(self, index):
        return Player.EDecision.YES

    def decide_auction_bid(self, index):
        from monopoly.board import Board
        return Board.COSTS[index]

    def decide_build_house(self, set_):
        return 15

    def decide_sell_house(self, set_):
        if self.funds < 0:
            return 15
        return 0

    def decide_offer_trade(self):
        return Player.EDecision.NO

    def decide_accept_trade(self):
        return Player.EDecision.NO
