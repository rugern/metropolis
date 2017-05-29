from os.path import join

from utility import assertOrCreateDirectory, saveToHdf

def createPredictions(model, dataset, path, **kwargs):
    options = {
        'prefix': 'bid',
        'batchSize': 32,
    }
    for key in kwargs:
        options[key] = kwargs[key]

    print('Create predictions')
    x = dataset['testX']
    # scales = dataset['scales']
    names = dataset['names']

    print('Predict..')
    predictions = model.predict(x)
    assert predictions.shape[0] == x.shape[0]
    # predictions = inverse_normalize(
        # predictions,
        # [scale for i in range(predictions.shape[1])]
    # )

    print('Create path')
    assertOrCreateDirectory(path["prediction"])
    for i in range(predictions.shape[1]):
        print('Create number {}'.format(i))
        # currentPrediction = splice(predictions[:, i], lookforward - 1 - i, -i) # Shift values to correct timestep
        saveToHdf(join(
            path["prediction"], "{}-{}.h5".format(options['prefix'], names[i])
        ), predictions[:, i])

    return predictions
