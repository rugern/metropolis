import h5py
import json
import time
from os import listdir
from os.path import isfile, join
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
import eventlet

eventlet.monkey_patch()
app = Flask(__name__)
# CORS(app)
socket = SocketIO(app)

successResponse = {
    "success": True,
    "text": "The operation was successful",
    "statusCode": 200
}

def readHdf(name):
    infile = h5py.File(name, "r")
    data = infile["data"][:]
    if len(data.shape) > 1:
        data = data[:, 3]
    infile.close()
    return data

def readJson(path):
    data = None
    with open(path, "r") as infile:
        data = json.load(infile)
    return data

def writeJson(path, data):
    with open(path, "w") as outfile:
        json.dump(data, outfile)

def getDirectoryList(path):
    filenames = [name for name in listdir(path) if isfile(join(path, name))]
    return filenames

# @app.route("/run", methods=["POST"])
# def run():
    # return jsonify(successResponse)

# @app.route("/results", methods=["GET"])
# def getResults():
    # if "name" in request.args:
        # result = readHdf("results/{}".format(request.args["name"])).tolist()
        # return jsonify(result)
    # resultNames = getDirectoryList("results/")
    # return jsonify(resultNames)

@socket.on("connect")
def connected():
    print("Client connected")

@socket.on("plots")
def emitPlot():
    emit("plots", getDirectoryList("results/"))

@socket.on("plot")
def emitPlotData(data):
    print(data)
    emit("plot", readHdf("results/{}".format(data)).tolist())

if __name__ == "__main__":
    socket.run(app)

