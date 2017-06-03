import sys
from os.path import join
import itertools
from pprint import pformat
import click

from data import readDataFiles
from bank import Bank
from actions import SHORT, LONG
from strategies import emaShort, emaLong
from trading import appendIndicators

def gridsearch(gridParams, data, shortStrat, longStrat, log=print, **kwargs):
    labels = []
    paramsMatrix = []
    for key, elem in gridParams.items():
        labels.append(key)
        paramsMatrix.append(elem)

    combinations = itertools.product(*paramsMatrix)
    best = {}
    results = []
    for combination in combinations:
        params = {}
        for i, elem in enumerate(combination):
            params[labels[i]] = elem
            kwargs[labels[i]] = elem

        result = test(data, shortStrat, longStrat, **kwargs)

        result['params'] = params
        if 'profit' not in best or result['profit'] > best['profit']:
            best = result
        results.append(result)

    log('Best result:')
    log(pformat(best))
    log('All results:')
    log(pformat(results))

def getSize(data):
    size = -1
    for currency, datasets in data.items():
        for dataset, prices in datasets.items():
            currentSize = prices.shape[0]
            if size == -1:
                size = currentSize
            if size != currentSize:
                print('{}.{} had the wrong size!'.format(currency, dataset))
                sys.exit(1)
    return size

def initializeOrders(data):
    orders = {}
    for key, value in data.items():
        orders[key] = []
    return orders

def test(data, shortStrat, longStrat, **kwargs):
    options = {
        'buySize': 0.065,
        'leverage': 10,
    }
    for key, value in kwargs.items():
        options[key] = value

    buyAmount = options['startMoney'] * options['buySize'] / options['leverage']
    bank = Bank(options['startMoney'])
    orders = initializeOrders(data)
    size = getSize(data)

    for i in range(size):
        for currency, prices in data.items():
            for j in range(len(orders[currency]) - 1, -1, -1):
                if longStrat(prices['ask'], i, orders[currency][j].entryIndex, **options) == LONG:
                    bank.closeOrder(prices['ask'][i, 3], orders[currency][j])
                    del orders[currency][j]
            if shortStrat(prices['bid'], i, **options) == SHORT:
                order = bank.openOrder(prices['bid'][i, 3], i, buyAmount, **options)
                if order is not None:
                    orders[currency].append(order)

    
    result = {
        'buys': bank.buys,
        'sells': bank.sells,
    }
    for currency, orders in orders.items():
        for order in orders:
            bank.closeOrder(prices['ask'][-1, 3], order)
    result['profit'] = '{}%'.format((100 * bank.funds / kwargs['startMoney']) - 100)
    return result

@click.command()
@click.option('--money', default=10000, help='Set amount of EUR to start with')
def main(money):
    options = {
        'startMoney': money,
        'batchSize': 32,
        'log': print,
    }
    # data = readDataFiles(pattern='2017_3-5_15m')
    data = readDataFiles(pattern='2017_03-05_15min')
    data = appendIndicators(data)

    stopLoss = [0.0001, 0.00005, 0.00001]
    takeProfit = [0.0005, 0.0001, 0.00005]
    buySize = [0.08, 0.075, 0.07, 0.065, 0.06]
    leverage = [10, 20, 40, 50]

    gridParams = dict(
        # stopLoss=stopLoss,
        # takeProfit=takeProfit,
        buySize=buySize,
        # leverage=leverage,
    )

    gridsearch(gridParams, data, emaShort, emaLong, **options)

if __name__ == '__main__':
    main()
