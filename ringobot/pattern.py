import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)

# read the data
df = pd.read_parquet('kline_data/BTCUSDT/BTCUSDT-5m.parquet')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Sort dataframe by timestamp
df = df.sort_values(by='timestamp')

# get the timestamps that where there has been at least 5 percent increase in price within 24 hours
df['price_change'] = df['close'].pct_change(periods=288)

# filter the data
df_filtered = df[df['price_change'] >= 0.05]

df_filtered = df_filtered[['timestamp', 'close', 'price_change']]

# filter df_filtered to get the first timestamp of each day

df_filtered['date'] = df_filtered['timestamp'].dt.date
df_filtered['time'] = df_filtered['timestamp'].dt.time

df_filtered = df_filtered.groupby('date').first().reset_index()

# plot the data
# make a plot using the df and df_filtered dataframes. for every record in df_filtered, plot the price change in df.
# make sure each plot has 48 hours of data. and is centered around the timestamp in df_filtered.
# make sure the plots are in the same figure and the colors are different before and after the timestamp in df_filtered.

for i, row in df_filtered.iterrows():
    fig, ax = plt.subplots()
    timestamp = row['timestamp']
    data_before = df[(df['timestamp'] >= timestamp - pd.Timedelta(hours=24)) & (df['timestamp'] <= timestamp)]
    data_after = df[(df['timestamp'] > timestamp) & (df['timestamp'] <= timestamp + pd.Timedelta(hours=24))]
    ax.plot(data_before['timestamp'], data_before['close'], color='blue')
    ax.plot(data_after['timestamp'], data_after['close'], color='red')
    plt.title(f'Price Change on {row["date"]}')
    plt.xlabel('Timestamp')
    plt.ylabel('Close Price')
    plt.xticks(rotation=45)
    plt.savefig(f"plots/{row['date']}.png")
    plt.close()
