import itertools

import backtrader as bt

from sample import configuration

# Unexpected keyword arguments
#pylint: disable=E1123
# Wrong hanging indentation
#pylint: disable=C0330

def main(config, plot):
	cerebro = bt.Cerebro()
	cerebro.addstrategy(config['strategy'], config=config)
	cerebro.adddata(bt.feeds.PandasData(dataname=config['data'], datetime=None))
	cerebro.broker.setcash(config['cash'])
	cerebro.broker.setcommission(commission=config['commission'])
	cerebro.run()
	if(plot): cerebro.plot()
	return

if __name__ == '__main__':
	config = configuration.getConfigFile('parameters/parameters.json')
	mode = config['mode']

	print('Starting Portfolio Value: %.2f' % config['cash'])
	if(mode == 'optimize'):
		start, size = (), ()
		for key in config['optimize']:
			start += (config[key],)
			size += (config['optimize'][key],)
		for number in itertools.product(*[range(i, i + j) for i, j in zip(start, size)]):
			index = 0
			for key in config['optimize']:
				config[key] = number[index]
				index += 1
			main(config, config['plot'])
	else:
		main(config, config['plot'])
