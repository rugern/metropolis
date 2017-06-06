import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from market import action

# def emaStop(bid, ask, predictions, entryIndex, currentIndex):
    # stopLoss = 0.001
    # takeProfit = 0.005
    # period = prices[entryIndex:]
    # loss = calculateLoss(period)
    # profit = calculateProfit(period)
    # order = HOLD
    # if loss > stopLoss or profit > takeProfit:
        # order = LONG
    # elif predictions[4][-1] < prices[-1]:
        # order = SHORT
    # return order

def short(prices, currentIndex, **kwargs):
    bidClose = prices['bid']['close'][currentIndex]
    bidsmashort = prices['bid']['smaShort'][currentIndex]
    order = action.HOLD
    if bidsmashort < bidClose:
        order = action.SHORT
    return order

def long(prices, currentIndex, entryIndex, **kwargs):
    ask = prices['ask']['close'][entryIndex:currentIndex + 1]
    bid = prices['bid']['close'][entryIndex:currentIndex + 1]
    loss = ask[-1] - bid[0]
    profit = bid[0] - ask[-1]
    order = action.HOLD
    if loss > kwargs['stopLoss'] or profit > kwargs['takeProfit']:
        order = action.LONG
    return order
