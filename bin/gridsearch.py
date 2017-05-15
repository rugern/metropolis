from os.path import join
import pandas
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier

import utility

datafile = 'EUR_USD_2017_1_10m'
baseFolder = 'data'
name = 'Test'

if __name__ == '__main__':
    path = utility.createPaths(baseFolder, datafile, name)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))
    rawBid = raw['Bid']
    bid = utility.createData(rawBid, 10, 5)
    trainData = bid['train']['data']
    trainLabels = bid['train']['labels']

    model = KerasClassifier(build_fn=utility.createModel, verbose=1)
    batch_size = [10, 20]
    epochs = [1, 2]
    param_grid = dict(batch_size=batch_size, epochs=epochs)
    grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
    grid_result = grid.fit(trainData, trainLabels)

    print('Best: %f using %s' % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print('%f (%f) with: %r' % (mean, stdev, param))
