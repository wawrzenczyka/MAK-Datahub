import logging
from django.utils import timezone # remove later after deleting the stub

from ..models import ProfileFile, Device

class ProfileService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

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
