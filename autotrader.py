import backtrader as bt

from sample import config

# Unexpected keyword arguments
#pylint: disable=E1123
# Wrong hanging indentation
#pylint: disable=C0330

def main(long_interval, short_interval, plot=False):
	cerebro = bt.Cerebro()
	cerebro.addstrategy(config.strategy, long_interval=long_interval, short_interval=short_interval)
	cerebro.adddata(bt.feeds.PandasData(dataname=config.data, datetime=None))
	cerebro.broker.setcash(config.cash)
	cerebro.broker.setcommission(commission=config.commission)

	cerebro.run()
	if(plot): cerebro.plot()
	return

if __name__ == '__main__':
	mode = 'backtest'

	config.initialize('strategies/strategy.json')
	print('Starting Portfolio Value: %.2f' % config.cash)
	if(mode == 'backtest'):
		for i in range(20, 25):
			main(i, config.sma_short_interval)
	else:
		main(config.sma_long_interval, config.sma_short_interval, True)
