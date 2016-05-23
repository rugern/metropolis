from sample import utility

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
		if(None in [self.units]): raise ValueError('Values in trade returns not set!')
		return self.units * self.numberOfPips() // 10000

	def numberOfPips(self):
		if(None in [self.closingRate, self.openingRate]): raise ValueError('Values in trade pips not set!')
		return self.closingRate - self.openingRate

	def spentTime(self):
		if(None in [self.closingTime, self.openingTime]): raise ValueError('Values in trade time not set!')
		difference = self.closingTime - self.openingTime
		return utility.convertToRegularTime(difference)
