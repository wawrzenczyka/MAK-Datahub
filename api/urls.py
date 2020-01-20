from rest_framework import routers

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from .views import DeviceViewSet, DeviceProfileInfos, LatestDeviceProfileInfo, DataFileInfoViewSet, \
    ProfileCreationRunViewSet, ProfileInfoViewSet, RetrieveProfileData, AuthorizeEndpoint, UserDevices, RetrieveProfileFile

router = routers.DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'my-devices', UserDevices, basename='My devices')
router.register(r'devices/(?P<id>\w+)/profiles', DeviceProfileInfos, basename='Device profiles')
router.register(r'datafiles', DataFileInfoViewSet)
router.register(r'runs', ProfileCreationRunViewSet)
router.register(r'profiles', ProfileInfoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^rest-auth/register/', include('rest_auth.registration.urls')),
    url(r'devices/(?P<id>\w+)/profiles/latest', LatestDeviceProfileInfo.as_view()),
    url(r'profiles/(?P<id>\d+)/data', RetrieveProfileData.as_view()),
    url(r'profiles/(?P<id>\d+)/file', RetrieveProfileFile.as_view()),
    url(r'biometric-auth/', AuthorizeEndpoint.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)