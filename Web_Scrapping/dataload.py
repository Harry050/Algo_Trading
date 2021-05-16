# %%
import pandas as pd
import psycopg2
import os
import matplotlib
from sqlalchemy import create_engine
from tqdm.notebook import tqdm


# %%
# Create a database connection
db_password = ''  # Set to your own password
engine = create_engine(
    'postgresql://postgres:{}@localhost/Algo_Trading_DB'.format(db_password))

# Set some variables of where the CSV files are containing the pricing and ticker information
bars_path = 'Raw Data'
tickers_path = 'tickers'


# %%
# Create a SQL table directly from a dataframe
def create_prices_table(symbol):

    # Import the bar csv file into a dataframe
    df = pd.read_csv('{}/{}.csv'.format(bars_path, symbol))

    # Some formatting
    df = df[['ticker', 'Datetime', 'volume', 'open', 'close', 'high', 'low']]
    df['date'] = pd.to_datetime(df['Datetime'])
    df = df.fillna(0)
    df['updated'] = pd.to_datetime('now')

    # Write the data into the database, this is so fucking cool
    df.to_sql('daily_prices', engine, if_exists='replace', index=False)

    # Create a primary key on the table
    query = """ALTER TABLE daily_prices 
                ADD PRIMARY KEY (ticker, date);"""
    engine.execute(query)

    return 'Daily prices table created'

# create_prices_table('BajFinance')


# %%
# This function will build out the sql insert statement to upsert (update/insert) new rows into the existing pricing table
def import_bar_file(symbol):
    path = bars_path + '/{}.csv'.format(symbol)
    df = pd.read_csv(path, index_col=[0], parse_dates=[0])

    # Some clean up for missing data
    if 'dividend' not in df.columns:
        df['dividend'] = 0
    df = df.fillna(0.0)

    # First part of the insert statement
    insert_init = """INSERT INTO daily_prices
                    (ticker, date, volume, open, close, high, low)
                    VALUES
                """

    # Add values for all days to the insert statement
    vals = ",".join(["""('{}', '{}', '{}', '{}', '{}', '{}', '{}')""".format(
                     symbol,
                     date,
                     row.Volume,
                     row.Open,
                     row.Close,
                     row.High,
                     row.Low
                     ) for date, row in df.iterrows()])

    # Handle duplicate values - Avoiding errors if you've already got some data in your table
    insert_end = """ ON CONFLICT (ticker, date) DO UPDATE 
                SET
                volume = EXCLUDED.volume,
                open = EXCLUDED.open,
                close = EXCLUDED.close,
                high = EXCLUDED.high,
                low = EXCLUDED.low;
                """

    # Put together the query string
    query = insert_init + vals + insert_end

    # Fire insert statement
    engine.execute(query)

# This function will loop through all the files in the directory and process the CSV files


def process_symbols():
    symbols = [s[:-4] for s in os.listdir(bars_path)]
    # symbols = ['AAPL', 'MO']
    for symbol in tqdm(symbols, desc='Importing...'):
        import_bar_file(symbol)

    return 'Process symbols complete'


# Load bars into the database
process_symbols()


# %%
def process_tickers():
    # Read in the tickers file from a csv
    df = pd.read_csv('{}/polygon_tickers_us.csv'.format(tickers_path))

    # Formatting
    df = df[['ticker', 'name', 'market', 'locale', 'type',
             'currency', 'active', 'primaryExch', 'updated']]
    df.rename(columns={'ticker': 'symbol', 'name': 'symbol_name',
              'primaryExch': 'primary_exch'}, inplace=True)
    df['updated'] = pd.to_datetime('now')

    # Run this once to create the table
    df.to_sql('tickers', engine, if_exists='replace', index=False)

    # Add a primary key to the symbol
    query = """ALTER TABLE tickers  
                ADD PRIMARY KEY (symbol);"""
    engine.execute(query)

    return 'Tickers table created'


# Load tickers into the database
process_tickers()


# %%
# Read in the PostgreSQL table into a dataframe
prices_df = pd.read_sql('daily_prices', engine, index_col=['ticker', 'date'])

# Show results of df
prices_df


# %%
# I can also pass in a sql query
prices_df2 = pd.read_sql_query(
    'select * from daily_prices', engine, index_col=['ticker', 'date'])

# Plot the results
# prices_df2.loc[['TSLA']]['close_adj'].plot()
