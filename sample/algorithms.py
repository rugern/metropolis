from sample import metrics
from sample import trade
from sample import config

class BollingerBand:
	def getAllParameters(self):
		values = [5, 10, 15, 20, 25, 30, 35, 40]
		parameters = []
		for value in values:
			parameters.append({'bollingerInterval': value})
		return parameters

	def shouldBuy(self, history, strategy):
		interval = strategy['bollingerInterval']
		upperBand = self.getBands(history, interval)[0]
		return history[-1] >= upperBand[-1]

	def shouldSell(self, history, strategy):
		interval = strategy['bollingerInterval']
		lowerBand = self.getBands(history, interval)[2]
		return history[-1] < lowerBand[-1]

	@staticmethod
	def getBands(history, interval):
		middleBand = metrics.movingAverages(history, interval)
		deviations = metrics.runningStandardDeviation(middleBand, interval)
		upperBand = []
		lowerBand = []
		for index, middle in enumerate(middleBand):
			upperBand.append(middle + 2 * deviations[index])
			lowerBand.append(middle - 2 * deviations[index])
		return (upperBand, middleBand, lowerBand)

class MovingAverages:
	def getAllParameters(self):
		longValues = [5, 10, 15, 20, 25, 30, 35, 40]
		shortValues = [2, 3, 4, 5, 6, 7, 8, 9]
		if(len(longValues) != len(shortValues)): raise ValueError('Wrong number of values in MovingAverages parameters!')

		parameters = []
		for i in range(longValues):
			parameters.append({'shortAveragesInterval': shortValues[i], 'longAveragesInterval': longValues[i]})
		return parameters

	def shouldBuy(self, history, strategy):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverage = self.getAverage(history, long_interval)
		shortAverage = self.getAverage(history, short_interval)
		return shortAverage >= longAverage

	def shouldSell(self, history, strategy):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverage = self.getAverage(history, long_interval)
		shortAverage = self.getAverage(history, short_interval)
		return shortAverage < longAverage

	def getAverage(self, data, interval):
		length = len(data)
		start = metrics.getIntervalStart(length, interval)
		return metrics.calculateAverage(data[start:])

def backtest(algorithm, strategy, data):
	datetimes = data['datetimes']
	buy_close = data['buy_close']
	sell_close = data['sell_close']
	length = len(buy_close)
	for i in range(1, length):
		datetime = datetimes[i]

		currentSecurities = len(config.bank.activeSecurities)
		if(currentSecurities == 0 and algorithm.shouldBuy(buy_close[:i], strategy)):
			print('Bought')
			units = config.bank.calculateNumberOfUnits(buy_close[-1])
			security = trade.Trade('EUR_USD', units, buy_close[-1], datetime)
			config.bank.openTrade(security)

		for security in config.bank.activeSecurities:
			if(algorithm.shouldSell(sell_close[:i], strategy, security)):
				print('Sold')
				security.closingTime = datetime
				security.closingRate = sell_close[-1]
				security.profit = security.calculateReturns()
				config.bank.closeTrade(security)
	return config.bank.calculateReturns()
