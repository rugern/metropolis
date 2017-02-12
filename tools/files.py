import os
import sys
import numpy
import pandas
import datetime

def dateparse(timestamp):    
    return datetime.datetime.fromtimestamp(float(timestamp))

def sample(data):
    return data.resample("10min").ohlc()

def readCsv(infile):
    return pandas.read_csv(infile, usecols=[0, 1], header=None, names=["DateTime", "Buy"], index_col=0, parse_dates=True, date_parser=dateparse)

def readHdf(infile):
    return pandas.read_hdf(infile, key="bitcoin")

def writeData(outfile, data):
    data.to_hdf(outfile, key="bitcoin")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Input and output name required")
        sys.exit(1)

    inputName = sys.argv[1]
    outputName = sys.argv[2]
    if not os.path.isfile(inputName):
        print("Could not find datafile: {}".format(inputName))
        sys.exit(1)

    if os.path.isfile(outputName):
        answer = input("The file '{}' already exists. Are you sure you want to overwrite (y/n)?")
        if answer != "y":
            print("No changes made")
            sys.exit(0)

    print("Reading CSV")
    raw = readCsv(inputName)

    print("Filtering by date")
    filtered = raw.ix["2016-07-01":"2016-07-31"]

    print("Sampling data")
    sampled = sample(filtered)

    print("Writing to HDF5")
    writeData(outputName, sampled)

    print("Complete!")

