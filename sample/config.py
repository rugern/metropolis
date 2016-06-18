import json
from datetime import datetime

import pandas

from sample import strategies

# Too many ancestors
#pylint: disable=R0901
# Too many attributes
#pylint: disable=R0902
# Using global statement
#pylint: disable=W0603

data = None
mode = None
startDate = None
endDate = None
cash = None
commission = None
stake = None
strategy = None

leverage = None
sma_long_interval = None
sma_short_interval = None
bbands_interval = None
bbands_deviation = None

def initialize(path):
	global data, mode, startDate, endDate, cash, commission, stake, strategy, leverage, sma_long_interval, sma_short_interval, bbands_interval, bbands_deviation
	configFile = readConfigFile(path)
	startDate = datetime.strptime(configFile['startDate'], '%d.%m.%y')
	endDate = datetime.strptime(configFile['endDate'], '%d.%m.%y')
	data = pandas.read_pickle(configFile['data_path']).truncate(startDate, endDate)
	mode = configFile['mode']
	cash = configFile['cash']
	commission = configFile['commission']
	stake = configFile['stake']
	strategy = getStrategy()

	leverage = configFile['leverage']
	sma_short_interval = configFile['sma_short_interval']
	sma_long_interval = configFile['sma_long_interval']
	bbands_interval = configFile['bbands_interval']
	bbands_deviation = configFile['bbands_deviation']

def readConfigFile(path):
	jsonFile = open(path)
	configData = json.load(jsonFile)
	jsonFile.close()
	return configData

def writeConfigFile(content, path):
	jsonFile = open(path, 'w+')
	json.dump(content, jsonFile)
	jsonFile.close()

def getStrategy():
	return strategies.TestStrategy
