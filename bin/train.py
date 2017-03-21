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
from keras.optimizers import sgd
from bank import Bank
import trading
from matplotlib import pyplot

sampleScaler = MinMaxScaler(feature_range=(0, 1))
labelScaler = MinMaxScaler(feature_range=(0, 1))

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

def createTimesteps(data, lookback=2):
    timesteps = data[0 : lookback].reshape((1, lookback, data.shape[1]))
    for i in range(lookback * 2, data.shape[0]):
        temp = data[i - lookback : i].reshape((1, lookback, data.shape[1]))
        timesteps = numpy.append(timesteps, temp, axis=0)
    return timesteps

def saveToHdf(data, name):
    output = h5py.File("results/" + name, "w")
    output.create_dataset("data", data=data)
    output.close()

def createData(raw, lookback=4):
    # closePrices = data.iloc[:, 3].values
    # normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    # indicators, longestPeriod = trading.createIndicators(normalized)

    data, longestPeriod = trading.createIndicators(raw.values)
    data = data[longestPeriod:]
    offset = -3
    samples = sampleScaler.fit_transform(data[:offset-1])
    samples = samples.reshape((-1, lookback, samples.shape[1]))
    labels = labelScaler.fit_transform(data[1:offset, 3])
    labels = labels[lookback - 1::lookback]
    return samples, labels

def getModel(data, inputName=None):
    hiddenSize = 50

    # model = Sequential()
    # model.add(Dense(hiddenSize, input_dim=features, activation="relu"))
    # model.add(Dense(hiddenSize, activation="relu"))
    # model.add(Dense(features, activation="sigmoid"))
    # model.compile(sgd(lr=0.2), "mse")

    inputs = Input(shape=(data.shape[1], data.shape[2]))
    x = LSTM(data.shape[2])(inputs)
    x = Dense(hiddenSize, activation="relu")(x)
    # x = Dense(hiddenSize, activation="relu")(x)
    predictions = Dense(1, activation="sigmoid")(x)
    model = Model(inputs=inputs, outputs=predictions)
    model.compile(sgd(lr=0.2), "mse")

    if inputName is not None:
        inputName += ".h5"
        print("Loading saved model weights...")
        if os.path.isfile(inputName):
            model.load_weights(inputName)
        else:
            print("Sorry bro, could not find the weights file: {}".format(inputName))

    return model

def findAction(estimate, price):
    buy = estimate > price
    sell = estimate < price
    return buy, sell

# TODO: Test concatenation of features
# TODO: Test større nettverk (prøv gjerne å overfitte)
# TODO: Transfer learning
def train(model, data, labels):
    model.fit(data, labels, epochs=1, batch_size=32)

def test(model, data):
    printIntervals = 10
    modulo = data.shape[0] // printIntervals
    predictions = numpy.zeros((data.shape[0]))
    print(predictions.shape)
    print("Creating predictions...")
    for i in range(0, data.shape[0]):
        predictions[i] = model.predict(data[i].reshape(1, data.shape[1], data.shape[2]))
        if i % modulo == 0:
            print("Progress: {}/{}".format(i, data.shape[0]))
    return predictions
    
def marketTest(model, data, raw):
    startMoney = 10000
    bank = Bank(startMoney)
    print("Data rows: {}".format(len(data)))
    buys = 0
    sells = 0
    holds = 0
    initialPrice = raw.iloc[0][3]

    for i in range(data.shape[0]):
        estimate = model.predict(data[i].reshape(1 ,4))[0][3]
        price = raw.iloc[i][3]
        buy, sell = findAction(estimate, data[i][3])
        quota = random.random()
        if buy:
            bank.buy(price, quota)
            buys += 1
        elif sell:
            bank.sell(price, quota)
            sells += 1
        else:
            holds += 1
        
        if i % 10000 == 0:
            holdValue = (startMoney / initialPrice) * price
            total = bank.calculateValue(price)
            bound = total - bank.funds
            profit = 100 * (total - startMoney) / startMoney
            relativeProfit = 100 * (total - holdValue) / holdValue
            print("".join(["Progress: {} | Funds: ${:.2f} | Bound: ${:.2f} | ",
                   "Total: ${:.2f} | Hold: ${:.2f} | ",
                  "Relative profit: {:.2f}% | Profit: {:.2f}%"])
                  .format(i, bank.funds, bound, total, holdValue, relativeProfit, profit))
            print("Buys: {} | Holds: {} | Sells: {}"
                  .format(buys, holds, sells))

    lastPrice = raw.iloc[-1][3]
    print(initialPrice, lastPrice)
    holdValue = (10000 / initialPrice) * lastPrice
    total = bank.calculateValue(lastPrice)
    bound = total - bank.funds
    profit = 100 * (total - startMoney) / startMoney
    relativeProfit = 100 * (total - holdValue) / holdValue

    print("".join(["Funds: ${:.2f} | Bound: ${:.2f} | Total: ${:.2f} | Hold: ${:.2f} | ",
          "Relative profit: {:.2f}% | Profit: {:.2f}%"])
          .format(bank.funds, bound, total, holdValue, relativeProfit, profit))
    print("Buys: {} | Holds: {} | Sells: {}"
          .format(buys, holds, sells))

if __name__ == "__main__":
    inputName = "model/testmodel2"
    outputName = "model/testmodel2"

    raw = pandas.read_hdf("data/EUR_BITCOIN_2016/krakenEUR_2016_padded.hdf5")
    samples, labels = createData(raw)
    ratio = len(samples) * 75 // 100
    trainingData = samples[:ratio]
    trainingLabels = labels[:ratio]

    testData = samples[ratio:]
    testLabels = labels[ratio:]

    model = getModel(samples, inputName)
    train(model, trainingData, trainingLabels)
    save(model, outputName)

    predictions = test(model, testData)
    saveToHdf(predictions, "predictions2.h5")
    saveToHdf(testLabels, "labels2.h5")
