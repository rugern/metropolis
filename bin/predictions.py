import numpy

def createPredictions(model, data):
    printIntervals = 10
    predictions = numpy.zeros((data.shape[0]))
    modulo = predictions.shape[0] // printIntervals
    print("Creating predictions...")
    for i in range(0, predictions.shape[0]):
        predictions[i] = model.predict(data[i].reshape(1, data.shape[1], data.shape[2]))
        if i % modulo == 0:
            print("Progress: {}/{}".format(i, predictions.shape[0]))
    print("Progress: {}/{}".format(predictions.shape[0], predictions.shape[0]))
    print("Finished creating predictions")
    return predictions

# if __name__ == "__main__":
    # number = 1
    # inputName = "model/testmodel{}".format(number)

    # raw = pandas.read_hdf("data/EUR_USD_2017/EUR_USD_2017_01.hdf5")
    # trainData, trainLabels, testData, testLabels, testLabelDt = utility.createData(raw, 5)
    # model = utility.getModel(trainData, inputName)

    # predictions = createPredictions(model, testData)

    # assert len(predictions) == len(testLabels) == len(testLabelDt)
    # utility.saveToHdf("predictions/predictions{}.h5".format(number), predictions)
    # utility.saveToHdf("predictions/labels{}.h5".format(number), testLabels)
