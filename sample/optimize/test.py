import sys
import os
from os.path import join
import itertools
from pprint import pformat
import click

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from utility.data import readDataFiles
from market.bank import Bank
from market.orderbook import OrderBook
from market import action
from market.trading import appendIndicators
from strategies import sma

def gridsearch(gridParams, currency, prices, shortStrat=None, longStrat=None, strategy=None, **kwargs):
    labels = []
    paramsMatrix = []
    for key, elem in gridParams.items():
        labels.append(key)
        paramsMatrix.append(elem)

    combinations = itertools.product(*paramsMatrix)
    best = {}
    results = []
    data = {
        currency: prices,
    }
    for combination in combinations:
        params = {}
        for i, elem in enumerate(combination):
            params[labels[i]] = elem
            strategy[labels[i]] = elem

        currentStrategy = {
            currency: strategy
        }
        result = test(data, shortStrat=shortStrat, longStrat=longStrat, strategy=currentStrategy, **kwargs)

        result['params'] = params
        if 'profit' not in best or result['profit'] > best['profit']:
            best = result
        results.append(result)

    return best, results

def getSize(data):
    size = -1
    for currency, datasets in data.items():
        for dataset, prices in datasets.items():
            currentSize = prices.shape[0]
            if size == -1:
                size = currentSize
            if currentSize < size:
                size = currentSize
    return size

def initializeOrders(data):
    orders = {}
    for key, value in data.items():
        orders[key] = []
    return orders

def filterActive(data, strategy):
    outData = {}
    outStrategy = {}
    for currency, values in strategy.items():
        if values['active']:
            outData[currency] = data[currency]
            outStrategy[currency] = values
    return outData, outStrategy

def test(data, shortStrat=None, longStrat=None, strategy=None, **kwargs):
    bank = Bank(kwargs['startMoney'])
    orderBook = OrderBook()
    size = getSize(data)

    for i in range(size):
        for currency, prices in data.items():
            for order in orderBook.getOrders(currency):
                if longStrat(prices, i, order.entryIndex, **strategy[currency]) == action.LONG:
                    bank.deposit(orderBook.closeOrder(currency, order, prices['ask']['close'][i]))
            if shortStrat(prices, i, **strategy[currency]) == action.SHORT:
                buyAmount = kwargs['startMoney'] * strategy[currency]['buySize'] / strategy[currency]['leverage']
                amount = bank.withdraw(buyAmount)
                if amount > 0:
                    orderBook.openOrder(currency, prices['bid']['close'][i], i, amount, strategy[currency]['leverage'])
    result = {
        'buys': bank.withdrawals,
        'sells': bank.deposits,
    }
    for currency, prices in data.items():
        for order in orderBook.getOrders(currency):
            bank.deposit(orderBook.closeOrder(currency, order, prices['ask']['close'][-1]))
    result['profit'] = (100 * bank.funds / kwargs['startMoney']) - 100
    return result

def testRunner(pattern, money, searchParams=False):
    options = {
        'startMoney': money,
        'log': print,
        'verbose': 1,
    }

    strategy = {
        'EURAUD': {
            'stopLoss': 0.01,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.015,
        },
        'EURCAD': {
            'stopLoss': 0.005,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.015,
        },
        'EURCHF': {
            'stopLoss': 0.005,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURCZK': {
            'stopLoss': 0.005,
            'takeProfit': 0.01,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURDKK': {
            'stopLoss': 0.0005,
            'takeProfit': 0.02,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURGBP': {
            'stopLoss': 0.001,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURHUF': {
            'stopLoss': 0.005,
            'takeProfit': 0.02,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURJPY': {
            'stopLoss': 0.01,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURNOK': {
            'stopLoss': 0.01,
            'takeProfit': 0.02,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURNZD': {
            'stopLoss': 0.01,
            'takeProfit': 0.015,
            'leverage': 50,
            'buySize': 0.015,
        },
        'EURPLN': {
            'stopLoss': 0.01,
            'takeProfit': 0.02,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURSEK': {
            'stopLoss': 0.01,
            'takeProfit': 0.015,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURTRY': {
            'stopLoss': 0.005,
            'takeProfit': 0.015,
            'leverage': 50,
            'buySize': 0.001,
        },
        'EURUSD': {
            'stopLoss': 0.0005,
            'takeProfit': 0.005,
            'leverage': 50,
            'buySize': 0.001,
        },
    }

    # data = readDataFiles(pattern='2017_3-5_15m')
    data = readDataFiles(pattern=pattern)
    data = appendIndicators(data)

    if searchParams:
        stopLoss = [0.01, 0.005, 0.001, 0.0005]
        takeProfit = [0.02, 0.015, 0.01, 0.005]
        buySize = [0.015, 0.01, 0.005, 0.001]
        leverage = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

        gridParams = dict(
            # stopLoss=stopLoss,
            # takeProfit=takeProfit,
            buySize=buySize,
            # leverage=leverage,
            # spread=spread,
            # active=active,
        )

        for currency, prices in data.items():
            best, result = gridsearch(gridParams, currency, prices, shortStrat=sma.short, longStrat=sma.long, strategy=strategy[currency], **options)
            print('Best for {}:'.format(currency))
            print(pformat(best))
            if options['verbose'] == 2:
                print('All results for {}:'.format(currency))
                print(pformat(results))

    else:
        result = test(data, shortStrat=sma.short, longStrat=sma.long, strategy=strategy, **options)
        print(pformat(result))
