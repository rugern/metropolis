import functools
import trade

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
