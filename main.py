import json
from os import listdir
from os.path import isfile, join
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

successResponse = {
    "success": True,
    "text": "The operation was successful",
    "statusCode": 200
}
activeConfig = "";


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


@app.route("/configs", methods=["GET", "POST"])
def configuration():
    configPath = None
    if "name" in request.args:
        activeConfig = request.args["name"]
        configPath = "./config/" + activeConfig

    if request.method == "POST":
        writeJson(configPath, request.get_json())
        return jsonify(successResponse)

    if configPath is None:
        return jsonify({ "configs": getDirectoryList("./config") })
    return jsonify(readJson(configPath))


@app.route("/run", methods=["POST"])
def run():
    return jsonify(successResponse)


@app.route("/save", methods=["POST"])
def save():
    return jsonify(successResponse)


@app.route("/reset", methods=["POST"])
def reset():
    return jsonify(successResponse)


if __name__ == "__main__":
    app.run()

