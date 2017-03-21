import numpy
import talib

longestPeriod = 5

def createIndicators(prices):
    # sma = talib.SMA(prices)
    # real = talib.EMA(prices, timeperiod=30)
    # macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(prices[:, 3], timeperiod=longestPeriod, nbdevup=2, nbdevdn=2, matype=0)
    
    # return numpy.column_stack((sma, real, macd, macdsignal, macdhist, upperband, middleband, lowerband)), longestPeriod
    return numpy.column_stack((prices, upperband, middleband, lowerband)), longestPeriod

