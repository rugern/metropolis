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
	engine.addData(config['data'])
	engine.addBroker(config['broker'])
	engine.addSizer(config['sizer'])
	engine.run()
	if(plot): engine.plot()
	return

def optimize(config, plot):
	start, size = (), ()
	for key in config['optimize']:
		start += (config[key],)
		size += (config['optimize'][key],)
	for number in itertools.product(*[range(i, i + j) for i, j in zip(start, size)]):
		index = 0
		for key in config['optimize']:
			config[key] = number[index]
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
