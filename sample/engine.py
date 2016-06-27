import matplotlib.pyplot as pyplot

class Engine:

	indicators = []
	strategy = None
	data = None
	broker = None
	sizer = None

	def addStrategy(self, strategy):
		self.strategy = strategy
		self.indicators.append(strategy)
		return strategy

	def addData(self, data):
		self.data = data

	def addBroker(self, broker):
		self.broker = broker

	def addSizer(self, sizer):
		self.sizer = sizer

	def run(self):
		for i in range(len(self.data)):
			entry = self.data['buy']['close'][i]
			self.strategy.pushData(entry)
			signal = self.strategy.next()
			if(signal == 'buy'):
				size = self.sizer.getSizing(self.data[:i])
				strategy.inPosition = self.broker.buy(size)
			else:
				strategy.inPosition = self.broker.sell()

	def plot(self):
		for indicator in indicators:
			pyplot.plot(indicator)
		pyplot.show()


class Broker:

	cash = 0

	def __init__(self, cash):
		self.cash = cash
