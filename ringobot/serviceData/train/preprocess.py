import pandas as pd
import gc
from tqdm import tqdm
import os
from ringobot.serviceData.bulkDataImport import symbols
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import numpy as np
import pickle
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler

pd.set_option('display.max_columns', None)


def label_data(df, future_period=3, threshold=0.02, train=False):
    """
    Function to label the data based on the future price movement
    :param df: DataFrame with the price data
    :param future_period: Future period for the price change calculation
    :param threshold: Threshold for the price change
    :return: DataFrame with the labels
    """
    # Calculate the future price change
    df['future_price'] = df['close'].shift(-future_period)
    df['price_change'] = df['future_price'] - df['close']
    df['price_change_pct'] = df['price_change'] / df['close']

    # Label the data based on the price change
    df['label'] = 0
    df.loc[df['price_change_pct'] > threshold, 'label'] = 1
    df.loc[df['price_change_pct'] < -threshold, 'label'] = -1
    if train:
        df.dropna(inplace=True)
    labels = df['label'].values
    df.drop(['future_price', 'price_change', 'price_change_pct', 'label'], axis=1, inplace=True)
    if "symbol" in df.columns:
        df.drop("symbol", axis=1, inplace=True)
    return df, labels


def sliding_window(df, window_size):
    windows = []
    for i in range(len(df) - window_size):
        window = df.iloc[i:i + window_size].values
        windows.append(window)
    return np.array(windows)


def under_sample_data(X_train, y_train):
    # Balance the data using RandomUnderSampler
    rus = RandomUnderSampler()
    X_train_resampled, y_train_resampled = rus.fit_resample(X_train, y_train)
    return X_train_resampled, y_train_resampled


def over_sample_data(X_train, y_train):
    # Balance the data using RandomOverSampler
    ros = RandomOverSampler()
    X_train_resampled, y_train_resampled = ros.fit_resample(X_train, y_train)
    return X_train_resampled, y_train_resampled


def preprocess_data(df, window_size, test_size, threshold, future_period=3, balanace_data=False):
    # Label the data
    df, labels = label_data(df, future_period=future_period, threshold=threshold, train=True)
    # Perform sliding window method
    windows = sliding_window(df, window_size)
    labels = labels[window_size:]
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(windows, labels, test_size=test_size, shuffle=False)

    return X_train, X_test, y_train, y_test



if __name__ == "__main__":
    window_size = 24  # Define window size
    test_size = 0.2  # Define test size
    threshold = 0.02  # Define threshold for price change
    future_period = 3  # Define future period for price change

    X_train_list = []
    X_test_list = []
    y_train_list = []
    y_test_list = []

    for symbol in tqdm(symbols):
        df = pd.read_parquet(f"kline_data/{symbol}/{symbol}-1h.parquet")
        X_train, X_test, y_train, y_test = preprocess_data(df, window_size, test_size, threshold, future_period, symbol)
        X_train_list.append(X_train)
        X_test_list.append(X_test)
        y_train_list.append(y_train)
        y_test_list.append(y_test)
        del df, X_train, X_test, y_train, y_test
        gc.collect()

    # Combine data for all symbols
    X_train_combined = np.concatenate(X_train_list, axis=0)
    X_test_combined = np.concatenate(X_test_list, axis=0)
    y_train_combined = np.concatenate(y_train_list, axis=0)
    y_test_combined = np.concatenate(y_test_list, axis=0)


    #flattening the data
    time_steps, n_features = X_train_combined.shape[1], X_train_combined.shape[2]
    X_train_combined = X_train_combined.reshape(-1, time_steps * n_features)
    X_test_combined = X_test_combined.reshape(-1, time_steps * n_features)

    # Standardize the data
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_combined)
    X_test_scaled = scaler.transform(X_test_combined)
    os.makedirs(f"data/class-window{window_size}-threshold{threshold}-future{future_period}", exist_ok=True)
    with open(f"data/class-window{window_size}-threshold{threshold}-future{future_period}/scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    # Save combined data
    np.save(f"data/class-window{window_size}-threshold{threshold}-future{future_period}/X_train.npy", X_train_scaled)
    np.save(f"data/class-window{window_size}-threshold{threshold}-future{future_period}/X_test.npy", X_test_scaled)
    np.save(f"data/class-window{window_size}-threshold{threshold}-future{future_period}/y_train.npy", y_train_combined)
    np.save(f"data/class-window{window_size}-threshold{threshold}-future{future_period}/y_test.npy", y_test_combined)
    # print shape of files
    print(f"X_train shape: {X_train_scaled.shape}")
    print(f"X_test shape: {X_test_scaled.shape}")
    print(f"y_train shape: {y_train_combined.shape}")
    print(f"y_test shape: {y_test_combined.shape}")
