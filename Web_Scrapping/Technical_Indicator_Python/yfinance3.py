import pandas as pd
import numpy as np
import io

data = '''
Date Symbol Action Price
2020-03-01 AAPL Buy 80
2020-04-01 AAPL Sell 130
2020-05-01 AAPL Buy 90
2020-06-01 AAPL Sell 125
2020-07-01 AAPL Buy 125
2020-08-01 AAPL Sell 110
2020-09-01 AAPL Buy 95
2020-10-01 AAPL Sell 125
2020-11-01 AAPL Buy 125
2020-12-01 AAPL Sell 140
2021-01-01 AAPL Buy 115
2021-02-01 AAPL Sell 135
'''

df = pd.read_csv(io.StringIO(data), delim_whitespace=True)
df['Date'] = pd.to_datetime(df['Date'])

buy = df[df['Action'] == 'Buy']
buy2 = df[['Date']].merge(buy,how='outer')
sell = df[df['Action'] == 'Sell']
sell2 = df[['Date']].merge(sell,how='outer')

import mplfinance as mpf
import yfinance as yf


data = pd.read_csv('AAPL.csv')
data.set_index(['Date'], inplace=True)
data.index = pd.to_datetime(df.index)
data.index.name = 'Date'

data.dropna(how='any', inplace=True)

ap = [mpf.make_addplot(buy2['Price'], type='scatter', marker='^', markersize=200, color='g'),
      mpf.make_addplot(sell2['Price'], type='scatter', marker='v', markersize=200, color='r')
     ]
      
mpf.plot(data, type='candle', ylabel='Candle', addplot=ap, volume=False)