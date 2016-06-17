import backtrader as bt

from sample import configuration

def main():
	cerebro = bt.Cerebro()

	config = configuration.Config('strategies/strategy.json')
	data = bt.feeds.PandasData(dataname=config.data, datetime=None)

	cerebro.adddata(data)
	cerebro.broker.setcash(config.cash)
	cerebro.addstrategy(config.strategy)

	print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()
	print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

	return

if __name__ == '__main__':
	main()
