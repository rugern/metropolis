import sys
import pandas
import pickle

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
