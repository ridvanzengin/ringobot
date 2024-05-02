import pandas as pd
import numpy as np
import lightgbm as lgbm
import pickle
from ringobot.serviceData.train.preprocess import label_data, sliding_window

# Load the scaler
with open("data/class-window24-threshold0.02-future3/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

# Load the LightGBM model
lgbm_model = lgbm.Booster(model_file="data/class-window24-threshold0.02-future3/lgbm_classifier.txt")

def preprocess_new_data(new_data, window_size):
    """
    Preprocess new data before making predictions.

    Parameters:
    new_data (DataFrame): DataFrame containing new data.
    window_size (int): Size of the sliding window.

    Returns:
    numpy array: Preprocessed data ready for prediction.
    """
    # Make sure new_data has the same format and columns as the training data
    # For example:
    # 1. Label the data
    # 2. Perform sliding window method
    # 3. Standardize the data using the loaded scaler
    # 4. Reshape the data if necessary

    # Label the data (you might need to adjust this depending on your new_data format)
    labeled_data = label_data(new_data, train=False)

    # Perform sliding window method
    windows, _, _ = sliding_window(labeled_data, window_size)
    time_steps, n_features = windows.shape[1], windows.shape[2]
    windows = windows.reshape(-1, time_steps * n_features)
    # Standardize the data using the loaded scaler
    preprocessed_data = scaler.transform(windows)

    return preprocessed_data

def make_predictions(preprocessed_data):
    """
    Make predictions using the preprocessed data and the trained model.

    Parameters:
    preprocessed_data (numpy array): Preprocessed data ready for prediction.

    Returns:
    numpy array: Predicted labels.
    """
    # Use the trained LightGBM model to make predictions on the preprocessed data
    predictions = lgbm_model.predict(preprocessed_data)

