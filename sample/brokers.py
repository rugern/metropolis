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
		to_sell = round(self.position_size * ratio)
		self.cash += to_sell * price
		self.position_size -= to_sell
		self.sell_history.append(price)

	def getValue(self):
		return self.cash + self.position_size * self.sell_history[-1]
