import abc
import statistics

from numpy import array
import talib

class Indicator:

	def __init__(self):
		self.open = []
		self.high = []
		self.low = []
		self.close = []
		self.history = []

	def __getitem__(self, index):
		if(len(self.history) == 0): return 0
		return self.history[index]

	def addDataEntry(self, open, high, low, close):
		self.open.append(open)
		self.high.append(high)
		self.low.append(low)
		self.close.append(close)
		self.history.append(self.getResult())

	def getHistory(self):
		return self.history

	def clearData(self):
		self.open = []
		self.high = []
		self.low = []
		self.close = []
		self.history = []

	@abc.abstractmethod
	def getResult(self):
		'''This method should calculate and return the indicator's value given
			the available data'''
		return 0

class SimpleMovingAverage(Indicator):
	def __init__(self, period):
		super().__init__()
		self.period = period

	def getResult(self):
		if(len(self.close) < self.period): return 0
		return talib.SMA(array(self.close), timeperiod=self.period)[-1]

class ExponentialMovingAverage(Indicator):
	def __init__(self, period):
		super().__init__()
		self.period = period

	def getResult(self):
		if(len(self.close) < self.period): return 0
		return talib.EMA(array(self.close), timeperiod=self.period)[-1]

class High(Indicator):
	def getResult(self):
		return self.high[-1]

class Low(Indicator):
	def getResult(self):
		return self.low[-1]

class Close(Indicator):
	def getResult(self):
		return self.close[-1]

class Difference(Indicator):
	def getResult(self):
		if(len(self.close) < 2): return 0
		return self.close[-1] - self.close[-2]

class StandardDeviation(Indicator):
	def getResult(self):
		return statistics.stdev(self.close)

class RateOfChange(Indicator):
	def __init__(self, period):
		super().__init__()
		self.period = period

	def getResult(self):
		return talib.ROC(self.close, timeperiod=self.period)

class StochasticOscillator(Indicator):
	def __init__(self, fastk_period, slowk_period, slowd_period):
		super().__init__()
		self.fastk_period = fastk_period
		self.slowk_period = slowk_period
		self.slowd_period = slowd_period

	def getResult(self):
		(slowk, slowd) = talib.STOCH(self.high, self.low, self.close, fastk_period=self.fastk_period, slowk_period=self.slowk_period, slowk_matype=0, slowd_period=self.slowd_period, slowd_matype=0)
		return (slowk, slowd)

class MovingAverageConvergenceDivergence(Indicator):
	def __init__(self, fast_period, slow_period, signal_period):
		super().__init__()
		self.fast_period = fast_period
		self.slow_period = slow_period
		self.signal_period = signal_period

	def getResult(self):
		(macd, macdsignal, macdhist) = talib.MACD(self.close, fastperiod=self.fast_period, slowperiod=self.slow_period, signalperiod=self.signal_period)
		return (macd, macdsignal, macdhist)

class RelativeStrength(Indicator):
	def __init__(self, period):
		super().__init__()
		self.period = period

	def getResult(self):
		return talib.RSI(self.close, timeperiod=self.period)

class AverageDirectionalMovement(Indicator):
	def __init__(self, period):
		super().__init__()
		self.period = period

	def getResult(self):
		return talib.ADX(self.high, self.low, self.close, timeperiod=self.period)

class MaximumDrawdown(Indicator):
	def __init__(self):
		super().__init__()
		self.max = 0
		self.drawdown = 0

	def getResult(self):
		value = self.close[-1]
		if(value > self.max): self.max = value
		else:
			difference = self.max - value
			if(self.drawdown < difference): self.drawdown = difference
		return self.drawdown

class AverageDrawdown(Indicator):
	def __init__(self):
		super().__init__()
		self.last_high = 0
		self.last = 0
		self.drawdowns = []

	def getResult(self):
		value = self.close[-1]
		if(value > self.last):
			self.last_high = value
		self.drawdowns.append(self.last_high - value)
		self.last = value
		return statistics.mean(self.drawdowns)

class RinaIndex(Indicator):
	def __init__(self, broker, averageDrawdown):
		super().__init__()
		self.broker = broker
		self.averageDrawdown = averageDrawdown

	def getResult(self):
		deviation = statistics.stdev(self.broker.profits)
		mean = statistics.mean(self.broker.profits)
		select = [i for i in self.broker.profits if abs(i - mean) <= 3 * deviation]
		return select / (self.averageDrawdown[-1] * self.broker.getMarketTime())