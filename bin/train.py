from os.path import join
import pandas

from data import createData, saveIndicators
from model import saveModel, loadModel
from utility import createPaths
from predictions import createPredictions

def train(**kwargs):
    options = {
        'epochs': 5,
        'datafile': 'EUR_USD_2017_10-3_30m',
        'model': 'Test',
        'prefix': 'bid',
        'batchSize': 32,
        'baseFolder': 'data',
    }
    for key in kwargs:
        options[key] = kwargs[key]

    path = createPaths(options['baseFolder'], options['datafile'], options['model'])
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(options['datafile'])))

    bid = createData(raw['Bid'])
    saveIndicators(bid['testX'], path, options['prefix'], bid['names'])

    features = bid['trainX'].shape[2]
    outputs = bid['trainY'].shape[1]
    bidModel = loadModel(path, features=features, outputs=outputs)
    for i in range(options['epochs']):
        bidModel.fit(
            x=bid['trainX'],
            y=bid['trainY'],
            batch_size=options['batchSize'],
            shuffle=False,
            validation_data=(bid['testX'], bid['testY'])
        )
        bidModel.reset_states()
        print('Finished epoch {}/{}'.format(i + 1, options['epochs']))
    
    evaluation = bidModel.evaluate(bid['testX'], bid['testY'], batch_size=options['batchSize'])
    print('\nLoss: {} | Accuracy: {}'.format(evaluation[0], evaluation[1]))

    saveModel(bidModel, join(path['model'], options['prefix']))

    createPredictions(
        bidModel, bid, path,
        prefix='pred',
        batchSize=options['batchSize']
    )

if __name__ == '__main__':
    train()
