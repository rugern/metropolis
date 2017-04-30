from os.path import join
import numpy
import utility

def createPredictions(model, dataset, path, name, prefix):
    data = dataset["test"]["data"] 
    labels = dataset["test"]["labels"] 
    dt = dataset["test"]["labelDt"]
    scale = dataset["scales"][3]

    predictions = model.predict(data)
    predictions = utility.inverse_normalize(predictions, [scale for i in range(predictions.shape[1])])

    assert len(predictions) == len(labels) == len(dt)
    utility.assertOrCreateDirectory(path["prediction"])
    for i in range(predictions.shape[1]):
        utility.saveToHdf(join(path["prediction"], "{}-{}-{}.h5".format(prefix, i, name)), predictions[:, i])

    return predictions

# if __name__ == "__main__":
    # number = 1
    # inputName = "model/testmodel{}".format(number)

    # raw = pandas.read_hdf("data/EUR_USD_2017/EUR_USD_2017_01.hdf5")
    # trainData, trainLabels, data, testLabels, testLabelDt = utility.createData(raw, 5)
    # model = utility.getModel(trainData, inputName)

    # predictions = createPredictions(model, testData)

    # assert len(predictions) == len(testLabels) == len(testLabelDt)
    # utility.saveToHdf("predictions/predictions{}.h5".format(number), predictions)
    # utility.saveToHdf("predictions/labels{}.h5".format(number), testLabels)
