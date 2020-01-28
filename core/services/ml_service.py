import logging, os, json, joblib
import pandas as pd
import numpy as np

from django.core.files.storage import default_storage

from abc import ABC, abstractmethod

from sklearn.neighbors import LocalOutlierFactor
from sklearn.feature_selection import RFECV, RFE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from sklearn_porter import Porter

from imblearn.combine import SMOTETomek

class AbstractMLService(ABC):
    @abstractmethod
    def train(self, X, y, device_id):
        pass

    @abstractmethod
    def predict(self, estimator, x, expected_y):
        pass

    @abstractmethod
    def serialize(self, profile):
        pass

class RFE20step005_RF100_SMOTETomek_MLService(AbstractMLService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def train(self, X, y, device, user_device_ids):
        X = self.__filter_features(X)

        y_device = np.where(np.isin(y, user_device_ids), 1, 0)
        self.logger.info(f'Profile creation: device {device.id} ({device.user.username}@{device.android_id}), {np.sum(y_device)} class / {len(y_device)} total samples')

        X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2)
        X_oversampled, y_oversampled = SMOTETomek().fit_resample(X_train, y_train)

        classifier = RandomForestClassifier(n_estimators = 50, min_samples_leaf = 1, min_samples_split = 2, \
            bootstrap = False, max_features = 'sqrt', max_depth = 20)
        selector = RFE(classifier, n_features_to_select = 20, step = 0.05)
        selector = selector.fit(X_oversampled, y_oversampled)

        score = selector.score(X_test, y_test)
        self.logger.info(f'Profile creation: device {device.id} ({device.user.username}@{device.android_id})' \
            + f'\n\tSelector score: {round(score * 100, 2)}%' 
            + f'\n\tSelected features: {X.columns[selector.support_]}' 
            + f'\n\tClassification report:\n{classification_report(y_test, selector.predict(X_test))}')

        report = classification_report(y_test, selector.predict(X_test), output_dict=True)
        precision = report['1']['precision']
        recall = report['1']['recall']
        fscore = report['1']['f1-score']

        return selector, score, precision, recall, fscore, 'RandomForestClassifier(n_estimators = 50), RFE(n_features_to_select = 20, step = 0.05), SMOTETomek()'

    def predict(self, estimator, x, expected_y):
        predicted_y = estimator.predict(x)
        probabilities = estimator.predict_proba(x)

        class_index = np.where(estimator.classes_ == 1)[0]
        yes_probability = probabilities[0][class_index][0]

        detailed_proba_log = ''
        for i in range(len(probabilities[0])):
            detailed_proba_log += f'\n\tProbability of {bool(estimator.classes_[i])}: {round(probabilities[0][i] * 100, 2)}%'
        self.logger.info(f'Prediction for data from class ${expected_y} - predicted class ${bool(predicted_y)}' + detailed_proba_log)
        return yes_probability

    def serialize(self, profile_info):
        profile = joblib.load(profile_info)
        estimator = profile.estimator_
        support = profile.support_

        porter = Porter(estimator, language='js')
        serialized_profile = porter.export(embed_data=True)
        serialized_support = json.dumps(support.tolist())

        return serialized_profile, serialized_support

    def __filter_features(self, X):
        return X.loc[:, \
            ['AccMgn_amin', 'AccMgn_amax', 'AccMgn_mean', 'AccMgn_median', 'AccMgn_std', 'AccMgn_kurt', 'AccMgn_skew', 'AccMgn_mad', 'AccMgn_sem', \
            'AccX_amin', 'AccX_amax', 'AccX_mean', 'AccX_median', 'AccX_std', 'AccX_kurt', 'AccX_skew', 'AccX_mad', 'AccX_sem', \
            'AccY_amin', 'AccY_amax', 'AccY_mean', 'AccY_median', 'AccY_std', 'AccY_kurt', 'AccY_skew', 'AccY_mad', 'AccY_sem', \
            'AccZ_amin', 'AccZ_amax', 'AccZ_mean', 'AccZ_median', 'AccZ_std', 'AccZ_kurt', 'AccZ_skew', 'AccZ_mad', 'AccZ_sem', \
            'GyrMgn_amin', 'GyrMgn_amax', 'GyrMgn_mean', 'GyrMgn_median', 'GyrMgn_std', 'GyrMgn_kurt', 'GyrMgn_skew', 'GyrMgn_mad', 'GyrMgn_sem', \
            'GyrX_amin', 'GyrX_amax', 'GyrX_mean', 'GyrX_median', 'GyrX_std', 'GyrX_kurt', 'GyrX_skew', 'GyrX_mad', 'GyrX_sem', \
            'GyrY_amin', 'GyrY_amax', 'GyrY_mean', 'GyrY_median', 'GyrY_std', 'GyrY_kurt', 'GyrY_skew', 'GyrY_mad', 'GyrY_sem', \
            'GyrZ_amin', 'GyrZ_amax', 'GyrZ_mean', 'GyrZ_median', 'GyrZ_std', 'GyrZ_kurt', 'GyrZ_skew', 'GyrZ_mad', 'GyrZ_sem', \
            'LinMgn_amin', 'LinMgn_amax', 'LinMgn_mean', 'LinMgn_median', 'LinMgn_std', 'LinMgn_kurt', 'LinMgn_skew', 'LinMgn_mad', 'LinMgn_sem', \
            'LinX_amin', 'LinX_amax', 'LinX_mean', 'LinX_median', 'LinX_std', 'LinX_kurt', 'LinX_skew', 'LinX_mad', 'LinX_sem', \
            'LinY_amin', 'LinY_amax', 'LinY_mean', 'LinY_median', 'LinY_std', 'LinY_kurt', 'LinY_skew', 'LinY_mad', 'LinY_sem', \
            'LinZ_amin', 'LinZ_amax', 'LinZ_mean', 'LinZ_median', 'LinZ_std', 'LinZ_kurt', 'LinZ_skew', 'LinZ_mad', 'LinZ_sem', \
            'RotMgn_amin', 'RotMgn_amax', 'RotMgn_mean', 'RotMgn_median', 'RotMgn_std', 'RotMgn_kurt', 'RotMgn_skew', 'RotMgn_mad', 'RotMgn_sem', \
            'RotX_amin', 'RotX_amax', 'RotX_mean', 'RotX_median', 'RotX_std', 'RotX_kurt', 'RotX_skew', 'RotX_mad', 'RotX_sem', \
            'RotY_amin', 'RotY_amax', 'RotY_mean', 'RotY_median', 'RotY_std', 'RotY_kurt', 'RotY_skew', 'RotY_mad', 'RotY_sem', \
            'RotZ_amin', 'RotZ_amax', 'RotZ_mean', 'RotZ_median', 'RotZ_std', 'RotZ_kurt', 'RotZ_skew', 'RotZ_mad', 'RotZ_sem']]