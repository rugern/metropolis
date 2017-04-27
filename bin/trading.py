import numpy
import talib


def createIndicators(prices, datetimes):
    # openPrice, highPrice, lowPrice, closePrice = prices[:]
    openPrice = prices[:, 0]
    highPrice = prices[:, 1]
    lowPrice = prices[:, 2]
    closePrice = prices[:, 3]

    # sma = talib.SMA(prices)
    ema = talib.EMA(closePrice, timeperiod=20)
    # macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, \
                                            # signalperiod=9)
    upperband, middleband, lowerband = \
        talib.BBANDS(closePrice, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    rsi = talib.RSI(closePrice, timeperiod=14)
    adx = talib.ADX(highPrice, lowPrice, closePrice, timeperiod=14)
    slowk, slowd = \
        talib.STOCH(highPrice, lowPrice, closePrice, fastk_period=5, \
                    slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    
    values = numpy.column_stack((prices, ema, rsi, upperband, middleband, \
                                 lowerband, adx, slowk, slowd))
    names = ["open", "high", "low", "close", "ema", "rsi", "upperband", \
             "middleband", "lowerband", "adx", "slowk", "slowd"]

    index = -1
    for row in values:
        index += 1
        if not numpy.isnan(row).any():
            break

    return values[index:], datetimes[index:], names



