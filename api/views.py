from django.http.response import Http404
from rest_framework.response import Response
from rest_framework import viewsets, mixins, permissions, generics, views, authentication, status

from MAKDataHub.services import Services

from core.models import Device, DataFileInfo, ProfileCreationRun, ProfileInfo
from .serializers import DeviceSerializer, DataFileInfoSerializer, ProfileCreationRunSerializer, \
    ProfileInfoSerializer, ProfileDataSerializer, AuthorizeDataSerializer, DeviceSimpleSerializer, \
    ProfileInfoSimpleSerializer

class AnonCreateAndUpdateOwnerOnly(permissions.BasePermission):
    """
    Custom permission:
        - allow anonymous POST
        - allow authenticated GET and PUT on *own* record
        - allow all actions for staff
    """
    def has_permission(self, request, view):
        return (view.action == 'list' and request.user.is_staff) or \
            (view.action != 'list' and (view.action == 'create' or (request.user and request.user.is_authenticated)))

    def has_object_permission(self, request, view, obj):
        return view.action in ['retrieve', 'update', 'partial_update'] and obj.user.id == request.user.id or request.user.is_staff

class DeviceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, AnonCreateAndUpdateOwnerOnly,)
    serializer_class = DeviceSerializer
    queryset = Device.objects.all()

    def __init__(self, *args, **kwargs):
        super(DeviceViewSet, self).__init__(*args, **kwargs)
        self.serializer_action_classes = {
            'list': DeviceSerializer,
            'create': DeviceSimpleSerializer,
            'retrieve': DeviceSerializer,
            'update': DeviceSimpleSerializer,
            'partial_update': DeviceSimpleSerializer,
            'destroy': DeviceSimpleSerializer,
        }

    def get_serializer_class(self, *args, **kwargs):
        """Instantiate the list of serializers per action from class attribute (must be defined)."""
        kwargs['partial'] = True
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(DeviceViewSet, self).get_serializer_class()

class UserDevices(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DeviceSimpleSerializer
    def get_queryset(self):
        user = self.request.user
        qs = Device.objects.filter(user = user)
        return qs

class DataFileInfoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = DataFileInfoSerializer
    queryset = DataFileInfo.objects.all()

class ProfileCreationRunViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = ProfileCreationRunSerializer
    queryset = ProfileCreationRun.objects.all()

class ProfileInfoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = ProfileInfoSerializer
    queryset = ProfileInfo.objects.all()

class DeviceProfileInfos(viewsets.GenericViewSet, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated, permissions.IsAdminUser)
    serializer_class = ProfileInfoSerializer

    def get_queryset(self):
        id = self.kwargs['id']
        try:
            qs = ProfileInfo.objects.filter(device = Device.objects.get(id = id))
            return qs
        except Device.DoesNotExist:
            raise Http404

class LatestDeviceProfileInfo(generics.RetrieveAPIView):
    class IsOwnerOrStaff(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.device.user.id == request.user.id or request.user.is_staff
    
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrStaff)
    serializer_class = ProfileInfoSimpleSerializer
    queryset = ProfileInfo.objects.all()
    
    def get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        try:
            obj = self.queryset.filter(device = Device.objects.get(id = id)).latest('-run__run_date')
            self.check_object_permissions(self.request, obj)
            return obj
        except ProfileInfo.DoesNotExist:
            raise Http404
        except Device.DoesNotExist:
            raise Http404

class RetrieveProfileData(generics.RetrieveAPIView):
    class IsOwnerOrStaff(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.device.user.id == request.user.id or request.user.is_staff

    permission_classes = (permissions.IsAuthenticated, IsOwnerOrStaff)
    serializer_class = ProfileDataSerializer
    queryset = ProfileInfo.objects.all()

    def get_object(self, *args, **kwargs):
        id = self.kwargs['id']
        try:
            obj = self.queryset.get(id = id)
            self.check_object_permissions(self.request, obj)
            return obj
        except ProfileInfo.DoesNotExist:
            raise Http404

class AuthorizeEndpoint(views.APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def __init__(self, *args, **kwargs):
        self.profile_service = Services.profile_service()
        super().__init__(*args, **kwargs)

    class IsOwnerOrStaff(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            return obj.device.user.id == request.user.id or request.user.is_staff

    def post(self, request, format=None):
        serializer = AuthorizeDataSerializer(data=request.data)
        if serializer.is_valid():
            device_id = serializer.data['device']
            sensor_data = serializer.data['sensor_data']
            profile_type = serializer.data['profile_type']

            try:
                device = Device.objects.get(id = device_id)

                yes_proba = self.profile_service.authorize(device, profile_type, sensor_data)
                if (yes_proba != None):
                    response = { 'matching_user_probability': yes_proba }
                else:
                    raise Http404
                return Response(response, status=status.HTTP_200_OK)
            except Device.DoesNotExist:
                return Response({'device': 'Device doesn\'t exist'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)