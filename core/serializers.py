from rest_framework import serializers
from .models import Device, DataFileInfo, ProfileCreationRun, ProfileInfo
from MAKDataHub.services import Services

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'token', 'datafileinfo_set', 'profileinfo_set']

class DataFileInfoSerializer(serializers.HyperlinkedModelSerializer):
    file_type = serializers.ChoiceField(choices = [tag.value for tag in DataFileInfo.DataFileType])
    class Meta:
        model = DataFileInfo
        fields = ['device', 'file_type', 'start_date', 'data']

class ProfileCreationRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProfileCreationRun
        fields = ['run_date', 'parsed_event_files', 'unlock_data', 'checkpoint_data', 'profileinfo_set']

class ProfileInfoSerializer(serializers.HyperlinkedModelSerializer):
    profile_type = serializers.ChoiceField(choices = [tag.value for tag in ProfileInfo.ProfileType])
    profile_serialized = serializers.SerializerMethodField()
    support_serialized = serializers.SerializerMethodField()
    class Meta:
        model = ProfileInfo
        fields = ['device', 'run', 'profile_file', 'profile_serialized', 'support_serialized', 'profile_type', 'used_class_samples', 'score', 'precision', 'recall', 'fscore']

    def get_profile_serialized(self, obj):
        profile, _ = Services.ml_service().serialize_joblib(obj.profile_file)
        return profile

    def get_support_serialized(self, obj):
        _, support = Services.ml_service().serialize_joblib(obj.profile_file)
        return support