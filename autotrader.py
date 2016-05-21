import sys
from matplotlib import pyplot
import math

import data
import statistic
import algorithms
import bankroll
import error
import metrics
import trade
import optimization

bank = 0;
strategy = 0;

def main(data_path, strategy_path, training):
	excludedNames = ['.DS_Store']

	bank = Bank()
	strategy = data.readStrategy(strategy_path)
	data = data.loadData(data_path, excludedNames)
	optimizeStrategy(data) if training else runAlgorithm(data)
	# statistic.printStats(profits)
	# drawPlot(profits)

def runAlgorithm(data):
	algorithm = getAlgorithm(strategy['algorithm'])
	for df in data:
		buys = df['Buy']['open']
		sells = df['Sell']['open']
		times = df['DateTime']
		for i in range(len(buys)):
			datetime = convertToDatetime(times[i])
			history = buys[:i]
			buy = buys[i]
			sell = sells[i]
			for j in range(len(bank.activeTrades)):
				trade = bank.activeTrades[j]
				if(algorithm.shouldSell(history, trade)):
					trade.closingTime = datetime
					trade.closingRate = sell
					trade.profit = trade.calculateReturns();
					bank.closeTrade(trade)
			if(algorithm.shouldBuy(history)):
				units = bank.calculateNumberOfUnits(buy)
				trade = Trade("EUR_USD", units, buy, openingTime)
				bank.openTrade(trade)

def optimizeStrategy(data):
	algorithm = getAlgorithm(strategy['algorithm'])
	optimizer = getOptimizer(strategy['optimization'])

	optimizedStrategy = optimizer.optimize(strategy, algorithm, training)
	data.writeStrategy(optimizedStrategy, 'strategies/optimized_strat.json')

def getAlgorithm(algorithm_name):
	algorithm = 0
	if(algorithm_name == 'MA') algorithm = algorithms.MovingAverages()
	else if(algorithm_name == 'BB') algorithm = algorithms.BollingerBand()
	return algorithm

def getOptimizer(optimizer_name):
	optimizer = 0
	if(optimizer_name == 'WFA') optimizer = optimization.walkForward
	return optimizer

def printStats(profits):
	total = sum(profits)
	print("Profit sum: ", total)

def drawPlot(data):
	pyplot.plot(data)
	pyplot.show();

if(len(sys.argv) == 4): main(sys.argv[1], sys.argv[2], sys.argv[3])
else: main(sys.argv[1], sys.argv[2], False)
