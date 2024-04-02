from monopoly.player import Player


class NeuralPlayer(Player):
    def __init__(self):
        super().__init__()
        self.network = None
        self.adapter = None

    def decide_buy(self, index):
        y = self.network.propagate(self.adapter.pack)
        if y[0] > 0.5:
            return self.EBuyDecision.BUY
        return self.EBuyDecision.AUCTION

    def decide_jail(self):
        y = self.network.propagate(self.adapter.pack)
        if y[1] < 0.333:
            return self.EJailDecision.CARD
        elif y[1] < 0.666:
            return self.EJailDecision.ROLL
        return self.EJailDecision.PAY

    def decide_mortgage(self, index):
        y = self.network.propagate(self.adapter.pack)
        if y[2] > 0.5:
            return self.EDecision.YES
        return self.EDecision.NO

    def decide_advance(self, index):
        y = self.network.propagate(self.adapter.pack)
        if y[3] > 0.5:
            return self.EDecision.YES
        return self.EDecision.NO

    def decide_auction_bid(self, index):
        from analytics import Analytics
        y = self.network.propagate(self.adapter.pack)
        result = y[4]
        money = self.adapter.convert_money_value(result)

        Analytics.instance.make_bid(index, int(money))

        return int(money)

    def decide_build_house(self, set_):
        y = self.network.propagate(self.adapter.pack)
        result = y[5]
        money = self.adapter.convert_house_value(result)

        return int(money)

    def decide_sell_house(self, set_):
        y = self.network.propagate(self.adapter.pack)
        result = y[6]
        money = self.adapter.convert_house_value(result)

        return int(money)

    def decide_offer_trade(self):
        y = self.network.propagate(self.adapter.pack)
        if y[7] > 0.5:
            return self.EDecision.YES
        return self.EDecision.NO

    def decide_accept_trade(self):
        y = self.network.propagate(self.adapter.pack)
        if y[8] > 0.5:
            return self.EDecision.YES
        return self.EDecision.NO
