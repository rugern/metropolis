import json
import os
from keras.layers import Input, Dense, LSTM, Dropout, Reshape
from keras.models import Model

from utility import assertOrCreateDirectory

def saveModel(model, outputName):
    if outputName is None:
        return
    print('Saving model weights...')
    model.save_weights(outputName + '.h5', overwrite=True)
    with open(outputName + '.json', 'w') as outfile:
        json.dump(model.to_json(), outfile)
    print('Finished saving model weights')

def loadWeights(model, name):
    name += '.h5'
    print('Loading saved model weights...')
    if os.path.isfile(name):
        model.load_weights(name)
    else:
        print('Sorry bro, could not find the weights file: {}'.format(name))

def createModel(
        optimizer='Nadam',
        dropout=0.2,
        neurons=100,
        activation='softsign',
        loss='mean_squared_logarithmic_error',
        **kwargs
):
    options = {
        'features': 20,
        'outputs': 20,
        'batchSize': 32,
    }
    for key in kwargs:
        options[key] = kwargs[key]

    features = options['features']

    # inputs = Input(shape=(inData.shape[1], inData.shape[2]))
    # inputs = Input(shape=(options['timesteps'], features))
    inputs = Input(batch_shape=(options['batchSize'], 1, features))

    x = LSTM(features, stateful=True, return_sequences=True)(inputs)
    x = Dropout(dropout)(x)
    x = LSTM(neurons, stateful=True, return_sequences=False)(inputs)
    x = Dropout(dropout)(x)

    x = Dense(neurons, activation=activation)(x)
    x = Dropout(dropout)(x)

    outputs = Dense(options['outputs'], activation='sigmoid')(x)

    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    return model

def loadModel(path, **kwargs):
    options = {
        'prefix': 'bid',
    }
    for key in kwargs:
        options[key] = kwargs[key]

    modelPath = os.path.join(path['model'], options['prefix'])
    assertOrCreateDirectory(path['model'])
    model = createModel(**kwargs)
    loadWeights(model, modelPath)
    return model
