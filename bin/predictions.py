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

def createPredictions(model, data):
    printIntervals = 10
    predictions = numpy.zeros((data.shape[0] - 1))
    modulo = predictions.shape[0] // printIntervals
    print("Creating predictions...")
    for i in range(0, predictions.shape[0]):
        predictions[i] = model.predict(data[i].reshape(1, data.shape[1], data.shape[2]))
        if i % modulo == 0:
            print("Progress: {}/{}".format(i, predictions.shape[0]))
    return predictions

if __name__ == "__main__":
    number = 7
    inputName = "model/testmodel{}".format(number)

    raw = pandas.read_hdf("data/EUR_USD_2017/EUR_USD_2017_01.hdf5")
    trainingData, trainingLabels, testData, testLabels = utility.createData(raw, 10)
    model = utility.getModel(trainingData, inputName)

    predictions = createPredictions(model, testData)
    utility.saveToHdf(predictions, "predictions/predictions{}.h5".format(number))
    utility.saveToHdf(testLabels, "predictions/labels{}.h5".format(number))
