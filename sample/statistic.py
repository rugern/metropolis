from matplotlib import pyplot

from sample import algorithms

def plotMovingAverages(data, strategy):
	averages = algorithms.MovingAverages()
	long_interval = strategy['longAveragesInterval']
	short_interval = strategy['shortAveragesInterval']

	buy_open = data[1]
	longAverages = averages.movingAverages(buy_open, long_interval)
	shortAverages = averages.movingAverages(buy_open, short_interval)

	limit = 100
	pyplot.plot(buy_open[limit])
	pyplot.plot(longAverages)
	pyplot.plot(shortAverages)
	pyplot.show()
