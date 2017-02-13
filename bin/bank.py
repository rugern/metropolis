import actions

class Bank(object):
    def __init__(self, funds):
        self.funds = funds
        self.bound = 0

    def performAction(self, price, nextPrice, action, quota=0.3):
        if action == actions.BUY:
            return self.buy(price, nextPrice, quota)
        elif action == actions.SELL:
            return self.sell(price, nextPrice, quota)
        else: # actions.HOLD
            return 0.0

    def buy(self, price, nextPrice, quota):
        amount = self.funds * quota
        self.funds -= amount
        self.bound += amount / price
        currentValue = self.bound * price
        nextValue = self.bound * nextPrice
        return nextValue - currentValue

    def sell(self, price, nextPrice, quota):
        amount = self.bound * quota
        self.bound -= amount
        self.funds += amount * price
        currentValue = self.bound * price
        nextValue = self.bound * nextPrice
        return nextValue - currentValue

    def calculateValue(self, price):
        return self.funds + self.bound * price
