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




