from django.db import models

from uploader.models import Device

class ProfileFile(models.Model):
    device = models.OneToOneField(
        Device,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    file_uri = models.CharField(max_length=200)
    creation_date = models.DateTimeField()

    def __str__(self):
        return f'PROFILE_{self.device.id}_{self.creation_date.strftime("%Y%m%d_%H%M%S")}'
