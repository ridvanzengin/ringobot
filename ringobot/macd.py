import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)

# read the data
df = pd.read_parquet('kline_data/ADAUSDT/ADAUSDT-5m.parquet')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Sort dataframe by timestamp
df = df.sort_values(by='timestamp')

# resample the data to 1 hour
df = df.set_index('timestamp')
df = df.resample('1H').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum',
    'close_time': 'last',
    'quote_asset_volume': 'sum',
    'number_of_trades': 'sum',
    'taker_buy_base_asset_volume': 'sum',
    'taker_buy_quote_asset_volume': 'sum',
    'ignore': 'last'
}).dropna()

# get the 12 and 26 hour exponential moving averages
df['ema12'] = df['close'].ewm(span=12, adjust=False).mean()
df['ema26'] = df['close'].ewm(span=26, adjust=False).mean()

# calculate the MACD line
df['macd'] = df['ema12'] - df['ema26']

# calculate the signal line
df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# macd histogram
df['macd_histogram'] = df['macd'] - df['signal']

# determine the buy and sell signals
df['buy'] = (df['macd'] > df['signal']) & (df['macd_histogram'] > 0) & (df['macd'].shift() < df['signal'].shift())
df['sell'] = (df['macd'] < df['signal']) & (df['macd_histogram'] < 0) & (df['macd'].shift() > df['signal'].shift())


# plot the last N hours of data with buy and sell signals
last_N = df[-17300:-17100]
fig, ax = plt.subplots()
ax.plot(last_N.index, last_N['close'], label='Close Price', color='black')
ax.plot(last_N.index, last_N['ema12'], label='EMA12', color='blue')
ax.plot(last_N.index, last_N['ema26'], label='EMA26', color='red')
ax.plot(last_N[last_N['buy']].index, last_N[last_N['buy']]['close'], '^', markersize=10, color='g', lw=0, label='Buy Signal')
ax.plot(last_N[last_N['sell']].index, last_N[last_N['sell']]['close'], 'v', markersize=10, color='r', lw=0, label='Sell Signal')
ax.legend()
plt.title('BTCUSDT 1H MACD')
plt.xlabel('Timestamp')
plt.ylabel('Price')
plt.xticks(rotation=45)
plt.show()
plt.close()

# calculate and print the cumulative profit and loss for each buy and sell signal
initial_balance = 1000
balance = initial_balance
shares = 0
for i, row in last_N.iterrows():
    if row['buy']:
        shares = balance / row['close']
        balance = 0
        buy_price = row['close']
    if row['sell'] and shares > 0:
        balance = shares * row['close']
        shares = 0
        profit = balance - initial_balance
        print(f"time: {i}, buy: {buy_price}, sell: {row['close']}, profit: {profit}")
        initial_balance = balance
if shares > 0:
    balance = shares * last_N.iloc[-1]['close']
    shares = 0
print(f"Final Balance: {balance}")




