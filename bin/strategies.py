from actions import BUY, HOLD, SELL

def calculateLoss(prices):
    return prices.max() - prices[-1]

def calculateProfit(prices):
    return prices[-1] - prices[0]

def emaStop(bid, ask, predictions, entryIndex, currentIndex):
    stopLoss = 0.001
    takeProfit = 0.005
    period = prices[entryIndex:]
    loss = calculateLoss(period)
    profit = calculateProfit(period)
    order = HOLD
    if loss > stopLoss or profit > takeProfit:
        order = SELL
    elif predictions[4][-1] < prices[-1]:
        order = BUY
    return order

def emaEntry(ask, predictions, currentIndex):
    order = HOLD
    if predictions[currentIndex][4] < ask[currentIndex]:
        order = BUY
    return order

def emaExit(bid, predictions, entryIndex, currentIndex):
    stopLoss = 0.001
    takeProfit = 0.005
    loss = calculateLoss(bid[entryIndex:])
    profit = calculateProfit(bid[entryIndex:])
    order = HOLD
    if loss > stopLoss or profit > takeProfit or predictions[currentIndex][4] > prices[currentIndex]:
        order = SELL
    return order
    
