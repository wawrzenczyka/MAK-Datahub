import logging, json

from django.utils import timezone # remove later after deleting the stub
from django.db import connection

from ..models import ProfileFile, Device, ProfileCreationRun

class ProfileService:
    def __init__(self, ml_service, storage_service):
        self.ml_service = ml_service
        self.storage_service = storage_service
        self.logger = logging.getLogger(__name__)

    def authorize(self, device, sensor_data_string):
        assert type(device) is Device
        assert type(sensor_data_string) is str

        sensor_data = json.loads(sensor_data_string)

        df = self.ml_service.create_dataframe_from_jsondata(sensor_data)        
        aggregated_df = self.ml_service.aggregate_data_portion_with_stats_functions(df)

        return self.ml_service.predict(aggregated_df, device.id)
        
    def get_profile_model_and_file(self, device):
        assert type(device) is Device

        # TODO: get real profile
        # profile_file = device.profilefile_set.order_by('-run__run_date').first()
        # if profile_file is None:
        #     return None, None
        # profile = storage_service.get_file(profile_model.file_uri)
        # return profile_file, profile

        try:
            return ProfileFile(device = device, creation_date = timezone.now(), file_uri = '1234'), [[0, 0], [0, 0]]
        except ProfileFile.DoesNotExist:
            return None, None

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
            profile_file_uri = self.storage_service.upload_profile(selector, run.run_date, device_id)
            connection.close()
            profile_file = ProfileFile(device = Device.objects.get(id = device_id), profile_file_uri = profile_file_uri, run = run, profile_type = profile_type)
            profile_file.save()