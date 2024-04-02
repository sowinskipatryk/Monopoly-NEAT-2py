from typing import List

from monopoly.neural_player import NeuralPlayer
from monopoly.player import Player
from rng import RNG


class Board:
    class EOutcome:
        ONGOING = 0
        DRAW = 1
        WIN1 = 2
        WIN2 = 3
        WIN3 = 4
        WIN4 = 5

    class EMode:
        ROLL = 0

    class ETile:
        NONE = 0
        PROPERTY = 1
        TRAIN = 2
        UTILITY = 3
        CHANCE = 4
        CHEST = 5
        TAX = 6
        JAIL = 7

    class ECard:
        ADVANCE = 0
        RAILROAD2 = 1
        UTILITY10 = 2
        REWARD = 3
        CARD = 4
        BACK3 = 5
        JAIL = 6
        REPAIRS = 7
        STREET = 8
        FINE = 9
        CHAIRMAN = 10
        BIRTHDAY = 11

    class CardEntry:
        def __init__(self, c, v):
            self.card = c
            self.val = v

    # constants
    PLAYER_COUNT = 4
    BANK_INDEX = -1
    BOARD_LENGTH = 40
    STALEMATE_TURN = 300
    GO_BONUS = 200
    GO_LANDING_BONUS = 200
    JAIL_INDEX = 10
    JAIL_PENALTY = 50
    MORTGAGE_INTEREST = 1.1

    # penalties for landing on a property (all circumstances)
    PROPERTY_PENALTIES = [
        [2, 10, 30, 90, 160, 250],
        [4, 20, 60, 180, 320, 450],
        [6, 30, 90, 270, 400, 550],
        [8, 40, 100, 300, 450, 600],
        [10, 50, 150, 450, 625, 750],
        [12, 60, 180, 500, 700, 900],
        [14, 70, 200, 550, 750, 950],
        [16, 80, 220, 600, 800, 1000],
        [18, 90, 250, 700, 875, 1050],
        [20, 100, 300, 750, 925, 1100],
        [22, 110, 330, 800, 975, 1150],
        [22, 120, 360, 850, 1025, 1200],
        [26, 130, 390, 900, 1100, 1275],
        [28, 150, 450, 1000, 1200, 1400],
        [35, 175, 500, 1100, 1300, 1500],
        [50, 200, 600, 1400, 1700, 2000]
    ]

    # penalities for landing on utilities (needs to be multiplied by roll)
    UTILITY_POSITIONS = [12, 28]
    UTILITY_PENALTIES = [4, 10]

    # penalties for landing on trains
    TRAIN_POSITIONS = [5, 15, 25, 35]
    TRAIN_PENALTIES = [25, 50, 100, 200]

    TYPES = [
        ETile.NONE, ETile.PROPERTY, ETile.CHEST, ETile.PROPERTY, ETile.TAX,
        ETile.TRAIN, ETile.PROPERTY, ETile.CHANCE,
        ETile.PROPERTY, ETile.PROPERTY, ETile.NONE, ETile.PROPERTY,
        ETile.UTILITY, ETile.PROPERTY, ETile.PROPERTY,
        ETile.TRAIN, ETile.PROPERTY, ETile.CHEST, ETile.PROPERTY,
        ETile.PROPERTY, ETile.NONE, ETile.PROPERTY,
        ETile.CHANCE, ETile.PROPERTY, ETile.PROPERTY, ETile.TRAIN,
        ETile.PROPERTY, ETile.PROPERTY, ETile.UTILITY,
        ETile.PROPERTY, ETile.JAIL, ETile.PROPERTY, ETile.PROPERTY, ETile.CHEST,
        ETile.PROPERTY, ETile.TRAIN,
        ETile.CHANCE, ETile.PROPERTY, ETile.TAX, ETile.PROPERTY
    ]

    COSTS = [
        0, 60, 0, 60, 200, 200, 100, 0, 100, 120, 0, 140, 150, 140, 160, 200,
        180, 0, 180, 200, 0, 220, 0, 220, 240,
        200, 260, 260, 150, 280, 0, 300, 300, 0, 320, 200, 0, 250, 100, 400
    ]

    BUILD = [50, 50, 50, 50, 100, 100, 100, 100, 150, 150, 150, 150, 200, 200,
             200, 200]

    SETS = [[1, 3, -1],
            [6, 8, 9],
            [11, 13, 14],
            [16, 18, 19],
            [21, 23, 24],
            [26, 27, 29],
            [31, 32, 34],
            [37, 39, -1]]

    mortgaged = [False] * 40
    owners = [-1] * 40
    property_ = [-1, 0, -1, 1, -1, -1, 2, -1, 2, 3, -1, 4, -1, 4, 5, -1, 6, -1, 6, 7,
                 -1, 8, -1, 8, 9, -1, 10, 10, -1, 11, -1, 12, 12, -1, 13, -1, -1, 14,
                 -1, 15]
    houses = [0] * 40
    original = [-1] * 40

    mode = EMode.ROLL
    players = []
    adapter = None
    random = None
    turn = 0
    count = 0
    remaining = 0
    last_roll = 0

    chance = []
    chest = []

    def __init__(self, _adapter):
        self.players = [NeuralPlayer() for _ in range(self.PLAYER_COUNT)]
        self.random = RNG()
        self.adapter = _adapter

        for i in range(self.PLAYER_COUNT):
            self.adapter.set_position(i, self.players[i].position)
            self.adapter.set_money(i, self.players[i].funds)

        self.remaining = self.PLAYER_COUNT

        chance = [self.CardEntry(self.ECard.ADVANCE, 39),
                  self.CardEntry(self.ECard.ADVANCE, 0),
                  self.CardEntry(self.ECard.ADVANCE, 24),
                  self.CardEntry(self.ECard.ADVANCE, 11),
                  self.CardEntry(self.ECard.RAILROAD2, 0),
                  self.CardEntry(self.ECard.RAILROAD2, 0),
                  self.CardEntry(self.ECard.UTILITY10, 0),
                  self.CardEntry(self.ECard.REWARD, 50),
                  self.CardEntry(self.ECard.CARD, 0),
                  self.CardEntry(self.ECard.BACK3, 0),
                  self.CardEntry(self.ECard.JAIL, 0),
                  self.CardEntry(self.ECard.REPAIRS, 0),
                  self.CardEntry(self.ECard.FINE, 15),
                  self.CardEntry(self.ECard.ADVANCE, 5),
                  self.CardEntry(self.ECard.CHAIRMAN, 0),
                  self.CardEntry(self.ECard.REWARD, 150)]
        self.chance = self.random.shuffle_card_entries(chance)

        chest = [self.CardEntry(self.ECard.ADVANCE, 0),
                 self.CardEntry(self.ECard.REWARD, 200),
                 self.CardEntry(self.ECard.FINE, 50),
                 self.CardEntry(self.ECard.REWARD, 50),
                 self.CardEntry(self.ECard.CARD, 0),
                 self.CardEntry(self.ECard.JAIL, 0),
                 self.CardEntry(self.ECard.REWARD, 100),
                 self.CardEntry(self.ECard.REWARD, 20),
                 self.CardEntry(self.ECard.BIRTHDAY, 0),
                 self.CardEntry(self.ECard.REWARD, 100),
                 self.CardEntry(self.ECard.FINE, 100),
                 self.CardEntry(self.ECard.FINE, 50),
                 self.CardEntry(self.ECard.FINE, 25),
                 self.CardEntry(self.ECard.STREET, 0),
                 self.CardEntry(self.ECard.REWARD, 10),
                 self.CardEntry(self.ECard.REWARD, 100)]
        self.chest = self.random.shuffle_card_entries(chest)

    def step(self):
        if self.mode == Board.EMode.ROLL:
            return self.roll()
        return Board.EOutcome.ONGOING

    def roll(self):
        self.before_turn()

        d1 = self.random.gen.randint(1, 6)
        d2 = self.random.gen.randint(1, 6)

        self.last_roll = d1 + d2

        is_double = d1 == d2
        double_in_jail = False

        if self.players[self.turn].state == Player.EState.JAIL:
            self.adapter.set_turn(self.turn)
            decision = self.players[self.turn].decide_jail()

            if decision == Player.EJailDecision.ROLL:
                if is_double:
                    self.players[self.turn].jail = 0
                    self.players[self.turn].state = Player.EState.NORMAL

                    self.adapter.set_jail(self.turn, 0)

                    double_in_jail = True
                else:
                    self.players[self.turn].jail += 1

                    if self.players[self.turn].jail >= 3:
                        self.payment(self.turn, self.JAIL_PENALTY)

                        self.players[self.turn].jail = 0
                        self.players[self.turn].state = Player.EState.NORMAL

                        self.adapter.set_jail(self.turn, 0)
            elif decision == Player.EJailDecision.PAY:
                self.payment(self.turn, self.JAIL_PENALTY)

                self.players[self.turn].jail = 0
                self.players[self.turn].state = Player.EState.NORMAL

                self.adapter.set_jail(self.turn, 0)
            elif decision == Player.EJailDecision.CARD:
                if self.players[self.turn].card > 0:
                    self.players[self.turn].card -= 1
                    self.players[self.turn].jail = 0
                    self.players[self.turn].state = Player.EState.NORMAL

                    self.adapter.set_jail(self.turn, 0)
                    self.adapter.set_card(self.turn, 1 if self.players[self.turn].card > 0 else 0)
                else:
                    if is_double:
                        self.players[self.turn].jail = 0
                        self.players[self.turn].state = Player.EState.NORMAL

                        self.adapter.set_jail(self.turn, 0)
                    else:
                        self.players[self.turn].jail += 1

                        if self.players[self.turn].jail >= 3:
                            self.payment(self.turn, self.JAIL_PENALTY)

                            self.players[self.turn].jail = 0
                            self.players[self.turn].state = Player.EState.NORMAL

                            self.adapter.set_jail(self.turn, 0)

        if self.players[self.turn].state == Player.EState.NORMAL:
            not_final_double = (not is_double) or (self.players[self.turn].doub <= 1)

            if not_final_double:
                self.movement(d1 + d2, is_double)

        # Start turn again (unless retired or the double was from jail)
        if self.players[self.turn].state != Player.EState.RETIRED and is_double and not double_in_jail:
            self.players[self.turn].doub += 1

            if self.players[self.turn].doub >= 3:
                self.players[self.turn].position = self.JAIL_INDEX
                self.players[self.turn].doub = 0
                self.players[self.turn].state = Player.EState.JAIL

                self.adapter.set_jail(self.turn, 1)

        outcome = self.end_turn(
            (not is_double) or self.players[self.turn].state == Player.EState.RETIRED or
            self.players[self.turn].state == Player.EState.JAIL)
        return outcome

    def end_turn(self, increment=True):
        if increment:
            self.increment_turn()

            self.count = 0

            while self.players[self.turn].state == Player.EState.RETIRED and self.count <= self.PLAYER_COUNT * 2:
                self.increment_turn()
                self.count += 1

            if self.remaining <= 1:
                return [Board.EOutcome.WIN1, Board.EOutcome.WIN2, Board.EOutcome.WIN3, Board.EOutcome.WIN4][self.turn]

        self.count += 1

        if self.count >= self.STALEMATE_TURN:
            return Board.EOutcome.DRAW

        return Board.EOutcome.ONGOING

    def increment_turn(self):
        self.turn += 1

        if self.turn >= self.PLAYER_COUNT:
            self.turn = 0

    def before_turn(self):
        if self.players[self.turn].state == Player.EState.RETIRED:
            return

        item_count = len(self.players[self.turn].items)

        for j in range(item_count):
            index = self.players[self.turn].items[j]

            if self.mortgaged[index]:
                advance_price = int(self.COSTS[index] * self.MORTGAGE_INTEREST)

                if advance_price > self.players[self.turn].funds:
                    continue

                self.adapter.set_turn(self.turn)

                self.adapter.set_selection_state(index, 1)

                decision = self.players[self.turn].decide_advance(index)

                self.adapter.set_selection_state(index, 0)

                if decision == Player.EDecision.YES:
                    self.advance(index)
            else:
                self.adapter.set_turn(self.turn)

                self.adapter.set_selection_state(index, 1)

                decision = self.players[self.turn].decide_mortgage(index)

                self.adapter.set_selection_state(index, 0)

                if decision == Player.EDecision.YES:
                    # Mortgage(index)
                    pass

        sets = self.find_sets(self.turn)
        set_count = len(sets)

        for j in range(set_count):
            house_total = self.houses[self.SETS[sets[j]][0]] + self.houses[self.SETS[sets[j]][1]]

            if sets[j] != 0 and sets[j] != 7:
                house_total += self.houses[self.SETS[sets[j]][2]]

            sell_max = house_total

            self.adapter.set_turn(self.turn)

            self.adapter.set_selection_state(self.SETS[sets[j]][0], 1)

            decision = self.players[self.turn].decide_sell_house(sets[j])

            self.adapter.set_selection_state(self.SETS[sets[j]][0], 0)

            decision = min(decision, sell_max)

            if decision > 0:
                self.sell_houses(sets[j], decision)
                self.players[self.turn].funds += int(
                    decision * self.BUILD[self.property_[self.SETS[sets[j]][0]]] * 0.5)

        sets = self.find_sets(self.turn)
        set_count = len(sets)

        for j in range(set_count):
            max_house = 10
            house_total = self.houses[self.SETS[sets[j]][0]] + self.houses[self.SETS[sets[j]][1]]

            if self.SETS[j] != 0 and self.SETS[j] != 7:
                max_house = 15
                house_total += self.houses[self.SETS[sets[j]][2]]

            build_max = max_house - house_total
            afford_max = int(self.players[self.turn].funds / self.BUILD[self.property_[self.SETS[sets[j]][0]]])

            if afford_max < 0:
                afford_max = 0

            build_max = min(build_max, afford_max)

            self.adapter.set_turn(self.turn)

            self.adapter.set_selection_state(self.SETS[sets[j]][0], 1)

            decision = self.players[self.turn].decide_build_house(sets[j])

            self.adapter.set_selection_state(self.SETS[sets[j]][0], 0)

            decision = min(decision, build_max)

            if decision > 0:
                self.build_houses(sets[j], decision)
                self.payment(self.turn, decision * self.BUILD[self.property_[self.SETS[sets[j]][0]]])

        self.trading()

    def trading(self):
        from analytics import Analytics
        candidates: List[Player] = []
        candidates_index: List[int] = []

        for i in range(self.PLAYER_COUNT):
            if i == self.turn:
                continue

            if self.players[i].state == Player.EState.RETIRED:
                continue

            candidates.append(self.players[i])
            candidates_index.append(i)

        if len(candidates) == 0:
            return

        trade_attempts = 4
        trade_item_max = 5
        trade_money_max = 500

        for t in range(trade_attempts):
            give = self.random.gen.randint(0, max(min(len(self.players[self.turn].items), trade_item_max), 1) - 1)

            selected_player = self.random.gen.randrange(0, len(candidates))

            other = candidates[selected_player]
            other_index = candidates_index[selected_player]

            receive = self.random.gen.randint(0, max(min(len(other.items), trade_item_max), 1) - 1)

            if self.players[self.turn].funds < 0 or other.funds < 0:
                continue

            money_give = self.random.gen.randint(0, max(min(self.players[self.turn].funds, trade_money_max), 1) - 1)
            money_receive = self.random.gen.randint(0, max(min(other.funds, trade_money_max), 1) - 1)
            money_balance = money_give - money_receive

            if give == 0 or receive == 0:
                continue

            gift = self.random.gen.sample(self.players[self.turn].items, give)  # !
            returning = self.random.gen.sample(other.items, receive)

            # set neurons for trade
            for item in gift:
                self.adapter.set_selection_state(item, 1)

            for item in returning:
                self.adapter.set_selection_state(item, 1)

            self.adapter.set_money_context(money_balance)

            decision = self.players[self.turn].decide_offer_trade()

            if decision == Player.EDecision.NO:
                self.adapter.clear_selection_state()
                continue

            decision2 = other.decide_accept_trade()

            if decision2 == Player.EDecision.NO:
                continue

            for item in gift:
                Analytics.instance.made_trade(item)

                self.players[self.turn].items.remove(item)
                other.items.append(item)

                self.owners[item] = other_index
                self.adapter.set_owner(item, other_index)

            for item in returning:
                Analytics.instance.made_trade(item)

                other.items.remove(item)
                self.players[self.turn].items.append(item)

                self.owners[item] = self.turn
                self.adapter.set_owner(item, self.turn)

            self.adapter.clear_selection_state()

            self.players[self.turn].funds -= money_balance
            other.funds += money_balance

    def auction(self, index):
        participation = [self.players[i].state != Player.EState.RETIRED for i in range(self.PLAYER_COUNT)]

        bids = [0] * self.PLAYER_COUNT

        for i in range(self.PLAYER_COUNT):
            self.adapter.set_turn(i)
            self.adapter.set_selection_state(index, 1)

            bids[i] = self.players[i].decide_auction_bid(index)

            self.adapter.set_selection_state(index, 0)

            if bids[i] > self.players[i].funds:
                participation[i] = False

        max_ = 0
        for i in range(self.PLAYER_COUNT):
            if participation[i] and bids[i] > max_:
                max_ = bids[i]

        candidates = []
        backup = []

        for i in range(self.PLAYER_COUNT):
            if participation[i] and bids[i] == max_:
                candidates.append(i)

            if self.players[i].state != Player.EState.RETIRED:
                backup.append(i)

        if candidates:
            winner = candidates[self.random.gen.randint(0, len(candidates) - 1)]
            self.payment(winner, max_)
        else:
            winner = backup[self.random.gen.randint(0, len(backup) - 1)]

        self.owners[index] = winner
        self.players[winner].items.append(index)

        if self.original[index] == -1:
            self.original[index] = winner

        self.adapter.set_owner(index, winner)

    def movement(self, roll, is_double):
        self.players[self.turn].position += roll

        # Wrap around
        if self.players[self.turn].position >= self.BOARD_LENGTH:
            self.players[self.turn].position -= self.BOARD_LENGTH
            self.players[self.turn].funds += self.GO_BONUS if self.players[self.turn].position == 0 else self.GO_LANDING_BONUS

        self.adapter.set_money(self.turn, self.players[self.turn].funds)
        self.adapter.set_position(self.turn, self.players[self.turn].position)

        self.activate_tile()

    def activate_tile(self):
        index = self.players[self.turn].position
        tile = self.TYPES[index]

        if tile == self.ETile.PROPERTY:
            owner = self.owner(index)

            if owner == self.BANK_INDEX:
                self.adapter.set_turn(self.turn)
                self.adapter.set_selection(index)
                decision = self.players[self.turn].decide_buy(index)

                if decision == Player.EBuyDecision.BUY:
                    if self.players[self.turn].funds < self.COSTS[index]:
                        self.auction(index)
                    else:
                        self.payment(self.turn, self.COSTS[index])
                        self.owners[index] = self.turn
                        if self.original[index] == -1:
                            self.original[index] = self.turn
                        self.players[self.turn].items.append(index)
                        self.adapter.set_owner(index, owner)
                elif decision == Player.EBuyDecision.AUCTION:
                    self.auction(index)
            elif owner == self.turn:
                pass
            elif not self.mortgaged[index]:
                self.payment_to_player(self.turn, owner, self.PROPERTY_PENALTIES[self.property_[index]][self.houses[index]])
        elif tile == self.ETile.TRAIN:
            owner = self.owner(index)

            if owner == self.BANK_INDEX:
                self.adapter.set_turn(self.turn)
                self.adapter.set_selection(index)
                decision = self.players[self.turn].decide_buy(index)

                if decision == Player.EBuyDecision.BUY:
                    if self.players[self.turn].funds < self.COSTS[index]:
                        self.auction(index)
                    else:
                        self.payment(self.turn, self.COSTS[index])
                        self.owners[index] = self.turn
                        if self.original[index] == -1:
                            self.original[index] = self.turn
                        self.players[self.turn].items.append(index)
                        self.adapter.set_owner(index, self.turn)
                elif owner == self.turn:
                    pass
                elif decision == Player.EBuyDecision.AUCTION:
                    self.auction(index)
            elif not self.mortgaged[index]:
                trains = self.count_trains(owner)
                if 1 <= trains <= 4:
                    fine = self.TRAIN_PENALTIES[trains - 1]
                    self.payment_to_player(self.turn, owner, fine)
        elif tile == self.ETile.UTILITY:
            owner = self.owner(index)

            if owner == self.BANK_INDEX:
                self.adapter.set_turn(self.turn)
                self.adapter.set_selection_state(index, 1)
                decision = self.players[self.turn].decide_buy(index)
                self.adapter.set_selection_state(index, 0)

                if decision == Player.EBuyDecision.BUY:
                    if self.players[self.turn].funds < self.COSTS[index]:
                        self.auction(index)
                    else:
                        self.payment(self.turn, self.COSTS[index])
                        self.owners[index] = self.turn
                        if self.original[index] == -1:
                            self.original[index] = self.turn
                        self.players[self.turn].items.append(index)
                        self.adapter.set_owner(index, self.turn)
                elif self.owner == self.turn:
                    pass
                elif decision == Player.EBuyDecision.AUCTION:
                    self.auction(index)
            elif owner != self.turn and not self.mortgaged[index]:
                utilities = self.count_utilities(owner)
                if 1 <= utilities <= 2:
                    fine = self.UTILITY_PENALTIES[utilities - 1] * self.last_roll
                    self.payment_to_player(self.turn, owner, fine)
        elif tile == self.ETile.TAX:
            self.payment(self.turn, self.COSTS[index])
        elif tile == self.ETile.CHANCE:
            self.draw_chance()
        elif tile == self.ETile.CHEST:
            self.draw_chest()
        elif tile == self.ETile.JAIL:
            self.players[self.turn].position = self.JAIL_INDEX
            self.players[self.turn].doub = 0
            self.players[self.turn].state = Player.EState.JAIL
            self.adapter.set_jail(self.turn, 1)

    def payment(self, owner, fine):
        self.players[owner].funds -= fine
        self.adapter.set_money(owner, self.players[owner].funds)
        original = self.players[owner].funds

        # Prompt for selling self.SETS
        if self.players[owner].funds < 0:
            sets = self.find_sets(self.turn)
            set_count = len(sets)

            for j in range(set_count):
                house_total = self.houses[self.SETS[sets[j]][0]] + self.houses[self.SETS[sets[j]][1]]

                if self.SETS[j] != 0 and self.SETS[j] != 7:
                    house_total += self.houses[self.SETS[sets[j]][2]]

                sell_max = house_total

                self.adapter.set_turn(self.turn)
                self.adapter.set_selection_state(self.SETS[sets[j]][0], 1)

                decision = self.players[self.turn].decide_sell_house(sets[j])

                self.adapter.set_selection_state(self.SETS[sets[j]][0], 0)
                decision = min(decision, sell_max)

                if decision > 0:
                    self.sell_houses(sets[j], decision)
                    self.players[owner].funds += int(
                        decision * self.BUILD[self.property_[self.SETS[sets[j]][0]]] * 0.5)
                    self.adapter.set_money(owner, self.players[owner].funds)

        # Prompt for mortgages once
        if self.players[owner].funds < 0:
            item_count = len(self.players[owner].items)

            for i in range(item_count):
                item = self.players[owner].items[i]
                self.adapter.set_turn(owner)
                self.adapter.set_selection_state(self.players[owner].items[i], 1)

                decision = self.players[owner].decide_mortgage(self.players[owner].items[i])

                self.adapter.set_selection_state(self.players[owner].items[i], 0)

                if decision == Player.EDecision.YES:
                    self.mortgage(item)

        # Bankrupt
        if self.players[owner].funds < 0:
            regained = self.players[owner].funds - original
            item_count = len(self.players[owner].items)
            house_money = 0

            for i in range(item_count):
                item = self.players[owner].items[i]
                self.owners[item] = self.BANK_INDEX
                self.adapter.set_owner(item, self.BANK_INDEX)

                if self.houses[item] > 0:
                    liquidated = self.houses[item]
                    sell = (liquidated * self.BUILD[self.property_[item]]) // 2
                    house_money += sell
                    self.houses[item] = 0

            self.players[owner].items.clear()
            self.players[owner].state = Player.EState.RETIRED
            self.remaining -= 1

    def payment_to_player(self, owner, recipient, fine):
        self.players[owner].funds -= fine
        self.adapter.set_money(owner, self.players[owner].funds)

        self.players[recipient].funds += fine
        self.adapter.set_money(recipient, self.players[recipient].funds)

        original = self.players[owner].funds

        # Prompt for selling sets
        if self.players[owner].funds < 0:
            sets = self.find_sets(self.turn)
            set_count = len(sets)

            for j in range(set_count):
                house_total = self.houses[self.SETS[sets[j]][0]] + self.houses[self.SETS[sets[j]][1]]

                if self.SETS[j] != 0 and self.SETS[j] != 7:
                    house_total += self.houses[self.SETS[sets[j]][2]]

                sell_max = house_total

                self.adapter.set_turn(self.turn)
                self.adapter.set_selection_state(self.SETS[sets[j]][0], 1)

                decision = self.players[self.turn].decide_sell_house(sets[j])

                self.adapter.set_selection_state(self.SETS[sets[j]][0], 0)
                decision = min(decision, sell_max)

                if decision > 0:
                    self.sell_houses(sets[j], decision)
                    self.players[owner].funds += int(
                        decision * self.BUILD[self.property_[self.SETS[sets[j]][0]]] * 0.5)
                    self.adapter.set_money(owner, self.players[owner].funds)

        # Prompt for mortgages once
        if self.players[owner].funds < 0:
            item_count = len(self.players[owner].items)

            for i in range(item_count):
                self.adapter.set_turn(owner)
                self.adapter.set_selection_state(self.players[owner].items[i], 0)

                decision = self.players[owner].decide_mortgage(self.players[owner].items[i])
                self.adapter.set_selection_state(self.players[owner].items[i], 1)

                if decision == Player.EDecision.YES:
                    self.mortgage(self.players[owner].items[i])

        # Bankrupt
        if self.players[owner].funds < 0:
            self.players[recipient].funds += self.players[owner].funds
            self.adapter.set_money(recipient, self.players[recipient].funds)
            item_count = len(self.players[owner].items)
            house_money = 0

            for i in range(item_count):
                self.players[recipient].items.append(self.players[owner].items[i])
                self.adapter.set_owner(self.players[owner].items[i], recipient)
                self.owners[self.players[owner].items[i]] = recipient

                if self.houses[self.players[owner].items[i]] > 0:
                    liquidated = self.houses[self.players[owner].items[i]]
                    sell = (liquidated * self.BUILD[self.property_[self.players[owner].items[i]]]) // 2
                    house_money += sell
                    self.houses[self.players[owner].items[i]] = 0

            self.players[recipient].funds += house_money
            self.adapter.set_money(recipient, self.players[recipient].funds)
            self.players[owner].items.clear()
            self.players[owner].state = Player.EState.RETIRED
            self.remaining -= 1

    def owner(self, index):
        return self.owners[index]

    def mortgage(self, index):
        self.mortgaged[index] = True
        self.adapter.set_mortgage(index, 1)
        self.players[self.owners[index]].funds += self.COSTS[index] // 2
        self.adapter.set_money(self.owners[index], self.players[self.owners[index]].funds)

    def advance(self, index):
        self.mortgaged[index] = False
        self.adapter.set_mortgage(index, 0)

        cost = int(self.COSTS[index] * self.MORTGAGE_INTEREST)
        self.payment(self.owners[index], cost)

    def count_trains(self, player):
        count = 0

        for item in self.players[player].items:
            if item in self.TRAIN_POSITIONS:
                count += 1

        return count

    def count_utilities(self, player):
        count = 0

        for item in self.players[player].items:
            if item in self.UTILITY_POSITIONS:
                count += 1

        return count

    def draw_chance(self):
        card = self.chance[0]
        self.chance.pop(0)
        self.chance.append(card)

        if card.card == self.ECard.ADVANCE:
            if self.players[self.turn].position > card.val:
                self.players[self.turn].funds += self.GO_BONUS
                self.adapter.set_money(self.turn, self.players[self.turn].funds)

            self.players[self.turn].position = card.val
            self.adapter.set_position(self.turn, self.players[self.turn].position)

            self.activate_tile()
        elif card.card == self.ECard.REWARD:
            self.players[self.turn].funds += card.val
            self.adapter.set_money(self.turn, self.players[self.turn].funds)
        elif card.card == self.ECard.FINE:
            self.payment(self.turn, card.val)
        elif card.card == self.ECard.BACK3:
            self.players[self.turn].position -= 3
            self.adapter.set_position(self.turn, self.players[self.turn].position)

            self.activate_tile()
        elif card.card == self.ECard.CARD:
            self.players[self.turn].card += 1
            self.adapter.set_card(self.turn, self.players[self.turn].card)
        elif card.card == self.ECard.JAIL:
            self.players[self.turn].position = self.JAIL_INDEX
            self.players[self.turn].doub = 0
            self.players[self.turn].state = Player.EState.JAIL

            self.adapter.set_position(self.turn, self.players[self.turn].position)
            self.adapter.set_jail(self.turn, 1)
        elif card.card == self.ECard.RAILROAD2:
            self.advance_to_train2()
        elif card.card == self.ECard.UTILITY10:
            self.advance_to_utility10()
        elif card.card == self.ECard.CHAIRMAN:
            for i in range(self.PLAYER_COUNT):
                if i == self.turn:
                    continue

                if self.players[i].state != Player.EState.RETIRED:
                    self.payment_to_player(self.turn, i, 50)
        elif card.card == self.ECard.REPAIRS:
            house_count = 0
            hotel_count = 0

            for item in self.players[self.turn].items:
                index = item

                if self.houses[index] <= 4:
                    house_count += self.houses[index]
                else:
                    hotel_count += 1

            self.payment(self.turn, house_count * 25 + hotel_count * 100)

    def draw_chest(self):
        card = self.chest[0]
        self.chest.pop(0)
        self.chest.append(card)

        if card.card == self.ECard.ADVANCE:
            if self.players[self.turn].position > card.val:
                self.players[self.turn].funds += self.GO_BONUS
                self.adapter.set_money(self.turn, self.players[self.turn].funds)

            self.players[self.turn].position = card.val
            self.adapter.set_position(self.turn, self.players[self.turn].position)

            self.activate_tile()
        elif card.card == self.ECard.REWARD:
            self.players[self.turn].funds += card.val
            self.adapter.set_money(self.turn, self.players[self.turn].funds)
        elif card.card == self.ECard.FINE:
            self.payment(self.turn, card.val)
        elif card.card == self.ECard.CARD:
            self.players[self.turn].card += 1
            self.adapter.set_card(self.turn, self.players[self.turn].card)
        elif card.card == self.ECard.JAIL:
            self.players[self.turn].position = self.JAIL_INDEX
            self.players[self.turn].doub = 0
            self.players[self.turn].state = Player.EState.JAIL

            self.adapter.set_position(self.turn, self.players[self.turn].position)
            self.adapter.set_jail(self.turn, 1)
        elif card.card == self.ECard.BIRTHDAY:
            for i in range(self.PLAYER_COUNT):
                if i == self.turn:
                    continue

                if self.players[i].state != Player.EState.RETIRED:
                    self.payment_to_player(i, self.turn, 10)
        elif card.card == self.ECard.STREET:
            house_count = 0
            hotel_count = 0

            for item in self.players[self.turn].items:
                index = item

                if self.houses[index] <= 4:
                    house_count += self.houses[index]
                else:
                    hotel_count += 1

            self.payment(self.turn, house_count * 40 + hotel_count * 115)

    def advance_to_train2(self):
        index = self.players[self.turn].position

        if index < self.TRAIN_POSITIONS[0]:
            self.players[self.turn].position = self.TRAIN_POSITIONS[0]
        elif index < self.TRAIN_POSITIONS[1]:
            self.players[self.turn].position = self.TRAIN_POSITIONS[1]
        elif index < self.TRAIN_POSITIONS[2]:
            self.players[self.turn].position = self.TRAIN_POSITIONS[2]
        elif index < self.TRAIN_POSITIONS[3]:
            self.players[self.turn].position = self.TRAIN_POSITIONS[3]
        else:
            self.players[self.turn].position = self.TRAIN_POSITIONS[0]
            self.players[self.turn].funds += self.GO_BONUS
            self.adapter.set_money(self.turn, self.players[self.turn].funds)

        self.adapter.set_position(self.turn, self.players[self.turn].position)

        index = self.players[self.turn].position
        owner = self.owner(index)

        if owner == self.BANK_INDEX:
            self.adapter.set_turn(self.turn)
            self.adapter.set_selection_state(index, 0)
            decision = self.players[self.turn].decide_buy(index)
            self.adapter.set_selection_state(index, 1)

            if decision == Player.EBuyDecision.BUY:
                if self.players[self.turn].funds < self.COSTS[index]:
                    self.auction(index)
                else:
                    self.payment(self.turn, self.COSTS[index])
                    self.owners[index] = self.turn

                    if self.original[index] == -1:
                        self.original[index] = self.turn

                    self.players[self.turn].items.append(index)
                    self.adapter.set_owner(index, self.turn)
            elif decision == Player.EBuyDecision.AUCTION:
                self.auction(index)
        elif owner == self.turn:
            pass
        elif not self.mortgaged[index]:
            trains = self.count_trains(owner)

            if 1 <= trains <= 4:
                fine = self.TRAIN_PENALTIES[trains - 1]
                self.payment_to_player(self.turn, owner, fine * 2)

    def advance_to_utility10(self):
        index = self.players[self.turn].position

        if index < self.UTILITY_POSITIONS[0]:
            self.players[self.turn].position = self.UTILITY_POSITIONS[0]
        elif index < self.UTILITY_POSITIONS[1]:
            self.players[self.turn].position = self.UTILITY_POSITIONS[1]
        else:
            self.players[self.turn].position = self.UTILITY_POSITIONS[0]
            self.players[self.turn].funds += self.GO_BONUS
            self.adapter.set_money(self.turn, self.players[self.turn].funds)

        self.adapter.set_position(self.turn, self.players[self.turn].position)

        index = self.players[self.turn].position
        owner = self.owner(index)

        if owner == self.BANK_INDEX:
            self.adapter.set_turn(self.turn)
            decision = self.players[self.turn].decide_buy(index)

            if decision == Player.EBuyDecision.BUY:
                if self.players[self.turn].funds < self.COSTS[index]:
                    self.auction(index)
                else:
                    self.payment(self.turn, self.COSTS[index])
                    self.owners[index] = self.turn

                    if self.original[index] == -1:
                        self.original[index] = self.turn

                    self.players[self.turn].items.append(index)
                    self.adapter.set_owner(index, self.turn)
            if decision == Player.EBuyDecision.AUCTION:
                self.auction(index)
        elif owner == self.turn:
            pass
        elif not self.mortgaged[index]:
            fine = 10 * self.last_roll
            self.payment_to_player(self.turn, owner, fine)

    def find_sets(self, owner):
        sets = []

        for i in range(8):
            if i == 0 or i == 7:
                if self.SETS[i][0] in self.players[owner].items and self.SETS[i][1] in self.players[owner].items:
                    sets.append(i)
                continue

            if self.SETS[i][0] in self.players[owner].items and self.SETS[i][1] in self.players[owner].items and self.SETS[i][2] in self.players[owner].items:
                sets.append(i)

        return sets

    def build_houses(self, set_, amount):
        last = 2 if set_ != 0 and set_ != 7 else 1

        for _ in range(amount):
            bj = last

            for j in range(last - 1, -1, -1):
                if self.houses[self.SETS[set_][bj]] > self.houses[self.SETS[set_][j]]:
                    bj = j

            self.houses[self.SETS[set_][bj]] += 1
            self.adapter.set_house(self.SETS[set_][bj], self.houses[self.SETS[set_][bj]])

    def sell_houses(self, set_, amount):
        last = 2 if set_ != 0 and set_ != 7 else 1

        for _ in range(amount):
            bj = 0

            for j in range(last + 1):
                if self.houses[self.SETS[set_][bj]] < self.houses[self.SETS[set_][j]]:
                    bj = j

            self.houses[self.SETS[set_][bj]] -= 1
            self.adapter.set_house(self.SETS[set_][bj], self.houses[self.SETS[set_][bj]])
