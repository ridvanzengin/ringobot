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
from ringobot.serviceData.featureEngineering import sliding_window, label_data, calculate_price_diff

pd.set_option('display.max_columns', None)


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


def preprocess_data(df, window_size, test_size, columns):
    # Label the data
    df = calculate_price_diff(df)
    df, labels = label_data(df, train=True)
    df = df[columns]
    # Perform sliding window method
    windows = sliding_window(df, window_size)
    labels = labels[window_size:]
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(windows, labels, test_size=test_size, shuffle=False)

    return X_train, X_test, y_train, y_test



if __name__ == "__main__":
    window_size = 24  # Define window size
    test_size = 0.2  # Define test size
    test_name_date = "20240509"
    columns = ['close', 'volume',
      # 'bollinger_upper', 'bollinger_lower', 'bollinger_width', 'bollinger_pct_b', 'macd', 'macd_signal', 'macd_hist', 'rsi',
       'rolling_mean_12h', 'rolling_std_12h', 'rolling_mean_36h', 'rolling_std_36h', 'rolling_mean_96h',
       'rolling_std_96h', 'vwma_4h', 'vwma_24h', 'vwma_96h', 'priceDiff1d', 'priceDiff3d', 'priceDiff7d']

    X_train_list = []
    X_test_list = []
    y_train_list = []
    y_test_list = []

    for symbol in tqdm(symbols):
        df = pd.read_parquet(f"kline_data/{symbol}/{symbol}-1h.parquet")
        X_train, X_test, y_train, y_test = preprocess_data(df, window_size, test_size, columns)
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
    os.makedirs(f"data/class{test_name_date}-window{window_size}", exist_ok=True)
    with open(f"ringobot/serviceData/train/models/scaler{test_name_date}.pkl", "wb") as f:
        pickle.dump(scaler, f)
    # Save combined data
    np.save(f"data/class{test_name_date}-window{window_size}/X_train.npy", X_train_scaled)
    np.save(f"data/class{test_name_date}-window{window_size}/X_test.npy", X_test_scaled)
    np.save(f"data/class{test_name_date}-window{window_size}/y_train.npy", y_train_combined)
    np.save(f"data/class{test_name_date}-window{window_size}/y_test.npy", y_test_combined)
    # print shape of files
    print(f"X_train shape: {X_train_scaled.shape}")
    print(f"X_test shape: {X_test_scaled.shape}")
    print(f"y_train shape: {y_train_combined.shape}")
    print(f"y_test shape: {y_test_combined.shape}")
