import actions

class Bank(object):
    def __init__(self, funds):
        self.funds = funds
        self.bound = 0
        self.buys = 0
        self.sells = 0

    def performAction(self, price, nextPrice, action, quota=0.3):
        if action == actions.BUY:
            return self.buy(price, nextPrice, quota)
        elif action == actions.SELL:
            return self.sell(price, nextPrice, quota)
        else: # actions.HOLD
            return 0.0

    # def buy(self, price, nextPrice, quota):
        # amount = self.funds * quota
        # self.funds -= amount
        # self.bound += amount / price
        # currentValue = self.bound * price
        # nextValue = self.bound * nextPrice
        # return nextValue - currentValue

    # def sell(self, price, nextPrice, quota):
        # amount = self.bound * quota
        # self.bound -= amount
        # self.funds += amount * price
        # currentValue = self.bound * price
        # nextValue = self.bound * nextPrice
        # return nextValue - currentValue

    def buy(self, price, quota=1.0):
        self.buys += 1
        amount = self.funds * quota
        self.funds -= amount
        self.bound += amount / price

    def sell(self, price, quota=1.0):
        self.sells += 1
        amount = self.bound * quota
        self.bound -= amount
        self.funds += amount * price

    def getResult(self, price):
        return self.funds + self.bound * price

    def getBuys(self):
        return self.buys

    def getSells(self):
        return self.sells
