import talib
from numpy import array

class SimpleMovingAverage:

	def __init__(self, period):
		self.period = period
		self.data = []

	def __getitem__(self, index):
		if(len(self.data) == 0): return 0
		return talib.SMA(array(self.data), timeperiod=self.period)[index]

	def addData(self, entry):
		self.data.append(entry)

	def getResult(self):
		result = []
		for index, entry in enumerate(self.data):
			result.append(talib.SMA(array(self.data[:index + 1]), timeperiod=self.period)[-1])
		return result
