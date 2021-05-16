import yfinance as yf
import mplfinance as mpf
import talib as ta
import numpy as np
import pandas as pd
import math
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
from mplfinance.original_flavor import candlestick_ohlc
from datetime import datetime, time
import datetime as dt
from datetime import timezone
from . import performance as performance
from . import ADX_Indicator as adx_value

def EMA():
    ticker_code = ['Raw Data/BajFinance.csv']
    plt.style.use('bmh')

    for code in ticker_code:
        data = pd.read_csv(code)
        data.set_index(['Datetime'])
        data.index = pd.to_datetime(data.index)
        data.index.name = 'Date'

        #data = data.set_index(pd.DatetimeIndex(data['Datetime'].values))
        
        data['EMA5'] = data['Close'].ewm(span=8, adjust=False).mean()
        data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
        data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
        
        
        data["rsi"] = ta.RSI(data["Close"])
        adx_data = adx_value.adx_indicator_call(code)

        data["strip_name"] = data["ticker"]

        data['Buy'], data['Sell'], signals = buy_sell_signal(data, 0)
        performance.print_performance_summary(signals)


        plt.figure(figsize=(12.2, 4.5))
        plt.title('Buy and Sell Price', fontsize = 18)
        plt.plot(data['Close'], label='Close Price', color='blue')
        
        #plt.plot(data['EMA5'], label='EMA5', color='red', alpha=0.35)
        #plt.plot(data['EMA20'], label='EMA20', color='orange', alpha=0.35)
        #plt.plot(data['EMA200'], label='EMA200', color = 'green')
        plt.scatter(data.index, data['Buy'], color='green', marker='^', alpha=1)
        plt.scatter(data.index, data['Sell'], color='red', marker='v', alpha=1)    
        plt.xlabel('Date', fontsize = 18)
        plt.ylabel('Close Price ', fontsize = 18)


        #plt.show()
    #data.to_csv('SBIN EMA sell signal.csv')

def buy_sell_signal(data, adx_data_value):
    buy_list = []
    sell_list = []
    flag_long = False
    flag_short = False
    signals = []
    short_buy_price = 0
    pull_buy_price = 0
    df_concat = []

    for i in range(0, len(data)):
        #if data['EMA5'][i] < data['EMA20'][i] and data['EMA20'][i] < data['EMA200'][i] and flag_long == False and flag_short == False and data['rsi'][i] <= 60:
        if data['EMA5'][i] < data['EMA20'][i] and data['EMA20'][i] < data['EMA200'][i] and flag_long == False and flag_short == False and data['rsi'][i] <= 60:
            buy_list.append(data['Close'][i])
            price = (data['Open'][i] + data['Close'][i]) / 2
            short_buy_price = price
            sell_list.append(np.nan)
            signals.append({
                'date': data.index[i],
                'action': 'short_buy',
                'short_price': short_buy_price,
                'ema5': data['EMA5'][i],
                'ema20': data['EMA20'][i],
                'ema200': data['EMA200'][i],
                'ticker_name': data['strip_name'][i],
                #'adx_value': adx_data_value['ADX'][i],
                'rsi': data['rsi'][i],
                'target': ((data['Open'][i] + data['Close'][i] )/2) - ((((data['Open'][i] +data['Close'][i])/2) * 1)/100),
            })
            flag_short = True
        elif (flag_short == True and flag_long == False and data['EMA5'][i] > data['EMA20'][i]) or (flag_short == True and flag_long == False and ((data['Open'][i] + data['Close'][i] )/2) <= (short_buy_price) - (((short_buy_price) * 1)/100)):
            sell_list.append(data['Close'][i])
            price = (data['Open'][i] + data['Close'][i]) / 2
            buy_list.append(np.nan)
            signals.append({
                'date': data.index[i],
                'action': 'short_sell',
                'short_price': price,
                'ema5': data['EMA5'][i],
                'ema20': data['EMA20'][i],
                'ema200': data['EMA200'][i],
                'ticker_name': data['strip_name'][i],
                #'adx_value': adx_data_value['ADX'][i],
                'rsi': data['rsi'][i],
            })
            short_buy_price = 0
            flag_short = False
        elif data['EMA5'][i] > data['EMA20'][i] and data['EMA20'][i] > data['EMA200'][i] and flag_long == False and flag_short == False  and data['rsi'][i] >= 40:
            buy_list.append(data['Close'][i])
            sell_list.append(np.nan)
            price = (data['Open'][i] + data['Close'][i]) / 2
            pull_buy_price = price
            signals.append({
                'date': data.index[i],
                'action': 'pull_buy',
                'pull_price': pull_buy_price,
                'ema5': data['EMA5'][i],
                'ema20': data['EMA20'][i],
                'ema200': data['EMA200'][i],
                'ticker_name': data['strip_name'][i],
                #'adx_value': adx_data_value['ADX'][i],
                'rsi': data['rsi'][i],
                'target': price + ((((data['Open'][i] + data['Close'][i])/2) * 1)/100),
            })
            flag_long = True
        elif (flag_long == True and flag_short == False and data['EMA5'][i] < data['EMA20'][i]) or (flag_long == True and flag_short == False and (((data['Open'][i] + data['Close'][i] )/2)) >= (pull_buy_price) + ((((pull_buy_price) * 1)/100))):
            sell_list.append(data['Close'][i])
            buy_list.append(np.nan)
            price = (data['Open'][i] + data['Close'][i]) / 2
            signals.append({
                'date': data.index[i],
                'action': 'pull_sell',
                'pull_price': price,
                'ema5': data['EMA5'][i],
                'ema20': data['EMA20'][i],
                'ema200': data['EMA200'][i],
                'ticker_name': data['strip_name'][i],
                #'adx_value': adx_data_value['ADX'][i],
                'rsi': data['rsi'][i],
            })
            flag_long = False
            pull_buy_price = 0
        else:
            buy_list.append(np.nan)
            sell_list.append(np.nan)
        df_signal =  pd.DataFrame(signals, columns=['date', 'action', 'pull_price', 'short_price', 'ema5', 'ema20', 'ema200', 'ticker_name',  'rsi', 'target'])
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            df_concat.append(df_signal)

        df_signal.to_csv('Target.csv')
        #print(df_signal)
    return (buy_list, sell_list, signals)

EMA()
#ema_sma()