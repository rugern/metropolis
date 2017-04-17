import os
from os.path import isfile, join
import numpy
import pandas
from flask import Flask
from flask_socketio import SocketIO, emit

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

def createPaths():
    return {
        "base": join(baseFolder, datafile),
        "prediction": join(baseFolder, datafile, "predictions"),
        "indicator": join(baseFolder, datafile, "indicators"),
        "model": join(baseFolder, datafile, "models"),
        "label": join(baseFolder, datafile, "labels")
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
    datetimes = numpy.array(readHdf(join(path["label"], "datetimes.h5")), dtype="datetime64[m]").tolist()
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
    data["models"] = getFileList(path["model"], ".h5")
    data["datafiles"] = getDirectoryList(baseFolder)
    data["datafile"] = datafile
    data["datasize"] = len(datetimes)

    emit("set_data", data)

@socket.on("get_metropolis_status")
def getStatus():
    emitStatus()

@socket.on("start_train")
def train():
    setStatus("Initializing training")
    path = createPaths()
    raw = pandas.read_hdf(join(path["base"], "{}.h5".format(datafile)))

    setStatus("Creating training data")
    trainData, trainLabels, testData, testLabels, testLabelDt, scales = utility.createData(raw, path, 5)
    model = utility.getModel(trainData, join(path["model"], name))

    setStatus("Training")
    model.fit(trainData, trainLabels, epochs=epochs, batch_size=32)
    utility.saveModel(model, join(path["model"], name))

    setStatus("Creating predictions")
    predictions = createPredictions(model, testData)
    predictions = utility.inverse_normalize(predictions, scales[3])

    assert len(predictions) == len(testLabels) == len(testLabelDt)
    utility.saveToHdf(join(path["prediction"], "{}.h5".format(name)), predictions)

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
    files.append(join(path["model"], "{}.h5".format(name)))
    files.append(join(path["model"], "{}.json".format(name)))
    files.append(join(path["prediction"], "{}.h5".format(name)))
    for filename in files:
        if not isfile(filename):
            print("Could not find filename: {}".format(filename))
            continue
        os.remove(filename)
    setStatus("Idle")

@socket.on("set_datafile")
def setDatafile(newDatafile):
    global datafile
    datafile = newDatafile
    paths = createPaths()
    for key, path in paths.items():
        if not os.path.exists(path):
            print("Creating directory '{}'".format(path))
            os.makedirs(path)

if __name__ == "__main__":
    socket.run(app)
