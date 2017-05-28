import numpy
import talib


def createIndicators(prices, datetimes):
    # openPrice = prices[:, 0]
    highPrice = prices[:, 1]
    lowPrice = prices[:, 2]
    closePrice = prices[:, 3]

    # sma = talib.SMA(prices)
    emaShort = talib.EMA(closePrice, timeperiod=5)
    emaMedium = talib.EMA(closePrice, timeperiod=10)
    emaLong = talib.EMA(closePrice, timeperiod=20)
    # macd, macdsignal, macdhist = talib.MACD(prices, fastperiod=12, slowperiod=26, \
                                            # signalperiod=9)
    upperband, middleband, lowerband = \
        talib.BBANDS(closePrice, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    rsi = talib.RSI(closePrice, timeperiod=14)
    adx = talib.ADX(highPrice, lowPrice, closePrice, timeperiod=14)
    slowk, slowd = \
        talib.STOCH(highPrice, lowPrice, closePrice, fastk_period=5, \
                    slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

    values = numpy.column_stack((prices, emaShort, emaMedium, emaLong, rsi, \
                                 upperband, middleband, \
                                 lowerband, adx, slowk, slowd))
    names = ["open", "high", "low", "close", "ema_short", "ema_medium", \
             "ema_long", "rsi", "upperband", "middleband", "lowerband", "adx", \
             "slowk", "slowd"]

    assert values.shape[1] == len(names)
    index = -1
    for row in values:
        index += 1
        if not numpy.isnan(row).any():
            break

    return values[index:], datetimes[index:], names
