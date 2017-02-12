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

class ExperienceReplay(object):
    def __init__(self, features, maxMemory=100, discount=0.9):
        self.maxMemory = maxMemory
        self.discount = discount
        self.states = numpy.zeros((maxMemory, features))
        self.actions = numpy.zeros(maxMemory, dtype=numpy.int)
        self.rewards = numpy.zeros(maxMemory)
        self.nextStates = numpy.zeros((maxMemory, features))
        self.memoryIndex = 0
        self.memoryFull = False

    def remember(self, state, action, reward, nextState):
        self.states[self.memoryIndex] = state
        self.actions[self.memoryIndex] = action
        self.rewards[self.memoryIndex] = reward
        self.nextStates[self.memoryIndex] = nextState
        self.memoryIndex += 1
        if self.memoryIndex >= self.maxMemory:
            self.memoryIndex = 0
            self.memoryFull = True

    def getBatch(self, model, batchSize=10):
        features = self.states[0].shape[0]
        actionSize = model.output_shape[-1]
        memoryLength = self.maxMemory if self.memoryFull else self.memoryIndex + 1
        inputs = numpy.zeros((min(memoryLength, batchSize), features))
        targets = numpy.zeros((inputs.shape[0], actionSize))

        for i, randomInt in enumerate(random.randint(0, memoryLength, size=inputs.shape[0])):
            state = self.states[randomInt].reshape(1, features)
            action = self.actions[randomInt]
            reward = self.rewards[randomInt]
            nextState = self.nextStates[randomInt].reshape(1, features)
            inputs[i] = state
            targets[i] = model.predict(state)
            futureReward = numpy.max(model.predict(nextState))
            targets[i, action] = reward + self.discount * futureReward
        return inputs, targets

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
            sys.exit(1)

    return model

def save(model, outputName):
    if outputName is None:
        return
    print("Saving model weights...")
    model.save_weights(outputName + ".h5", overwrite=True)
    with open(outputName + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

# TODO: La prediction bestemme størrelse på kjøp/salg
def run():
    inputName = "model/testmodel"
    outputName = "model/testmodel"
    threshold = 0.1
    loss = 0.

    data = pandas.read_hdf("data/krakenEUR_2016_07.hdf5").dropna()
    closePrices = data.iloc[:, 3].values
    normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    indicators, longestPeriod = trading.createIndicators(normalized)
    features = indicators[0].shape[0]

    model = getModel(features, inputName)
    experienceReplay = ExperienceReplay(features)
    bank = Bank(10000)

    state = None
    nextState = indicators[longestPeriod].reshape(1, features)
    action = None
    print("Number of entries: {}".format(indicators.shape[0]))

    for i in range(longestPeriod, indicators.shape[0] - 1):
        if (i - longestPeriod) % 100 == 0:
            progress = 100 * (i - longestPeriod) / (indicators.shape[0] - longestPeriod)
            holdValue = (10000 / closePrices[longestPeriod]) * closePrices[i]
            print("Progess: {:.2f}% | Value: ${:.2f} | Hold: ${:.2f}"
                  .format(progress, bank.calculateValue(closePrices[i]), holdValue))

        state = nextState
        nextState = indicators[i + 1].reshape((1, features))

        if random.random() <= threshold:
            action = random.randint(0, 3, size=1)
        else:
            prediction = model.predict(state)
            action = numpy.argmax(prediction)

        reward = bank.performAction(closePrices[i], closePrices[i + 1], action)
        experienceReplay.remember(state, action, reward, nextState)
        inputs, targets = experienceReplay.getBatch(model)
        loss += model.train_on_batch(inputs, targets)

    total = bank.calculateValue(closePrices[-1])
    holdValue = (10000 / closePrices[longestPeriod]) * closePrices[-1]
    print("Loss: {:.4f}".format(loss))
    print("Funds: ${:.2f} | Bound: ${:.2f} | Total: ${:.2f} | Hold: ${:.2f}"
          .format(bank.funds, total - bank.funds, total, holdValue))
    save(model, outputName)

if __name__ == "__main__":
    run()
