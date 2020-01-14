from rest_framework import routers

from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from .views import DeviceViewSet, DataFileInfoViewSet, ProfileCreationRunViewSet, ProfileInfoViewSet

router = routers.DefaultRouter()
router.register(r'devices', DeviceViewSet)
router.register(r'datafiles', DataFileInfoViewSet)
router.register(r'runs', ProfileCreationRunViewSet)
router.register(r'profiles', ProfileInfoViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)