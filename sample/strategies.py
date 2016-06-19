import backtrader as bt

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

class TestStrategy(bt.Strategy):
	params = (
		('short_interval', 0),
		('long_interval', 0),
		('stake', 0),
	)

	def __init__(self):
		self.dataclose = self.datas[0].close
		self.sizer.setsizing(self.params.stake)
		self.bar_executed = 0
		self.order = None

		self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_interval)
		bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_interval)

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# Buy/Sell order submitted/accepted to/by broker - Nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enougth cash
		if order.status in [order.Completed, order.Canceled, order.Margin]:
			if order.isbuy():
				self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))

			else:  # Sell
				self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' % (order.executed.price, order.executed.value, order.executed.comm))

			self.bar_executed = len(self)

		# Write down: no pending order
		self.order = None

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

	# def notify(self, order):
	# 	if order.status in [order.Submitted, order.Accepted]:
	# 		# Buy/Sell order submitted/accepted to/by broker - Nothing to do
	# 		return
	#
	# 	if order.status in [order.Completed, order.Canceled, order.Margin]:
	# 		self.bar_executed = len(self)
	#
	# 	self.order = None

	def next(self):
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
