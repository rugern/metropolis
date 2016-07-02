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
	in_position = False
	data = []
	buy = None
	sell = None
	indicators = []

	def __init__(self, config):
		self.config = config

	def stop(self, value):
		print('(Long: {0}) (Short: {1}) Ending value: {2:.2f}'.format(self.config['sma_long_interval'], self.config['sma_short_interval'], value))

	def addDataEntry(self, entry):
		self.data.append(entry)


class TestStrategy(Strategy):
	config = None

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
			if(self.long_sma[-1] > self.short_sma[-1]):
				self.sell()
