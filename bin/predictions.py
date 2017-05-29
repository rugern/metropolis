from os.path import join

from utility import assertOrCreateDirectory, splice, saveToHdf
from data import inverse_normalize

def createPredictions(model, dataset, path, name, prefix):
    print('Create predictions')
    data = dataset["test"]["data"]
    labels = dataset["test"]["labels"]
    dt = dataset["dt"]
    scale = dataset["scales"][dataset['labelColumn']]

    print('Predict..')
    predictions = model.predict(data)
    predictions = inverse_normalize(
        predictions,
        [scale for i in range(predictions.shape[1])]
    )
    print('Assert len')
    assert len(predictions) == len(labels)

    print('Create path')
    assertOrCreateDirectory(path["prediction"])
    lookforward = predictions.shape[1]
    for i in range(lookforward):
        print('Create number {}'.format(i))
        currentPrediction = splice(predictions[:, i], lookforward - 1, 0) # Show info available at each timestep
        # currentPrediction = splice(predictions[:, i], lookforward - 1 - i, -i) # Shift values to correct timestep
        print('Assert length again')
        assert len(dt) == len(currentPrediction)
        saveToHdf(join(
            path["prediction"], "{}-{}-{}.h5".format(prefix, i, name)
        ), currentPrediction)

    return predictions
