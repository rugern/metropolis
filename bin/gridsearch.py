import utility

from sklearn.model_selection import GridSearchCV
from keras.wrappers.scikit_learn import KerasClassifier

datafile = 'EUR_USD_2017_1_10m'
baseFolder = 'data'
name = 'Test'

if __name__ == '__main__':
    path = utility.createPaths(baseFolder, datafile, name)
    raw = pandas.read_hdf(join(path["base"], "{}.h5".format(datafile)))
    rawBid = raw["Bid"]
    bid = utility.createData(rawBid, 10, 5, path, "bid", True)
    utility.getModel(trainData, trainLabels, modelPath)

    model = KerasClassifier(build_fn=create_model, verbose=0)
    grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1)
    grid_result = grid.fit(X, Y)

