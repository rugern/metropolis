import pandas
import matplotlib.pyplot as pyplot
from talib import abstract


def main():
    dataframes = pandas.read_hdf('result_15.h5')

    buy_opens = dataframes[('buy', 'open')]
    pyplot.plot(buy_opens)

    test = dataframes['buy']
    output = abstract.SMA(test, timeperiod=100)
    pyplot.plot(output)

    pyplot.show()


if __name__ == '__main__':
    main()
