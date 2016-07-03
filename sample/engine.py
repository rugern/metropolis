import matplotlib.pyplot as pyplot

class Engine:

	def __init__(self):
		self.indicators = []
		self.strategy = None
		self.data = None
		self.current_data_entry = None
		self.broker = None
		self.sizer = None

	def addStrategy(self, strategy):
		self.strategy = strategy
		self.strategy.buy = self.buy
		self.strategy.sell = self.sell
		self.indicators = self.strategy.indicators
		if(self.broker is not None): self.strategy.broker = self.broker
		return strategy

	def addData(self, data):
		self.data = data['buy']['close'].values

	def addBroker(self, broker):
		self.broker = broker
		if(self.strategy is not None): self.strategy.broker = self.broker

	def addSizer(self, sizer):
		self.sizer = sizer

	def buy(self):
		ratio = self.sizer(self.broker.buy_history, self.broker.sell_history)
		self.broker.buy(ratio, self.current_data_entry)
		self.strategy.in_position = True

	def sell(self):
		ratio = 1
		self.broker.sell(ratio, self.current_data_entry)
		self.strategy.in_position = False

	def run(self):
		if(any(item is None for item in [self.strategy, self.broker, self.sizer, self.data])): raise ValueError('Missing required data in Engine')
		for i in range(len(self.data)):
			self.current_data_entry = self.data[i]
			self.strategy.addDataEntry(self.current_data_entry)
			for indicator in self.indicators:
				indicator.addData(self.current_data_entry)
			self.strategy.next()
		self.strategy.stop()

	def plot(self):
		for indicator in self.indicators:
			pyplot.plot(indicator.getResult())
		pyplot.plot(self.data)
		pyplot.show()
