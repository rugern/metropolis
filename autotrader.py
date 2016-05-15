import pickle
import os
import sys
import pandas
from matplotlib import pyplot
import json
import math

def main(data_path, strategy_path):
	excludedNames = ['.DS_Store']

	strategy = readStrategy(strategy_path)
	data = loadData(data_path, excludedNames)
	profits = runAlgorithm(data, strategy);
	printStats(profits)
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

def runAlgorithm(data, strategy):
	units = 0
	spent = 0
	profits = []
	for df in data:
		buy = df['Buy']['open'][:]
		sell = df['Sell']['open'][:]
		for i in range(len(buy)):
			if(units > 0):
				sell_value = sell[i] * units - spent
				if math.isnan(sell_value):
					print("Sell: ", df.iloc[i])
					continue
				else:
					profits.append(sell_value)
					units = 0
					spent = 0
			else:
				units = 1000
				buy_value = units * buy[i]
				if(math.isnan(buy_value)):
					print("Buy: ", df.iloc[i])
					units = 0
				else:
					spent = buy_value
	return profits

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
