from sample import algorithms
from sample import utility

class WalkForward:
	algorithm = None
	data = None

	def optimize(self, algorithm, data):
		self.algorithm = algorithm
		self.data = data

		test_size = len(data) // 4
		training = data[:-test_size]
		test = data[3 * test_size:]

		parameter_combinations = algorithm.availableParameters(3)
		result, strategy = self.testParameters(parameter_combinations)

		self.reset()
		return strategy

	def testParameters(self, parameter_combinations):
		if(None in [self.algorithm, self.data]): raise ValueError('Values in WF not set!')

		bestResult = None
		bestStrategy = None

		for parameters in parameter_combinations:
			names = self.algorithm.parameterNames
			strategy = {}
			for i in range(len(names)):
				strategy[names[i]] = parameters[i]
			print('Testing parameters: ', utility.arrayToString(parameters))

			result = algorithms.testAlgorithm(self.algorithm, strategy, self.data)
			if(bestResult == None or result > bestResult):
				bestResult = result
				bestStrategy = strategy

		return bestResult, bestStrategy

	def recursiveParameterTest(self, parameters, index):
		if(None in [self.algorithm, self.data]): raise ValueError('Values in WF not set!')

		if(index >= len(parameters)):
			names = self.algorithm.parameterNames
			strategy = {}
			for i in range(len(names)):
				strategy[names[i]] = parameters[i]
			print('Testing parameters: ', utility.arrayToString(parameters))
			return (algorithms.testAlgorithm(self.algorithm, strategy, self.data), strategy)

		increment = self.algorithm.increments[index]
		bestResult = None
		bestStrategy = None
		for i in range(10):
			parameters[index] += i * increment
			result, strategy = self.recursiveParameterTest(parameters, index + 1)
			if(bestResult == None or result > bestResult):
				bestResult = result
				bestStrategy = strategy
		return (bestResult, bestStrategy)

	def reset(self):
		self.algorithm = None
		self.data = None
