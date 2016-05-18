import pickle
import os
import sys
import pandas
from matplotlib import pyplot
import json
import math

def main(data_path, strategy_path):
	excludedNames = ['.DS_Store']

	bank = Bank()
	strategy = readStrategy(strategy_path)
	data = loadData(data_path, excludedNames)
	runAlgorithm(data, strategy, bank)
	# printStats(profits)
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

def runAlgorithm(data, strategy, bank):
	for df in data:
		buys = df['Buy']['open']
		sells = df['Sell']['open']
		times = df['DateTime']
		for i in range(len(buys)):
			datetime = convertToDatetime(times[i])
			buy = buys[i]
			sell = sells[i]
			for j in range(len(bank.activeTrades)):
				trade = bank.activeTrades[j]
				if(shouldSell(trade, sell)):
					trade.closingTime = datetime
					trade.closingRate = sell
					trade.profit = trade.calculateReturns();
					bank.closeTrade(trade)
			if(shouldBuy(buy)):
				units = calculateNumberOfUnits(bank, buy)
				trade = Trade("EUR_USD", units, buy, openingTime)
				bank.openTrade(trade)

def readPkl(filename):
	return pandas.read_pickle(filename)

def loadData(directory, excludedNames):
	data = []
	filePaths = getFilePaths(directory, excludedNames)
	for path in filePaths:
		data.append(readPkl(path))
	return data

def getFilePaths(directory, excludedNames):
	paths = []
	for root, subFolders, files in os.walk(directory):
		if len(subFolders) != 0: continue
		files = list(filter(lambda x: x not in excludedNames, files))
		if len(files) == 0: continue

		for filename in files:
			paths.append(root + '/' + filename)
	return paths

main(sys.argv[1], sys.argv[2])
