class Order(object):
    def __init__(self, amount, entryPrice, entryIndex, leverage=1, **kwargs):
        self.amount = amount
        self.entryPrice = entryPrice
        self.leverage = leverage
        self.entryIndex = entryIndex

    def calculateReturn(self, price):
        leveragedAmount = self.amount * self.leverage
        bought = leveragedAmount * self.entryPrice
        sold = bought / price
        profit = sold - leveragedAmount
        return self.amount + profit

class Bank(object):
    def __init__(self, funds):
        self.funds = funds
        self.buys = 0
        self.sells = 0

    def withdraw(self, amount):
        self.buys += 1
        self.funds -= amount

    def deposit(self, amount):
        self.sells += 1
        self.funds += amount

    def getResult(self, price, openOrders):
        bound = 0
        for order in openOrders:
            bound += order.calculateReturn(price)
        return self.funds + bound

    def openOrder(self, price, entryIndex, amount, **kwargs):
        if self.funds == 0:
            return None
        if self.funds < amount:
            amount = self.funds
        self.withdraw(amount)
        return Order(amount, price, entryIndex, **kwargs)

    def closeOrder(self, price, order):
        self.deposit(order.calculateReturn(price))
