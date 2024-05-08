from ringobot.serviceData.featureEngineering import *
from ringobot.serviceData.train.preprocess import sliding_window, label_data
from ringobot.serviceData.binance import BinanceAPI
import pandas as pd
import matplotlib.pyplot as plt
from ringobot.db.session import Coin
from ringobot.db.utils import session_scope
from catboost import CatBoostClassifier
import pickle
pd.set_option('display.max_columns', None)

# Initialize Binance API
binanceApi = BinanceAPI()


def create_signals(df):
    df = calculate_bollinger_bands(df)
    df = calculate_macd(df)
    df = calculate_rsi(df)
    df = calculate_rolling_mean_std(df)
    df = calculate_vwma(df)
    df, labels = label_data(df)
    windows = sliding_window(df, window_size=24)
    return windows, labels


def predict_signals(windows):
    # Load the trained model
    catboostModel = CatBoostClassifier().load_model("ringobot/serviceData/train/models/catboost_classifier.cbm")
    # Flatten the windows
    time_steps, n_features = windows.shape[1], windows.shape[2]
    windows = windows.reshape(-1, time_steps * n_features)
    # Standardize the data
    scaler = pickle.load(open("ringobot/serviceData/train/models/scaler.pkl", "rb"))
    windows = scaler.transform(windows)
    # Load the trained model
    catboost_predictions = catboostModel.predict(windows)
    return catboost_predictions

def get_the_first_signal(data):
    """
    Finds the first non-zero signal in a pandas Series efficiently.
    If a signal is found, all subsequent signals of the same type are set to zero until a new signal is found.
    When a new signal is found, it is set as the last signal and the process repeats.

    Args:
        data (pd.DataFrame): The DataFrame containing the data.

    Returns:
        pd.DataFrame: The DataFrame with the signal column modified.
    """

    last_signal = 0
    for index, row in data.iterrows():  # Iterate using iterrows
        value = row["result"]  # Store the value for clarity
        if value != 0 and last_signal == 0:
            last_signal = value
        elif value == 1 and last_signal == 1:
            last_signal = 1
            data.loc[index, "result"] = 0  # Direct assignment using loc
        elif value == -1 and last_signal == -1:
            last_signal = -1
            data.loc[index, "result"] = 0  # Direct assignment using loc
        elif value != 0 and last_signal != 0:
            last_signal = value
    return data



def calculateProfitPercent(df, symbol):
    """
    Calculate the profit percentage for each trade.
    The target column should start with 1 and end with -1
    """
    df = df[df['result'] != 0].copy()
    # make sure df has at least 4 rows
    if len(df) < 4:
        return 0
    # make sure the first signal is buy and the last signal is sell
    if df['result'].iloc[0] == -1:
        df = df[1:].copy()
    if df['result'].iloc[-1] == 1:
        df = df[:-1].copy()
    df['profit'] = df['close'].diff().shift(-1)
    df["profit_percent"] = df["profit"] / df["close"]
    print(f"Profit percent for {symbol}: {df['profit_percent'].sum() * 100:.2f}%")



def plotTheData(df, symbol):
    # Plot the data
    fig, ax = plt.subplots()
    ax.plot(df.index, df['close'], label='Close Price', color='black')
    # Plotting buy and sell signals
    ax.plot(df[df['result'] == 1].index, df[df['result'] == 1]['close'], '^', markersize=10, color='g', lw=0,
            label='buy')
    ax.plot(df[df['result'] == -1].index, df[df['result'] == -1]['close'], 'v', markersize=10, color='r', lw=0,
            label='sell')

    ax.legend()
    plt.title(f'{symbol} Price and Signals')
    plt.xlabel('Timestamp')
    plt.ylabel('Price')
    plt.xticks(rotation=45)
    plt.savefig(f"plots/{symbol}.png")
    plt.close()


if __name__ == "__main__":
    window_size = 24
    binance = BinanceAPI()
    with session_scope() as db_session:
        symbols = Coin.get_active_coins(db_session)
        symbols = [symbol.name for symbol in symbols]
    for symbol in symbols:
        interval = "1h"
        df = binance.get_symbol_data(symbol, interval, limit=240)
        windows, labels = create_signals(df)
        probs = predict_signals(windows)
        df = df.iloc[window_size:]
        df["result"] = probs
        df = get_the_first_signal(df)
        df.dropna(inplace=True)
        calculateProfitPercent(df, symbol)
        plotTheData(df, symbol)
