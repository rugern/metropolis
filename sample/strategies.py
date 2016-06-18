import backtrader as bt

from sample import config

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

class TestStrategy(bt.Strategy):
	params = (('long_interval', 20),('short_interval', 5),)

	def __init__(self):
		self.dataclose = self.datas[0].close
		self.sizer.setsizing(config.stake)
		self.bar_executed = 0
		self.order = None

		self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_interval)
		bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.long_interval)
		bt.indicators.WeightedMovingAverage(self.datas[0], period=self.params.long_interval).subplot = True
		bt.indicators.StochasticSlow(self.datas[0])
		bt.indicators.MACDHisto(self.datas[0])
		rsi = bt.indicators.RSI(self.datas[0])
		bt.indicators.SmoothedMovingAverage(rsi, period=config.sma_short_interval)
		bt.indicators.ATR(self.datas[0]).plot = False

	def notify(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		if order.status in [order.Completed, order.Canceled, order.Margin]:
			self.bar_executed = len(self)

		self.order = None

	def next(self):
		# self.log('Close, %f' % self.dataclose[0])

		if self.order:
			return

		if not self.position:
			if self.dataclose[0] > self.sma[0]:
				self.order = self.buy()
		else:
			if self.dataclose[0] < self.sma[0]:
				self.order = self.sell()

	def stop(self):
		self.log('(MA Period %2d) Ending Value %.2f' % (self.params.long_interval, self.broker.getvalue()), doprint=True)

	def log(self, txt, dt=None, doprint=False):
		if doprint:
			dt = dt or self.datas[0].datetime.date(0)
			print('%s, %s' % (dt.isoformat(), txt))
