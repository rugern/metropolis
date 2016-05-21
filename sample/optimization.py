import algorithms

class WalkForward:
	algorithm = None
	data = None

	def optimize(self, algorithm, data):
		self.algorithm = algorithm
		self.data = data

		test_size = len(data) // 4
		training = data[:-test_size]
		test = data[3 * test_size:]

		parameters = [0] * len(algorithm.parameterNames)
		result, strategy = self.recursiveParameterTest(parameters, 0)

		self.reset()
		return strategy

	def recursiveParameterTest(self, parameters, index):
		if(None in [self.algorithm, self.data]) raise NotSetError('Values in WF not set!')

		if(index >= len(parameters)):
			names = self.algorithm.parameterNames
			strategy = {}
			for i in range(len(names)):
				strategy[names[i]] = parameters[i]
			return (algorithms.runAlgorithm(self.algorithm, strategy, self.data), strategy)

		increment = self.algorithm.increments[index]
		bestResult = None
		bestStrategy = None
		for i in range(1:11):
			parameters[index] = i * increment
			result, strategy = self.recursiveParameterTest(parameters, index + 1)
			if(bestResult == None or result > bestResult):
				bestResult = result
				bestStrategy = strategy
		return (bestResult, bestStrategy)

	def reset(self):
		self.algorithm = None
		self.data = None
