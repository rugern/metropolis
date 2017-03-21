import os
import sys
import h5py
from matplotlib import pyplot

def assertExists(name):
    if not os.path.isfile(name):
        print("Could not find datafile: {}".format(name))
        sys.exit(1)

def readHdf(name):
    infile = h5py.File(name, "r")
    data = infile["data"][:]
    if len(data.shape) > 1:
        data = data[:, 3]
    infile.close()
    return data

def plotSingle(args):
    name = args[1]
    data = readHdf(name)
    pyplot.plot(data)
    pyplot.show()

def plotDouble(args):
    first, second = args[1:]
    assertExists(first)
    assertExists(second)
    firstData = readHdf(first)
    secondData = readHdf(second)
    firstPlot = pyplot.plot(firstData, label=first)
    secondPlot = pyplot.plot(secondData, label=second)
    pyplot.legend()
    pyplot.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Datafile required")
        sys.exit(1)
    elif len(sys.argv) == 2:
        plotSingle(sys.argv)
    elif len(sys.argv) == 3:
        plotDouble(sys.argv)
    else:
        print("Does not support so many arguments")
