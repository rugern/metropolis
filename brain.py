import os
import random
import json
import numpy
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import sgd

class ExperienceReplay:
    def __init__(self, maxMemory=100, discount=0.9):
        #initialize

    def remember(self, states):
        #add state to memory

    def getBatch(self, model, batchSize=10):
        
        # iterate through random memories
            # retrieve state and next states from memory
            # calculate value of current state
            # get max next state
            # give reward

        # return batch
    

def getModel(config):
    model = Sequential()
    model.add(Dense(config["hiddenSize"], input_shape=(9,), activation="relu"))
    model.add(Dense(config["hiddenSize"], activation="relu"))
    model.add(Dense(config["numberOfActions"], activation="sigmoid"))
    model.compile(sgd(lr=0.2), "mse")

    weightsFilename = # TODO
    if (os.path.isfile(weightsFilename)):
        model.load_weights(weightsFilename)

    return model

def getAction(model, previousState):
    action = None
    # if explore return random action
    # else return max state


def train(self, previousState, action, reward, state, gameOver):
    # remember current experience
    # retrieve batch
    # train model on batch


def run():
    for epoch in range(epochs):
        while (True):
            # store previous state
            # get current state
            # predict and perform action for current state
            # train on state


def save(model):
    filename = #TODO
    model.save_weights(filename + ".h5", overwrite=True)
    with open(filename + ".json", "w") as outfile:
        json.dump(model.to_json(), outfile)


if __name__ == "__main__":
    #initialize alg
