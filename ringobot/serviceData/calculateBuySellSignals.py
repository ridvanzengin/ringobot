
def calculate_macd_buy_sell_signals(data):
    """
    This function calculates buy and sell signals based on MACD crossover strategy.

    Args:
        data (pd.DataFrame): DataFrame containing MACD data.

    Returns:
        pd.DataFrame: DataFrame with new columns for buy and sell signals.
    """
    data['buy_signal_macd'] = (data['macd'] > data['macd_signal']) & (data['macd'].shift() < data['macd_signal'].shift())
    data['sell_signal_macd'] = (data['macd'] < data['macd_signal']) & (data['macd'].shift() > data['macd_signal'].shift())

    return data


def calculate_rsi_buy_sell_signals(data, lower=40, upper=60, trend_window=14):
    """
    This function calculates buy and sell signals based on RSI overbought/oversold levels with trend confirmation.

    Args:
        data (pd.DataFrame): DataFrame containing RSI data.
        lower (int, optional): Lower threshold for RSI (default: 40).
        upper (int, optional): Upper threshold for RSI (default: 60).
        trend_window (int, optional): Window size for calculating RSI trend (default: 14).

    Returns:
        pd.DataFrame: DataFrame with new columns for buy and sell signals.
    """
    # Calculate RSI trend
    data['rsi_trend'] = data['rsi'].diff(trend_window)

    # Generate buy and sell signals based on modified RSI thresholds with trend confirmation
    data['buy_signal_rsi'] = (data['rsi'] < lower) & (data['rsi_trend'] > 0)
    data['sell_signal_rsi'] = (data['rsi'] > upper) & (data['rsi_trend'] < 0)

    # Drop the RSI trend column
    data.drop(columns=['rsi_trend'], inplace=True)

    return data


def calculate_bollinger_band_buy_sell_signals(data, threshold_pct_b_sell=0.8, min_hold_below_bb_lower=1, bollinger_pct_b_window=3):
    """
    This function calculates buy and sell signals based on Bollinger Bands with a more balanced approach.

    Args:
        data (pd.DataFrame): DataFrame containing Bollinger Bands data.
        threshold_pct_b_sell (float, optional): Threshold for bollinger_pct_b (default: 0.8).
        min_hold_below_bb_lower (int, optional): Minimum number of periods price needs to stay below lower Bollinger Band for a buy signal (default: 1).

    Returns:
        pd.DataFrame: DataFrame with new columns for buy and sell signals.
    """
    data['prev_close'] = data['close'].shift(1)  # Previous day's closing price

    # Buy signal:
    # - Price closes below lower Bollinger Band
    # - Price on the previous day was above the lower Bollinger Band (to avoid noise)
    # - Price stays below lower Bollinger Band for at least min_hold_below_bb_lower periods
    data['buy_signal_bollinger'] = (data['close'] < data['bollinger_lower']) & \
                                   (data['prev_close'] > data['bollinger_lower']) & \
                                   (data['close'].rolling(min_hold_below_bb_lower).min() < data['bollinger_lower'])

    # Sell signal:
    # - Price closes above the upper Bollinger Band
    # - %B indicator exceeding a threshold
    data['bollinger_pct_b_rolling'] = data['bollinger_pct_b'].rolling(bollinger_pct_b_window).min()
    data['sell_signal_bollinger'] = (data['close'] > data['bollinger_upper']) & \
                                    (data['bollinger_pct_b'] > threshold_pct_b_sell) & \
                                    (data['bollinger_pct_b_rolling'] > threshold_pct_b_sell)

    return data

def calculate_vwma_buy_sell_signals(data, volume_threshold=1.5):
    """
    This function calculates buy and sell signals based on VWMA crossover strategy with volume confirmation.

    Args:
        data (pd.DataFrame): DataFrame containing VWMA and volume data.
        volume_threshold (float, optional): Threshold multiplier for volume confirmation (default: 1.5).

    Returns:
        pd.DataFrame: DataFrame with new columns for buy and sell signals.
    """
    # Calculate average volume over a specified period
    avg_volume = data['volume'].rolling(window=20).mean()

    # Buy signal condition: Short-term VWMA above medium-term VWMA and volume exceeds threshold
    buy_condition = (
        (data['vwma_4h'] > data['vwma_24h']) &
        (data['vwma_24h'] > data['vwma_96h']) &
        (data['close'] > data['vwma_4h']) &
        (data['volume'] > avg_volume * volume_threshold)
    )

    # Sell signal condition: Short-term VWMA below medium-term VWMA and volume exceeds threshold
    sell_condition = (
        (data['vwma_4h'] < data['vwma_24h']) &
        (data['vwma_24h'] < data['vwma_96h']) &
        (data['close'] < data['vwma_4h']) &
        (data['volume'] > avg_volume * volume_threshold)
    )

    # Generate buy and sell signals based on conditions
    data['buy_signal_vwma'] = buy_condition
    data['sell_signal_vwma'] = sell_condition

    return data


def calculate_rolling_mean_std_buy_sell_signals(data):
    """
    This function calculates buy and sell signals based on rolling mean and standard deviation.

    Args:
        data (pd.DataFrame): DataFrame containing rolling mean and standard deviation data.

    Returns:
        pd.DataFrame: DataFrame with new columns for buy and sell signals.
    """
    # Add logic for multi-timeframe analysis
    # For example, compare rolling mean + std for different timeframes (12h, 36h, 96h)
    data['buy_signal_rolling'] = (
        (data['close'] < data['rolling_mean_12h'] - data['rolling_std_12h']) &
        (data['close'].shift() > data['rolling_mean_12h'].shift() - data['rolling_std_12h'].shift()) &
        (data['rolling_mean_12h'] > data['rolling_mean_36h']) &  # Short-term above medium-term
        (data['rolling_mean_36h'] > data['rolling_mean_96h'])     # Medium-term above long-term
    )

    data['sell_signal_rolling'] = (
        (data['close'] > data['rolling_mean_12h'] + data['rolling_std_12h']) &
        (data['close'].shift() < data['rolling_mean_12h'].shift() + data['rolling_std_12h'].shift()) &
        (data['rolling_mean_12h'] < data['rolling_mean_36h']) &  # Short-term below medium-term
        (data['rolling_mean_36h'] < data['rolling_mean_96h'])     # Medium-term below long-term
    )

    return data

