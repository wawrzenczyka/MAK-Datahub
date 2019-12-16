import logging, os
import joblib

import pandas as pd
import numpy as np

# from sklearn.feature_selection import RFECV
# from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import LocalOutlierFactor

class MLService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        ### Global model
        # if os.path.exists('model.joblib'):
        #     model = joblib.load('model.joblib')
        #     if type(model) is RFECV:
        #         self.has_model = True
        #         self.model = model
        ###
        ### Local models
        if os.path.exists('device_models'):
            self.models = {}
            subfolders = [(f.name, f.path) for f in os.scandir('device_models') if f.is_dir()]
            for device_id, device_path in subfolders:
                model = joblib.load(os.path.join(device_path, 'model.joblib'))
                # if type(model) is RFECV:
                if type(model) is LocalOutlierFactor:
                    self.models[device_id] = model
        ###
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

        def magnitude(x, y, z):
            return np.sqrt(x**2 + y**2 + z**2)
        
        df = pd.DataFrame(sensor_data, columns = columns)
        df = df\
            .assign(AccMgn = magnitude(df.AccX, df.AccY, df.AccZ))\
            .assign(MgfMgn = magnitude(df.MgfX, df.MgfY, df.MgfZ))\
            .assign(GyrMgn = magnitude(df.GyrX, df.GyrY, df.GyrZ))\
            .assign(GrvMgn = magnitude(df.GrvX, df.GrvY, df.GrvZ))\
            .assign(LinMgn = magnitude(df.LinX, df.LinY, df.LinZ))\
            .assign(RotMgn = magnitude(df.RotX, df.RotY, df.RotZ))\
            .loc[:, ['Time', \
                'AccX', 'AccY', 'AccZ', 'AccMgn', \
                'MgfX', 'MgfY', 'MgfZ', 'MgfMgn', \
                'GyrX', 'GyrY', 'GyrZ', 'GyrMgn', \
                'GrvX', 'GrvY', 'GrvZ', 'GrvMgn', \
                'LinX', 'LinY', 'LinZ', 'LinMgn', \
                'RotX', 'RotY', 'RotZ', 'RotMgn', \
        ]]

        self.logger.info(f'Prediction input data:\n\t${df.values.tolist()}')

        return df

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
        if expected_y not in self.models:
            return None

        self.logger.info(f'Prediction for data from class ${expected_y} - input vector:\n\t${x.iloc[0, :].values.tolist()}')

        model = self.models[expected_y]

        predicted_y = model.predict(x)[0]
        self.logger.info(f'Prediction for data from class ${expected_y} - predicted class ${bool(predicted_y == 1)}\n\tSample score: ${model.score_samples(x)[0]}')

        # if predicted_y == 1:
        #     return 1.0
        # else:
        #     return 0.0
        return model.score_samples(x)[0]

    # def predict(self, x, expected_y):

    #     ### Global model
    #     # if not self.has_model:
    #     #     return None
    #     # model = self.model
    #     ###

    #     ### Device models
    #     if expected_y not in self.models:
    #         return None
    #     model = self.models[expected_y]
    #     ###

    #     predicted_y = model.predict(x)
    #     probabilities = model.predict_proba(x)

    #     ### Global model
    #     # if expected_y not in model.classes_:
    #     #     return None
    #     ###
    #     class_index = np.where(model.classes_ == 1)[0]
    #     yes_probability = probabilities[0][class_index][0]

    #     detailed_proba_log = ''
    #     for i in range(len(probabilities[0])):
    #         detailed_proba_log += f'\n\tProbability of {bool(model.classes_[i])}: {probabilities[0][i] * 100}%'
    #     self.logger.info(f'Prediction for data from class ${expected_y} - predicted class ${bool(predicted_y)}' + detailed_proba_log)
    #     return yes_probability

    def recalculate_model(self):
        pass