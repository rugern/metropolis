from sample import statistic

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


class TestStrategy(Strategy):
	params = (
		('config', 0),
	)
	config = None
	buy_history = []
	sell_history = []
	position = False

	def __init__(self):
		self.config = self.params.config

		self.dataclose = self.datas[0].close
		self.setsizer(MySizer())
		self.sizer.setsizing(self.config['stake'])
		self.bar_executed = 0
		self.order = None

		self.long_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.config['sma_long_interval'])
		self.short_sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.config['sma_short_interval'])

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

	def notify_trade(self, trade):
		if not trade.isclosed:
			return

		self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))


	def next(self):
		if self.order:
			return

		if not self.position:
			if self.long_sma[0] < self.short_sma[0]:
				self.order = self.buy()
				self.position = True
				position_size = statistic.kellyCriterion(self.buy_history, self.sell_history)
				self.buy_history.append(self.dataclose[0])
		else:
			if self.short_sma[0] < self.long_sma[0]:
				self.order = self.sell()
				self.position = False
				self.sell_history.append(self.dataclose[0] * self.config['stake'])

	def stop(self):
		self.log('(Long Period %2d) (Short period %2d) Ending Value %.2f' % (self.config['sma_long_interval'], self.config['sma_short_interval'], self.broker.getvalue()), doprint=True)

	def log(self, txt, dt=None, doprint=False):
		if doprint:
			dt = dt or self.datas[0].datetime.date(0)
			print('%s, %s' % (dt.isoformat(), txt))

class KellySizer():

	params = (
		('broker', None),
		('stake', 1)
		)

	def getsizing(self, data=None, broker=None):
		broker = broker or self.params.broker
		return self._getsizing(broker.getcommissioninfo(data),
							   broker.getcash(), data=data)

	def _getsizing(self, comminfo, cash, data=None):
		if not data:
			return self.params.stake

		# Get total available cash and portfolio value
		cash = self.params.broker.getcash()
		value = self.params.broker.getvalue()
		# Get asset price to determine right number of shares to buy
		price = data.close[0]
		# Determine number of shares
		shares = cash / price
		return shares

	def setsizing(self, stake):
		self.params.stake = stake

	def setbroker(self, broker):
		self.params.broker = broker

	def getbroker(self):
		return self.params.broker
