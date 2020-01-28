# %%
import os
import sys
# os.chdir("../../..")
os.environ['DJANGO_SETTINGS_MODULE'] = 'MAKDataHub.settings'
import django
django.setup()

# %%
import math
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from MAKDataHub.services import Services

profile_service = Services.profile_service()
storage_service = Services.storage_service()
last_run = profile_service.get_last_profile_creation_run()

## New database
full_df: pd.DataFrame = pickle.load(last_run.unlock_data.open('rb'))
# full_df = full_df.loc[full_df.DeviceId != 3].reset_index(drop = True)

## Old database
# unlock_data_path = storage_service.download_file(last_run.unlock_data_uri)
# full_df: pd.DataFrame = pickle.load(open(unlock_data_path, 'rb'))
# full_df = full_df.loc[full_df.DeviceId != '1439cbc3ad71ac06'].reset_index(drop = True)

# %%
df = full_df.iloc[:, list(range(36)) + list(range(72, 108)) + list(range(108, 144)) + list(range(180, 216)) + [216]].reset_index(drop = True)
df = df.loc[(df.DeviceId != 4) & (df.DeviceId != 7), :].reset_index(drop = True)
X, y = df.iloc[:, 0:-1], df.iloc[:, -1]

#%%
full_df.shape

# %%
display(full_df.iloc[:, list(range(36)) + [216]].groupby('DeviceId').agg([np.min, np.max]))
display(full_df.iloc[:, list(range(36, 72)) + [216]].groupby('DeviceId').agg([np.min, np.max]))
display(full_df.iloc[:, list(range(72, 108)) + [216]].groupby('DeviceId').agg([np.min, np.max]))
display(full_df.iloc[:, list(range(108, 144)) + [216]].groupby('DeviceId').agg([np.min, np.max]))
display(full_df.iloc[:, list(range(144, 180)) + [216]].groupby('DeviceId').agg([np.min, np.max]))
display(full_df.iloc[:, list(range(180, 216)) + [216]].groupby('DeviceId').agg([np.min, np.max]))

# %%
display(full_df.iloc[:, list(range(36)) + [216]].groupby('DeviceId').agg([np.mean]))
display(full_df.iloc[:, list(range(36, 72)) + [216]].groupby('DeviceId').agg([np.mean]))
display(full_df.iloc[:, list(range(72, 108)) + [216]].groupby('DeviceId').agg([np.mean]))
display(full_df.iloc[:, list(range(108, 144)) + [216]].groupby('DeviceId').agg([np.mean]))
display(full_df.iloc[:, list(range(144, 180)) + [216]].groupby('DeviceId').agg([np.mean]))
display(full_df.iloc[:, list(range(180, 216)) + [216]].groupby('DeviceId').agg([np.mean]))

# %%
sns.boxplot(df.DeviceId, df.AccMgn_mean)

# %%
sns.boxplot(df.DeviceId, df.AccMgn_median)

# %%
sns.boxplot(df.DeviceId, df.GyrMgn_amax)

# %%
sns.pairplot(df.loc[df.DeviceId != 3, :], hue="DeviceId", vars=["AccMgn_mean", "AccMgn_median"], markers='.')

# %%
test = df.loc[df.DeviceId != '3', :]
sns.swarmplot(data = test, x="DeviceId", y="RotMgn_median")

# %%
test = full_df.loc[:, :]
sns.boxplot(data = test, x="DeviceId", y="GrvMgn_amax")

# %%
print('OneClassSVM')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = y[y == device_id]
    X_device = X.loc[y == device_id, :]
    X_non_device = X.loc[y != device_id, :]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_device, y_device, test_size=0.2)

    from sklearn.svm import OneClassSVM

    estimator = OneClassSVM(random_state = 12369)
    estimator.fit_predict(X_train)

    tp = np.mean(estimator.predict(X_test) == 1)
    fn = np.mean(estimator.predict(X_test) == -1)
    tn = np.mean(estimator.predict(X_non_device) == 1)
    fp = np.mean(estimator.predict(X_non_device) == 1)

    accuracy = (tp + tn) / (tp + tn + fn + fp)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = 2 * recall * precision / (recall + precision)

    accuracies.append(accuracy if not np.isnan(accuracy) else 0)
    precisions.append(precision if not np.isnan(precision) else 0)
    recalls.append(recall if not np.isnan(recall) else 0)
    fscores.append(fscore if not np.isnan(fscore) else 0)

    print(f'{device_id} - accuracy: {round(accuracy, 2)}, precision: {round(precision, 2)}, recall: {round(recall, 2)}')
    # print(f'{device_id} - Class acc: {round(np.mean(estimator.predict(X_test) == 1), 2)}, non-class acc: {round(np.mean(estimator.predict(X_non_device) == -1), 2)}')

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('IsolationForest')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = y[y == device_id]
    X_device = X.loc[y == device_id, :]
    X_non_device = X.loc[y != device_id, :]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_device, y_device, test_size=0.2)

    from sklearn.ensemble import IsolationForest

    estimator = IsolationForest(n_estimators = 10)
    estimator.fit(X_train)

    tp = np.mean(estimator.predict(X_test) == 1)
    fn = np.mean(estimator.predict(X_test) == -1)
    tn = np.mean(estimator.predict(X_non_device) == 1)
    fp = np.mean(estimator.predict(X_non_device) == 1)

    accuracy = (tp + tn) / (tp + tn + fn + fp)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = 2 * recall * precision / (recall + precision)

    accuracies.append(accuracy if not np.isnan(accuracy) else 0)
    precisions.append(precision if not np.isnan(precision) else 0)
    recalls.append(recall if not np.isnan(recall) else 0)
    fscores.append(fscore if not np.isnan(fscore) else 0)

    print(f'{device_id} - accuracy: {round(accuracy, 2)}, precision: {round(precision, 2)}, recall: {round(recall, 2)}')
    # print(f'{device_id} - Class acc: {round(np.mean(estimator.predict(X_device) == 1), 2)}, non-class acc: {round(np.mean(estimator.predict(X_non_device) == -1), 2)}')

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('LOF')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = y[y == device_id]
    X_device = X.loc[y == device_id, :]
    X_non_device = X.loc[y != device_id, :]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_device, y_device, test_size=0.2)

    from sklearn.neighbors import LocalOutlierFactor

    estimator = LocalOutlierFactor(n_neighbors = 10, novelty = True, contamination = 'auto')
    estimator.fit(X_train)

    tp = np.mean(estimator.predict(X_test) == 1)
    fn = np.mean(estimator.predict(X_test) == -1)
    tn = np.mean(estimator.predict(X_non_device) == 1)
    fp = np.mean(estimator.predict(X_non_device) == 1)

    accuracy = (tp + tn) / (tp + tn + fn + fp)
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    fscore = 2 * recall * precision / (recall + precision)

    accuracies.append(accuracy if not np.isnan(accuracy) else 0)
    precisions.append(precision if not np.isnan(precision) else 0)
    recalls.append(recall if not np.isnan(recall) else 0)
    fscores.append(fscore if not np.isnan(fscore) else 0)

    print(f'{device_id} - accuracy: {round(accuracy, 2)}, precision: {round(precision, 2)}, recall: {round(recall, 2)}')
    # print(f'{device_id} - Class acc: {round(np.mean(estimator.predict(X_device) == 1), 2)}, non-class acc: {round(np.mean(estimator.predict(X_non_device) == -1), 2)}')

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('LinearSVC')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.svm import LinearSVC

    estimator = LinearSVC(random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, estimator.predict(X_test)))

    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('KNeighborsClassifier')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.neighbors import KNeighborsClassifier

    estimator = KNeighborsClassifier()
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, estimator.predict(X_test)))
    
    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('GaussianNB')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.naive_bayes import GaussianNB

    estimator = GaussianNB()
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, estimator.predict(X_test)))
    
    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, estimator.predict(X_test)))
    
    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier - global model')
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 12369)

from sklearn.ensemble import RandomForestClassifier

estimator = RandomForestClassifier(random_state = 12369)
estimator.fit(X_train, y_train)

from sklearn.metrics import classification_report
print(classification_report(y_test, estimator.predict(X_test)))

# %% 
print('RandomForestClassifier - standardized')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.preprocessing import StandardScaler
    X_std = StandardScaler().fit_transform(X)
    
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X_std, y_device, test_size=0.2, random_state = 12369)

    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(classification_report(y_test, estimator.predict(X_test)))
    
    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + RFECV')
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 12369)

from yellowbrick.model_selection import RFECV
from sklearn.ensemble import RandomForestClassifier

estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
selector = RFECV(estimator, cv = 5, scoring='f1_weighted', step = 0.05)
selector.fit(X_train, y_train)

selector.show()

from sklearn.metrics import classification_report
print(classification_report(y_test, selector.predict(X_test)))

# %% 
print('RandomForestClassifier + RFE20')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + SelectFromModel')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.feature_selection import SelectFromModel
    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = SelectFromModel(estimator, max_features = 20)
    selector.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.estimator_.predict(X_test)))
    
    report = classification_report(y_test, selector.estimator_.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + PCA')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)
    
    from sklearn.decomposition import PCA
    pca = PCA(n_components=20).fit(X_train)
    X_train = pca.transform(X_train)
    X_test = pca.transform(X_test)

    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, estimator.predict(X_test)))
    
    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + SelectKBest (f_classif)')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)
    
    from sklearn.feature_selection import SelectKBest, f_classif
    selector = SelectKBest(score_func = f_classif, k=20).fit(X_train, y_train)
    X_train = selector.transform(X_train)
    X_test = selector.transform(X_test)

    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, estimator.predict(X_test)))

    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + SelectKBest (mutual_info_classif)')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)
    
    from sklearn.feature_selection import SelectKBest, mutual_info_classif
    selector = SelectKBest(score_func = mutual_info_classif, k=20).fit(X_train, y_train)
    X_train = selector.transform(X_train)
    X_test = selector.transform(X_test)

    from sklearn.ensemble import RandomForestClassifier

    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    estimator.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, estimator.predict(X_test)))

    report = classification_report(y_test, estimator.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + RandomUnderSampler')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.under_sampling import RandomUnderSampler
    X_oversampled, y_oversampled = RandomUnderSampler().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + RandomOverSampler')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.over_sampling import RandomOverSampler
    X_oversampled, y_oversampled = RandomOverSampler().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + SMOTE')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.over_sampling import SMOTE
    X_oversampled, y_oversampled = SMOTE().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %% 
print('RandomForestClassifier + SMOTEENN')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.combine import SMOTEENN
    X_oversampled, y_oversampled = SMOTEENN().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %%
print('RandomForestClassifier + SMOTETomek')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.combine import SMOTETomek
    X_oversampled, y_oversampled = SMOTETomek().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %%
print('BalancedRandomForestClassifier')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from sklearn.feature_selection import RFE
    from imblearn.ensemble import BalancedRandomForestClassifier
    
    estimator = BalancedRandomForestClassifier(n_estimators = 10, random_state = 12369)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_train, y_train)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %%
print('Hyperparameter tuning')
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.combine import SMOTETomek
    X_oversampled, y_oversampled = SMOTETomek().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(random_state = 12369, \
        n_estimators = 50,
        min_samples_leaf = 1, \
        min_samples_split = 2, \
        bootstrap = False, \
        max_features = 'sqrt', \
        max_depth = 20)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)

    # from sklearn.model_selection import GridSearchCV
    # param_grid = { 
    #     'estimator__n_estimators': [10, 50, 100, 200, 500],
    #     'estimator__max_features': ['auto', 'sqrt', 'log2'],
    #     'estimator__max_depth': [4, 5, 6, 7, 8],
    #     'estimator__criterion': ['gini', 'entropy']
    # }
    from sklearn.model_selection import RandomizedSearchCV
    param_grid = {
        'estimator__n_estimators': [10, 20, 50, 100],
        'estimator__max_features': ['auto', 'sqrt', 'log2'],
        'estimator__max_depth': [int(x) for x in np.linspace(2, 20, num = 2)] + [None],
        'estimator__min_samples_split': [2, 3, 4, 5],
        'estimator__min_samples_leaf': [1, 2, 3],
        'estimator__bootstrap': [True, False]
    }
    grid = RandomizedSearchCV(estimator = selector, \
        param_distributions = param_grid, \
        n_iter = 100, \
        cv = 3, \
        verbose = 2, \
        random_state = 42, \
        n_jobs = -1)
    grid.fit(X_oversampled, y_oversampled)
    
    print(grid.best_params_)

# %%
print('RandomForestClassifier + SMOTETomek + parameters')
accuracies = []
precisions = []
recalls = []
fscores = []
for device_id in y.unique():
    y_device = np.where(y == device_id, 1, 0)

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2, random_state = 12369)

    from imblearn.combine import SMOTETomek
    X_oversampled, y_oversampled = SMOTETomek().fit_resample(X_train, y_train)

    from sklearn.feature_selection import RFE
    from sklearn.ensemble import RandomForestClassifier
    
    estimator = RandomForestClassifier(random_state = 12369, \
        n_estimators = 50,
        min_samples_leaf = 1, \
        min_samples_split = 2, \
        bootstrap = False, \
        max_features = 'sqrt', \
        max_depth = 20)
    selector = RFE(estimator, n_features_to_select = 20, step = 0.05)
    selector.fit(X_oversampled, y_oversampled)

    from sklearn.metrics import classification_report
    print(f'Device {device_id}:')
    print(classification_report(y_test, selector.predict(X_test)))
    
    report = classification_report(y_test, selector.predict(X_test), output_dict=True)
    accuracies.append(report['accuracy'])
    precisions.append(report['1']['precision'])
    recalls.append(report['1']['recall'])
    fscores.append(report['1']['f1-score'])

print(f'Accuracy: {round(np.mean(accuracies), 2)}, precision: {round(np.mean(precisions), 2)}, recall: {round(np.mean(recalls), 2)}, fscore: {round(np.mean(fscores), 2)}')

# %%
