import math

from sklearn import linear_model

from sample import indicators

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
		self.open = []
		self.high = []
		self.low = []
		self.close = []
		self.predictions = []
		self.buy = None
		self.sell = None
		self.broker = None
		self.indicators = []

	def stop(self):
		print('(Long: {0}) (Short: {1}) (Stop: {2}) Ending value: {3:.2f}'.format(self.config['sma_long_interval'], self.config['sma_short_interval'], self.config['stop_loss'], self.broker.getValue()))

	def addDataEntry(self, open, high, low, close):
		self.open.append(open)
		self.high.append(high)
		self.low.append(low)
		self.close.append(close)
		for indicator in self.indicators:
			indicator.addDataEntry(open, high, low, close)


class MovingAverages(Strategy):

	def __init__(self, config):
		super().__init__(config)

		self.long_sma = indicators.SimpleMovingAverage(self.config['sma_long_interval'])
		self.short_sma = indicators.SimpleMovingAverage(self.config['sma_short_interval'])
		self.indicators.extend([self.long_sma, self.short_sma])

	def next(self):
		if not self.in_position:
			if(self.long_sma[-1] < self.short_sma[-1]):
				self.buy()
		else:
			if(self.broker.loss >= self.broker.cash * self.config['stop_loss']):
				self.sell()
			elif(self.long_sma[-1] > self.short_sma[-1]):
				self.sell()

class LogisticRegression(Strategy):
	def __init__(self, config):
		super().__init__(config)

		ticks = config['data'].truncate(config['startTrain'], config['endTrain'])
		self.setup_period = 20
		self.indicators.append(indicators.SimpleMovingAverage(20))
		self.indicators.append(indicators.ExponentialMovingAverage(20))
		self.indicators.append(indicators.High())
		self.indicators.append(indicators.Low())
		self.indicators.append(indicators.Close())
		training_data = self.createTrainingData(ticks)
		clearIndicators(self.indicators)
		targets = getTargets(training_data)
		print(targets)
		self.LR = linear_model.LogisticRegression()
		self.LR.fit(training_data, targets)

	def createTrainingData(self, ticks):
		if(len(self.indicators) == 0): raise ValueError("You need to add indicators before training data can be created")

		training_data = []
		open = ticks['buy']['open']
		high = ticks['buy']['high']
		low = ticks['buy']['low']
		close = ticks['buy']['close']
		for index, item in enumerate(close):
			for indicator in self.indicators:
				indicator.addDataEntry(open[index], high[index], low[index], close[index])
			training_data.append(self.getFeatures())
		return training_data

	def getFeatures(self):
		if(len(self.indicators) == 0): raise ValueError("You need to add indicators before training data can be created")
		return [indicator[-1] for indicator in self.indicators]

	def next(self):
		if(len(self.close) < self.setup_period): return

		features = [self.getFeatures()]
		signal = self.LR.predict(features)[0]
		self.predictions.append(signal)
		if not self.in_position:
			if(signal):
				self.buy()
		else:
			if(self.broker.loss >= self.broker.cash * self.config['stop_loss']):
				self.sell()
			elif(not signal):
				self.sell()

def getTarget(data, index):
	if(len(data) <= index + 1): return False
	if(data[index + 1] > data[index]): return True
	return False

def getTargets(data):
	return [getTarget(data, index) for index, item in enumerate(data)]

def clearIndicators(indicators):
	for indicator in indicators:
		indicator.clearData()
