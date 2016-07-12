class Broker:

	def __init__(self, cash):
		self.cash = cash
		self.position_size = 0
		self.buy_history = []
		self.sell_history = []
		self.price_history = []
		self.profits = []
		self.ticks_in_market = 0
		self.loss = 0

	def buy(self, ratio, price):
		if(self.position_size != 0): raise ValueError('Should not buy if already in position!')
		self.position_size = ratio * self.cash // price
		self.cash -= self.position_size * price
		self.buy_history.append(price)

	def sell(self, ratio, price):
		if(self.position_size == 0): raise ValueError('Cannot sell if not in position!')

		if(price < self.buy_history[-1]):
			self.loss += self.position_size * (self.buy_history[-1] - price)
		else: self.loss = 0

		self.cash += self.position_size * price
		self.position_size = 0
		self.sell_history.append(price)
		self.profits.append(price - self.buy_history[-1])

	def getValue(self):
		unrealized = 0 if len(self.sell_history) == 0 else self.position_size * self.sell_history[-1]
		return self.cash + unrealized

	def addDataEntry(self, close):
		self.price_history.append(close)
		if(len(self.buy_history) > len(self.sell_history)): self.ticks_in_market += 1

	def getMarketTime(self):
		return self.ticks_in_market / len(self.price_history)
