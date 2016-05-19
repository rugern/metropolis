import functools
import trade
import math

def sumProfits(trades):
	return functools.reduce(lambda x, y: x + y.profit, trades, 0);

def profitFactor(trades):
	losses = filter(lambda x: x.profit < 0, trades)
	profits = filter(lambda x: x.profit > 0, trades)
	return sum(profits) / sum(losses)

def averageWinningTrade(trades):
	return sumProfits(trades) / len(trades)

def maximumDrawdown(trades):
	maximum_drawdown = 0
	drawdown_high = 0

	high = trades[0].profit
	low = trades[0].profit

	for trade in trades:
		profit = trade.profit
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

def relativeMaximumDrawdown(trades):
	(maximum_drawdown, drawdown_high) = maximumDrawdown(trades)
	return maximum_drawdown / drawdown_high

def absoluteMaximumDrawdown(trades):
	(maximum_drawdown, drawdown_high) = maximumDrawdown(trades)
	return maximum_drawdown

def timeAverages(trades):
	total = functools.reduce(lambda x, y: x + y.spentTime(), trades, 0)
	return total / len(trades)

def riskStopLoss(trades):
	profit = sumProfits(trades)
	maximum_drawdown = absoluteMaximumDrawdown(trades)[0]
	return profit / maximum_drawdown

def calculateAverage(history):
	total = sum(history)
	return total / len(history)

def standardDeviation(history):
	average = calculateAverage(history)
	inner_sum = functools.reduce(lambda x, y: x + (y - average) ** 2, history, 0)
	return math.sqrt(inner_sum / len(history))

def rinaIndex(trades):
	profit = selectTotalNetProfit(trades)
	average_drawdown = averageDrawdown(trades)
	percent_time_active = percentTimeInMarket(trades)
	return profit / (average_drawdown * percent_time_active)

def averageDrawdown(trades):
	drawdowns = []

	high = trades[0].profit
	low = trades[0].profit

	for trade in trades:
		profit = trade.profit
		if(profit > high):
			if(high != low):
				drawdowns.append(high - low)
			high = profit
			low = profit
		if(profit < low): low = profit
	if(high != low):
		drawdowns.append(high - low)

	return sum(drawdowns) / len(drawdowns)

def percentTimeInMarket(trades):
	total = trades[-1].closingTime - trades[0].openingTime
	time_spent = functools.reduce(lambda x, y: x + (y.closingTime - y.openingTime), trades, 0)
	return 100 * time_spent / total

def selectTotalNetProfit(trades):
	profits = map(lambda x: x.profit, trades)
	average = calculateAverage(profits)
	triple_standard_deviation = 3 * standardDeviation(profits)
	counting_profits = filter(lambda x: math.fabs(x - average) <= triple_standard_deviation, profits)
	return sum(counting_profits)
