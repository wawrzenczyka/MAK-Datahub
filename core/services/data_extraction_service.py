import logging, os, math
import numpy as np
import pandas as pd

from ProfileCreator.parsers.sensors_parser import SensorParser
from ProfileCreator.parsers.event_parser import EventParser, EventType

class DataExtractionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensor_parser = SensorParser(open('ProfileCreator/parsers/sensor_config.json'))
        self.event_parser = EventParser()
        self.PREUNLOCK_TIME = 3000
        self.POSTUNLOCK_TIME = 1000

    def extract_events(self, event_file_path):
        unlocks = []
        try:
            event_list = self.event_parser.parseFile(open(event_file_path, 'rb'))
            for event in event_list:
                if (event.EventType == EventType.UNLOCKED):
                    unlocks.append(event.Timestamp)
        except ValueError:
            self.logger.error(f'Parsing error in file {event_file_path}')

        return unlocks

    def get_readings_from_sensor_files(self, sensor_file_path):
        try:
            return self.sensor_parser.parseFile(open(sensor_file_path, 'rb'))
        except ValueError:
            return []

    def create_unlock_df_from_readings(self, unlock_timestamp, reading_list):
        time = []

        acc_x = []
        acc_y = []
        acc_z = []
        acc_mgn = []

        mgf_x = []
        mgf_y = []
        mgf_z = []
        mgf_mgn = []

        gyr_x = []
        gyr_y = []
        gyr_z = []
        gyr_mgn = []

        grv_x = []
        grv_y = []
        grv_z = []
        grv_mgn = []

        lin_x = []
        lin_y = []
        lin_z = []
        lin_mgn = []

        rot_x = []
        rot_y = []
        rot_z = []
        rot_mgn = []

        for reading in reading_list:
            if unlock_timestamp - 10000 <= reading.Timestamp <= unlock_timestamp + 5000:
                def mgn(vector):
                    return math.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
                time.append(reading.Timestamp)
                acc_x.append(reading.Acceleration[0])
                acc_y.append(reading.Acceleration[1])
                acc_z.append(reading.Acceleration[2])
                acc_mgn.append(mgn(reading.Acceleration))

                mgf_x.append(reading.MagneticField[0])
                mgf_y.append(reading.MagneticField[1])
                mgf_z.append(reading.MagneticField[2])
                mgf_mgn.append(mgn(reading.MagneticField))

                gyr_x.append(reading.Gyroscope[0])
                gyr_y.append(reading.Gyroscope[1])
                gyr_z.append(reading.Gyroscope[2])
                gyr_mgn.append(mgn(reading.Gyroscope))

                grv_x.append(reading.Gravity[0])
                grv_y.append(reading.Gravity[1])
                grv_z.append(reading.Gravity[2])
                grv_mgn.append(mgn(reading.Gravity))

                lin_x.append(reading.LinearAcceleration[0])
                lin_y.append(reading.LinearAcceleration[1])
                lin_z.append(reading.LinearAcceleration[2])
                lin_mgn.append(mgn(reading.LinearAcceleration))

                rot_x.append(reading.Rotation[0])
                rot_y.append(reading.Rotation[1])
                rot_z.append(reading.Rotation[2])
                rot_mgn.append(mgn(reading.Rotation))

        time = np.array(time)
        
        acc_x = np.array(acc_x)
        acc_y = np.array(acc_y)
        acc_z = np.array(acc_z)
        acc_mgn = np.array(acc_mgn)

        mgf_x = np.array(mgf_x)
        mgf_y = np.array(mgf_y)
        mgf_z = np.array(mgf_z)
        mgf_mgn = np.array(mgf_mgn)

        gyr_x = np.array(gyr_x)
        gyr_y = np.array(gyr_y)
        gyr_z = np.array(gyr_z)
        gyr_mgn = np.array(gyr_mgn)

        grv_x = np.array(grv_x)
        grv_y = np.array(grv_y)
        grv_z = np.array(grv_z)
        grv_mgn = np.array(grv_mgn)

        lin_x = np.array(lin_x)
        lin_y = np.array(lin_y)
        lin_z = np.array(lin_z)
        lin_mgn = np.array(lin_mgn)

        rot_x = np.array(rot_x)
        rot_y = np.array(rot_y)
        rot_z = np.array(rot_z)
        rot_mgn = np.array(rot_mgn)

        df = pd.DataFrame({ 'Time': time, \
                'AccX': acc_x, 'AccY': acc_y, 'AccZ': acc_z, 'AccMgn': acc_mgn, \
                'MgfX': mgf_x, 'MgfY': mgf_y, 'MgfZ': mgf_z, 'MgfMgn': mgf_mgn, \
                'GyrX': gyr_x, 'GyrY': gyr_y, 'GyrZ': gyr_z, 'GyrMgn': gyr_mgn, \
                'GrvX': grv_x, 'GrvY': grv_y, 'GrvZ': grv_z, 'GrvMgn': grv_mgn, \
                'LinX': lin_x, 'LinY': lin_y, 'LinZ': lin_z, 'LinMgn': lin_mgn, \
                'RotX': rot_x, 'RotY': rot_y, 'RotZ': rot_z, 'RotMgn': rot_mgn, \
            })\
            .sort_values(by = ['Time'])\
            .reset_index(drop = True)

        return df

    def aggregate_df_with_stats_functions(self, df):
        if len(df.index) == 0:
            return None

        agg_df = df.set_index('Time')\
            .assign(temp=0)\
            .groupby('temp')\
            .agg([np.min, np.max, np.mean, np.median, np.std, pd.Series.kurt, pd.Series.skew, pd.Series.mad, pd.Series.sem])
        agg_df.columns = ['_'.join(col).strip() for col in agg_df.columns.values]
        agg_df = agg_df.reset_index(drop = True)
        return agg_df

    def transform_df_list_to_df(self, df_list):
        if len(df_list) > 0:
            return pd.concat(df_list).reset_index(drop = True)
        return None

    def add_device_id_to_unlock_df(self, unlock_df, device_id):
        return unlock_df.assign(DeviceId = device_id)