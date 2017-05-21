import json
import os
from os import listdir
from os.path import isfile, join
import numpy
import h5py
from keras.layers import Input, Dense, LSTM, Dropout
from keras.models import Model
from keras.optimizers import sgd
import trading

def assertOrCreateDirectory(path):
    if not os.path.exists(path):
        print('Creating directory "{}"'.format(path))
        os.makedirs(path)

def normalize(inMatrix):
    scales = []
    matrix = inMatrix.copy()

    for index in range(matrix.shape[1]):
        columnMin = matrix[:, index].min()
        columnMax = matrix[:, index].max()
        matrix[:, index] = (matrix[:, index] - columnMin) / (columnMax - columnMin)
        scales.append((columnMin, columnMax))

    return matrix, scales

def inverse_normalize(inMatrix, scales):
    matrix = inMatrix.copy()

    for index in range(matrix.shape[1]):
        scale = scales[index]
        matrix[:, index] = matrix[:, index] * (scale[1] - scale[0]) + scale[0]

    return matrix

def loadWeights(model, name):
    name += '.h5'
    print('Loading saved model weights...')
    if os.path.isfile(name):
        model.load_weights(name)
    else:
        print('Sorry bro, could not find the weights file: {}'.format(name))

def createModel(
        optimizer='Nadam',
        dropout=0.05,
        neurons=180,
        activation='softplus',
        loss='logcosh',
):
    options = {
        'lookforward': 10,
        'features': 12,
        'outputs': 5,
    }

    # model = Sequential()
    # model.add(Dense(hiddenSize, input_dim=features, activation='relu'))
    # model.add(Dense(hiddenSize, activation='relu'))
    # model.add(Dense(features, activation='sigmoid'))
    # model.compile(sgd(lr=0.2), 'mse')

    # inputs = Input(shape=(inData.shape[1], inData.shape[2]))
    inputs = Input(shape=(options['lookforward'], options['features']))
    x = LSTM(options['features'])(inputs)
    x = Dropout(dropout)(x)
    x = Dense(neurons, activation=activation)(x)
    x = Dropout(dropout)(x)
    x = Dense(neurons, activation=activation)(x)
    x = Dropout(dropout)(x)
    outputs = Dense(options['outputs'], activation='sigmoid')(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    return model

def getFileList(path, filetype=None):
    if not os.path.exists(path):
        return []
    filenames = [name for name in listdir(path) if isfile(join(path, name))]
    if filetype is not None:
        filenames = list(filter(lambda filename: filetype in filename, filenames))
        filenames = list(map(lambda filename: ''.join(filename.split('.')[:-1]), filenames))
    return filenames

def getDirectoryList(path):
    if not os.path.exists(path):
        return []
    folderNames = [name for name in listdir(path) if not isfile(join(path, name))]
    return folderNames

def saveToHdf(filename, data):
    output = h5py.File(filename, 'w')
    output.create_dataset('data', data=data)
    output.close()

def readHdf(name, column=None):
    if not isfile(name):
        return []
    infile = h5py.File(name, 'r')
    data = infile['data'][:]
    if column is not None and data.shape[1] > column:
        data = data[:, column]
    infile.close()
    return data

def readJson(path):
    data = None
    with open(path, 'r') as infile:
        data = json.load(infile)
    return data

def writeJson(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)

def saveModel(model, outputName):
    if outputName is None:
        return
    print('Saving model weights...')
    model.save_weights(outputName + '.h5', overwrite=True)
    with open(outputName + '.json', 'w') as outfile:
        json.dump(model.to_json(), outfile)
    print('Finished saving model weights')

def splitTrainAndTest(values, datetimes=None):
    trainLength = round(len(values) * 0.7)
    train = values[:trainLength]
    test = values[trainLength:]

    trainDt = None
    testDt = None
    if datetimes is not None:
        trainDt = datetimes[:trainLength]
        testDt = datetimes[trainLength:]
    return train, test, trainDt, testDt

def takeEvery(values, interval):
    # Note to self: Offset mellom train og test er allerede tatt høyde for, derfor '-1'
    return values[interval-1::interval]

def splice(values, start, end):
    return values[start:end] if end != 0 else values[start:]

def correctData(inValues, offset, lookback):
    values = inValues.copy()
    correction = (len(values) - offset) % lookback
    return splice(values, offset, offset - correction)

def reshape(values, lookback):
    output = numpy.concatenate(
        tuple(values[i:lookback+i] for i in range(values.shape[0] - lookback + 1))
    )
    return output.reshape((-1, lookback, output.shape[1]))
    # return values.reshape((-1, lookback, values.shape[1]))

def saveIndicators(indicators, dt, path, prefix, names):
    stringLabelDt = numpy.array(dt, dtype=numpy.dtype('S48'))
    assertOrCreateDirectory(path['indicator'])
    saveToHdf(join(path['base'], 'datetimes.h5'), stringLabelDt)
    for index in range(indicators.shape[1]):
        saveToHdf(join(
            path['indicator'],
            '{}-{}.h5'.format(prefix, names[index])
        ), indicators[:, index])

def createData(raw, lookback, lookforward, path=None, prefix=None, save=False):
    # 1. Dra ut datetime og values
    datetimes = raw.index.values
    rawValues = raw.values

    # 3. Lag indikatordata, fjern NaN
    rawValues, datetimes, names = trading.createIndicators(rawValues, datetimes)

    # 2. normaliser values
    values, scales = normalize(rawValues)

    # 4. splitTrainAndTest
    train, test, _, testDt = splitTrainAndTest(values, datetimes)
    _, testRaw, _, _ = splitTrainAndTest(rawValues)

    # 5. For hver av train og test:
    dataset = {
        'scales': scales
    }

    trainData = splice(reshape(train, lookback), 0, -lookforward)
    testData = splice(reshape(test, lookback), 0, -lookforward)

    trainLabels = numpy.column_stack([
        splice(train, lookback + i, i - lookforward + 1)[:, 3]
        for i in range(0, lookforward)
    ])
    testLabels = numpy.column_stack([
        splice(test, lookback + i, i - lookforward + 1)[:, 3]
        for i in range(0, lookforward)
    ])

    dt = splice(testDt, lookback + lookforward - 1, -lookforward + 1)
    indicators = splice(testRaw, lookback + lookforward - 1, -lookforward + 1)

    assert len(trainData) == len(trainLabels)
    assert len(testData) == len(testLabels)
    assert len(dt) == len(indicators)

    if save:
        saveIndicators(indicators, dt, path, prefix, names)

    dataset['train'] = {
        'data': trainData,
        'labels': trainLabels,
    }
    dataset['test'] = {
        'data': testData,
        'labels': testLabels,
    }
    dataset['indicators'] = indicators
    dataset['dt'] = dt

    # 6. returner train og test, med data og labels
    return dataset

def createPaths(base, dataName, modelName=None):
    paths = {
        'base': join(base, dataName),
        'prediction': join(base, dataName, 'predictions'),
        'indicator': join(base, dataName, 'indicators'),
        'model': '',
    }
    if modelName is not None:
        paths['model'] = join(base, dataName, 'models', modelName)
    # if dataName != '' and modelName != '':
        # for key in paths:
            # assertOrCreateDirectory(paths[key])
    return paths
