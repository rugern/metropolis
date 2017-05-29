from os.path import join
import numpy

from utility import assertOrCreateDirectory, saveToHdf, splice
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

def correctData(inValues, offset, lookback):
    values = inValues.copy()
    correction = (len(values) - offset) % lookback
    return splice(values, offset, offset - correction)

def reshape(values, lookback):
    output = numpy.concatenate(
        tuple(values[i:lookback+i] for i in range(values.shape[0] - lookback + 1))
    )
    return output.reshape((-1, lookback, output.shape[1]))

def saveIndicators(indicators, dt, path, prefix, names):
    stringLabelDt = numpy.array(dt, dtype=numpy.dtype('S48'))
    assertOrCreateDirectory(path['indicator'])
    saveToHdf(join(path['data'], 'datetimes.h5'), stringLabelDt)
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
    rawValues, datetimes, names = createIndicators(rawValues, datetimes)

    # 2. normaliser values
    values, scales = normalize(rawValues)

    # 4. splitTrainAndTest
    train, test, _, testDt = splitTrainAndTest(values, datetimes)
    _, testRaw, _, _ = splitTrainAndTest(rawValues)

    # 5. For hver av train og test:
    trainData = splice(reshape(train, lookback), 0, -lookforward)
    testData = splice(reshape(test, lookback), 0, -lookforward)

    labelColumn = 6
    trainLabels = numpy.column_stack([
        splice(train, lookback + i, i - lookforward + 1)[:, labelColumn]
        for i in range(0, lookforward)
    ])
    testLabels = numpy.column_stack([
        splice(test, lookback + i, i - lookforward + 1)[:, labelColumn]
        for i in range(0, lookforward)
    ])

    dt = splice(testDt, lookback + lookforward - 1, -lookforward + 1)
    indicators = splice(testRaw, lookback + lookforward - 1, -lookforward + 1)

    assert len(trainData) == len(trainLabels)
    assert len(testData) == len(testLabels)
    assert len(dt) == len(indicators)

    if save:
        saveIndicators(indicators, dt, path, prefix, names)

    dataset = {
        'scales': scales
    }
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
    dataset['labelColumn'] = labelColumn

    # 6. returner train og test, med data og labels
    return dataset
