import logging

from ..models import Device

class SimpleAuthService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.application_access_token = '944d5555-48bf-48b2-b690-0065b9ba0bdd'

    def verify_app_token(self, app_token):
        assert type(app_token) is str

        if app_token != self.application_access_token:
            self.logger.error(f'Invalid application token ${app_token}')
            return False
        return True

    def verify_device_token(self, device, device_token):
        assert type(device) is Device and type(device_token) is str

        if device_token != device.token:
            self.logger.error(f'Invalid device token ${device_token} for device ${device.id}')
            return False
        return True