from django.db import models

class DataFile(models.Model):
    file_uri = models.CharField('file URI', max_length=200)
    device_id = models.CharField('device ID', max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return f'{self.device_id} (<{self.start_date.strftime("%Y-%m-%d %H:%M:%S")}> - <{self.end_date.strftime("%Y-%m-%d %H:%M:%S")}>)'

