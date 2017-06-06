class Order(object):
    def __init__(self, amount, entryPrice, entryIndex, leverage):
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

class OrderBook(object):
    def __init__(self):
        self.orders = {}

    def openOrder(self, currency, entryPrice, entryIndex, amount, leverage=1):
        if currency not in self.orders:
            self.orders[currency] = []
        order = Order(amount, entryPrice, entryIndex, leverage)
        self.orders[currency].append(order)
        return order

    def closeOrder(self, currency, order, exitPrice):
        amount = order.calculateReturn(exitPrice)
        self.orders[currency].remove(order)
        return amount

    def getOrders(self, currency):
        orders = []
        if currency in self.orders:
            orders = self.orders[currency]
        return orders
