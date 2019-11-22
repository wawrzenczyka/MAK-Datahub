import logging

class SimpleAuthService:
    logger = logging.getLogger(__name__)
    application_access_token = '944d5555-48bf-48b2-b690-0065b9ba0bdd'

    @classmethod
    def verify_app_token(cls, app_token):
        if app_token != cls.application_access_token:
            cls.logger.error(f'Invalid application token ${app_token}')
            return False
        return True

    @classmethod
    def verify_device_token(cls, device, device_token):
        if device_token != device.token:
            cls.logger.error(f'Invalid device token ${device_token} for device ${device.id}')
            return False
        return True