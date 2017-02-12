import json
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
    def __init__(self, maxMemory=100, discount=0.9):
        self.maxMemory = maxMemory
        self.discount = discount
        self.memory = []
        self.memoryIndex = 0
        self.memoryFull = False

    def remember(self, memory):
        self.memory.append(memory)
        if len(self.memory) >= self.maxMemory:
            del(self.memory[0])

    def getBatch(self, model, batchSize=10):
        stateSize = self.memory[0][0].shape[1]
        actionSize = model.output_shape[-1]
        memoryLength = self.maxMemory if self.memoryFull else self.memoryIndex + 1
        inputs = numpy.zeros((min(memoryLength, batchSize), stateSize))
        targets = numpy.zeros((inputs.shape[0], actionSize))

        for i, randomInt in enumerate(random.randint(0, memoryLength, size=inputs.shape[0])):
            previousState, action, reward, state = self.memory[randomInt]
            inputs[i] = previousState
            targets[i] = model.predict(previousState)
            futureReward = numpy.max(model.predict(state))
            targets[i, action] = reward + self.discount * futureReward
        return inputs, targets

def getModel():
    hiddenSize = 100
    actionSize = 3

    model = Sequential()
    model.add(Dense(hiddenSize, input_dim=8, activation="relu"))
    model.add(Dense(hiddenSize, activation="relu"))
    model.add(Dense(actionSize))
    model.compile(sgd(lr=0.2), "mse")

    # weightsFilename = # TODO
    # if (os.path.isfile(weightsFilename)):
        # model.load_weights(weightsFilename)

    return model

def getAction(model, state):
    if numpy.random.rand() > 0.9:
        return numpy.random.randint(0, 3)
    rewards = model.predict(state)
    return numpy.argmax(rewards[0])

def train(model, experienceReplay, experience):
    experienceReplay.remember(experience)
    inputs, targets = experienceReplay.getBatch(model)
    return model.train_on_batch(inputs, targets)

def save(model):
    filename = "test"
    model.save_weights(filename + ".h5", overwrite=True)
    with open(filename + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

def run():
    threshold = 0.1
    loss = 0.

    data = pandas.read_hdf("./data/krakenEUR.hdf5", key="bitcoin").dropna()
    closePrices = data.iloc[:, 3].values
    normalized = (closePrices - closePrices.mean()) / (closePrices.max() - closePrices.min())
    indicators, longestPeriod = trading.createIndicators(normalized)

    model = getModel()
    experienceReplay = ExperienceReplay()
    bank = Bank(10000)

    state = None
    nextState = indicators[longestPeriod].reshape(1, 8)
    action = None
    print("Number of entries: {}".format(indicators.shape[0]))

    for i in range(longestPeriod, indicators.shape[0] - 1):
        if (i - longestPeriod) % 100 == 0:
            progress = math.floor(100 * (i - longestPeriod) / (indicators.shape[0] - longestPeriod))
            holdValue = (10000 / closePrices[longestPeriod]) * closePrices[i]
            print("Progess: {:.2f}% | Value: ${:.2f} | Hold: ${:.2f}"
                  .format(progress, bank.calculateValue(closePrices[i]), holdValue))

        state = nextState
        nextState = indicators[i + 1].reshape((1, 8))

        if random.random() <= threshold:
            action = random.randint(0, 3, size=1)
        else:
            prediction = model.predict(state)
            action = numpy.argmax(prediction)

        reward = bank.performAction(closePrices[i], closePrices[i + 1], action)
        experienceReplay.remember([state, action, reward, nextState])
        inputs, targets = experienceReplay.getBatch(model)
        loss += model.train_on_batch(inputs, targets)

    print("Loss: {:.4f}".format(loss))

if __name__ == "__main__":
    run()
