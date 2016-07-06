import itertools

from sample import configuration
from sample import engine as system

# Unexpected keyword arguments
#pylint: disable=E1123
# Wrong hanging indentation
#pylint: disable=C0330

def main(config, plot):
	engine = system.Engine()
	engine.addStrategy(config['strategy'](config))
	engine.addData(config['data'], config['startDate'], config['endDate'])
	engine.addBroker(config['broker'])
	engine.addSizer(config['sizer'])
	engine.run()
	if(plot): engine.plot()
	return

def optimize(config, plot):
	values = [value for key, value in config['optimize'].items()]
	for numbers in itertools.product(*values):
		config = configuration.getConfigFile('parameters/parameters.json')
		index = 0
		for key in config['optimize']:
			config[key] = numbers[index]
			index += 1
		main(config, plot)

if __name__ == '__main__':
	config = configuration.getConfigFile('parameters/parameters.json')
	print('Starting Portfolio Value: %.2f' % config['cash'])

	mode = config['mode']
	if(mode == 'optimize'):
		optimize(config, config['plot'])
	else:
		main(config, config['plot'])
