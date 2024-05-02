import os
import requests
import pandas as pd
import glob
from tqdm import tqdm

# Base URL for Binance data API
base_url = "https://data.binance.vision"


# Function to download kline data for a cryptocurrency
def download_kline_data(symbol, interval, year, month):
    url = f"{base_url}/data/spot/monthly/klines/{symbol.upper()}/{interval}/{symbol.upper()}-{interval}-{year}-{month:02}.zip"
    response = requests.get(url)
    if response.status_code == 200:
        # Create folder if it doesn't exist
        folder_name = f"kline_data/{symbol.upper()}/{interval}"
        os.makedirs(folder_name, exist_ok=True)
        # Save the zip file
        file_name = f"{folder_name}/{symbol.upper()}-{interval}-{year}-{month:02}.zip"
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download {symbol.upper()} data for {year}-{month:02}")
        return False


def merge_all_csv_to_one_parquet(symbol, interval):
    # Get all zip files in the folder
    zip_files = glob.glob(f"kline_data/{symbol.upper()}/{interval}/*.zip")
    # Unzip all the files
    for file in zip_files:
        os.system(f"unzip -o {file} -d kline_data/{symbol.upper()}")

    # Get all csv files in the folder
    csv_files = glob.glob(f"kline_data/{symbol.upper()}/*.csv")

    # Read all csv files and concatenate them if there are any
    if len(csv_files) > 0:
        # Define column names
        columns = [
            "timestamp", "open", "high", "low", "close",
            "volume", "close_time", "quote_asset_volume",
            "number_of_trades", "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume", "ignore"
        ]
        # Read and concatenate CSV files with explicit column names
        dfs = []
        for file in csv_files:
            df = pd.read_csv(file, header=None, names=columns)
            dfs.append(df)
        df = pd.concat(dfs)
        # Save the concatenated dataframe to a parquet file
        df.to_parquet(f"kline_data/{symbol.upper()}/{symbol.upper()}-{interval}.parquet")

        # Remove the csv and zip files
        for file in zip_files + csv_files:
            os.remove(file)
        os.rmdir(f"kline_data/{symbol.upper()}/{interval}")

    print(f"Saved {symbol.upper()} data for {interval} interval to parquet file")


# Main function to iterate over the period, symbols, and intervals
def main():
    # Define the period
    start_year = 2019
    end_year = 2024
    months = range(1, 13)  # January to December

    # List of top 50 cryptocurrencies
    symbols = [
        "BTCUSDT", "ETHUSDT", "XRPUSDT", "BCHUSDT", "LTCUSDT",
        "ADAUSDT", "BNBUSDT", "USDCUSDT", "DOTUSDT",
        "SOLUSDT", "DOGEUSDT", "UNIUSDT", "WBTCUSDT",
        "XLMUSDT", "LINKUSDT", "AAVEUSDT", "VETUSDT", "THETAUSDT",
        "ALGOUSDT", "ATOMUSDT", "FILUSDT", "KSMUSDT",
        "EOSUSDT", "TRXUSDT", "XVGUSDT", "ZECUSDT", "MKRUSDT",
        "BATUSDT", "COMPUSDT", "SUSHIUSDT", "SNXUSDT",
        "YFIUSDT", "UMAUSDT", "CRVUSDT", "RSRUSDT", "KAVAUSDT",
        "NMRUSDT", "BANDUSDT", "RENUSDT", "KNCUSDT",
        "ZILUSDT", "PAXGUSDT", "OMGUSDT", "DASHUSDT", "ZRXUSDT"
    ]

    # List of intervals
    intervals = ["5m"]

    # Iterate over each year, month, symbol, and interval
    for year in range(start_year, end_year + 1):
        for month in months:
            print(f"Downloading data for {year}-{month:02}")
            for interval in intervals:
                # Iterate over each symbol and download data
                for symbol in tqdm(symbols):
                    download_kline_data(symbol, interval, year, month)

    # Merge all downloaded CSV files to Parquet for each symbol and interval
    for symbol in symbols:
        for interval in intervals:
            merge_all_csv_to_one_parquet(symbol, interval)


if __name__ == "__main__":
    main()


