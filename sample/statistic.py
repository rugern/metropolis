from matplotlib import pyplot

from sample import algorithms
from sample import utility
from sample import metrics


def plotMovingAverages(data, strategy):
	long_interval = strategy['longAveragesInterval']
	short_interval = strategy['shortAveragesInterval']

	limit = 100
	datetimes = [''] * limit
	for i in range(limit):
		if(i % 4 == 0): datetimes[i] = utility.datetimeToString(data[0][i])
	buy_open = data[1][:limit]
	long_averages = metrics.movingAverages(buy_open, long_interval)
	short_averages = metrics.movingAverages(buy_open, short_interval)

	plotArrays([buy_open, long_averages, short_averages], datetimes)
	pyplot.show()

def plotBollinger(data, strategy):
	interval = strategy['bollingerInterval']

	limit = 100
	datetimes = [''] * limit
	for i in range(limit):
		if(i % 4 == 0): datetimes[i] = utility.datetimeToString(data[0][i])
	buy_open = data[1][:limit]
	upper, middle, lower = algorithms.BollingerBand.getBands(buy_open, interval)

	plotArrays([buy_open, upper, middle, lower], datetimes)

def plotArrays(arrays, xLabels=None):
	for array in arrays:
		pyplot.plot(array)

	if(xLabels is not None): pyplot.xticks(range(len(xLabels)), xLabels, size='small')
	pyplot.show()
