from os.path import join
from pprint import pformat
import numpy
import pandas

from utility import createPaths
from data import createData
from model import createModel, loadWeights
from predictions import createPredictions
from bank import Bank
from actions import BUY, HOLD, SELL
from order import Order

lookback = 20
lookforward = 5

def test(logger, **kwargs):
    prefix = 'bid'
    baseFolder = kwargs['baseFolder']
    datafile = kwargs['datafile']
    modelName = kwargs['modelName']
    startMoney = kwargs['startMoney']

    path = createPaths(baseFolder, datafile, modelName)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))

    bid = createData(raw['Bid'], lookback, lookforward)
    ask = createData(raw['Ask'], lookback, lookforward)

    model = createModel()
    loadWeights(model, join(path['model'], prefix))

    predictions = createPredictions(model, bid, path, modelName, prefix)

    bidClose = bid['indicators'][:, 3]
    askClose = ask['indicators'][:, 3]

    averageSpread = numpy.average(askClose - bidClose)
    print('Average spread: {}'.format(averageSpread))
    difference = numpy.transpose(numpy.transpose(predictions) - bidClose)
    assert len(difference) == len(askClose) == len(bidClose)

    bank = Bank(startMoney)
    samples = difference.shape[0]
    dimension = difference.shape[1]
    printInterval = samples // 10
    for i in range(samples):
        buy = False
        sell = False
        total = 0
        for j in range(dimension):
            total += difference[i, j]
            if total > averageSpread:
                buy = True
                break
            elif total < -1 * averageSpread:
                sell = True
        if buy:
            bank.buy(askClose[i])
        elif sell:
            bank.sell(bidClose[i])
        if i % printInterval == 0:
            logger('Market test: {}/{}'.format(i, samples))


    data = {
        'startMoney': startMoney,
        'endMoney': bank.getResult(bidClose[-1]),
        'stayMoney': startMoney * bidClose[-1] / askClose[0],
        'buys': bank.getBuys(),
        'sells': bank.getSells(),
    }
    logger(pformat(data))

if __name__ == '__main__':
    options = {
        'datafile': 'EUR_USD_2017_10-3_30m',
        'modelName': 'Test',
        'baseFolder': 'data',
        'startMoney': 10000,
    }

    test(print, **options)
