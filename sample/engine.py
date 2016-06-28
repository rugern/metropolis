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
				self.strategy.inPosition = self.broker.buy(ratio=size)
			else:
				self.strategy.inPosition = self.broker.sell(ratio=1)

	def plot(self):
		for indicator in self.indicators:
			pyplot.plot(indicator)
		pyplot.show()
