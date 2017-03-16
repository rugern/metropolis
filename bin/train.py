import json
import sys
import os
import math
import numpy
import random
from numpy import random
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd
import trading
from bank import Bank

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

def createData(raw):
    # closePrices = data.iloc[:, 3].values
    # normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    # indicators, longestPeriod = trading.createIndicators(normalized)

    normalized = normalize(raw)
    data = normalized.iloc[:-1, :].values
    labels = normalized.iloc[1:, :].values
    return data, labels

def getModel(features, inputName=None):
    hiddenSize = 50

    model = Sequential()
    model.add(Dense(hiddenSize, input_dim=features, activation="relu"))
    model.add(Dense(hiddenSize, activation="relu"))
    model.add(Dense(features, activation="sigmoid"))
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
# TODO: Test LSTM
# TODO: Test større nettverk (prøv gjerne å overfitte)
# TODO: Transfer learning
def train(model, data, labels):
    model.fit(data, labels, epochs=10, batch_size=32)

def test(model, data, raw):
    startMoney = 10000
    bank = Bank(startMoney)
    print("Starting value: {}".format(len(data)))
    buys = 0
    sells = 0
    holds = 0
    initialPrice = raw.iloc[0][3]
    print(initialPrice)

    for i in range(data.shape[0] // 5):
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

    # holdValue = (10000 / closePrices[longestPeriod]) * closePrices[-1]
    # total = bank.calculateValue(closePrices[-1])
    # bound = total - bank.funds
    # profit = 100 * (total - startMoney) / startMoney
    # relativeProfit = 100 * (total - holdValue) / holdValue
    # print("Loss: {:.4f}".format(loss))
    # print("".join(["Funds: ${:.2f} | Bound: ${:.2f} | Total: ${:.2f} | Hold: ${:.2f} | ",
          # "Relative profit: {:.2f}% | Profit: {:.2f}%"])
          # .format(bank.funds, bound, total, holdValue, relativeProfit, profit))
    # print("Buys: {} | Holds: {} | Sells: {}"
          # .format(actionsPerformed[2], actionsPerformed[1], actionsPerformed[0]))

if __name__ == "__main__":
    inputName = "model/testmodel"
    outputName = "model/testmodel"

    model = getModel(4, inputName)
    raw = pandas.read_hdf("data/EUR_BITCOIN_2016/krakenEUR_2016_padded.hdf5")
    data, labels = createData(raw)
    ratio = round(len(data) * 75/100)
    training_data = data[:ratio]
    training_labels = labels[:ratio]

    # train(model, training_data, training_labels)
    # save(model, outputName)

    test(model, data, raw)
