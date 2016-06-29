import functools

class KellySizer:

	def getSize(self, buy, sell):
		if(len(buy) == 0): return 0.2
		wins = 0
		profits = []
		for index in enumerate(buy):
			profits.append(sell[index] - buy[index])
			if(profits[-1] > 0): wins += 1

		if(wins == len(buy)): return 0.2
		p = wins / len(buy)
		average_win = functools.reduce(lambda x, y: x + y if y > 0 else x, profits, 0) / wins
		average_loss = functools.reduce(lambda x, y: x + y if y < 0 else x, profits, 0) / (len(buy) - wins)
		r = average_win / average_loss

		return p - (1 - p) / r
