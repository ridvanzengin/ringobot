import lightgbm as lgbm
import os
import pickle
from ringobot.config import ROOT_DIR

class CatBoostModel20231201:
    columns = ['close', 'volume', 'symbol', 'bollinger_upper', 'bollinger_lower',
       'bollinger_width', 'bollinger_pct_b', 'macd', 'macd_signal',
       'macd_hist', 'rsi', 'rolling_mean_12h', 'rolling_std_12h',
       'rolling_mean_36h', 'rolling_std_36h', 'rolling_mean_96h',
       'rolling_std_96h', 'vwma_4h', 'vwma_24h', 'vwma_96h']
    resample = '1h'
    windowSize = 24  # hour
    shift = 1
    matrixSize = 24  # matrix size as model input
    model = lgbm.Booster(model_file=os.path.join(ROOT_DIR, "ringobot/serviceData/train/models/lgbm_classifier.txt"))
    means =[38.671, 291.89, 284.236, 287.935, 289.955, 0.0, 0.0, 0.0, -4.397, -0.0, 286.181, 117.674, 415.509, 38.669, 38.669, 0.626, -1.018, -0.001, -1.246, -0.0, 0.03]
    stds = [0.4, 1979.246, 974.825, 829.44, 781.82, 0.034, 0.034, 0.339, 2637.569, 0.098, 1039.331, 434.478, 1831.852, 0.417, 0.42, 0.573, 0.39, 0.553, 0.326, 0.11, 0.587]
    features = ['temp', 'xyz_std', 'last6daysMean_xyz_std', 'last13daysMean_xyz_std', 'last20daysMean_xyz_std',
                'tempDiff10days_temp', 'tempDiff6days_temp', 'tempDiff3days_temp', 'delta_xyz_std', 'delta_temp',
                'rolling_mean_1h_xyz_std', 'rolling_median_1h_xyz_std', 'rolling_std_1h_xyz_std', 'rolling_mean_1h_temp',
                'rolling_median_1h_temp', 'rolling_skewness_1h_xyz_std', 'rolling_kurtosis_1h_xyz_std', 'rolling_skewness_1h_temp',
                'rolling_kurtosis_1h_temp', 'rolling_1h_temp_diff', 'rolling_corr_1h_xyz_std_temp']