def convertToRegularTime(datetime):
	hours = datetime.seconds // 3600
	minutes = (datetime.seconds % 3600) // 60
	seconds = datetime.seconds % 60
	return (hours, minutes, seconds)
