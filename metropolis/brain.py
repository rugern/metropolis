"""Performs data prosessing."""

import pandas
from talib import abstract


def createIndicators():
    """Creates all indicators."""
    dataframes = load('result_15.h5')
    result = abstract.SMA(dataframes['buy'], timeperiod=100).to_frame('SMA') \
        .join(abstract.BBANDS(dataframes['buy'], timeperiod=200, nbdevup=2,
                              nbdevdn=2, matype=0))

    csv = result.to_csv()
    print(csv)
    return csv


def load(filename):
    """Reads HDF5 file named 'filename'."""
    return pandas.read_hdf(filename)
