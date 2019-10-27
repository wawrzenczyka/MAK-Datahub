from django.contrib import admin

from .models import DataFile, Device

admin.site.register(DataFile)
admin.site.register(Device)