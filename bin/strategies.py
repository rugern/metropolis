def calculateLoss(prices):
    return prices.max() - prices[-1]



def emaStop(prices, predictions, entryIndex):
    stopLoss = 0.001
    takeProfit = 0.005
    period = prices[entryIndex:]
    loss = calculateLoss(period)
    profit = calculateProfit(period)
    order = action.NOTHING
    if loss > stopLoss or profit > takeProfit:
        order = action.SELL
    elif predictions[4][-1] < prices[-1]:
        order = action.BUY
    return order

def ema(prices, predictions, entryIndex):
    stopLoss = 0.001
    takeProfit = 0.005
    period = prices[entryIndex:]
    loss = calculateLoss(period)
    profit = calculateProfit(period)
    order = action.NOTHING
    if loss > stopLoss or profit > takeProfit or predictions[4][-1] > prices[-1]:
        order = action.SELL
    elif predictions[4][-1] < prices[-1]:
        order = action.BUY
    return order
