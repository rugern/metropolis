import os
from os.path import isfile, join
import shutil
import numpy
import pandas
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import keras

import utility
from utility import readHdf, getFileList, getDirectoryList
from bank import Bank
from predictions import createPredictions

app = Flask(__name__)
CORS(app)
socket = SocketIO(app)

lookback = 20
lookforward = 5
baseFolder = 'data'

class KerasLogger(keras.callbacks.Callback):
    def __init__(self, eventName):
        super().__init__()
        self.eventName = eventName
        self.samples = None
        self.seen = None
        self.epochs = None
        self.batchSize = None

    def __call__(self, message):
        socket.start_background_task(target=self.log, message=message)

    def log(self, message):
        socket.emit(self.eventName, message)

    def on_epoch_begin(self, epoch, logs=None):
        self.samples = self.params['samples']
        self.seen = 0
        self.__call__('Epoch {}/{}'.format(epoch + 1, self.epochs))

    def on_epoch_end(self, epoch, logs=None):
        self.__call__('Loss: {}'.format(logs['loss']))

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        # batchSize = logs.get('size', 0)
        # self.seen += batchSize
        # self.__call__('Progress: {}/{}'.format(self.seen, self.samples))
        pass


    def on_train_begin(self, logs=None):
        self.epochs = self.params['epochs']
        self.batchSize = self.params['batch_size']
        self.__call__('Train begin')
        self.__call__('Batch size: {}'.format(self.batchSize))


    def on_train_end(self, logs=None):
        self.__call__('Train end')

def calculateDatetimeRange(start, end, dt):
    offset = dt.index(min(dt, key=lambda x: abs(x - start)))
    limit = dt.index(min(dt, key=lambda x: abs(x - end))) - offset
    return offset, limit

def readData(path, offset, limit):
    data = {}
    filenames = getFileList(path)
    minValue = None
    maxValue = None
    for filename in filenames:
        shortName = ''.join(filename.split('.')[:-1])
        values = readHdf(join(path, filename))

        newMin = values.min()
        newMax = values.max()
        if newMin > 0 and newMax < 2:
            minValue = newMin if minValue is None or newMin < minValue else minValue
            maxValue = newMax if maxValue is None or newMax > maxValue else maxValue

        data[shortName] = {}
        data[shortName]['data'] = values.tolist()[offset:offset+limit]
    minValue = 0 if minValue is None else minValue.astype(numpy.float64)
    maxValue = 1 if maxValue is None else maxValue.astype(numpy.float64)
    return data, minValue, maxValue

def backgroundEmitStatus(status):
    socket.emit('set_metropolis_status', status)

def emitStatus(status):
    socket.start_background_task(target=backgroundEmitStatus, status=status)

def incomingEvent(eventName):
    print('Incoming event: {}'.format(eventName))

@app.route('/datafiles/<datafile>/data')
def getData(datafile):
    incomingEvent('data')
    path = utility.createPaths(baseFolder, datafile)
    datetimes = numpy \
        .array(readHdf(join(path['data'], 'datetimes.h5')), dtype='datetime64[m]') \
        .tolist()
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 200, int)
    offset = max(0, offset)
    limit = min(len(datetimes) - offset, limit)

    labels = numpy.array(datetimes, dtype=numpy.dtype('str')).tolist()[offset:offset+limit]

    data = {}
    data['labels'] = labels
    data['indicators'], minValue, maxValue = readData(path['indicator'], offset, limit)
    data['predictions'], _, _ = readData(path['prediction'], offset, limit)
    data['datasize'] = len(datetimes)
    data['minValue'] = minValue
    data['maxValue'] = maxValue

    return jsonify(data), 200

def trainModel(dataset, logger, **kwargs):
    path = kwargs['path']
    prefix = kwargs['prefix']
    epochs = kwargs['epochs']

    trainData = dataset['train']['data']
    trainLabels = dataset['train']['labels']

    modelPath = join(path['model'], prefix)
    utility.assertOrCreateDirectory(path['model'])
    model = utility.createModel(features=trainData.shape[2])
    utility.loadWeights(model, modelPath)

    model.fit(trainData, trainLabels, epochs=epochs, batch_size=32, callbacks=[logger])
    utility.saveModel(model, modelPath)
    return model


@socket.on('start_train')
def train(options):
    emitStatus('Busy')
    incomingEvent('start_train')
    logger = KerasLogger('add_metropolis_info')

    epochs = options['epochs']
    datafile = options['datafile']
    modelName = options['model']
    prefix = 'bid'

    path = utility.createPaths(baseFolder, datafile, modelName)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))
    rawBid = raw['Bid']
    # rawAsk = raw['Ask']

    bid = utility.createData(rawBid, lookback, lookforward, path, prefix, True)
    # ask = utility.createData(rawAsk, path, 'ask', 5)

    bidModel = trainModel(bid, logger, path=path, prefix=prefix, epochs=epochs)
    # askModel = trainModel(ask, path, 'ask', logger)

    createPredictions(bidModel, bid, path, modelName, prefix)
    # createPredictions(askModel, ask, path, name, 'ask')

    emitStatus('Finished training')

@app.route('/datafiles/<datafile>/models/<modelName>', methods=['DELETE'])
def deleteModel(datafile, modelName):
    incomingEvent('models/delete')

    path = utility.createPaths(baseFolder, datafile, modelName)
    files = []
    allFiles = getFileList(path['prediction'])
    for fullName in allFiles:
        if fullName.split('-')[2] == '{}.h5'.format(modelName):
            files.append(join(path['prediction'], fullName))
    # files.append(join(path['prediction'], '{}-{}.h5'.format('ask', modelName)))

    dirs = []
    dirs.append(join(path['base'], 'models', modelName))

    for filename in files:
        if not isfile(filename):
            print('Could not find filename: {}'.format(filename))
            continue
        os.remove(filename)

    for dirname in dirs:
        if not os.path.exists(dirname):
            print('Could not find directory: {}'.format(dirname))
            continue
        shutil.rmtree(dirname)
    return '', 200

@app.route('/datafiles')
def getDatafiles():
    incomingEvent('datafiles')
    return jsonify(getFileList(baseFolder, '.h5')), 200

@app.route('/datafiles/<datafile>/models')
def getModels(datafile):
    incomingEvent('models')
    path = utility.createPaths(baseFolder, datafile)
    return jsonify(getDirectoryList(join(path['base'], 'models'))), 200

@socket.on('start_test')
def marketTest(options):
    incomingEvent('start_test')
    emitStatus('Busy')
    logger = KerasLogger('add_metropolis_info')

    datafile = options['datafile']
    modelName = options['model']
    prefix = 'bid'

    path = utility.createPaths(baseFolder, datafile, modelName)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))

    bid = utility.createData(raw['Bid'], lookback, lookforward)
    ask = utility.createData(raw['Ask'], lookback, lookforward)

    model = utility.createModel()
    utility.loadWeights(model, join(path['model'], prefix))

    predictions = createPredictions(model, bid, path, modelName, prefix)

    bidClose = bid['indicators'][:, 3]
    askClose = ask['indicators'][:, 3]

    averageSpread = numpy.average(askClose - bidClose)
    print('Average spread: {}'.format(averageSpread))
    difference = numpy.transpose(numpy.transpose(predictions) - bidClose)
    assert len(difference) == len(askClose) == len(bidClose)

    startMoney = 10000
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

    emitStatus('Finished testing')
    emit('set_test_result', data)

if __name__ == '__main__':
    socket.run(app)
