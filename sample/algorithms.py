import metrics

class BollingerBand:
	parameterNames = ['bollingerInterval']
	parameterIncrements = [1]

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
	parameterNames = ['longAveragesInterval', 'shortAveragesInterval']
	parameterIncrements = [1, 1]

	def shouldBuy(self, history, strategy):
		long_interval = strategy['longAveragesInterval']
		short_interval = strategy['shortAveragesInterval']
		longAverages = self.movingAverages(history, long_interval)
		shortAverages = self.movingAverages(history, short_interval)
		return shortAverages[-1] >= longAverages[-1]

	def shouldSell(self, history, strategy, trade):
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
			averages.append(movingAverage(history[:-span + i + 1], span))
		return averages

def testAlgorithm(algorithm, strategy, data):
	datetimes, buy_open, buy_high, buy_low, buy_close, sell_open, sell_high, sell_low, sell_close = data
	length = len(buy_open)

	for i in range(1:length):
		datetime = datetimes[i]

		if(algorithm.shouldBuy(buy_open[:i], strategy)):
			trade = Trade("EUR_USD", units, buy_open[-1], datetime)
			bank.openTrade(trade)

		for trade in bank.activeTrades:
			if(algorithm.shouldSell(sell_close[:i], strategy, trade)):
				trade.closingTime = datetime
				trade.closingRate = sell
				trade.profit = trade.calculateReturns()
				bank.closeTrade(trade)
