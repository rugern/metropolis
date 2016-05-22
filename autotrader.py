import sys
from matplotlib import pyplot
import math

from sample import filemanager
from sample import algorithms
from sample import bankroll
from sample import optimization
from sample import config
from sample import utility
from sample import statistic

def main(data_path, strategy_path, training):
	excludedNames = ['.DS_Store']

	config.bank = bankroll.Bank()
	config.strategy = filemanager.readStrategy(strategy_path)
	data = filemanager.loadData(data_path, excludedNames)
	# optimizeStrategy(data) if training else testAlgorithm(data)
	statistic.plotBollinger(data, config.strategy)

def testAlgorithm(data):
	algorithm = getAlgorithm(config.strategy['algorithm'])
	algorithms.backtest(algorithm, config.strategy, data)

def optimizeStrategy(data):
	algorithm = getAlgorithm(config.strategy['algorithm'])
	optimizer = getOptimizer(config.strategy['optimization'])

	optimizedStrategy = optimizer.optimize(algorithm, data)
	optimizedStrategy = utility.mergeDictionaries(config.strategy, optimizedStrategy)
	filemanager.writeStrategy(optimizedStrategy, 'strategies/optimized_strat.json')

def getAlgorithm(algorithm_name):
	algorithm = 0
	if(algorithm_name == 'MA'): algorithm = algorithms.MovingAverages()
	elif(algorithm_name == 'BB'): algorithm = algorithms.BollingerBand()
	return algorithm

def getOptimizer(optimizer_name):
	optimizer = 0
	if(optimizer_name == 'WFA'): optimizer = optimization.WalkForward()
	return optimizer

def printStats(profits):
	total = sum(profits)
	print("Profit sum: ", total)

def drawPlot(data):
	pyplot.plot(data)
	pyplot.show()

mode = sys.argv[1]
data_path = strategy_path = training = None
if(mode == 'default'):
	data_path = 'data/15min/EUR_USD/2016/'
	strategy_path = 'strategies/strategy.json'
	training = True

main(data_path, strategy_path, training)
