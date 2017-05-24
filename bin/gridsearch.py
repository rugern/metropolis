from os.path import join
import pandas
from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasRegressor
from keras.models import Sequential

import utility

datafile = 'EUR_USD_2017_10-3_30m'
baseFolder = 'data'
name = 'Test'

class CustomKerasRegressor(KerasRegressor):
    def score(self, x, y, **kwargs):
        '''
        Override maximizing score function with minimizing
        '''
        kwargs = self.filter_sk_params(Sequential.evaluate, kwargs)
        loss = self.model.evaluate(x, y, **kwargs)
        if isinstance(loss, list):
            return -loss[0]
        return -loss

if __name__ == '__main__':
    path = utility.createPaths(baseFolder, datafile, name)
    raw = pandas.read_hdf(join(path['base'], '{}.h5'.format(datafile)))
    rawBid = raw['Bid']
    bid = utility.createData(rawBid, 20, 5)
    trainData = bid['train']['data']
    trainLabels = bid['train']['labels']

    batch_size = [10, 20, 30]
    optimizer = ['SGD', 'RMSprop', 'Adagrad', 'Adadelta', 'Adam', 'Adamax', 'Nadam']
    dropout = [0.01, 0.05, 0.1]
    neurons = [180, 200, 220, 240, 260]
    loss = [
        'mean_squared_error',
        'mean_absolute_error',
        'mean_absolute_percentage_error',
        'mean_squared_logarithmic_error',
        'squared_hinge',
        'hinge',
        'logcosh',
        # 'kullback_leibler_divergence', #negative value
        'poisson',
        # 'cosine_proximity', #negative value
    ]
    activation = [
        'softmax',
        'elu',
        'softplus',
        'softsign',
        'relu',
        'tanh',
        # 'sigmoid',
        # 'hard_sigmoid',
        'linear',
    ]
    param_grid = dict(
        # batch_size=batch_size,
        # optimizer=optimizer,
        # dropout=dropout,
        # neurons=neurons,
        # loss=loss,
        activation=activation,
    )

    model = CustomKerasRegressor(build_fn=utility.createModel, epochs=2,
                                 batch_size=10, verbose=0)
    grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
    grid_result = grid.fit(trainData, trainLabels)

    print('Best: %f using %s' % (grid_result.best_score_, grid_result.best_params_))
    means = grid_result.cv_results_['mean_test_score']
    stds = grid_result.cv_results_['std_test_score']
    params = grid_result.cv_results_['params']
    for mean, stdev, param in zip(means, stds, params):
        print('%f (%f) with: %r' % (mean, stdev, param))
