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


def save(model, outputName):
    if outputName is None:
        return
    print("Saving model weights...")
    model.save_weights(outputName + ".h5", overwrite=True)
    with open(outputName + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

def createTimesteps(data, lookback=2):
    timesteps = data[0 : lookback].reshape((1, lookback, data.shape[1]))
    for i in range(lookback * 2, data.shape[0]):
        temp = data[i - lookback : i].reshape((1, lookback, data.shape[1]))
        timesteps = numpy.append(timesteps, temp, axis=0)
    return timesteps

def findAction(estimate, price):
    buy = estimate > price
    sell = estimate < price
    return buy, sell

# TODO: Test større nettverk (prøv gjerne å overfitte)
# TODO: Transfer learning
def train(model, data, labels):
    model.fit(data, labels, epochs=1, batch_size=32)

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
    number = 7
    inputName = "model/testmodel{}".format(number)
    outputName = "model/testmodel{}".format(number)

    raw = pandas.read_hdf("data/EUR_BITCOIN_2016/krakenEUR_2016_padded.hdf5")
    trainingData, trainingLabels, testData, testLabels = utility.createData(raw, 10)

    model = utility.getModel(trainingData, inputName)
    train(model, trainingData, trainingLabels)
    save(model, outputName)
