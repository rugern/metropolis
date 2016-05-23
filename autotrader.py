import sys

from sample import filemanager
from sample import algorithms
from sample import bankroll
from sample import optimization
from sample import config
from sample import statistic

def main(strategy_path):
	excludedNames = ['.DS_Store']
	config.strategy = filemanager.readStrategy(strategy_path)
	config.bank = bankroll.Bank()

	data_path = config.strategy['data_path']
	mode = config.strategy['mode']
	data = filemanager.loadData(data_path, excludedNames)
	algorithm = getAlgorithm(config.strategy['algorithm'])

	if(mode == 'plot'): statistic.plotBollinger(data, config.strategy)
	elif(mode == 'backtest'): algorithms.backtest(algorithm, data, config.strategy)
	elif(mode == 'training'): optimization.optimize(algorithm, data)

def getAlgorithm(algorithm_name):
	if(algorithm_name == 'MA'): return algorithms.MovingAverages()
	elif(algorithm_name == 'BB'): return algorithms.BollingerBand()
	raise ValueError('Could not find the specified algorithm')

main(sys.argv[1])
