import logging
import uuid

from ..models import Device

class DeviceService:
    logger = logging.getLogger(__name__)

    @classmethod
    def get_device(cls, device_id):
        try:
            dev = Device.objects.get(id = device_id)
            return dev
        except Device.DoesNotExist:
            return None

    @classmethod
    def create_device(cls, device_id):
        device_token = uuid.uuid4()
        dev = Device(id = device_id, token = device_token)
        dev.save()
        cls.logger.info(f'Device ${device_id} created')
        return dev