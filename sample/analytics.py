import talib
from numpy import array

class SimpleMovingAverage:
	period = 0
	data = []

	def __init__(self, period):
		self.period = period

	def __getitem__(self, index):
		if(len(self.data) == 0): return 0
		return talib.SMA(array(self.data), timeperiod=self.period)[index]

	def addData(self, entry):
		self.data.append(entry)
