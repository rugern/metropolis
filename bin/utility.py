import json
import sys
import os
import math
import numpy
import random
import pandas
import h5py
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Input, Dense, LSTM, Embedding
from keras.models import Model
from keras.optimizers import sgd, RMSprop
from bank import Bank
import trading
from matplotlib import pyplot
import utility

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

def saveToHdf(filename, data):
    output = h5py.File(filename, "w")
    output.create_dataset("data", data=data)
    output.close()

def scaleMatrix(values):
    scaler = MinMaxScaler(feature_range=(0, 1))
    return scaler.fit_transform(values)

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

def createDataAndLabels(values, datetimes, lookback, save=False):
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
    assert(len(labels) == len(data) == len(labelDt))

    # 2. Lagre test-labels og -indicators (inkl ohlc) sammen med test-datetime
    if save:
        comparisonData = splice(values, 1, -correction)
        comparisonData = takeEvery(comparisonData, 1, lookback)
        # h5py doesnt support utf-8, so store as ascii
        stringLabelDt = numpy.array(labelDt, dtype=numpy.dtype("S48"))

        # 4. assert(len(data) == len(labels)) for test og train
        assert(comparisonData.shape[1] > 9)
        assert(len(comparisonData) == len(labels) == len(stringLabelDt))

        saveToHdf("labels/datetimes.h5", stringLabelDt)
        saveToHdf("indicators/open.h5", comparisonData[:, 0])
        saveToHdf("indicators/high.h5", comparisonData[:, 1])
        saveToHdf("indicators/low.h5", comparisonData[:, 2])
        saveToHdf("indicators/close.h5", comparisonData[:, 3])
        saveToHdf("indicators/ema.h5", comparisonData[:, 4])
        saveToHdf("indicators/rsi.h5", comparisonData[:, 5])
        saveToHdf("indicators/upperband.h5", comparisonData[:, 6])
        saveToHdf("indicators/middleband.h5", comparisonData[:, 7])
        saveToHdf("indicators/lowerband.h5", comparisonData[:, 8])

    # 5. returner data og labels
    return data, labels, labelDt


def createData(raw, lookback=5):
    # 1. Dra ut datetime og values
    datetimes = raw.index.values
    values = raw.values

    # 3. Lag indikatordata, fjern NaN
    values, datetimes = trading.createIndicators(values, datetimes)

    # 2. normaliser values
    values = scaleMatrix(values)

    # 4. splitTrainAndTest
    train, test, trainDt, testDt = splitTrainAndTest(values, datetimes)

    # 5. For hver av train og test:
    trainData, trainLabels, trainLabelDt = createDataAndLabels(train, trainDt, lookback)
    testData, testLabels, testLabelDt = createDataAndLabels(test, testDt, lookback, True)

    # 6. returner train og test, med data og labels
    return trainData, trainLabels, testData, testLabels, testDt
