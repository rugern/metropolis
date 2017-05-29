from os.path import join
from pprint import pformat
import pandas
import numpy

from utility import createPaths
from data import createData
from model import createModel, loadWeights
from predictions import createPredictions
from bank import Bank
from actions import BUY, SELL
from strategies import emaEntry, emaExit

batchSize = 32

def test(entryStrategy, exitStrategy, logger, **kwargs):
    prefix = 'bid'
    baseFolder = kwargs['baseFolder']
    datafile = kwargs['datafile']
    modelName = kwargs['modelName']
    startMoney = kwargs['startMoney']
    buySize = kwargs['buySize']
    batchSize = kwargs['batchSize']

    path = createPaths(baseFolder, datafile, modelName)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))

    bid = createData(raw['Bid'])
    ask = createData(raw['Ask'])

    model = createModel()
    loadWeights(model, join(path['model'], prefix))

    predictions = createPredictions(
        model, bid['testX'], path,
        prefix='pred',
        batchSize=batchSize
    )

    bidClose = numpy.squeeze(bid['testX'][:, 1, 3])
    askClose = numpy.squeeze(ask['testX'][:, 1, 3])

    bank = Bank(startMoney)
    samples = bidClose.shape[0]
    printInterval = samples // 10
    orders = []
    for i in range(samples):
        for j in range(len(orders) - 1, -1, -1):
            if exitStrategy(bidClose, predictions, orders[j].entryIndex, i) == SELL:
                bank.closeOrder(bidClose[i], orders[j])
                del orders[j]
        if entryStrategy(askClose, predictions, i) == BUY:
            orders.append(bank.openOrder(askClose[i], buySize, i))
        if i % printInterval == 0:
            logger('Market test: {}/{}'.format(i, samples))

    data = {
        'startMoney': startMoney,
        'endMoney': bank.getResult(bidClose[-1]),
        'stayMoney': startMoney * bidClose[-1] / askClose[0],
        'buys': bank.buys,
        'sells': bank.sells,
    }
    data['profit'] = '{}%'.format(100 * data['endMoney'] / startMoney)
    data['relativeProfit'] = '{}%'.format(100 * data['endMoney'] / data['stayMoney'])
    logger(pformat(data))

if __name__ == '__main__':
    options = {
        'datafile': 'EUR_USD_2017_10-3_30m',
        'modelName': 'Test',
        'baseFolder': 'data',
        'startMoney': 10000,
        'buySize': 0.02,
        'batchSize': 32,
    }

    test(emaEntry, emaExit, print, **options)
