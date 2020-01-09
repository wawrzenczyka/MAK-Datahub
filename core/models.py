from tzlocal import get_localzone
from pytz import timezone

from django.db import models

class Device(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    token = models.CharField(max_length=36)

    def __str__(self):
        return f'Device {self.id}'

class DataFile(models.Model):
    file_uri = models.CharField(max_length=200)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    file_type = models.CharField(max_length=1)

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'{self.file_type}_{self.device.id}_{self.start_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'

class ProfileCreationRun(models.Model):
    run_date = models.DateTimeField()
    parsed_event_files_uri = models.CharField(max_length=200)
    unlock_data_uri = models.CharField(max_length=200)
    checkpoint_data_uri = models.CharField(max_length=200)

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'RUN_{self.creation_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'

class ProfileFile(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    run = models.ForeignKey(ProfileCreationRun, on_delete=models.CASCADE)
    profile_file_uri = models.CharField(max_length=200)
    profile_type = models.CharField(max_length=20)

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'PROFILE_{self.device.id}_{self.run.creation_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'
