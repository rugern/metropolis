from actions import SHORT, HOLD, LONG

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

def emaShort(prices, currentIndex, **kwargs):
    order = HOLD
    for i in range(4, 10):
        if prices[currentIndex, i] < prices[currentIndex, 3]:
            order = SHORT
            break
    return order

def emaLong(prices, currentIndex, entryIndex, 
            stopLoss=0.00005,
            takeProfit=0.00005,
            **kwargs):
    period = prices[entryIndex:currentIndex + 1, 3]
    loss = period[-1] - period.min()
    profit = period[0] - period[-1]
    order = HOLD
    if loss > stopLoss or profit > takeProfit:
        order = LONG
    return order
