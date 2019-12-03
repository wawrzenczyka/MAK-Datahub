import logging, json
from django.utils import timezone # remove later after deleting the stub

from ..models import ProfileFile, Device

class ProfileService:
    def __init__(self, ml_service):
        self.ml_service = ml_service
        self.logger = logging.getLogger(__name__)

    def authorize(self, device, sensor_data_string):
        assert type(device) is Device
        assert type(sensor_data_string) is str

        sensor_data = json.loads(sensor_data_string)

        df = self.ml_service.create_dataframe_from_jsondata(sensor_data)        
        aggregated_df = self.ml_service.aggregate_data_portion_with_stats_functions(df)

        return bool(self.ml_service.predict(aggregated_df, device.id)[0])
        
    def get_profile_model_and_file(self, device):
        assert type(device) is Device

        try:
            # TODO: get real profile
            ## profile_model = device.profilefile
            ## profile = GoogleDriveService.get_profile_file(profile_model.file_uri)
            ## return profile_model, profile
            return ProfileFile(device = device, creation_date = timezone.now(), file_uri = '1234'), [[0, 0], [0, 0]]
        except ProfileFile.DoesNotExist:
            return None, None

    def update_profiles(self):
        # TODO: profile creation
        pass
