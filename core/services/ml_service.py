import logging, os
import joblib

import pandas as pd
import numpy as np

from sklearn.feature_selection import RFECV
from sklearn.ensemble import RandomForestClassifier

class MLService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        if os.path.exists('model.joblib'):
            model = joblib.load('model.joblib')
            if type(model) is RFECV:
                self.has_model = True
                self.model = model
        else:
            self.has_model = False
    
    def create_dataframe_from_jsondata(self, sensor_data):
        columns = ['Time', \
            'AccX', 'AccY', 'AccZ', \
            'MgfX', 'MgfY', 'MgfZ', \
            'GyrX', 'GyrY', 'GyrZ', \
            'GrvX', 'GrvY', 'GrvZ', \
            'LinX', 'LinY', 'LinZ', \
            'RotX', 'RotY', 'RotZ', \
        ]

        return pd.DataFrame(sensor_data, columns = columns)

    def aggregate_data_portion_with_stats_functions(self, sensor_df):
        if len(sensor_df.index) == 0:
            return None

        agg_df = sensor_df.set_index('Time')\
            .assign(temp=0)\
            .groupby('temp')\
            .agg([np.min, np.max, np.mean, np.median, np.std, pd.Series.kurt, pd.Series.skew, pd.Series.mad, pd.Series.sem])
        agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
        return agg_df.reset_index(drop = True)

    def predict(self, x, expected_y):
        if not self.has_model:
            return None
        
        predicted_y = self.model.predict(x)

        probabilities = self.model.predict_proba(x)
        if len(np.where(self.model.classes_ == expected_y)) == 0:
            return None
        class_index = np.where(self.model.classes_ == expected_y)[0]
        yes_probability = probabilities[0][class_index]

        detailed_proba_log = ''
        for i in range(len(probabilities)):
            detailed_proba_log += f'\n\tprobability of {self.model.classes_[i]}: {probabilities[i] * 100}%'
        self.logger.info(f'Prediction for data from class ${expected_y} - predicted class ${predicted_y}' + detailed_proba_log)
        return yes_probability

    def recalculate_model(self):
        pass