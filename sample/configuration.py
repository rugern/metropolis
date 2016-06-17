import json

import pandas

from sample import strategy

# Too many ancestors
#pylint: disable=R0901
# Too many attributes
#pylint: disable=R0902

class Config:
	data = None
	mode = None
	startDate = None
	endDate = None
	cash = None
	strategy = None

	leverage = None
	sma_long_interval = None
	sma_short_interval = None
	bbands_interval = None
	bbands_deviation = None

	def __init__(self, path):
		configFile = self.readConfigFile(path)
		self.data = pandas.read_pickle(configFile['data_path'])
		self.mode = configFile['mode']
		self.startDate = configFile['startDate']
		self.endDate = configFile['endDate']
		self.cash = configFile['cash']
		self.strategy = self.getStrategy()

		self.leverage = configFile['leverage']
		self.sma_short_interval = configFile['sma_short_interval']
		self.sma_long_interval = configFile['sma_long_interval']
		self.bbands_interval = configFile['bbands_interval']
		self.bbands_deviation = configFile['bbands_deviation']

	def readConfigFile(self, path):
		jsonFile = open(path)
		data = json.load(jsonFile)
		jsonFile.close()
		return data

	def writeConfigFile(self, content, path):
		jsonFile = open(path, 'w+')
		json.dump(content, jsonFile)
		jsonFile.close()

	def getStrategy(self):
		return strategy.TestStrategy
