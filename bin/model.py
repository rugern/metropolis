import json
import os
from keras.layers import Input, Dense, LSTM, Dropout
from keras.models import Model

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
        optimizer='Adam',
        dropout=0.01,
        neurons=200,
        activation='linear',
        loss='mean_squared_logarithmic_error',
        **kwargs
):
    options = {
        'lookforward': 20,
        'features': 14,
        'outputs': 5,
    }
    for key in kwargs:
        options[key] = kwargs[key]


    # model = Sequential()
    # model.add(Dense(hiddenSize, input_dim=features, activation='relu'))
    # model.add(Dense(hiddenSize, activation='relu'))
    # model.add(Dense(features, activation='sigmoid'))
    # model.compile(sgd(lr=0.2), 'mse')

    # inputs = Input(shape=(inData.shape[1], inData.shape[2]))
    inputs = Input(shape=(options['lookforward'], options['features']))
    x = LSTM(options['features'])(inputs)
    x = Dropout(dropout)(x)
    x = Dense(neurons, activation=activation)(x)
    x = Dropout(dropout)(x)
    x = Dense(neurons, activation=activation)(x)
    x = Dropout(dropout)(x)
    outputs = Dense(options['outputs'], activation='sigmoid')(x)
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'])
    return model
