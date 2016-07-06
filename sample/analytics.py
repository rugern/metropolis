from numpy import array
from sklearn.linear_model import LogisticRegression as LRBase
from talib import SMA

class Analytics:

	def __init__(self):
		self.data = []

	def addDataEntry(self, entry):
		self.data.append(entry)


class SimpleMovingAverage(Analytics):

	def __init__(self, period):
		super().__init__()
		self.period = period

	def __getitem__(self, index):
		if(len(self.data) == 0): return 0
		return SMA(array(self.data), timeperiod=self.period)[index]

	def getResult(self):
		result = [SMA(array(self.data[:index + 1]), timeperiod=self.period)[-1] for index, item in enumerate(self.data)]
		return result

class LogisticRegression(Analytics):

	def __init__(self, training_data, targets):
		super().__init__()
		self.LR = LRBase()
		self.LR.fit([[i] for i in training_data], targets)

	def __getitem__(self, index):
		return self.data[index]

	def getResult(self):
		return range(len(self.data))

	def predict(self):
		prediction = self.LR.predict(self.data[-1])[0]
		if(not prediction): print('usant!')
		return prediction
