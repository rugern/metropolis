from os.path import join
from pprint import pformat
import pandas
import numpy
import itertools

from utility import createPaths
from data import createData
from bank import Bank
from actions import BUY, SELL
from strategies import emaEntry, emaExit

def gridsearch(gridParams, entry, exit, log=print, **kwargs):
    labels = []
    paramsMatrix = []
    for key, elem in gridParams.items():
        labels.append(key)
        paramsMatrix.append(elem)

    combinations = itertools.product(*paramsMatrix)
    best = None
    results = []
    for combination in combinations:
        params = {}
        for i, elem in enumerate(combination):
            params[labels[i]] = elem
            kwargs[labels[i]] = elem

        result = test(entry, exit, **kwargs)

        result['params'] = params
        if best is None or result['profit'] > best['profit']:
            best = result.copy()
        del result['stayMoney']
        del result['relativeProfit']
        results.append(result)

    log('Best result:')
    log(pformat(best))
    log('All results:')
    log(pformat(results))

def test(entry, exit, **kwargs):
    options = {
        'buySize': 0.02,
    }
    for key, value in kwargs.items():
        options[key] = value

    startMoney = options['startMoney']
    bank = Bank(startMoney)
    bidClose = options['bid'][:, 3]
    askClose = options['ask'][:, 3]
    orders = []
    for i in range(bidClose.shape[0]):
        for j in range(len(orders) - 1, -1, -1):
            if exit(orders[j].entryIndex, i, **options) == SELL:
                bank.closeOrder(bidClose[i], orders[j])
                del orders[j]
        if entry(i, **options) == BUY:
            orders.append(bank.openOrder(askClose[i], options['buySize'], i))

    endMoney = bank.getResult(bidClose[-1])
    stayMoney = startMoney * bidClose[-1] / askClose[0]
    result = {
        'stayMoney': stayMoney,
        'buys': bank.buys,
        'sells': bank.sells,
        'profit': '{}%'.format((100 * endMoney / startMoney) - 100),
        'relativeProfit': '{}%'.format((100 * endMoney / stayMoney) - 100),
    }
    return result

if __name__ == '__main__':
    datafile = 'EUR_USD_2017_10-3_30m'
    modelName = 'Test'
    baseFolder = 'data'
    prefix = 'bid'
    path = createPaths(baseFolder, datafile, modelName)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))
    bid = numpy.squeeze(createData(raw['Bid'])['testX'][:, -1, :])
    ask = numpy.squeeze(createData(raw['Ask'])['testX'][:, -1, :])

    # model = createModel()
    # loadWeights(model, join(path['model'], prefix))
    # predictions = createPredictions(
        # model, bid, path,
        # prefix='pred',
        # batchSize=batchSize
    # )

    options = {
        'startMoney': 10000,
        'batchSize': 32,
        'bid': bid,
        'ask': ask,
        'log': print,
    }

    stopLoss = [0.00015, 0.0001, 0.00005]
    takeProfit = [0.01, 0.005, 0.001]
    buySize = [0.025, 0.02, 0.015]

    gridParams = dict(
        stopLoss=stopLoss,
        takeProfit=takeProfit,
        buySize=buySize,
    )

    gridsearch(gridParams, emaEntry, emaExit, **options)
