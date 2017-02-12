import os
import sys
import pandas
from matplotlib import pyplot

def plot(inputName):
    data = pandas.read_hdf(inputName).dropna()
    pyplot.plot(data)
    pyplot.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Datafile required")
        sys.exit(1)

    inputName = sys.argv[1]
    if not os.path.isfile(inputName):
        print("Could not find datafile: {}".format(inputName))
        sys.exit(1)

    plot(inputName)
