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
    print("Reading CSV")
    raw = readCsv("krakenEUR.csv")

    print("Filtering by date")
    filtered = raw[(raw.index.year == 2016)]

    print("Sampling data")
    sampled = sample(filtered)

    print("Writing to HDF5")
    writeData("data.hdf5", sampled)

    print("Complete!")

