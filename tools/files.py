import os
import sys
import numpy
import pandas
import datetime

def dateparse(timestamp):    
    return datetime.datetime.fromtimestamp(float(timestamp))

def sample(data, interval, pad=False):
    result = data.resample(interval).ohlc()
    if pad:
        return result.fillna(method="pad")
    return result

def readCsv(infile):
    # return pandas.read_csv(infile, usecols=[0, 1], header=None, names=["DateTime", "Buy"], index_col=0, parse_dates=True, date_parser=dateparse)
    return pandas.read_csv(infile, usecols=[3, 4], header=0, names=["DateTime", "Buy"], index_col=0, parse_dates=True)

def readHdf(infile):
    return pandas.read_hdf(infile, key="bitcoin")

def writeData(outfile, data):
    data.to_hdf(outfile, key="bitcoin")

if __name__ == "__main__":
    inputNames = [
        "data/EUR_USD_2017/EUR_USD_Week1.csv",
        "data/EUR_USD_2017/EUR_USD_Week2.csv",
        "data/EUR_USD_2017/EUR_USD_Week3.csv",
        "data/EUR_USD_2017/EUR_USD_Week4.csv",
        "data/EUR_USD_2017/EUR_USD_Week5.csv",
    ]
    # inputNames = [
        # "data/EUR_BITCOIN_2016/krakenEUR.csv",
    # ]
    outputName = "data/EUR_USD_2017/EUR_USD_2017_01.hdf5"

    for inputName in inputNames:
        if not os.path.isfile(inputName):
            print("Could not find datafile: {}".format(inputName))
            sys.exit(1)

    if os.path.isfile(outputName):
        answer = input("".join(["The file '{}' already exists. Are you sure you want to ",
                       "overwrite (y/n)?"]).format(outputName))
        if answer != "y":
            print("No changes made")
            sys.exit(0)

    print("Reading CSV")
    raws = map(readCsv, inputNames)
    raw = pandas.concat(raws)

    # print("Filtering by date")
    # filtered = raw.ix["2016-07-01":"2016-07-31"]
    filtered = raw

    print("Sampling data")
    sampled = sample(filtered, "10 min", True)

    print("Writing to HDF5")
    writeData(outputName, sampled)

    print("Complete!")

