from tzlocal import get_localzone
from pytz import timezone
from enum import Enum

from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    android_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'Device {self.android_id} (ID: {self.id})'

class DataFileInfo(models.Model):
    class DataFileType(Enum):
        Event = 'Event'
        Sensor = 'Sensor'
    
    def generate_data_path(self, filename):
        return f'data/{self.device.id}/{filename}'
    
    data = models.FileField(upload_to=generate_data_path)
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    file_type = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in DataFileType])

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'{self.file_type}_{self.device.id}_{self.start_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'

class ProfileCreationRun(models.Model):
    def generate_file_path(self, filename):
        return f'event_info/{self.run_date.strftime("%Y%m%d_%H%M%S")}/{filename}'
    
    run_date = models.DateTimeField()
    parsed_event_files = models.FileField(upload_to=generate_file_path)
    unlock_data = models.FileField(upload_to=generate_file_path)
    checkpoint_data = models.FileField(upload_to=generate_file_path)
    is_64bit = models.BooleanField()

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'Run_{self.run_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'

class ProfileInfo(models.Model):
    class ProfileType(Enum):
        Unlock = 'Unlock'
        Continuous = 'Continuous'
    
    def generate_profile_path(self, filename):
        return f'profiles/{self.run.run_date.strftime("%Y%m%d_%H%M%S")}/{filename}'
    
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    run = models.ForeignKey(ProfileCreationRun, on_delete=models.CASCADE)
    profile_file = models.FileField(upload_to=generate_profile_path)
    profile_type = models.CharField(max_length=20, choices=[(tag, tag.value) for tag in ProfileType])
    used_class_samples = models.IntegerField()
    score = models.FloatField()
    precision = models.FloatField()
    recall = models.FloatField()
    fscore = models.FloatField()
    description = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        tz = timezone('Europe/Warsaw')
        return f'PROFILE_{self.device.id}_{self.run.run_date.astimezone(tz).strftime("%Y%m%d_%H%M%S")}'
