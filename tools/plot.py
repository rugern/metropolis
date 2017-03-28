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

def plotN(args):
    name = args[1:]
    for i in range(len(name)):
        assertExists(name[i])

    for i in range(len(name)):
        data = readHdf(name[i])
        pyplot.plot(data, label=name[i])

    pyplot.legend()
    pyplot.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Datafile required")
        sys.exit(1)

    plotN(sys.argv)
