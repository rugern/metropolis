import sys

import backtrader as bt

from sample import filemanager
from sample import config

def main(strategy_path):
	config.strategy = filemanager.readStrategy(strategy_path)
	data_path = config.strategy['data_path']
	mode = config.strategy['mode']
	data = filemanager.loadData(data_path)

	cerebro = bt.Cerebro()
	cerebro.broker.setcash(100000.0)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())


if __name__ == '__main__':
	main(sys.argv[1])
