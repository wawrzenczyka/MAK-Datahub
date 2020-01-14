from django.contrib import admin

from .models import DataFileInfo, Device, ProfileInfo, ProfileCreationRun

admin.site.register(DataFileInfo)
admin.site.register(Device)
admin.site.register(ProfileInfo)
admin.site.register(ProfileCreationRun)