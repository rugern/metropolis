import os
from matplotlib import pyplot
import json
import math

import data
import statistic
import algorithm
import bankroll
import error
import metrics
import trade
import optimization

bank = 0;
strategy = 0;

def main(data_path, strategy_path):
	excludedNames = ['.DS_Store']

	bank = Bank()
	strategy = readStrategy(strategy_path)
	data = data.loadData(data_path, excludedNames)
	runAlgorithm(data)
	# statistic.printStats(profits)
	# drawPlot(profits)

def printStats(profits):
	total = sum(profits)
	print("Profit sum: ", total)

def drawPlot(data):
	pyplot.plot(data)
	pyplot.show();

def readStrategy(path):
	jsonFile = open(path)
	return json.load(jsonFile)

def runAlgorithm(data):
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
				if(shouldSell(history, trade)):
					trade.closingTime = datetime
					trade.closingRate = sell
					trade.profit = trade.calculateReturns();
					bank.closeTrade(trade)
			if(shouldBuy(history)):
				units = calculateNumberOfUnits(buy)
				trade = Trade("EUR_USD", units, buy, openingTime)
				bank.openTrade(trade)

def shouldBuy(history):
	longAverage = algorithm.movingAverage(history, strategy['longAverageValue'])
	shortAverage = algorithm.movingAverage(history, strategy['shortAverageValue'])
	return shortAverage >= longAverage

def shouldSell(history, trade):
	longAverage = algorithm.movingAverage(history, strategy['longAverageValue'])
	shortAverage = algorithm.movingAverage(history, strategy['shortAverageValue'])
	return shortAverage < longAverage

def calculateNumberOfUnits(value):
	return bank.assets / value

main(sys.argv[1], sys.argv[2])
