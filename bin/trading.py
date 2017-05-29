import numpy
import talib


def createIndicators(prices):
    # openPrice = prices[:, 0]
    highPrice = prices[:, 1]
    lowPrice = prices[:, 2]
    closePrice = prices[:, 3]

    smaShort = talib.SMA(closePrice, timeperiod=30)
    smaMedium = talib.SMA(closePrice, timeperiod=50)
    smaLong = talib.SMA(closePrice, timeperiod=200)

    emaShort = talib.EMA(closePrice, timeperiod=30)
    emaMedium = talib.EMA(closePrice, timeperiod=50)
    emaLong = talib.EMA(closePrice, timeperiod=200)

    macd, macdsignal, macdhist = talib.MACD(
        closePrice,
        fastperiod=12, slowperiod=26, signalperiod=9
    )

    upperband, middleband, lowerband = talib.BBANDS(
        closePrice, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
    )

    rsi = talib.RSI(closePrice, timeperiod=14)

    adx = talib.ADX(highPrice, lowPrice, closePrice, timeperiod=14)

    slowk, slowd = talib.STOCH(
        highPrice, lowPrice, closePrice,
        slowk_period=14, slowd_period=3, fastk_period=3,
        slowk_matype=0, slowd_matype=0
    )

    values = numpy.column_stack((
        prices,
        smaShort, smaMedium, smaLong,
        emaShort, emaMedium, emaLong,
        macd, macdsignal, macdhist,
        upperband, middleband, lowerband,
        rsi,
        adx,
        slowk, slowd
    ))
    names = [
        'open', 'high', 'low', 'close',
        'smaShort', 'smaMedium', 'smaLong',
        'emaShort', 'emaMedium', 'emaLong',
        'macd', 'macdsignal', 'macdhist',
        'upperband', 'middleband', 'lowerband',
        'rsi',
        'adx',
        'slowk', 'slowd'
    ]

    assert values.shape[1] == len(names)
    index = -1
    for row in values:
        index += 1
        if not numpy.isnan(row).any():
            break

    return values[index:], names
