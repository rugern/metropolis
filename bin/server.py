import os
from os.path import isfile, join
import numpy
import pandas
import eventlet
from flask import Flask
from flask_socketio import SocketIO, emit

import utility
from utility import readHdf, getFileList, getDirectoryList
from predictions import createPredictions

# eventlet.monkey_patch()
app = Flask(__name__)
socket = SocketIO(app)

status = "Idle"
name = "model"
dataFile = "EUR_USD_2017_01"
epochs = 1
baseFolder = "data"

def createPaths():
    return {
        "base": join(baseFolder, dataFile),
        "prediction": join(baseFolder, dataFile, "predictions"),
        "indicator": join(baseFolder, dataFile, "indicators"),
        "model": join(baseFolder, dataFile, "models"),
        "label": join(baseFolder, dataFile, "labels")
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

def setStatus(newStatus):
    global status
    status = newStatus
    emitStatus()

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
    data["data"] = getDirectoryList(baseFolder)

    emit("set_data", data)

@socket.on("get_metropolis_status")
def emitStatus():
    emit("set_metropolis_status", status)

@socket.on("start_train")
def train():
    path = createPaths()
    raw = pandas.read_hdf(join(path["base"], "{}.h5".format(dataFile)))
    trainData, trainLabels, testData, testLabels, testLabelDt = utility.createData(raw, path, 5)
    model = utility.getModel(trainData, join(path["model"], name))

    model.fit(trainData, trainLabels, epochs=epochs, batch_size=32)
    utility.saveModel(model, join(path["model"], name))

    predictions = createPredictions(model, testData)

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

if __name__ == "__main__":
    socket.run(app)
