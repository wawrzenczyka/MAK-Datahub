import logging
import uuid

from ..models import Device

class DeviceService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_device(self, device_id):
        try:
            dev = Device.objects.get(id = device_id)
            return dev
        except Device.DoesNotExist:
            return None

    def get_all_devices(self):
        return Device.objects.all()