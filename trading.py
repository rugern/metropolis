import talib

def createIndicators(prices):
    return talib.SMA(prices)
