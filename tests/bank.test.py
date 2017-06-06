import sys
import os
import unittest

sys.path.insert(1, os.path.join(sys.path[0], '../sample'))

from market.bank import Bank

class BankTest(unittest.TestCase):
    def setUp(self):
        self.funds = 1000

    def testWithdrawal(self):
        bank = Bank(self.funds)
        withdraw = 100
        amount = bank.withdraw(withdraw)
        self.assertEqual(withdraw, amount)
        self.assertEqual(bank.funds, self.funds - amount)

    def testMaxWithdrawal(self):
        bank = Bank(self.funds)
        amount = bank.withdraw(1100)
        self.assertEqual(self.funds, amount)
        
        amount = bank.withdraw(1000)
        self.assertEqual(amount, 0)

    def testDeposit(self):
        bank = Bank(self.funds)
        deposit = 100
        bank.deposit(deposit)
        self.assertEqual(self.funds + deposit, bank.funds)

if __name__ == '__main__':
    unittest.main()

