import backtrader as bt

from sample import config

# Unexpected keyword arguments
#pylint: disable=E1123
# Wrong hanging indentation
#pylint: disable=C0330

def main(mode):
	cerebro = bt.Cerebro()
	if(mode == 'backtest'):
		cerebro.optstrategy(config.strategy, long_interval=range(20, 25), short_interval=range(2, 5))
	else:
		cerebro.addstrategy(config.strategy, long_interval=config.sma_long_interval, short_interval=config.sma_short_interval)

	cerebro.adddata(bt.feeds.PandasData(dataname=config.data, datetime=None))
	cerebro.broker.setcash(config.cash)
	cerebro.broker.setcommission(commission=config.commission)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()
	cerebro.plot()
	return

if __name__ == '__main__':
	config.initialize('strategies/strategy.json')
	main('backtest')
