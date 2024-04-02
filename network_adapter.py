class NetworkAdapter:
    def __init__(self):
        self.pack = [0.0] * 127

        self.turn = 0
        self.pos = 4
        self.mon = 8
        self.card = 12
        self.jail = 16
        self.own = 20
        self.mort = 48
        self.house = 76
        self.select = 98
        self.select_money = 126

        self.PROPS = [-1, 0, -1, 1, -1, 2, 3, -1, 4, 5, -1, 6, 7, 8, 9, 10, 11,
                      -1, 12, 13, -1, 14, -1, 15, 16, 17, 18, 19, 20, 21, -1,
                      22, 23, -1, 24, 25, -1, 26, -1, 27]
        self.HOUSES = [-1, 0, -1, 1, -1, -1, 2, -1, 3, 4, -1, 5, -1, 6, 7, -1,
                       8, -1, 9, 10, -1, 11, -1, 12, 13, -1, 14, 15, -1, 16,
                       -1, 17, 18, -1, 19, -1, -1, 20, -1, 21]

    def reset(self):
        self.pack = [0.0] * 127

    @staticmethod
    def convert_money(money):
        norm = money / 4000.0
        clamp = max(0.0, min(norm, 1.0))
        return clamp

    @staticmethod
    def convert_money_value(value):
        return value * 4000.0

    @staticmethod
    def convert_house_value(value):
        if value <= 0.5:
            value = 0.0
        return value * 15.0

    @staticmethod
    def convert_position(position):
        norm = position / 39.0
        clamp = max(0.0, min(norm, 1.0))
        return clamp

    def convert_card(self, cards):
        clamp = max(0.0, min(float(self.card), 1.0))
        return clamp

    @staticmethod
    def convert_house(houses):
        norm = houses / 5.0
        clamp = max(0.0, min(norm, 1.0))
        return clamp

    def set_turn(self, index):
        for i in range(4):
            self.pack[i] = 0.0
        self.pack[index] = 1.0

    def set_selection(self, index):
        for i in range(self.select, self.select + 29):
            self.pack[i] = 0.0
        self.pack[self.select + self.PROPS[index]] = 1.0

    def set_selection_state(self, index, state):
        self.pack[self.select + self.PROPS[index]] = state

    def set_money_context(self, state):
        self.pack[self.select_money] = state

    def clear_selection_state(self):
        for i in range(self.select, self.select + 29):
            self.pack[i] = 0.0

    def set_position(self, index, position):
        self.pack[self.pos + index] = self.convert_position(position)

    def set_money(self, index, money):
        self.pack[self.mon + index] = self.convert_money(money)

    def set_card(self, index, cards):
        self.pack[self.card + index] = self.convert_card(cards)

    def set_jail(self, index, state):
        self.pack[self.jail + index] = state

    def set_owner(self, property_, state):
        convert = (state + 1) / 4.0
        self.pack[self.own + self.PROPS[property_]] = convert

    def set_mortgage(self, property_, state):
        self.pack[self.mort + self.PROPS[property_]] = state

    def set_house(self, property_, houses):
        self.pack[self.house + self.HOUSES[property_]] = self.convert_house(houses)
