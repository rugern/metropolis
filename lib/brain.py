"""Performs data prosessing."""

import matplotlib.pyplot as pyplot
import pandas
from talib import abstract


def createIndicators(dataframes):
    """Creates all indicators."""
    result = abstract.SMA(dataframes['buy'], timeperiod=100).to_frame('SMA') \
        .join(abstract.BBANDS(dataframes['buy'], timeperiod=200, nbdevup=2,
                              nbdevdn=2, matype=0))

    return result


def plot(data):
    """Plots dataframe with datetime as index."""
    pyplot.plot(data)
    pyplot.show()


def load(filename):
    """Reads HDF5 file named 'filename'."""
    return pandas.read_hdf(filename)
