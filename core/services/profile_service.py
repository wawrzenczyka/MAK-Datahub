import logging, json, joblib, os

from django.utils import timezone # remove later after deleting the stub
from django.db import connection

from sklearn_porter import Porter

from ..models import ProfileFile, Device, ProfileCreationRun

class ProfileService:
    def __init__(self, ml_service, storage_service, data_extraction_service):
        self.logger = logging.getLogger(__name__)
        self.ml_service = ml_service
        self.storage_service = storage_service
        self.data_extraction_service = data_extraction_service
    
    def authorize(self, device, profile_type, sensor_data_string):
        assert type(device) is Device
        assert type(sensor_data_string) is str

        sensor_data = json.loads(sensor_data_string)

        df = self.data_extraction_service.create_df_from_json_data(sensor_data)        
        aggregated_df = self.data_extraction_service.aggregate_df_with_stats_functions(df)
        profile_info, profile = self.get_latest_profile_for_device(device, profile_type)

        if profile_info is None or profile is None:
            return None
        
        return self.ml_service.predict(profile, aggregated_df, device.id)

    def get_latest_profile_for_device(self, device, profile_type):
        latest_profile = device.profilefile_set.filter(profile_type = profile_type).order_by('-run__run_date').first()

        if latest_profile is None:
            return None, None
        
        profile_filename = self.storage_service.download_file(latest_profile.profile_file_uri)
        profile = joblib.load(profile_filename)
        os.remove(profile_filename)

        return latest_profile, profile

    def serialize_profile(self, profile):
        estimator = profile.estimator_
        support = profile.support_

        porter = Porter(estimator, language='js')
        serialized_profile = porter.export(embed_data=True)
        serialized_support = json.dumps(support.tolist())

        return serialized_profile, serialized_support

    def create_profile_creation_run(self, run_date, parsed_event_files_uri, unlock_data_uri, checkpoint_data_uri):
        run = ProfileCreationRun(run_date = run_date, unlock_data_uri = unlock_data_uri, parsed_event_files_uri = parsed_event_files_uri, checkpoint_data_uri = checkpoint_data_uri)
        connection.close()
        run.save()
        return run

    def get_last_profile_creation_run(self):
        return ProfileCreationRun.objects.order_by('-run_date').first()

    def create_profiles(self, run, profile_data, profile_type):
        X, y = profile_data.iloc[:, 0:-1], profile_data.iloc[:, -1]
        
        min_samples = 10

        for device_id in y.unique():
            sample_count = self.ml_service.get_class_sample_count(y, device_id)
            if sample_count < min_samples:
                self.logger.info(f'Profile creation: device {device_id}, not enough data ({sample_count} samples) to create profile')
                continue
            
            selector = self.ml_service.rfe_rf_oversampled_10_features(X, y, device_id)
            profile_file_uri = self.storage_service.save_profile(selector, run.run_date, device_id, profile_type)
            connection.close()
            profile_file = ProfileFile(device = Device.objects.get(id = device_id), profile_file_uri = profile_file_uri, run = run, profile_type = profile_type)
            profile_file.save()