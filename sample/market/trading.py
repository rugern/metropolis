import numpy
import talib

def pruneInvalidRows(indicators):
    largestNan = -1
    data = {}
    for key, value in indicators.items():
        data[key] = value.copy()

    for name, values in data.items():
        nans = numpy.argwhere(numpy.isnan(values))
        print(nans)
        if nans[-1] > largestNan:
            largestNan = nans[-1]

    for name, values in data.items():
        data[name] = data[name][largestNan + 1:]
    return data

def createIndicators(prices):
    open = prices[:, 0]
    high = prices[:, 1]
    low = prices[:, 2]
    close = prices[:, 3]

    smaShort = talib.SMA(close, timeperiod=30)
    smaMedium = talib.SMA(close, timeperiod=50)
    smaLong = talib.SMA(close, timeperiod=200)

    emaShort = talib.EMA(close, timeperiod=30)
    emaMedium = talib.EMA(close, timeperiod=50)
    emaLong = talib.EMA(close, timeperiod=200)

    macd, macdsignal, macdhist = talib.MACD(
        close,
        fastperiod=12, slowperiod=26, signalperiod=9
    )

    upperband, middleband, lowerband = talib.BBANDS(
        close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
    )

    rsi = talib.RSI(close, timeperiod=14)

    adx = talib.ADX(high, low, close, timeperiod=14)

    slowk, slowd = talib.STOCH(
        high, low, close,
        slowk_period=14, slowd_period=3, fastk_period=3,
        slowk_matype=0, slowd_matype=0
    )

    indicators = dict(
        open=open,
        high=high,
        low=low,
        close=close,
        smaShort=smaShort,
        smaMedium=smaMedium,
        smaLong=smaLong,
        emaShort=emaShort,
        emaMedium=emaMedium,
        emaLong=emaLong,
        macd=macd,
        macdsignal=macdsignal,
        macdhist=macdhist,
        upperband=upperband,
        middleband=middleband,
        lowerband=lowerband,
        rsi=rsi,
        adx=adx,
        slowk=slowk,
        slowd=slowd,
    )

    indicators = pruneInvalidRows(indicators)
    return indicators

def appendIndicators(data):
    for currency, datasets in data.items():
        for dataset, prices in datasets.items():
            data[currency][dataset], _ = createIndicators(prices)
    return data
