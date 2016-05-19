def walkForward(history, strategy):
	fourth_length = len(history) // 4
	training = history[:3 * fourth_length]
	test = history[3 * fourth_length:]
	parameters = optimizeParameters(strategy, training)
	result = testStrategy(strategy, parameters, test)
	return result
