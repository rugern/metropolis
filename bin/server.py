import numpy
import pandas
import eventlet
from flask import Flask
from flask_socketio import SocketIO, emit

import utility
from utility import readHdf, getDirectoryList
from predictions import createPredictions

# eventlet.monkey_patch()
app = Flask(__name__)
socket = SocketIO(app)

status = "Idle"
name = "1"
dataFile = "data/EUR_USD_2017/EUR_USD_2017_01.hdf5"
epochs = 1

def calculateDatetimeRange(start, end, dt):
    offset = dt.index(min(dt, key=lambda x: abs(x - start)))
    limit = dt.index(min(dt, key=lambda x: abs(x - end))) - offset
    return offset, limit

def getData(dataType, offset, limit):
    data = {}
    names = getDirectoryList("{}/".format(dataType))
    for name in names:
        data[name] = {}
        data[name]["data"] = readHdf("{}/{}".format(dataType, name)).tolist()[offset:offset+limit]
    return data

def setStatus(newStatus):
    global status
    status = newStatus
    emitStatus()

@socket.on("get_data")
def emitData(options):
    datetimes = numpy.array(readHdf("labels/datetimes.h5"), dtype="datetime64[m]").tolist()
    # endTime = options["endTime"] if "endTime" in options else datetimes[-1]
    # startTime = options["startTime"] if "startTime" in options else datetimes[-min(len(datetimes), 1000)]
    limit = options["limit"] if "limit" in options else 200
    offset = options["offset"] if "offset" in options else len(datetimes) - limit
    offset = max(0, offset)
    limit = min(len(datetimes) - offset, limit)
    labels = numpy.array(datetimes, dtype=numpy.dtype("str")).tolist()[offset:offset+limit]

    data = {}
    data["labels"] = labels
    data["indicators"] = getData("indicators", offset, limit)
    data["predictions"] = getData("predictions", offset, limit)

    emit("set_data", data)

@socket.on("get_metropolis_status")
def emitStatus():
    emit("set_metropolis_status", status)

@socket.on("start_train")
def train():
    setStatus("Initializing training")
    raw = pandas.read_hdf(dataFile)
    trainData, trainLabels, testData, testLabels, testLabelDt = utility.createData(raw, 5)
    model = utility.getModel(trainData, "model/testmodel{}.h5".format(name))

    setStatus("Training")
    model.fit(trainData, trainLabels, epochs=epochs, batch_size=32)
    utility.saveModel(model, "model/testmodel{}.h5".format(name))

    setStatus("Creating predictions")
    predictions = createPredictions(model, testData)

    assert len(predictions) == len(testLabels) == len(testLabelDt)
    utility.saveToHdf("predictions/predictions{}.h5".format(name), predictions)
    utility.saveToHdf("predictions/labels{}.h5".format(name), testLabels)

    setStatus("Idle")

@socket.on("set_model_name")
def setModelName(newName):
    global name
    name = newName

@socket.on("set_epochs")
def setEpochs(newValue):
    global epochs
    epochs = newValue

if __name__ == "__main__":
    socket.run(app)
