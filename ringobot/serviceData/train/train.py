import numpy as np
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import GridSearchCV
import seaborn as sns
import matplotlib.pyplot as plt
from ringobot.serviceData.train.preprocess import under_sample_data, over_sample_data

# Load the data
X_train = np.load("data/class20240508-window24/X_train.npy")
X_test = np.load("data/class20240508-window24/X_test.npy")
y_train = np.load("data/class20240508-window24/y_train.npy")
y_test = np.load("data/class20240508-window24/y_test.npy")


# Balance the data
X_train, y_train = under_sample_data(X_train, y_train)

# print class distribution
print("Class Distribution train data")
unique, counts = np.unique(y_train, return_counts=True)
print(dict(zip(unique, counts)))

print("Class Distribution test data")
unique, counts = np.unique(y_test, return_counts=True)
print(dict(zip(unique, counts)))


def evaluate_classification(y_true, y_pred):
    """
    Evaluate the classification performance using precision, recall, and F1-score.

    Parameters:
    y_true (array-like): True labels.
    y_pred (array-like): Predicted labels.

    Returns:
    dict: Dictionary containing precision, recall, and F1-score for each class.
    """
    f1 = f1_score(y_true, y_pred, average="macro")
    precision = precision_score(y_true, y_pred, average="macro")
    recall = recall_score(y_true, y_pred, average="macro")
    print(f"Precision: {precision:.2f}, Recall: {recall:.2f}, F1-score: {f1:.2f}")
    return f1, precision, recall


# Random Forest Classifier
print("Random Forest Classifier Training Started")
rf_model = RandomForestClassifier(random_state=42, n_jobs=-1, verbose=2)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_f1, rf_precision, rf_recall = evaluate_classification(y_test, rf_pred)


# CatBoost Classifier
print("CatBoost Classifier Training Started")
catboost_model = CatBoostClassifier(random_seed=42, verbose=200, thread_count=-1)
catboost_model.fit(X_train, y_train)
catboost_pred = catboost_model.predict(X_test)
catboost_f1, catboost_precision, catboost_recall = evaluate_classification(y_test, catboost_pred)

# LightGBM Classifier
print("LightGBM Classifier Training Started")
lgbm_model = LGBMClassifier( random_state=42, n_jobs=-1, verbose=2)
lgbm_model.fit(X_train, y_train)
lgbm_pred = lgbm_model.predict(X_test)
lgbm_f1, lgbm_precision, lgbm_recall = evaluate_classification(y_test, lgbm_pred)

# Model Comparison

f1_scores = [rf_f1, catboost_f1, lgbm_f1]
precision_scores = [rf_precision, catboost_precision, lgbm_precision]
recall_scores = [rf_recall, catboost_recall, lgbm_recall]

for model, f1, precision, recall in zip(["Random Forest", "CatBoost", "LightGBM"], f1_scores, precision_scores, recall_scores):
    print(f"{model} Classifier:")
    print(f"F1-score: {f1:.3f}, Precision: {precision:.3f}, Recall: {recall:.3f}")
    print("\n")

# Get the confusion matrix
cm = confusion_matrix(y_test, catboost_pred)



# Plot the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False)
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

test_name_date = "20240507"
# Save the model
lgbm_model.booster_.save_model(f"ringobot/serviceData/train/models/{test_name_date}_lgbm_classifier.txt")
catboost_model.save_model(f"ringobot/serviceData/train/models/{test_name_date}_catboost_classifier.cbm")



"""
Initial Output:

Random Forest Classifier:
F1-score: 0.326, Precision: 0.500, Recall: 0.339
XGBoost Classifier:
F1-score: 0.325, Precision: 0.504, Recall: 0.339
CatBoost Classifier:
F1-score: 0.326, Precision: 0.501, Recall: 0.339
LightGBM Classifier:
F1-score: 0.322, Precision: 0.499, Recall: 0.337

confusion_matrix:
array([[   219,  17533,    109],
       [   257, 303696,    165],
       [   156,  18597,     97]])
"""

"""
Undersampled Output:

Random Forest Classifier:
F1-score: 0.407, Precision: 0.398, Recall: 0.443
CatBoost Classifier:
F1-score: 0.416, Precision: 0.405, Recall: 0.454
LightGBM Classifier:
F1-score: 0.416, Precision: 0.405, Recall: 0.451

confusion_matrix:
array([[  4792,   8877,   4192],
       [ 25946, 253488,  24684],
       [  4767,   9180,   4903]])
"""

"""
Oversampled Output:

Random Forest Classifier:
F1-score: 0.332, Precision: 0.471, Recall: 0.342
CatBoost Classifier:
F1-score: 0.417, Precision: 0.405, Recall: 0.453
LightGBM Classifier:
F1-score: 0.417, Precision: 0.406, Recall: 0.452

confusion_matrix:
array([[  4825,   8895,   4141],
       [ 25321, 254908,  23889],
       [  4809,   9292,   4749]])
       
       

"""