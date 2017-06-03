import json
import os
from os import listdir
from os.path import isfile, join
import h5py

def splice(values, start, end):
    return values[start:end] if end != 0 else values[start:]

def assertOrCreateDirectory(path):
    if not os.path.exists(path):
        print('Creating directory "{}"'.format(path))
        os.makedirs(path)


def getFileList(path, pattern=None, filetype=None):
    if not os.path.exists(path):
        return []
    filenames = [name for name in listdir(path) if isfile(join(path, name))]
    if filetype is not None:
        filenames = list(filter(lambda filename: filetype in filename, filenames))
    if pattern is not None:
        filenames = list(filter(lambda filename: pattern in filename, filenames))
    return filenames

def getDirectoryList(path):
    if not os.path.exists(path):
        return []
    folderNames = [name for name in listdir(path) if not isfile(join(path, name))]
    return folderNames

def saveToHdf(filename, data):
    print('Saving to {}'.format(filename))
    output = h5py.File(filename, 'w')
    output.create_dataset('data', data=data)
    output.close()

def readHdf(name, column=None):
    if not isfile(name):
        return []
    infile = h5py.File(name, 'r')
    data = infile['data'][:]
    if column is not None and data.shape[1] > column:
        data = data[:, column]
    infile.close()
    return data

def readJson(path):
    data = None
    with open(path, 'r') as infile:
        data = json.load(infile)
    return data

def writeJson(path, data):
    with open(path, 'w') as outfile:
        json.dump(data, outfile)

def createPaths(base, dataName, modelName=None):
    paths = {
        'base': base,
        'data': join(base, dataName),
        'prediction': join(base, dataName, 'predictions'),
        'indicator': join(base, dataName, 'indicators'),
        'model': '',
    }
    if modelName is not None:
        paths['model'] = join(base, dataName, 'models', modelName)
    return paths
