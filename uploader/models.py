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
        return f'{self.device.id}_{self.start_date.strftime("%Y%m%d_%H%M%S")}'