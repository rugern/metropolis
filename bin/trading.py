import numpy
import talib

longestPeriod = 33 # Hvorfor 33 og ikke 30? macd gjør noe rart

def createIndicators(prices):
    sma = talib.SMA(prices)
    real = talib.EMA(prices, timeperiod=30)
    macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    upperband, middleband, lowerband = talib.BBANDS(prices, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    
    return numpy.column_stack((sma, real, macd, macdsignal, macdhist, upperband, middleband, lowerband)), longestPeriod

