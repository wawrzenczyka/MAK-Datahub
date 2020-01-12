from django.contrib import admin

from .models import DataFile, Device, ProfileFile, ProfileCreationRun

admin.site.register(DataFile)
admin.site.register(Device)
admin.site.register(ProfileFile)
admin.site.register(ProfileCreationRun)