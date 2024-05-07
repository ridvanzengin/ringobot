import pandas as pd
import numpy as np


def calculate_macd(data, slow=26, fast=12, smooth=9):
    """
    This function calculates the Moving Average Convergence Divergence (MACD) indicator.

    Args:
        data (pd.DataFrame): DataFrame containing OHLC data.
        slow (int, optional): Period for the slow moving average (default: 26).
        fast (int, optional): Period for the fast moving average (default: 12).
        smooth (int, optional): Period for smoothing the MACD line with a moving average (default: 9).

    Returns:
        pd.DataFrame: DataFrame with new columns for MACD, MACD signal line, and MACD histogram.
    """
    ema_slow = data['close'].ewm(span=slow, min_periods=slow).mean()
    ema_fast = data['close'].ewm(span=fast, min_periods=fast).mean()
    data["macd"] = ema_fast - ema_slow
    data["macd_signal"] = data["macd"].ewm(span=smooth, min_periods=smooth).mean()
    data["macd_hist"] = data["macd"] - data["macd_signal"]
    return data


def calculate_rsi(data, period=14):
    """
    This function calculates the Relative Strength Index (RSI) indicator.

    Args:
        data (pd.DataFrame): DataFrame containing OHLC data.
        period (int, optional): Period for calculating RSI (default: 14).

    Returns:
        pd.DataFrame: DataFrame with a new column for RSI.
    """
    delta = data['close'].diff()
    delta = delta.dropna()
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    avg_gain = up.ewm(alpha=1 / period, min_periods=period).mean()
    avg_loss = abs(down).ewm(alpha=1 / period, min_periods=period).mean()

    # Handling division by zero
    avg_loss[avg_loss == 0] = np.nan

    rs = avg_gain / avg_loss
    rsi = 100 - 100 / (1 + rs)
    data['rsi'] = rsi
    return data


def calculate_bollinger_bands(data, window=20, std=2):
    """
    This function calculates the Bollinger Bands indicator.

    Args:
        data (pd.DataFrame): DataFrame containing OHLC data.
        window (int, optional): Window size for calculating moving average (default: 20).
        std (int, optional): Number of standard deviations for the bands (default: 2).

    Returns:
        pd.DataFrame: DataFrame with new columns for upper and lower Bollinger Bands.
    """
    moving_average = data['close'].rolling(window=window).mean()
    std_dev = data['close'].rolling(window=window).std()
    upper_band = moving_average + std * std_dev
    lower_band = moving_average - std * std_dev
    data['bollinger_upper'] = upper_band
    data['bollinger_lower'] = lower_band
    data['bollinger_width'] = (data['bollinger_upper'] - data['bollinger_lower']) / moving_average * 100
    data['bollinger_pct_b'] = (data['close'] - data['bollinger_lower']) / (data['bollinger_upper'] - data['bollinger_lower'])
    return data


def calculate_rolling_mean_std(data, windows=[12, 36, 96]):
    """
    This function calculates the rolling mean and standard deviation for different window sizes.

    Args:
        data (pd.DataFrame): DataFrame containing OHLC data.
        windows (list): List of window sizes for calculating the rolling mean.

    Returns:
        pd.DataFrame: DataFrame with new columns for rolling mean and standard deviation.
    """
    for window in windows:
        data[f'rolling_mean_{window}h'] = data['close'].rolling(window=window).mean()
        data[f'rolling_std_{window}h'] = data['close'].rolling(window=window).std()
    return data


def calculate_vwma(data, windows=[4, 24, 96]):
    """
    This function calculates the Volume Weighted Moving Average (VWMA) for different window sizes.

    Args:
        data (pd.DataFrame): DataFrame containing OHLCV data.
        windows (list): List of window sizes for calculating the VWMA.

    Returns:
        pd.DataFrame: DataFrame with new columns for VWMA.
    """
    for window in windows:
        data[f'vwma_{window}h'] = (data['close'] * data['volume']).rolling(window=window).sum() / data['volume'].rolling(window=window).sum()
    return data


def calculate_price_diff(data, windows=[1, 3, 7]):  # days
    """
    This function calculates the price difference for different window sizes.
    It
    """

    data["windowId"] = data.index.hour
    data["windowId"] = data["windowId"].astype(int)
    for window in windows:
        shifted_mean = data.groupby("windowId")["close"].transform(
            lambda grp: grp.shift(1, "d").rolling(window=f'{window}d').mean())
        data[f"priceDiff{window}d"] = data["close"] - shifted_mean
    data = data.drop("windowId", axis=1)
    data["priceDiffTrendPercent"] = data[[f"priceDiff{window}d" for window in windows]].rolling(window=12).mean().mean(axis=1) / data["close"]
    return data


def label_data(df, future_period=3, threshold=0.02, trend_threshold=0, train=False):
    """
    Function to label the data based on the future price movement and trend percentage
    :param df: DataFrame with the price data
    :param future_period: Future period for the price change calculation
    :param threshold: Threshold for the price change
    :param trend_threshold: Threshold for the trend percentage
    :param train: Boolean flag indicating whether to drop NaN values for training data
    :return: DataFrame with the labels
    """
    # Calculate the future price change
    df['future_price'] = df['close'].shift(-future_period)
    df['price_change'] = df['future_price'] - df['close']
    df['price_change_pct'] = df['price_change'] / df['close']

    # Label the data based on the price change and trend percentage
    df['label'] = 0
    df.loc[(df['price_change_pct'] > threshold) & (df['priceDiffTrendPercent'] > trend_threshold), 'label'] = 1
    df.loc[(df['price_change_pct'] < -threshold) & (df['priceDiffTrendPercent'] < -trend_threshold), 'label'] = -1

    if train:
        df.dropna(inplace=True)

    labels = df['label'].values
    df.drop(['future_price', 'price_change', 'price_change_pct', 'label', 'priceDiffTrendPercent'], axis=1, inplace=True)
    if "symbol" in df.columns:
        df.drop("symbol", axis=1, inplace=True)

    return df, labels


def sliding_window(df, window_size):
    windows = []
    for i in range(len(df) - window_size):
        window = df.iloc[i:i + window_size].values
        windows.append(window)
    return np.array(windows)

