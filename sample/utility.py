import pandas

def convertToRegularTime(datetime):
	hours = datetime.seconds // 3600
	minutes = (datetime.seconds % 3600) // 60
	seconds = datetime.seconds % 60
	return (hours, minutes, seconds)

def arrayToString(array):
	return '{0}'.format(', '.join(map(lambda x: str(x), array)))

def dictionaryToString(dictionary):
	strings = []
	for key in dictionary:
		strings.append('{0}:{1}'.format(key, dictionary[key]))
	return ', '.join(strings)

def mergeDictionaries(base, overwrites):
	for key in overwrites:
		base[key] = overwrites[key]
	return base

def datetimeToString(dt):
	time = pandas.to_datetime(str(dt))
	string = time.strftime('%H:%M')
	return string
