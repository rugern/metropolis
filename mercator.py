import pandas
import matplotlib.pyplot as pyplot
from talib import abstract


def main():
    dataframes = pandas.read_hdf('result_15.h5')

    sma = abstract.SMA(dataframes['buy'], timeperiod=100)
    bollinger = abstract.BBANDS(dataframes['buy'], timeperiod=200, nbdevup=2,
                                nbdevdn=2, matype=0)

    # pyplot.plot(dataframes[('buy', 'close')])
    # pyplot.plot(sma)
    pyplot.plot(bollinger['upperband'], 'b')
    pyplot.plot(bollinger['middleband'], 'r')
    pyplot.plot(bollinger['lowerband'], 'g')

    pyplot.show()


if __name__ == '__main__':
    main()
