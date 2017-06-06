import sys
import os
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '../sample'))

from market.orderbook import OrderBook

class OrderBookTest(unittest.TestCase):
    def setUp(self):
        self.currency = 'EURUSD'
        self.entryPrice = 1.0
        self.exitPrice = 0.5
        self.entryIndex = 0
        self.amount = 100

    def testOpenOrder(self):
        orderBook = OrderBook()
        order = orderBook.openOrder(self.currency, self.entryPrice, self.entryIndex, self.amount)
        self.assertEqual(len(orderBook.getOrders(self.currency)), 1)
        self.assertEqual(order.amount, self.amount)
        self.assertEqual(order.entryPrice, self.entryPrice)
        self.assertEqual(order.leverage, 1)
        self.assertEqual(order.entryIndex, self.entryIndex)

    def testCloseOrder(self):
        orderBook = OrderBook()
        order = orderBook.openOrder(self.currency, self.entryPrice, self.entryIndex, self.amount)
        amount = orderBook.closeOrder(self.currency, order, self.exitPrice)
        self.assertEqual(len(orderBook.getOrders(self.currency)), 0)
        self.assertEqual(amount, 200)

        orderBook = OrderBook()
        order = orderBook.openOrder(self.currency, self.entryPrice, self.entryIndex, self.amount, leverage=2)
        amount = orderBook.closeOrder(self.currency, order, self.exitPrice)
        self.assertEqual(amount, 300)

    def testGetOrders(self):
        orderBook = OrderBook()
        order = orderBook.openOrder(self.currency, self.entryPrice, self.entryIndex, self.amount)
        order2 = orderBook.openOrder(self.currency, self.entryPrice, self.entryIndex, self.amount)
        self.assertEqual(
            len(orderBook.orders[self.currency]),
            len(orderBook.getOrders(self.currency))
        )
        self.assertEqual(len(orderBook.getOrders(self.currency)), 2)
        self.assertEqual(orderBook.getOrders(self.currency)[0], order)
        self.assertEqual(orderBook.getOrders(self.currency)[1], order2)
    
if __name__ == '__main__':
    unittest.main()

