from sample import statistic
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
	inPosition = False
	data = []
	bar_executed = 0
	order = None
	buy = None
	sell = None
	buy_history = []
	sell_history = []

	def __init__(self, config):
		self.config = config

	def stop(self):
		self.log('(Long Period %2d) (Short period %2d) Ending Value %.2f' % (self.config['sma_long_interval'], self.config['sma_short_interval'], self.broker.getvalue()), doprint=True)

	def log(self, txt, dt=None, doprint=False):
		if doprint:
			dt = dt or self.datas[0].datetime.date(0)
			print('%s, %s' % (dt.isoformat(), txt))


class TestStrategy(Strategy):
	config = None

	def __init__(self, config):
		super().__init__(config)

		self.long_sma = indicators.SimpleMovingAverage(self.config['sma_long_interval'])
		self.short_sma = indicators.SimpleMovingAverage(self.config['sma_short_interval'])
		self.indicators.append(self.long_sma, self.short_sma)

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			return

		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))
			else:
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))

			self.bar_executed = len(self)

		self.order = None


	def next(self):
		if self.order:
			return

		if not self.inPosition:
			if self.long_sma[0] < self.short_sma[0]:
				self.order = self.buy()
		else:
			if self.short_sma[0] < self.long_sma[0]:
				self.order = self.sell()
