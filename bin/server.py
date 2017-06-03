import os
from os.path import isfile, join
import shutil
import numpy
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
import keras

from utility import readHdf, getFileList, getDirectoryList, createPaths
from train import train

app = Flask(__name__)
CORS(app)
socket = SocketIO(app)

baseFolder = 'data'
batchSize = 32

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
    maxLength = None
    for filename in filenames:
        shortName = ''.join(filename.split('.')[:-1])
        values = readHdf(join(path, filename))
        maxLength = values.shape[0]

        newMin = values.min()
        newMax = values.max()
        if newMin > 0 and newMax < 2:
            minValue = newMin if minValue is None or newMin < minValue else minValue
            maxValue = newMax if maxValue is None or newMax > maxValue else maxValue

        data[shortName] = {}
        data[shortName]['data'] = values.tolist()[offset:offset+limit]
    minValue = 0 if minValue is None else minValue.astype(numpy.float64)
    maxValue = 1 if maxValue is None else maxValue.astype(numpy.float64)
    return data, minValue, maxValue, maxLength

def backgroundEmitStatus(status):
    socket.emit('set_metropolis_status', status)

def emitStatus(status):
    socket.start_background_task(target=backgroundEmitStatus, status=status)

def incomingEvent(eventName):
    print('Incoming event: {}'.format(eventName))

@app.route('/datafiles/<datafile>/data')
def getData(datafile):
    incomingEvent('data')
    path = createPaths(baseFolder, datafile)
    offset = request.args.get('offset', 0, int)
    limit = request.args.get('limit', 200, int)

    data = {}
    data['indicators'], minValue, maxValue, maxLength = readData(path['indicator'], offset, limit)
    data['predictions'], _, _, _ = readData(path['prediction'], offset, limit)
    data['datasize'] = maxLength
    data['minValue'] = minValue
    data['maxValue'] = maxValue
    data['labels'] = list(range(offset, offset+limit))

    return jsonify(data), 200

@socket.on('start_train')
def startTrain(options):
    emitStatus('Busy')
    incomingEvent('start_train')
    train(**options)
    emitStatus('Finished training')

@app.route('/datafiles/<datafile>/models/<modelName>', methods=['DELETE'])
def deleteModel(datafile, modelName):
    incomingEvent('models/delete')

    path = createPaths(baseFolder, datafile, modelName)
    files = []
    allFiles = getFileList(path['prediction'])
    for fullName in allFiles:
        if fullName.split('-')[2] == '{}.h5'.format(modelName):
            files.append(join(path['prediction'], fullName))
    # files.append(join(path['prediction'], '{}-{}.h5'.format('ask', modelName)))

    dirs = []
    dirs.append(join(path['data'], 'models', modelName))

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
    return jsonify(getFileList(baseFolder, filetype='.h5')), 200

@app.route('/datafiles/<datafile>/models')
def getModels(datafile):
    incomingEvent('models')
    path = createPaths(baseFolder, datafile)
    return jsonify(getDirectoryList(join(path['data'], 'models'))), 200

if __name__ == '__main__':
    socket.run(app)
