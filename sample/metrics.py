import functools
import math

from sample import trade

def sumProfits(securities):
	return functools.reduce(lambda x, y: x + y.profit, securities, 0);

def profitFactor(securities):
	losses = filter(lambda x: x.profit < 0, securities)
	profits = filter(lambda x: x.profit > 0, securities)
	return sum(profits) / sum(losses)

def averageWinningTrade(securities):
	return sumProfits(securities) / len(securities)

def maximumDrawdown(securities):
	maximum_drawdown = 0
	drawdown_high = 0

	high = securities[0].profit
	low = securities[0].profit

	for security in securities:
		profit = security.profit
		if(profit > high):
			if(high - low > maximum_drawdown):
				maximum_drawdown = high - low
				drawdown_high = high
			high = profit
			low = profit
		if(profit < low): low = profit
	if(high - low > maximum_drawdown):
		maximum_drawdown = high - low
		drawdown_high = high

	return (maximum_drawdown, drawdown_high)

def relativeMaximumDrawdown(securities):
	(maximum_drawdown, drawdown_high) = maximumDrawdown(securities)
	return maximum_drawdown / drawdown_high

def absoluteMaximumDrawdown(securities):
	(maximum_drawdown, drawdown_high) = maximumDrawdown(securities)
	return maximum_drawdown

def timeAverages(securities):
	total = functools.reduce(lambda x, y: x + y.spentTime(), securities, 0)
	return total / len(securities)

def riskStopLoss(securities):
	profit = sumProfits(securities)
	maximum_drawdown = absoluteMaximumDrawdown(securities)[0]
	return profit / maximum_drawdown

def calculateAverage(history):
	if(len(history) == 0): return 0
	total = sum(history)
	return total / len(history)

def standardDeviation(history):
	if(len(history) == 0): return 0
	average = calculateAverage(history)
	inner_sum = functools.reduce(lambda x, y: x + (y - average) ** 2, history, 0)
	return math.sqrt(inner_sum / len(history))

def rinaIndex(securities):
	profit = selectTotalNetProfit(securities)
	average_drawdown = averageDrawdown(securities)
	percent_time_active = percentTimeInMarket(securities)
	return profit / (average_drawdown * percent_time_active)

def averageDrawdown(securities):
	drawdowns = []

	high = securities[0].profit
	low = securities[0].profit

	for security in securities:
		profit = security.profit
		if(profit > high):
			if(high != low):
				drawdowns.append(high - low)
			high = profit
			low = profit
		if(profit < low): low = profit
	if(high != low):
		drawdowns.append(high - low)

	return sum(drawdowns) / len(drawdowns)

def percentTimeInMarket(securities):
	total = securities[-1].closingTime - securities[0].openingTime
	time_spent = functools.reduce(lambda x, y: x + (y.closingTime - y.openingTime), securities, 0)
	return 100 * time_spent / total

def selectTotalNetProfit(securities):
	profits = map(lambda x: x.profit, securities)
	average = calculateAverage(profits)
	triple_standard_deviation = 3 * standardDeviation(profits)
	counting_profits = filter(lambda x: math.fabs(x - average) <= triple_standard_deviation, profits)
	return sum(counting_profits)
