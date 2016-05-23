from sample import algorithms
from sample import utility
from sample import statistic
from sample import config
from sample import filemanager

def optimize(algorithm, data):
	test_size = len(data) // 4
	training = data[:-test_size]
	test = data[3 * test_size:]

	trainingResults = []
	testResults = []
	bestResult = None
	parameters = algorithm.getAllParameters()
	for parameter in parameters:
		print('Testing parameters: ', utility.dictionaryToString(parameter))
		strategy = utility.mergeDictionaries(config.strategy, parameters)
		result = algorithms.backtest(algorithm, training, strategy)
		test_result = algorithms.backtest(algorithm, test, strategy)
		if(bestResult is None or result > bestResult):
			bestResult = result
			bestStrategy = strategy
		trainingResults.append(result)
		testResults.append(test_result)
		print('Result: ', result, ', test: ', test_result)

	statistic.plotArrays([trainingResults, testResults])
	filemanager.writeStrategy(bestStrategy, 'strategies/optimized_strat.json')
