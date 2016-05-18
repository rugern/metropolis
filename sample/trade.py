class Trade:
	closingTime = None
	closingRate = None
	profit = None

	def __init__(self, currency, units, rate, openingTime):
		self.currency = currency
		self.units = units
		self.openingRate = rate
		self.openingTime = openingTime

	def calculateReturns(self):
		return self.units * numberOfPips() / 10000;

	def numberOfPips(self):
		return self.closingRate - self.openingRate;

	def spentTime(self):
		difference = closingTime - openingTime
		hours = difference.seconds // 3600
		minutes = (difference.seconds % 3600) // 60
		seconds = difference.seconds % 60
		return (hours, minutes, seconds)
