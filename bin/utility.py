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

def splitTrainAndTest(values, datetimes, ratio=0.7):
    trainLength = round(len(values) * ratio)
    train = values[:trainLength]
    trainDt = datetimes[:trainLength]
    test = values[trainLength:]
    testDt = datetimes[trainLength:]
    return train, test, trainDt, testDt

def takeEvery(values, startOffset, interval):
    return values[interval-startOffset::interval]

def splice(values, start, end):
    return values[start:end] if end != 0 else values[start:]

def createDataAndLabels(values, datetimes, lookback, prefix=None, path=None, save=False, scales=None):
    # 1. Fiks correction (også datetime). Ta høyde for at data og labels len er -1
    correction = (len(values) - 1) % lookback
    data = splice(values, 0, -1-correction)
    labels = splice(values, 1, -correction)[:, 3]
    labelDt = splice(datetimes, 1, -correction)

    # 2. createData: reshape data
    data = data.reshape((-1, lookback, data.shape[1]))

    # 3. createLabels: Hopp over tilsvarende reshape
    labels = takeEvery(labels, 1, lookback)
    labelDt = takeEvery(labelDt, 1, lookback)

    # 1. assert(len(labels) == len(indicators) == len(datetime)) for test
    assert len(labels) == len(data) == len(labelDt)

    # 2. Lagre test-labels og -indicators (inkl ohlc) sammen med test-datetime
    if save:
        assert(path is not None and scales is not None and prefix is not None)
        comparisonData = splice(values, 1, -correction)
        comparisonData = takeEvery(comparisonData, 1, lookback)
        comparisonData = inverse_normalize(comparisonData, scales)

        # h5py doesnt support utf-8, so store as ascii
        stringLabelDt = numpy.array(labelDt, dtype=numpy.dtype("S48"))

        # 4. assert(len(data) == len(labels)) for test og train
        assert comparisonData.shape[1] > 9
        assert len(comparisonData) == len(labels) == len(stringLabelDt)

        assertOrCreateDirectory(path["indicator"])
        saveToHdf(join(path["base"], "datetimes.h5"), stringLabelDt)
        saveToHdf(join(path["indicator"], "{}-open.h5".format(prefix)), comparisonData[:, 0])
        saveToHdf(join(path["indicator"], "{}-high.h5".format(prefix)), comparisonData[:, 1])
        saveToHdf(join(path["indicator"], "{}-low.h5".format(prefix)), comparisonData[:, 2])
        saveToHdf(join(path["indicator"], "{}-close.h5".format(prefix)), comparisonData[:, 3])
        saveToHdf(join(path["indicator"], "{}-ema.h5".format(prefix)), comparisonData[:, 4])
        saveToHdf(join(path["indicator"], "{}-rsi.h5".format(prefix)), comparisonData[:, 5])
        saveToHdf(join(path["indicator"], "{}-upperband.h5".format(prefix)), comparisonData[:, 6])
        saveToHdf(join(path["indicator"], "{}-middleband.h5".format(prefix)), comparisonData[:, 7])
        saveToHdf(join(path["indicator"], "{}-lowerband.h5".format(prefix)), comparisonData[:, 8])

    # 5. returner data og labels
    return {
        "data": data,
        "labels": labels,
        "labelDt": labelDt
    }


def createData(raw, path, prefix, lookback=5):
    # 1. Dra ut datetime og values
    datetimes = raw.index.values
    values = raw.values

    # 3. Lag indikatordata, fjern NaN
    values, datetimes = trading.createIndicators(values, datetimes)

    # 2. normaliser values
    values, scales = normalize(values)

    # 4. splitTrainAndTest
    train, test, trainDt, testDt = splitTrainAndTest(values, datetimes)

    # 5. For hver av train og test:
    dataset = {
        "scales": scales
    }
    dataset["train"] = createDataAndLabels(train, trainDt, lookback)
    dataset["test"] = createDataAndLabels(test, testDt, lookback, prefix, path, True, scales)

    # 6. returner train og test, med data og labels
    return dataset
