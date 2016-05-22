from sample import metrics
from sample import trade
from sample import config

class BollingerBand:
	parameterNames = ['bollingerInterval']

	def availableParameters(self, number_of_increments):
		parameters = range(1, number_of_increments)
		return parameters

	def shouldBuy(self, history, strategy):
		interval = strategy['bollingerInterval']
		upper_band, middle_band, lower_band = bollingerBand(history, interval)
		return history[-1] >= upper_band[-1]

	def shouldSell(self, history, strategy):
		interval = strategy['bollingerInterval']
		upper_band, middle_band, lower_band = bollingerBand(history, interval)
		return history[-1] < lower_band[-1]

	@staticmethod
	def bollingerBand(history, interval):
		middle_band = MovingAverages.movingAverages(history, interval)
		deviations = BollingerBand.runningStandardDeviation(middle_band, interval)
		upper_band = []
		lower_band = []
		for i in range(len(middle_band)):
			upper_band.append(middle_band[i] + 2 * deviations[i])
			lower_band.append(middle_band[i] - 2 * deviations[i])
		return (upper_band, middle_band, lower_band)

	@staticmethod
	def runningStandardDeviation(data, interval):
		deviations = [0] * len(data)
		for i in range(1, len(data)):
			start = 0
			if(interval <= i): start = i - interval
			deviations[i] = metrics.standardDeviation(data[start:i + 1])
			if(deviations[i]==0):print(data[start:i+1])
		return deviations

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
		longAverage = self.movingAverage(history, long_interval)
		shortAverage = self.movingAverage(history, short_interval)
		return shortAverages >= longAverages

	def shouldSell(self, history, strategy, security):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverages = self.movingAverage(history, long_interval)
		shortAverages = self.movingAverage(history, short_interval)
		return shortAverages < longAverages

	@staticmethod
	def movingAverage(history, interval):
		start = interval if len(history) >= interval else len(history)
		return metrics.calculateAverage(history[-start:])

	@staticmethod
	def movingAverages(history, interval):
		averages = []
		for i in range(1, len(history)):
			averages.append(MovingAverages.movingAverage(history[:i], interval))
		return averages

def backtest(algorithm, strategy, data):
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
