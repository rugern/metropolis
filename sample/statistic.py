from matplotlib import pyplot
import numpy

from sample import algorithms
from sample import utility


def plotMovingAverages(data, strategy):
	long_interval = strategy['longAveragesInterval']
	short_interval = strategy['shortAveragesInterval']

	limit = 100
	datetimes = [''] * limit
	for i in range(limit):
		if(i % 4 == 0): datetimes[i] = utility.datetimeToString(data[0][i])
	buy_open = data[1][:limit]
	longAverages = algorithms.MovingAverages.movingAverages(buy_open, long_interval)
	shortAverages = algorithms.MovingAverages.movingAverages(buy_open, short_interval)

	pyplot.plot(buy_open, color='blue')
	pyplot.plot(longAverages, color='green')
	pyplot.plot(shortAverages, color='red')
	pyplot.xticks(range(len(datetimes)), datetimes, size='small')

	pyplot.show()

def plotBollinger(data, strategy):
	interval = strategy['bollingerInterval']

	limit = 100
	datetimes = [''] * limit
	for i in range(limit):
		if(i % 4 == 0): datetimes[i] = utility.datetimeToString(data[0][i])
	buy_open = data[1][:limit]
	upper, middle, lower = algorithms.BollingerBand.bollingerBand(buy_open, interval)

	pyplot.plot(buy_open, color='blue')
	pyplot.plot(upper, color='green')
	pyplot.plot(middle, color='gray')
	pyplot.plot(lower, color='red')
	pyplot.xticks(range(len(datetimes)), datetimes, size='small')

	pyplot.show()
