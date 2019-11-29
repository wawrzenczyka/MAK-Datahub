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

    def get_all_devices(self):
        return Device.objects.all()

    def create_device(self, device_id):
        assert type(device_id) is str
        
        if Device.objects.filter(id = device_id).exists():
            raise ValueError(f'Device of id {device_id} already exists')

        device_token = uuid.uuid4()
        dev = Device(id = device_id, token = device_token)
        dev.save()
        return dev