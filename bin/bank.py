class Order(object):
    def __init__(self, size, entryIndex):
        self.size = size
        self.entryIndex = entryIndex

class Bank(object):
    def __init__(self, funds):
        self.funds = funds
        self.bound = 0
        self.buys = 0
        self.sells = 0

    def buy(self, price, size=1.0):
        self.buys += 1
        amount = self.funds * size
        self.funds -= amount
        self.bound += amount / price

    def sell(self, price, size=1.0):
        self.sells += 1
        amount = self.bound * size
        self.bound -= amount
        self.funds += amount * price

    def getResult(self, price):
        return self.funds + self.bound * price

    def openOrder(self, price, size, entryIndex):
        self.buy(price, size)
        return Order(size, entryIndex)

    def closeOrder(self, price, order):
        self.sell(price, order.size)
