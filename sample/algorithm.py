import metrics

def movingAverage(history, interval):
	total = metrics.calculateAverage(history[-interval:])
	return total / interval

def movingAverages(history, span):
	averages = []
	for i in range(span):
		averages.append(movingAverage(history[:-span + i + 1], span))
	return averages

def bollingerBand(history, interval):
	middle_band = movingAverages(history, interval)
	double_standard_deviation = 2 * metrics.standardDeviation(middle_band)
	upper_band = [x + double_standard_deviation for x in middle_band]
	lower_band = [x - double_standard_deviation for x in middle_band]
	return (upper_band, middle_band, lower_band)
