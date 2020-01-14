from rest_framework import viewsets, mixins

from .models import Device, DataFileInfo, ProfileCreationRun, ProfileInfo
from .serializers import DeviceSerializer, DataFileInfoSerializer, ProfileCreationRunSerializer, ProfileInfoSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

class DataFileInfoViewSet(viewsets.ModelViewSet):
    queryset = DataFileInfo.objects.all()
    serializer_class = DataFileInfoSerializer

class ProfileCreationRunViewSet(viewsets.ModelViewSet):
    queryset = ProfileCreationRun.objects.all()
    serializer_class = ProfileCreationRunSerializer

class ProfileInfoViewSet(viewsets.ModelViewSet):
    queryset = ProfileInfo.objects.all()
    serializer_class = ProfileInfoSerializer