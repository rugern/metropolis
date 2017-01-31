import math
import json
import numpy
import pandas
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd
import trading

class ExperienceReplay(object):
    def __init__(self, maxMemory=100, discount=0.9):
        self.maxMemory = maxMemory
        self.discount = discount
        self.memory = []

    def remember(self, state):
        self.memory.append(state)
        if len(self.memory) > self.maxMemory:
            del self.memory[0]

    def getBatch(self, model, batchSize=10):
        stateSize = self.memory[0][0].shape[1]
        actionSize = self.memory[0][1].shape[1]
        memoryLength = len(self.memory)
        inputs = numpy.zeros((min(memoryLength, batchSize), stateSize))
        targets = numpy.zeros((inputs.shape[0], actionSize))

        for i, random in enumerate(numpy.random.randint(0, memoryLength, size=inputs.shape[0])):
            previousState, action, reward, state = self.memory[random]
            inputs[i] = previousState
            targets[i] = model.predict(previousState)[0]
            futureReward = numpy.max(model.predict(state)[0])
            targets[i, action] = reward + self.discount * futureReward
        return inputs, targets

def getModel():
    hiddenSize = 100
    actionSize = 3

    model = Sequential()
    model.add(Dense(hiddenSize, input_shape=(9,), activation="relu"))
    model.add(Dense(hiddenSize, activation="relu"))
    model.add(Dense(actionSize, activation="sigmoid"))
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

    filename = "test"
    model.save_weights(filename + ".h5", overwrite=True)
    with open(filename + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)

def run(model, experienceReplay):
    data = pandas.read_hdf("./data/krakenEUR.hdf5", key="bitcoin").dropna()
    prices = []
    index = 30
    # for index in range(30, len(data)):
    closePrices = data.iloc[:, 3].values
    print(trading.createIndicators(closePrices))
    print(len(closePrices))
        # prices.append(closePrice)
        # if len(prices) > 30:
            # del prices[0]

        # if math.isnan(closePrice):
            # continue

        # indicators = trading.createIndicators(prices)
        # print(indicators)
        # hent ut indikatorer og lag array
        # random valg vs spå kjøp/stå/selg
        # gjennomfør valg
        # husk erfaring
        # train på batch


if __name__ == "__main__":
    model = getModel()
    experienceReplay = ExperienceReplay()
    run(model, experienceReplay)
