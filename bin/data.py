from os.path import join
import numpy

from utility import assertOrCreateDirectory, saveToHdf
from trading import createIndicators

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

def reshape(values, lookback):
    output = numpy.concatenate(
        tuple(values[i:lookback+i] for i in range(values.shape[0] - lookback + 1))
    )
    return output.reshape((-1, lookback, output.shape[1]))

def saveIndicators(data, path, prefix, names):
    # stringLabelDt = numpy.array(dt, dtype=numpy.dtype('S48'))
    # saveToHdf(join(path['data'], 'datetimes.h5'), stringLabelDt)
    assertOrCreateDirectory(path['indicator'])
    for index in range(data.shape[2]):
        saveToHdf(join(
            path['indicator'],
            '{}-{}.h5'.format(prefix, names[index])
        ), numpy.squeeze(data[:data.shape[0] - 1, data.shape[1] - 1, index]))

# def alternativeCreateData(raw, lookback, lookforward, path=None, prefix=None, save=False):
    # # 1. Dra ut datetime og values
    # rawValues = raw.values

    # # 3. Lag indikatordata, fjern NaN
    # rawValues, names = createIndicators(rawValues)

    # # 2. normaliser values
    # values, scales = normalize(rawValues)

    # # 4. splitTrainAndTest
    # train, test = splitTrainAndTest(values)
    # _, testRaw = splitTrainAndTest(rawValues)

    # # 5. For hver av train og test:
    # trainData = splice(reshape(train, lookback), 0, -lookforward)
    # testData = splice(reshape(test, lookback), 0, -lookforward)

    # labelColumn = 6
    # trainLabels = numpy.column_stack([
        # splice(train, lookback + i, i - lookforward + 1)[:, labelColumn]
        # for i in range(0, lookforward)
    # ])
    # testLabels = numpy.column_stack([
        # splice(test, lookback + i, i - lookforward + 1)[:, labelColumn]
        # for i in range(0, lookforward)
    # ])

    # indicators = splice(testRaw, lookback + lookforward - 1, -lookforward + 1)

    # assert len(trainData) == len(trainLabels)
    # assert len(testData) == len(testLabels)

    # if save:
        # saveIndicators(indicators, path, prefix, names)

    # dataset = {
        # 'scales': scales
    # }
    # dataset['train'] = {
        # 'data': trainData,
        # 'labels': trainLabels,
    # }
    # dataset['test'] = {
        # 'data': testData,
        # 'labels': testLabels,
    # }
    # dataset['indicators'] = indicators
    # dataset['labelColumn'] = labelColumn

    # # 6. returner train og test, med data og labels
    # return dataset

def createDataAndLabels(data, batchSize):
    length = data.shape[0] - round((data.shape[0] - 1) % batchSize)
    return data[:length - 1], numpy.squeeze(data[1:length])

def splitTrainAndTest(data, ratio):
    splitIndex = round(data.shape[0] * ratio)
    return data[:splitIndex], data[splitIndex:]

def createData(raw, **kwargs):
    options = {
        'batchSize': 32,
    }
    for key in kwargs:
        options[key] = kwargs[key]

    rawValues = raw.values
    rawValues, names = createIndicators(rawValues)
    values, scales = normalize(rawValues)
    data = values.reshape((-1, 1, values.shape[1]))

    train, test = splitTrainAndTest(data, 0.6599)
    trainX, trainY = createDataAndLabels(train, options['batchSize'])
    testX, testY = createDataAndLabels(test, options['batchSize'])

    assert trainX.shape[0] % options['batchSize'] == 0
    assert trainY.shape[0] % options['batchSize'] == 0

    assert trainX.shape[0] == trainY.shape[0]
    assert trainX.shape[2] == trainY.shape[1]

    assert testX.shape[2] == testY.shape[1]

    assert trainX.shape[1] == testX.shape[1]
    assert trainY.shape[1] == testY.shape[1]

    dataset = {
        'scales': scales,
        'trainX': trainX,
        'trainY': trainY,
        'testX': testX,
        'testY': testY,
        'names': names,
    }

    return dataset
