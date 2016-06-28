
class SimpleMovingAverage:
	period = 0
	data = []

	def __init__(self, period):
		self.period = period

	def __getitem__(self, index):
		return self.data[index]

	def addData(self, entry):
		self.data.append(entry)
