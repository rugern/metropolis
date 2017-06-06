class Bank(object):
    def __init__(self, funds):
        self.funds = funds
        self.withdrawals = 0
        self.deposits = 0

    def withdraw(self, requestedAmount):
        amount = 0
        if self.funds > 0:
            self.withdrawals += 1
            amount = min(self.funds, requestedAmount)
            self.funds -= amount
        return amount

    def deposit(self, amount):
        self.deposits += 1
        self.funds += amount
