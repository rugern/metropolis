import json
import os
from os import listdir
from os.path import isfile, join
import numpy
import h5py
from keras.layers import Input, Dense, LSTM
from keras.models import Model
from keras.optimizers import sgd
import trading

def assertOrCreateDirectory(path):
    if not os.path.exists(path):
        print("Creating directory '{}'".format(path))
        os.makedirs(path)

def normalize(inMatrix):
    scales = []
    matrix = inMatrix.copy()

    # Reshape parameter to matrix
    isArray = len(matrix.shape) == 1
    if isArray:
        matrix = matrix.reshape((-1, 1))

    for index in range(matrix.shape[1]):
        columnMin = matrix[:, index].min()
        columnMax = matrix[:, index].max()
        matrix[:, index] = (matrix[:, index] - columnMin) / (columnMax - columnMin)
        scales.append((columnMin, columnMax))

    # Reshape back to match parameter shape (if changed)
    if isArray:
        matrix = matrix.reshape((-1))
        scales = scales[0]

    return matrix, scales

def inverse_normalize(inMatrix, scales):
    matrix = inMatrix.copy()

    # Reshape parameter to matrix
    isArray = len(matrix.shape) == 1
    if isArray:
        matrix = matrix.reshape((-1, 1))
        scales = [scales]

    for index in range(matrix.shape[1]):
        scale = scales[index]
        matrix[:, index] = matrix[:, index] * (scale[1] - scale[0]) + scale[0]

    # Reshape back to match parameter shape (if changed)
    if isArray:
        matrix = matrix.reshape((-1))

    return matrix

def getModel(data, inputName=None):
    # model = Sequential()
    # model.add(Dense(hiddenSize, input_dim=features, activation="relu"))
    # model.add(Dense(hiddenSize, activation="relu"))
    # model.add(Dense(features, activation="sigmoid"))
    # model.compile(sgd(lr=0.2), "mse")

    inputs = Input(shape=(data.shape[1], data.shape[2]))
    x = LSTM(data.shape[2])(inputs)
    x = Dense(50, activation="relu")(x)
    x = Dense(50, activation="relu")(x)
    predictions = Dense(1, activation="sigmoid")(x)
    model = Model(inputs=inputs, outputs=predictions)
    model.compile(sgd(lr=0.3), "mse")

    if inputName is not None:
        inputName += ".h5"
        print("Loading saved model weights...")
        if os.path.isfile(inputName):
            model.load_weights(inputName)
        else:
            print("Sorry bro, could not find the weights file: {}".format(inputName))

    return model

def getFileList(path, filetype=None):
    if not os.path.exists(path):
        return []
    filenames = [name for name in listdir(path) if isfile(join(path, name))]
    if filetype is not None:
        filenames = list(filter(lambda filename: filetype in filename, filenames))
        filenames = list(map(lambda filename: "".join(filename.split(".")[:-1]), filenames))
    return filenames

def getDirectoryList(path):
    if not os.path.exists(path):
        return []
    folderNames = [name for name in listdir(path) if not isfile(join(path, name))]
    return folderNames

def saveToHdf(filename, data):
    output = h5py.File(filename, "w")
    output.create_dataset("data", data=data)
    output.close()

def readHdf(name, column=None):
    if not isfile(name):
        return []
    infile = h5py.File(name, "r")
    data = infile["data"][:]
    if column is not None and data.shape[1] > column:
        data = data[:, column]
    infile.close()
    return data

def readJson(path):
    data = None
    with open(path, "r") as infile:
        data = json.load(infile)
    return data

def writeJson(path, data):
    with open(path, "w") as outfile:
        json.dump(data, outfile)

def saveModel(model, outputName):
    if outputName is None:
        return
    print("Saving model weights...")
    model.save_weights(outputName + ".h5", overwrite=True)
    with open(outputName + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)
    print("Finished saving model weights")

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
    return values[interval-1::interval]

def splice(values, start, end):
    return values[start:end] if end != 0 else values[start:]

def correctData(inValues, useOffset, lookback):
    values = inValues.copy()
    offset = 1 if useOffset else 0
    correction = (len(values) - 1) % lookback
    return splice(values, offset, offset - 1 - correction)

def reshape(inValues, lookback):
    values = inValues.copy()
    return values.reshape((-1, lookback, values.shape[1]))

def saveIndicators(indicators, dt, path, prefix, names):
    stringLabelDt = numpy.array(dt, dtype=numpy.dtype("S48"))
    assertOrCreateDirectory(path["indicator"])
    saveToHdf(join(path["base"], "datetimes.h5"), stringLabelDt)
    for index in range(indicators.shape[1]):
        saveToHdf(join(path["indicator"], "{}-{}.h5".format(prefix, names[index])), indicators[:, index])

def createData(raw, path=None, prefix=None, save=False):
    lookback = 5
    # 1. Dra ut datetime og values
    datetimes = raw.index.values
    rawValues = raw.values

    # 3. Lag indikatordata, fjern NaN
    rawValues, datetimes, names = trading.createIndicators(rawValues, datetimes)

    # 2. normaliser values
    values, scales = normalize(rawValues)

    # 4. splitTrainAndTest
    train, test, trainDt, testDt = splitTrainAndTest(values, datetimes)
    trainRaw, testRaw, _, _ = splitTrainAndTest(rawValues)

    # 5. For hver av train og test:
    dataset = {
        "scales": scales
    }

    trainData = reshape(correctData(train, False, lookback), lookback)
    testData = reshape(correctData(test, False, lookback), lookback)

    trainLabels = takeEvery(correctData(train, True, lookback), lookback)
    testLabels = takeEvery(correctData(test, True, lookback), lookback)
    testDt = takeEvery(correctData(testDt, True, lookback), lookback)
    indicators = takeEvery(correctData(testRaw, False, lookback), lookback)

    assert(len(trainData) == len(trainLabels))
    assert(len(testData) == len(testLabels) == len(testDt))

    if save:
        saveIndicators(indicators, testDt, path, prefix, names)

    dataset["train"] = {
        "data": trainData,
        "labels": trainLabels[:, 3],
    }
    dataset["test"] = {
        "data": testData,
        "labels": testLabels[:, 3],
        "labelDt": testDt,
    }
    dataset["indicators"] = indicators

    # 6. returner train og test, med data og labels
    return dataset
