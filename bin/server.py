import os
from os.path import isfile, join
import shutil
import numpy
import pandas
from flask import Flask
from flask_socketio import SocketIO, emit
import keras

import utility
from utility import readHdf, getFileList, getDirectoryList
from predictions import createPredictions

app = Flask(__name__)
socket = SocketIO(app)

status = "Idle"
name = "model"
datafile = "EUR_USD_2017_1_10m"
epochs = 1
baseFolder = "data"

class KerasLogger(keras.callbacks.Callback):
    def __init__(self, target, eventName):
        super()
        self.target = target
        self.eventName = eventName

    def __call__(self, message):
        self.target.start_background_task(target=self.log, message=message)

    def log(self, message):
        self.target.emit(self.eventName, message)

    def on_epoch_begin(self, epoch, logs=None):
        self.samples = self.params["samples"]
        self.__call__("Epoch {}/{}".format(epoch + 1, self.epochs))

    def on_epoch_end(self, epoch, logs=None):
        self.__call__("Loss: {}".format(logs["loss"]))

    def on_batch_begin(self, batch, logs=None):
        pass

    def on_batch_end(self, batch, logs=None):
        batchSize = logs.get('size', 0)
        self.seen += batchSize
        self.__call__("Progress: {}/{}".format(self.seen, self.samples))


    def on_train_begin(self, logs=None):
        self.epochs = self.params["epochs"]
        self.seen = 0
        self.batchSize = self.params["batch_size"]
        self.__call__("Train begin")


    def on_train_end(self, logs=None):
        self.__call__("Train end")

def createPaths():
    return {
        "base": join(baseFolder, datafile),
        "prediction": join(baseFolder, datafile, "predictions"),
        "indicator": join(baseFolder, datafile, "indicators"),
        "model": join(baseFolder, datafile, "models", name),
    }

def calculateDatetimeRange(start, end, dt):
    offset = dt.index(min(dt, key=lambda x: abs(x - start)))
    limit = dt.index(min(dt, key=lambda x: abs(x - end))) - offset
    return offset, limit

def getData(path, offset, limit):
    data = {}
    names = getFileList(path)
    for name in names:
        shortName = "".join(name.split(".")[:-1])
        data[shortName] = {}
        data[shortName]["data"] = readHdf(join(path, name)).tolist()[offset:offset+limit]
    return data

def emitStatus():
    socket.emit("set_metropolis_status", status)

def setStatus(newStatus):
    global status
    status = newStatus
    socket.start_background_task(target=emitStatus)

@socket.on("get_data")
def emitData(options):
    path = createPaths()
    datetimes = numpy.array(readHdf(join(path["base"], "datetimes.h5")), dtype="datetime64[m]").tolist()
    # endTime = options["endTime"] if "endTime" in options else datetimes[-1]
    # startTime = options["startTime"] if "startTime" in options else datetimes[-min(len(datetimes), 1000)]
    limit = options["limit"] if "limit" in options else 200
    offset = options["offset"] if "offset" in options else len(datetimes) - limit
    offset = max(0, offset)
    limit = min(len(datetimes) - offset, limit)
    labels = numpy.array(datetimes, dtype=numpy.dtype("str")).tolist()[offset:offset+limit]

    data = {}
    data["labels"] = labels
    data["indicators"] = getData(path["indicator"], offset, limit)
    data["predictions"] = getData(path["prediction"], offset, limit)
    data["models"] = getDirectoryList(join(path["base"], "models"))
    data["datafiles"] = getDirectoryList(baseFolder)
    data["datafile"] = datafile
    data["datasize"] = len(datetimes)

    emit("set_data", data)

@socket.on("get_metropolis_status")
def getStatus():
    emitStatus()

def trainModel(dataset, path, prefix, logger):
    trainData = dataset["train"]["data"]
    trainLabels = dataset["train"]["labels"]

    modelPath = join(path["model"], prefix)
    utility.assertOrCreateDirectory(path["model"])
    model = utility.getModel(trainData, modelPath)

    setStatus("Training {}".format(prefix))
    model.fit(trainData, trainLabels, epochs=epochs, batch_size=32, callbacks=[logger])
    utility.saveModel(model, modelPath)
    return model


@socket.on("start_train")
def train():
    logger = KerasLogger(socket, "add_metropolis_info")

    setStatus("Initializing training")
    path = createPaths()
    raw = pandas.read_hdf(join(path["base"], "{}.h5".format(datafile)))
    rawBuy = raw["Buy"]
    # rawSell = raw["Sell"]

    setStatus("Creating training data")
    bid = utility.createData(rawBuy, path, "bid", 5)
    # ask = utility.createData(rawSell, path, "ask", 5)

    bidModel = trainModel(bid, path, "bid", logger)
    # sellModel = trainModel(ask, path, "ask", logger)

    setStatus("Creating predictions")
    createPredictions(bidModel, bid, path, name, "bid")
    # createPredictions(sellModel, ask, path, name, "ask")

    setStatus("Idle")

@socket.on("set_model_name")
def setModelName(newName):
    global name
    name = newName

@socket.on("set_epochs")
def setEpochs(newValue):
    global epochs
    epochs = newValue

@socket.on("delete_model")
def deleteModel(name):
    path = createPaths()
    setStatus("Deleting model")
    files = []
    files.append(join(path["prediction"], "{}-{}.h5".format("bid", name)))
    # files.append(join(path["prediction"], "{}-{}.h5".format("ask", name)))

    dirs = []
    dirs.append(path["model"])

    for filename in files:
        if not isfile(filename):
            print("Could not find filename: {}".format(filename))
            continue
        os.remove(filename)

    for dirname in dirs:
        if not os.path.exists:
            print("Could not find directory: {}".format(dirname))
            continue
        shutil.rmtree(dirname)

    setStatus("Idle")

@socket.on("set_datafile")
def setDatafile(newDatafile):
    global datafile
    datafile = newDatafile

if __name__ == "__main__":
    socket.run(app)
