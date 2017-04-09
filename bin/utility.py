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

def saveToHdf(data, name):
    output = h5py.File(name, "w")
    output.create_dataset("data", data=data)
    output.close()

def createData(raw, lookback=5):
    sampleScaler = MinMaxScaler(feature_range=(0, 1))
    labelScaler = MinMaxScaler(feature_range=(0, 1))
    # closePrices = data.iloc[:, 3].values
    # normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    # indicators, longestPeriod = trading.createIndicators(normalized)

    data, longestPeriod = trading.createIndicators(raw.values)
    data = data[longestPeriod:]
    correction = -8

    samples = sampleScaler.fit_transform(data[:correction-lookback])
    samples = samples.reshape((-1, lookback, samples.shape[1]))
    labels = labelScaler.fit_transform(data[lookback+1:correction, 4])
    labels = labels[lookback - 1::lookback]

    ratio = len(samples) * 75 // 100
    trainingData = samples[:ratio]
    trainingLabels = labels[:ratio]
    testData = samples[ratio:]
    testLabels = labels[ratio:]

    # utility.saveToHdf(data[ratio+lookback+1:correction, 0], "indicators/open.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 1], "indicators/high.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 2], "indicators/low.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 3], "indicators/close.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 4], "indicators/ema.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 5], "indicators/rsi.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 6], "indicators/upperband.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 7], "indicators/middleband.h5")
    # utility.saveToHdf(data[ratio+lookback+1:correction, 8], "indicators/lowerband.h5")

    return trainingData, trainingLabels, testData, testLabels
