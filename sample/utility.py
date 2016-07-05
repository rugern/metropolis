import pandas

def convertToRegularTime(datetime):
	hours = datetime.seconds // 3600
	minutes = (datetime.seconds % 3600) // 60
	seconds = datetime.seconds % 60
	return (hours, minutes, seconds)

def arrayToString(array):
	return '{}'.format(', '.join(map(lambda x: str(x), array)))

def dictionaryToString(dictionary):
	strings = []
	for key in dictionary:
		strings.append('{}:{}'.format(key, dictionary[key]))
	return ', '.join(strings)

def mergeDictionaries(base, overwrites):
	for key in overwrites:
		base[key] = overwrites[key]
	return base

def datetimeToString(dt):
	time = pandas.to_datetime(str(dt))
	string = time.strftime('%d.%mT%H:%M')
	return string
