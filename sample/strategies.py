from sklearn.linear_model import LogisticRegression

from sample import analytics

# Too many ancestors
#pylint: disable=R0901
# Init not called
#pylint: disable=W0231
# Too many positional arguments
#pylint: disable=E1121
# Unexpected keyword arguments
#pylint: disable=E1123
# Has no member error
#pylint: disable=E1101
# Not callable
#pylint: disable=E1102
# Space after comma
#pylint: disable=C0326
# Wrong hanging indentation
#pylint: disable=C0330

class Strategy:

	def __init__(self, config):
		self.config = config
		self.in_position = False
		self.data = []
		self.buy = None
		self.sell = None
		self.broker = None
		self.indicators = []

	def stop(self):
		print('(Long: {0}) (Short: {1}) (Stop: {2}) Ending value: {3:.2f}'.format(self.config['sma_long_interval'], self.config['sma_short_interval'], self.config['stop_loss'], self.broker.getValue()))

	def addDataEntry(self, entry):
		self.data.append(entry)


class DoubleMovingAverages(Strategy):

	def __init__(self, config):
		super().__init__(config)

		self.long_sma = analytics.SimpleMovingAverage(self.config['sma_long_interval'])
		self.short_sma = analytics.SimpleMovingAverage(self.config['sma_short_interval'])
		self.indicators.extend([self.long_sma, self.short_sma])

	def next(self):
		if not self.in_position:
			if(self.long_sma[-1] < self.short_sma[-1]):
				self.buy()
		else:
			# print('Loss: {}, cash: {}, stop_loss: {}'.format(self.broker.loss, self.broker.cash, self.config['stop_loss']))
			if(self.broker.loss >= self.broker.cash * self.config['stop_loss']):
				self.sell()
			elif(self.long_sma[-1] > self.short_sma[-1]):
				self.sell()

class LRStrategy(Strategy):
	def __init__(self, config):
		super().__init__(config)

		self.strategy = LogisticRegression()
		self.indicators.append(self.strategy)
		self.training_data = config['data'].truncate(config['startTrain'], config['endTrain'])['buy']['close'].values
		self.targets = self.getTargets(self.training_data)

	def getTargets(self, data):
		targets = [data[index] <= data[index + 1] for index in range(len(data) - 1)]
		return targets

	def next(self):
		pass
