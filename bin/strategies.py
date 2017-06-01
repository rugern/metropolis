from actions import BUY, HOLD, SELL

def calculateLoss(prices):
    return prices.max() - prices[-1]

def calculateProfit(prices):
    return prices[-1] - prices[0]

# def emaStop(bid, ask, predictions, entryIndex, currentIndex):
    # stopLoss = 0.001
    # takeProfit = 0.005
    # period = prices[entryIndex:]
    # loss = calculateLoss(period)
    # profit = calculateProfit(period)
    # order = HOLD
    # if loss > stopLoss or profit > takeProfit:
        # order = SELL
    # elif predictions[4][-1] < prices[-1]:
        # order = BUY
    # return order

def emaEntry(currentIndex, **kwargs):
    ask = kwargs['ask']
    order = HOLD
    for i in range(4, 10):
        if ask[currentIndex, i] > ask[currentIndex, 3]:
            order = BUY
            break
    return order

def emaExit(entryIndex, currentIndex, 
            stopLoss=0.0001,
            takeProfit=0.005,
            **kwargs):
    bidClose = kwargs['bid'][:, 3]
    loss = calculateLoss(bidClose[entryIndex:currentIndex])
    profit = calculateProfit(bidClose[entryIndex:currentIndex])
    order = HOLD
    if loss > stopLoss or profit > takeProfit:
        order = SELL
    return order
