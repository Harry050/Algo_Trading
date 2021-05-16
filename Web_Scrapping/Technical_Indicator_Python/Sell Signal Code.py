
def detect_macd_signals(data):
    """Use MACD cross-over to decide buy/sell

    Args:
      data: panda DataFrame with OHLC with MACD data
    
    Return:
      buy_signals, sell_signals: for chart plot
      signals: buy/sell transaction for summary printing
    """

    buy_signals = [np.nan]
    sell_signals = [np.nan]
    signals = []
    last_signal = None
    for i in range(1, len(data)):
        if data['macd_hist'][i-1] < 0 and data['macd_hist'][i] > 0:
            price = (data['Open'][i] + data['Close'][i]) / 2
            buy_signals.append(price)
            last_signal = 'buy'
            signals.append({
                'date': data.index[i],
                'action': 'buy',
                'price': price
                })            
            sell_signals.append(np.nan)
        elif data['macd_hist'][i-1] > 0 and data['macd_hist'][i] < 0 and last_signal == 'buy':
            price = (data['Open'][i] + data['Close'][i]) / 2
            sell_signals.append(price)
            last_signal = 'sell'
            signals.append({
                'date': data.index[i],
                'action': 'sell',
                'price': price
                })            
            buy_signals.append(np.nan)
        else:
            buy_signals.append(np.nan)
            sell_signals.append(np.nan)

    return buy_signals, sell_signals, signals
