import logging
import uuid

from ..models import Device

class DeviceService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_device(self, device_id):
        assert type(device_id) is str

        try:
            dev = Device.objects.get(id = device_id)
            return dev
        except Device.DoesNotExist:
            return None

    def create_device(self, device_id):
        assert type(device_id) is str
        
        device_token = uuid.uuid4()
        dev = Device(id = device_id, token = device_token)
        dev.save()
        return dev