import pandas as pd
import gc
from ringobot.config import org, bucketMain, influxDBwriteApi
from ringobot.serviceData.featureEngineering import *
from ringobot.serviceData.calculateBuySellSignals import *
from tqdm import tqdm
pd.set_option('display.max_columns', None)

symbols = [
    "BTCUSDT", "ETHUSDT", "XRPUSDT", "BCHUSDT", "LTCUSDT",
    "ADAUSDT", "BNBUSDT", "DOTUSDT",
    "SOLUSDT", "DOGEUSDT", "UNIUSDT", "WBTCUSDT",
    "XLMUSDT", "LINKUSDT", "AAVEUSDT", "VETUSDT", "THETAUSDT",
    "ALGOUSDT", "ATOMUSDT", "FILUSDT", "KSMUSDT",
    "EOSUSDT", "TRXUSDT", "XVGUSDT", "ZECUSDT", "MKRUSDT",
    "BATUSDT", "COMPUSDT", "SUSHIUSDT", "SNXUSDT",
    "YFIUSDT", "UMAUSDT", "CRVUSDT", "RSRUSDT", "KAVAUSDT",
    "NMRUSDT", "BANDUSDT", "RENUSDT", "KNCUSDT",
    "ZILUSDT", "PAXGUSDT", "OMGUSDT", "DASHUSDT", "ZRXUSDT"
]


def import_coin_data(symbol):
    try:
        print(f"Importing data for {symbol}")
        df = pd.read_parquet(f"kline_data/{symbol}/{symbol}-5m.parquet")
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.sort_values(by='timestamp')
        df = df.set_index('timestamp')
        df = df[["close", "volume"]]
        df = df.resample('1h').agg({'close': 'last', 'volume': 'sum'}).dropna()
        df["symbol"] = symbol
        df = calculate_bollinger_bands(df)
        df = calculate_macd(df)
        df = calculate_rsi(df)
        df = calculate_rolling_mean_std(df)
        df = calculate_vwma(df)
        df.to_parquet(f"kline_data/{symbol}/{symbol}-1h.parquet")
        influxDBwriteApi.write(bucketMain, org, df, data_frame_measurement_name="coinsH", data_frame_tag_columns=["symbol"])
        influxDBwriteApi.close()
        del df
        gc.collect()
    except Exception as e:
        print(e)


def import_buy_sell_signals(symbol):
    try:
        print(f"Importing buy/sell signals for {symbol}")
        df = pd.read_parquet(f"kline_data/{symbol}/{symbol}-1h.parquet")
        df = calculate_macd_buy_sell_signals(df)
        df = calculate_rsi_buy_sell_signals(df)
        df = calculate_bollinger_band_buy_sell_signals(df)
        df = calculate_rolling_mean_std_buy_sell_signals(df)
        df = calculate_vwma_buy_sell_signals(df)
        df.drop(["bollinger_upper", "bollinger_lower", "bollinger_width", "bollinger_pct_b", "macd", "macd_signal", "macd_hist",
                    "rsi", "rolling_mean_12h", "rolling_std_12h", "rolling_mean_36h", "rolling_std_36h", "rolling_mean_96h", "rolling_std_96h",
                    "vwma_4h", "vwma_24h", "vwma_96h"], axis=1, inplace=True)
        signal_cols = [col for col in df.columns if "buy" in col or "sell" in col]
        df[signal_cols] = df[signal_cols].astype(int)
        # drop records with no 1s in signal_cols
        df = df[df[signal_cols].sum(axis=1) > 0]
        df.to_parquet(f"kline_data/{symbol}/{symbol}-1h-signals.parquet")
        influxDBwriteApi.write(bucketMain, org, df, data_frame_measurement_name="signalsv1", data_frame_tag_columns=["symbol"])
        influxDBwriteApi.close()
        del df
        gc.collect()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    for symbol in tqdm(symbols):
        #import_coin_data(symbol)
        import_buy_sell_signals(symbol)




