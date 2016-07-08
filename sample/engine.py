import matplotlib.pyplot as pyplot

from sample import utility

class Engine:

	def __init__(self):
		self.indicators = []
		self.strategy = None
		self.datetimes = None
		self.open = None
		self.high = None
		self.low = None
		self.close = None
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

	def addData(self, data, start=None, end=None):
		if(start and end): data = data.truncate(start, end)
		self.datetimes = data.index.values
		self.open = data['buy']['open'].values
		self.high = data['buy']['high'].values
		self.low = data['buy']['low'].values
		self.close = data['buy']['close'].values

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
		if(any(item is None for item in [self.strategy, self.broker, self.sizer, self.datetimes])): raise ValueError('Missing required data in Engine')
		for i in range(len(self.open)):
			self.current_data_entry = (self.open[i], self.high[i], self.low[i], self.close[i])
			self.strategy.addDataEntry(self.current_data_entry)
			self.strategy.next()
		self.strategy.stop()

	def plot(self):
		for indicator in self.indicators:
			pyplot.plot(indicator.getHistory())
		pyplot.plot(self.close)

		ticks = 10
		interval = len(self.datetimes) // ticks
		labels = [utility.datetimeToString(item) for index, item in enumerate(self.datetimes) if index % interval == 0]
		pyplot.xticks([i * interval for i in range(ticks)], labels, size='small', rotation=45)

		pyplot.show()
