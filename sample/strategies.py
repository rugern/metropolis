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

	def stop(self):
		self.log('(Long Period %2d) (Short period %2d) Ending Value %.2f' % (self.config['sma_long_interval'], self.config['sma_short_interval'], self.broker.getValue()), doprint=True)

	def log(self, txt, dt=None, doprint=False):
		if doprint:
			dt = dt or self.datas[0].datetime.date(0)
			print('%s, %s' % (dt.isoformat(), txt))

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
			self.buy()
		else:
			self.sell()
