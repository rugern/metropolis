from sample import metrics
from sample import trade
from sample import config

class BollingerBand:
	parameterNames = ['bollingerInterval']
	increments = [1]
	minimum_parameters = [2]

	def shouldBuy(self, history, strategy):
		interval = strategy['bollingerInterval']
		upper_band, middle_band, lower_band = bollingerBand(history, interval)
		return history[-1] >= upper_band[-1]

	def shouldSell(self, history, strategy):
		interval = strategy['bollingerInterval']
		upper_band, middle_band, lower_band = bollingerBand(history, interval)
		return history[-1] < lower_band[-1]

	def bollingerBand(history, interval):
		middle_band = movingAverages(history, interval)
		double_standard_deviation = 2 * metrics.standardDeviation(middle_band)
		upper_band = [x + double_standard_deviation for x in middle_band]
		lower_band = [x - double_standard_deviation for x in middle_band]
		return (upper_band, middle_band, lower_band)

class MovingAverages:
	parameterNames = ['shortAveragesInterval', 'longAveragesInterval']

	def availableParameters(self, number_of_increments):
		parameters = []
		for i in range(1, number_of_increments):
			for j in range(i + 1, number_of_increments):
				parameters.append((i, j))
		return parameters

	def shouldBuy(self, history, strategy):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverages = self.movingAverages(history, long_interval)
		shortAverages = self.movingAverages(history, short_interval)
		return shortAverages[-1] >= longAverages[-1]

	def shouldSell(self, history, strategy, security):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverages = self.movingAverages(history, long_interval)
		shortAverages = self.movingAverages(history, short_interval)
		return shortAverages[-1] < longAverages[-1]

	def movingAverage(self, history, interval):
		return metrics.calculateAverage(history[-interval:])

	def movingAverages(self, history, span):
		averages = []
		for i in range(span):
			averages.append(self.movingAverage(history[:-span + i + 1], span))
		return averages

def testAlgorithm(algorithm, strategy, data):
	datetimes, buy_open, buy_high, buy_low, buy_close, sell_open, sell_high, sell_low, sell_close = data
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
