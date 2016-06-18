import backtrader as bt

from sample import config

# Unexpected keyword arguments
#pylint: disable=E1123

def main(mode):
	cerebro = bt.Cerebro()
	config.initialize('strategies/strategy.json')
	data = bt.feeds.PandasData(dataname=config.data, datetime=None)

	cerebro.adddata(data)
	cerebro.broker.setcash(config.cash)
	cerebro.broker.setcommission(commission=config.commission)
	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

	if(mode == 'backtest'):
		cerebro.optstrategy(config.strategy, long_interval=range(10, 31))
	else:
		cerebro.addstrategy(config.strategy, long_interval=config.sma_long_interval)

	cerebro.run()
	cerebro.plot()
	return

if __name__ == '__main__':
	main('backtest')
