class Trade:
	profit = 0
	openingTime = 0
	closingTime = 0

	def spentTime(self):
		difference = closingTime - openingTime
		hours = difference.seconds // 3600
		minutes = (difference.seconds % 3600) // 60
		seconds = difference.seconds % 60
		return (hours, minutes, seconds)
