import json
from datetime import datetime

import pandas

from sample import strategies
from sample import sizers
from sample import utility
from sample import brokers

# Too many ancestors
#pylint: disable=R0901
# Too many attributes
#pylint: disable=R0902
# Using global statement
#pylint: disable=W0603

def getConfigFile(path):
	config = readConfigFile(path)
	config['startDate'] = datetime.strptime(config['startDate'], '%d.%m.%y')
	config['endDate'] = datetime.strptime(config['endDate'], '%d.%m.%y')
	config['startTrain'] = datetime.strptime(config['startTrain'], '%d.%m.%y')
	config['endTrain'] = datetime.strptime(config['endTrain'], '%d.%m.%y')
	config['data'] = pandas.read_pickle(config['data_path'])
	config['strategy'] = getStrategy(config['strategy_name'])
	config['broker'] = getBroker(config['cash'])
	config['sizer'] = getSizer(config['sizer_name'])
	return config

def readConfigFile(path):
	jsonFile = open(path)
	configData = json.load(jsonFile)
	jsonFile.close()
	return configData

def writeConfigFile(content, path):
	jsonFile = open(path, 'w+')
	json.dump(content, jsonFile)
	jsonFile.close()

def getBroker(cash):
	return brokers.Broker(cash)

def getStrategy(strategy_name):
	if(strategy_name == 'sma'): return strategies.MovingAveragesStrategy
	elif(strategy_name == 'ml'): return strategies.LRStrategy
	raise ValueError('Strategy not found')

def getSizer(sizer_name):
	if(sizer_name == 'kelly'): return sizers.kellyCriterion
	raise ValueError('Sizer not found')
