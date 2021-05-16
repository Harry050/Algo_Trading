import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import pandas_datareader as pdr
import datetime as dt
import talib as ta
import matplotlib.pyplot as plt
'exec(%matplotlib inline)'
import numpy as np
from talib import RSI, BBANDS
from plotly.offline import plot
import plotly.graph_objs as go
import mplfinance as mpf
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpdates
import math

def vwap_plot():

    df = pd.read_csv('Bajaj Finance.csv', sep=',', quotechar='"')

    df.set_index(['Datetime'], inplace=True)
    df.index = pd.to_datetime(df.index)
    df.index.name = 'Date'


    # from here = https://www.tradingtechnologies.com/xtrader-help/x-study/technical-indicator-definitions/volume-weighted-average-price-vwap/
    df['VWAP'] = (df.Volume * (df.High + df.Low) / 2).cumsum() / df.Volume.cumsum()
    df['VWAP_MEAN_DIFF'] = ((df.High + df.Low) / 2) - df.VWAP
    df['SQ_DIFF'] = df.VWAP_MEAN_DIFF.apply(lambda x: math.pow(x, 2))
    df['SQ_DIFF_MEAN'] = df.SQ_DIFF.expanding().mean()
    df['STDEV_TT'] = df.SQ_DIFF_MEAN.apply(math.sqrt)

    stdev_multiple_1 = 1.28
    stdev_multiple_2 = 2.01
    stdev_multiple_3 = 2.51

    #df['STDEV_1'] = df.VWAP + stdev_multiple_1 * df['STDEV_TT']
    #df['STDEV_N1'] = df.VWAP - stdev_multiple_1 * df['STDEV_TT']

    addplot  = [
        mpf.make_addplot(df['VWAP']),
        #mpf.make_addplot(df['STDEV_1']),
        #mpf.make_addplot(df['STDEV_N1']),
    ]

    mpf.plot(df, type='candle', addplot=addplot)


def candlestick_chart():
    plt.style.use('dark_background')
    # extracting Data for plotting
    df = pd.read_csv('Bajaj Finance.csv',index_col=0,parse_dates=True)

    df[['Close']].plot(figsize=(15,8))


    df['20_SMA'] = df['Close'].rolling(window = 20, min_periods = 1).mean()
    df['50_SMA'] = df['Close'].rolling(window = 50, min_periods = 1).mean()

    df['Signal'] = 0.0
    df['Signal'] = np.where(df['20_SMA'] > df['50_SMA'], 1.0, 0.0)
    df['Position'] = df['Signal'].diff()

    #plt.figure(figsize = (20,10))
    # plot close price, short-term and long-term moving averages 
    df[['Close']].plot(color = 'k', label= 'Close') 
    df['20_SMA'].plot(color = 'b',label = '20-day SMA') 
    df['50_SMA'].plot(color = 'g', label = '50-day SMA')
    
    # plot 'buy' signals
    plt.plot(df[df['Position'] == 1].index, 
            df['20_SMA'][df['Position'] == 1], 
            '^', markersize = 10, color = 'g', label = 'buy')
    
    # plot 'sell' signals
    plt.plot(df[df['Position'] == -1].index, df['20_SMA'][df['Position'] == -1], 'v', markersize = 10, color = 'y', label = 'sell')

    buy_signal = df[df['Position'] == 1].index,df['20_SMA'][df['Position'] == 1]
    sell_signal= df[df['Position'] == -1].index, df['20_SMA'][df['Position'] == -1]
    
    addplot  = [
        #mpf.make_addplot(df['20_SMA'], scatter=True, marker='-', markersize=9, color='b'),
        #mpf.make_addplot(df['50_SMA'], scatter=True, marker='-', markersize=9, color='b'),
        mpf.make_addplot(df[[df['Position'] == 1].index,df['20_SMA'][df['Position'] == 1]], scatter=True, marker='v', markersize=9, color='g'),
        #mpf.make_addplot(df[df['Position'] == -1], type='scatter', marker='v', markersize=10, color='r'),
        #mpf.make_addplot(df['STDEV_1']),
        #mpf.make_addplot(df['STDEV_N1']),
    ]

    mpf.plot(df,  type='candle', addplot=addplot, mav=(20,50))


def signal():
    ultratech_df = pd.read_csv('SBIN.csv')
    ultratech_df[['Close']].plot(figsize=(15,8))


    ultratech_df['20_SMA'] = ultratech_df['Close'].rolling(window = 20, min_periods = 1).mean()
    ultratech_df['50_SMA'] = ultratech_df['Close'].rolling(window = 50, min_periods = 1).mean()

    ultratech_df['Signal'] = 0.0
    ultratech_df['Signal'] = np.where(ultratech_df['20_SMA'] > ultratech_df['50_SMA'], 1.0, 0.0)
    ultratech_df['Position'] = ultratech_df['Signal'].diff()

    plt.figure(figsize = (20,10))
    # plot close price, short-term and long-term moving averages 
    ultratech_df[['Close']].plot(color = 'k', label= 'Close') 
    ultratech_df['20_SMA'].plot(color = 'b',label = '20-day SMA') 
    ultratech_df['50_SMA'].plot(color = 'g', label = '50-day SMA')

    # plot 'buy' signals
    plt.plot(ultratech_df[ultratech_df['Position'] == 1].index, 
            ultratech_df['20_SMA'][ultratech_df['Position'] == 1], 
            '^', markersize = 10, color = 'g', label = 'buy')
    # plot 'sell' signals
    plt.plot(ultratech_df[ultratech_df['Position'] == -1].index, ultratech_df['20_SMA'][ultratech_df['Position'] == -1], 'v', markersize = 10, color = 'r', label = 'sell')
    
    plt.ylabel('Price in Rupees', fontsize = 15 )
    plt.xlabel('Date', fontsize = 15 )
    plt.title('SBIN', fontsize = 20)
    plt.legend()
    plt.grid()
    plt.show()

def pattern_recognition():
    data = pd.read_csv('Stock Market.csv')

    hammer = ta.CDLHAMMER(data['Open'], data['High'], data['Low'], data['Close'])
    #CDLHAMMER is best strategy for intraday. After several confirmation the price go trending against.

    gap_crows = ta.CDLXSIDEGAP3METHODS(data['Open'], data['High'], data['Low'], data['Close'])
    #CDLXSIDEGAP3METHODS is best strategy for intraday. After several confirmation the price go trending against. 

    evening_star = ta.CDLEVENINGSTAR(data['Open'], data['High'], data['Low'], data['Close'])

    data['Gap_Crow'] = gap_crows
    data['Hammer'] = hammer 
    #data['Evening_Star'] = evening_star
    
    print(data[data['Hammer'] != 0])

def ema_sma():
    plt.style.use('bmh')
    ticker_code = ['SBIN.csv']
    df_list = list()

    for code in ticker_code:
        data = pd.read_csv('Sun Pharma.csv')
        #data = yf.download(tickers = code, period = "1d", interval = "15m",  group_by = 'ticker', auto_adjust = True,  prepost = True, threads = True, proxy = None)
        data['ticker'] = code
        df_list.append(data)
        data['Simple MA'] = ta.SMA(data['Close'],14)
        data['EMA'] = ta.EMA(data['Close'], timeperiod = 10)
        data[['Close','Simple MA','EMA']].plot(figsize=(15,15))
        plt.show()

def download_yfinance_data():
    plt.style.use('bmh')
    ticker_code = ['SBIN.NS','SUNPHARMA.NS', 'BAJFINANCE.NS', 'RELIANCE.NS']
    df_list = list()
    for code in ticker_code:
        data = yf.download(tickers = code, period = "7d", interval = "15m",  group_by = 'ticker', auto_adjust = True,  prepost = True, threads = True, proxy = None)
        data['ticker'] = code
        df_list.append(data)        
        df = pd.concat(df_list)
        df.to_csv('Stock Market.csv')

#download_yfinance_data()
#ema_sma()
#pattern_recognition()
candlestick_chart()

#vwap_plot()