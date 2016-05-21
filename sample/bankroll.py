class Bank:

	assets = 1000
	securities = 0
	activeTrades = []
	tradeHistory = []

	def openTrade(self, trade):
		value = trade.units * trade.openingRate
		assets -= value
		securities += value
		activeTrades.append(trade)


	def closeTrade(self, trade):
		if(None in [trade.closingRate, trade.closingTime, trade.profit]) raise NotSetError('Selling info for trade was not set')

		net_value = trade.units * trade.closingRate
		assets += net_value
		securities -= net_value
		activeTrades.remove(trade)
		tradeHistory.append(trade)

	def calculateNumberOfUnits(self, value):
		return (self.assets // value) // 2
