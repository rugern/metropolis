import os
import pandas
import pickle
import json

def readPkl(filename):
	return pandas.read_pickle(filename)

def loadData(directory, excludedNames):
	data = []
	filePaths = getFilePaths(directory, excludedNames)
	for path in filePaths:
		data.append(readPkl(path))
	datetimes = []
	for row in data:
		datetimes.extend(row.index.values)
	buy_open = getColumn(data, ('Buy', 'open'))
	buy_high = getColumn(data, ('Buy', 'high'))
	buy_low = getColumn(data, ('Buy', 'low'))
	buy_close = getColumn(data, ('Buy', 'close'))
	sell_open = getColumn(data, ('Sell', 'open'))
	sell_high = getColumn(data, ('Sell', 'high'))
	sell_low = getColumn(data, ('Sell', 'low'))
	sell_close = getColumn(data, ('Sell', 'close'))
	return (datetimes, buy_open, buy_high, buy_low, buy_close, sell_open, sell_high, sell_low, sell_close)

def getColumn(data, column_name):
	result = []
	for entry in data:
		result.extend(entry[column_name])
	return result

def getFilePaths(directory, excludedNames):
	paths = []
	for root, subFolders, files in os.walk(directory):
		if len(subFolders) != 0: continue
		files = list(filter(lambda x: x not in excludedNames, files))
		if len(files) == 0: continue

		for filename in files:
			paths.append(root + '/' + filename)
	return paths

def readStrategy(path):
	jsonFile = open(path)
	strategy = json.load(jsonFile)
	jsonFile.close()
	return strategy

def writeStrategy(content, path):
	jsonFile = open(path, 'w+')
	json.dump(content, jsonFile)
	jsonFile.close()
