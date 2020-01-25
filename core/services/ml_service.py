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

from imblearn.over_sampling import SMOTE

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

class RFE10_RF10_SMOTE_MLService(AbstractMLService):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def train(self, X, y, device, user_device_ids):
        y_device = np.where(np.isin(y, user_device_ids), 1, 0)
        self.logger.info(f'Profile creation: device {device.id} ({device.user.username}@{device.android_id}), {np.sum(y_device)} class / {len(y_device)} total samples')

        X_train, X_test, y_train, y_test = train_test_split(X, y_device, test_size=0.2)
        X_oversampled, y_oversampled = SMOTE().fit_resample(X_train, y_train)

        classifier = RandomForestClassifier(n_estimators = 100)
        selector = RFE(classifier, n_features_to_select=10, step=1)
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

        return selector, score, precision, recall, fscore, 'RandomForestClassifier(n_estimators = 100), RFE(n_features_to_select=10, step=1), SMOTE()'

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