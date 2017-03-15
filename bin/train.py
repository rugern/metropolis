import json
import sys
import os
import math
import numpy
from numpy import random
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd
import trading
from bank import Bank


def getModel(features, inputName=None):
    hiddenSize = 50
    actionSize = 3

    model = Sequential()
    model.add(Dense(hiddenSize, input_dim=features, activation="relu"))
    model.add(Dense(hiddenSize, activation="relu"))
    model.add(Dense(actionSize, activation="sigmoid"))
    model.compile(sgd(lr=0.2), "mse")

    if inputName is not None:
        inputName += ".h5"
        print("Loading saved model weights...")
        if os.path.isfile(inputName):
            model.load_weights(inputName)
        else:
            print("Sorry bro, could not find the weights file: {}".format(inputName))

    return model

def save(model, outputName):
    if outputName is None:
        return
    print("Saving model weights...")
    model.save_weights(outputName + ".h5", overwrite=True)
    with open(outputName + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

def normalize(raw):
    maximum = max(raw.max().values)
    minimum = min(raw.min().values)
    return (raw - minimum) / (maximum - minimum)

def createTrainingData(raw):
    normalized = normalize(raw)
    examples = normalized.iloc[:-1, :].values
    labels = normalized.iloc[1:, :].values
    ratio = round(len(examples) * 75/100)
    return examples[:ratio], labels[:ratio]


# TODO: Test concatenation of features
# TODO: Test LSTM
# TODO: Test større nettverk (prøv gjerne å overfitte)
# TODO: Transfer learning
def train():
    inputName = "model/testmodel2"
    outputName = "model/testmodel2"
    threshold = 0.1
    loss = 0.

    # data = pandas.read_hdf("data/krakenEUR_2016_07.hdf5").dropna()
    examples, labels = createTrainingData(pandas.read_hdf("data/EUR_BITCOIN_2016/krakenEUR_2016_padded.hdf5"))

    # closePrices = data.iloc[:, 3].values
    # normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    # indicators, longestPeriod = trading.createIndicators(normalized)
    features = examples.shape[1]

    model = getModel(features, inputName)

    # action = None
    # actionsPerformed = numpy.zeros(3) # SELL, HOLD, BUY

    # print("Number of entries: {}".format(indicators.shape[0]))

    # save(model, outputName)
    # return model

def test():
    startMoney = 10000
    bank = Bank(startMoney)
    # quota = 0.
        # if (i - longestPeriod) % 100 == 0:
            # progress = 100 * (i - longestPeriod) / (indicators.shape[0] - longestPeriod)
            # holdValue = (10000 / closePrices[longestPeriod]) * closePrices[i]
            # total = bank.calculateValue(closePrices[i])
            # print("".join(["Progess: {:.2f}% | Price: ${:.5f} | Funds: ${:.2f} | ",
                  # "Bound: ${:.2f} | Total: ${:.2f}| Hold: ${:.2f}"])
                  # .format(progress, closePrices[i], bank.funds, total - bank.funds, total, holdValue))
    # quota = prediction[action]
    # reward = bank.performAction(closePrices[i], closePrices[i + 1], action, quota)

    holdValue = (10000 / closePrices[longestPeriod]) * closePrices[-1]
    total = bank.calculateValue(closePrices[-1])
    bound = total - bank.funds
    profit = 100 * (total - startMoney) / startMoney
    relativeProfit = 100 * (total - holdValue) / holdValue
    print("Loss: {:.4f}".format(loss))
    print("".join(["Funds: ${:.2f} | Bound: ${:.2f} | Total: ${:.2f} | Hold: ${:.2f} | ",
          "Relative profit: {:.2f}% | Profit: {:.2f}%"])
          .format(bank.funds, bound, total, holdValue, relativeProfit, profit))
    print("Buys: {} | Holds: {} | Sells: {}"
          .format(actionsPerformed[2], actionsPerformed[1], actionsPerformed[0]))

if __name__ == "__main__":
    train()
    # test(model)
