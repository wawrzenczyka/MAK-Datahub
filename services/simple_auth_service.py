import logging

from application_access_token import app_access_token
from uploader.models import Device

class SimpleAuthService:
    logger = logging.getLogger(__name__)

    @classmethod
    def verify_app_token(cls, app_token):
        if app_token != app_access_token:
            cls.logger.error(f'Invalid application token ${app_token}')
            return False
        return True

    @classmethod
    def verify_device_token(cls, device, device_token):
        if device_token != device.token:
            cls.logger.error(f'Invalid device token ${device_token} for device ${device.id}')
            return False
        return True