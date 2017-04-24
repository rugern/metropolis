import os
from os.path import join
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
    return pandas.read_csv(infile, usecols=[3, 4, 5], header=0, names=["DateTime", "Bid", "Ask"], index_col=0, parse_dates=True)

def writeData(outfile, data):
    data.to_hdf(outfile, key="bitcoin")

if __name__ == "__main__":
    inputNames = [
        # "raw/EUR_USD_2016/october/EUR_USD_Week1.csv",
        # "raw/EUR_USD_2016/october/EUR_USD_Week2.csv",
        # "raw/EUR_USD_2016/october/EUR_USD_Week3.csv",
        # "raw/EUR_USD_2016/october/EUR_USD_Week4.csv",
        # "raw/EUR_USD_2016/october/EUR_USD_Week5.csv",
        # "raw/EUR_USD_2016/november/EUR_USD_Week2.csv",
        # "raw/EUR_USD_2016/november/EUR_USD_Week3.csv",
        # "raw/EUR_USD_2016/november/EUR_USD_Week4.csv",
        # "raw/EUR_USD_2016/november/EUR_USD_Week5.csv",
        # "raw/EUR_USD_2016/december/EUR_USD_Week1.csv",
        # "raw/EUR_USD_2016/december/EUR_USD_Week2.csv",
        # "raw/EUR_USD_2016/december/EUR_USD_Week3.csv",
        # "raw/EUR_USD_2016/december/EUR_USD_Week4.csv",
        "raw/EUR_USD_2017/january/EUR_USD_Week1.csv",
        "raw/EUR_USD_2017/january/EUR_USD_Week2.csv",
        "raw/EUR_USD_2017/january/EUR_USD_Week3.csv",
        "raw/EUR_USD_2017/january/EUR_USD_Week4.csv",
        "raw/EUR_USD_2017/january/EUR_USD_Week5.csv",
        # "raw/EUR_USD_2017/february/EUR_USD_Week1.csv",
        # "raw/EUR_USD_2017/february/EUR_USD_Week2.csv",
        # "raw/EUR_USD_2017/february/EUR_USD_Week3.csv",
        # "raw/EUR_USD_2017/february/EUR_USD_Week4.csv",
        # "raw/EUR_USD_2017/march/EUR_USD_Week1.csv",
        # "raw/EUR_USD_2017/march/EUR_USD_Week2.csv",
        # "raw/EUR_USD_2017/march/EUR_USD_Week3.csv",
        # "raw/EUR_USD_2017/march/EUR_USD_Week4.csv",
    ]
    # inputNames = [
        # "data/EUR_BITCOIN_2016/krakenEUR.csv",
    # ]
    dataname = "EUR_USD_2017_1_1m"
    outputFolder = join("data", dataname)
    outputPath = join(outputFolder, "{}.h5".format(dataname))

    for inputName in inputNames:
        if not os.path.isfile(inputName):
            print("Could not find datafile: {}".format(inputName))
            sys.exit(1)

    if not os.path.exists(outputFolder):
        print("Creating directory '{}'".format(outputFolder))
        os.makedirs(outputFolder)
    elif os.path.isfile(outputPath):
        answer = input("".join(["The file '{}' already exists. Are you sure you want to ",
                       "overwrite (y/n)?"]).format(outputPath))
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
    sampled = sample(filtered, "1 min", True)

    print("Writing to HDF5")
    writeData(outputPath, sampled)

    print("Complete!")

