class Broker:

	cash = 0
	position_size = 0
	buy_history = []
	sell_history = []

	def __init__(self, cash):
		self.cash = cash

	def buy(self, ratio, price):
		pass

	def sell(self, ratio, price):
		position_size = 0
