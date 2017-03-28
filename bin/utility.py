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
    output = h5py.File("results/" + name, "w")
    output.create_dataset("data", data=data)
    output.close()

def createData(raw, lookback=4):
    sampleScaler = MinMaxScaler(feature_range=(0, 1))
    labelScaler = MinMaxScaler(feature_range=(0, 1))
    # closePrices = data.iloc[:, 3].values
    # normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    # indicators, longestPeriod = trading.createIndicators(normalized)

    data, longestPeriod = trading.createIndicators(raw.values)
    data = data[longestPeriod:]
    correction = -4
    offset = 5 # number of timesteps to predict ahead

    # utility.saveToHdf(data[:correction-1, 3], "close.h5")
    # utility.saveToHdf(data[:correction-1, 4], "ema.h5")
    # utility.saveToHdf(data[:correction-1, 5], "rsi.h5")
    # utility.saveToHdf(data[:correction-1, 6], "upperband.h5")
    # utility.saveToHdf(data[:correction-1, 7], "middleband.h5")
    # utility.saveToHdf(data[:correction-1, 8], "lowerband.h5")

    samples = sampleScaler.fit_transform(data[:correction-offset])
    samples = samples.reshape((-1, lookback, samples.shape[1]))
    labels = labelScaler.fit_transform(data[offset:correction, 4])
    labels = labels[lookback - 1::lookback]

    ratio = len(samples) * 75 // 100
    trainingData = samples[:ratio]
    trainingLabels = labels[:ratio]
    testData = samples[ratio:]
    testLabels = labels[ratio:]

    return trainingData, trainingLabels, testData, testLabels
