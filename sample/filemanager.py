import json
import pandas

def readPkl(filename):
	return pandas.read_pickle(filename)

def loadData(directory):
	return readPkl(directory)

def readStrategy(path):
	jsonFile = open(path)
	strategy = json.load(jsonFile)
	jsonFile.close()
	return strategy

def writeStrategy(content, path):
	jsonFile = open(path, 'w+')
	json.dump(content, jsonFile)
	jsonFile.close()
