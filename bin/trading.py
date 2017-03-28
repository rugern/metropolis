import numpy
import talib


def createIndicators(prices):
    # sma = talib.SMA(prices)
    ema = talib.EMA(prices[:, 3], timeperiod=20)
    # macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(prices[:, 3], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    rsi = talib.RSI(prices[:, 3], timeperiod=14)
    
    # return numpy.column_stack((sma, real, macd, macdsignal, macdhist, upperband, middleband, lowerband)), longestPeriod
    return numpy.column_stack((prices, ema, rsi, upperband, middleband, lowerband)), 20


