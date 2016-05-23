
class Bank:

	assets = 1000
	initial_assets = assets
	securities_value = 0
	activeSecurities = []
	securityHistory = []

	def openTrade(self, security):
		value = security.units * security.openingRate
		self.assets -= value
		self.securities_value += value
		self.activeSecurities.append(security)

	def closeTrade(self, security):
		if(None in [security.closingRate, security.closingTime, security.profit]): raise ValueError('Selling info for security was not set')

		net_value = security.units * security.closingRate
		self.assets += net_value
		self.securities_value -= net_value
		self.activeSecurities.remove(security)
		self.securityHistory.append(security)

	def calculateNumberOfUnits(self, value):
		return (self.assets // value) // 2

	def calculateResult(self):
		return self.assets - self.initial_assets
