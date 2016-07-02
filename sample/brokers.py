class Broker:

	cash = 0
	position_size = 0
	buy_history = []
	sell_history = []

	def __init__(self, cash):
		self.cash = cash

	def buy(self, ratio, price):
		if(self.position_size != 0): raise ValueError('Should not buy if already in position!')
		self.position_size = ratio * self.cash // price
		self.cash -= self.position_size * price
		self.buy_history.append(price)

	def sell(self, ratio, price):
		if(self.position_size == 0): raise ValueError('Cannot sell if not in position!')
		self.cash += self.position_size * price
		self.position_size = 0
		self.sell_history.append(price)

	def getValue(self):
		unrealized = 0 if len(self.sell_history) == 0 else self.position_size * self.sell_history[-1]
		return self.cash + unrealized
