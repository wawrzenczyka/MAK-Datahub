import json

from rest_framework import serializers
from core.models import Device, DataFileInfo, ProfileCreationRun, ProfileInfo
from MAKDataHub.services import Services

class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Device
        fields = ['id', 'android_id', 'user', 'datafileinfo_set', 'profileinfo_set']
        read_only_fields = ['id', 'user', 'datafileinfo_set', 'profileinfo_set']

class DeviceSimpleSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    class Meta:
        model = Device
        fields = ['user', 'id', 'android_id']

class DataFileInfoSerializer(serializers.ModelSerializer):
    file_type = serializers.ChoiceField(choices = [tag.value for tag in DataFileInfo.DataFileType])
    class Meta:
        model = DataFileInfo
        fields = ['id', 'device', 'file_type', 'start_date', 'data']

class ProfileCreationRunSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ProfileCreationRun
        fields = ['id', 'run_date', 'parsed_event_files', 'unlock_data', 'checkpoint_data', 'profileinfo_set']

class ProfileInfoSerializer(serializers.HyperlinkedModelSerializer):
    profile_type = serializers.ChoiceField(choices = [tag.value for tag in ProfileInfo.ProfileType])
    creation_date = serializers.DateTimeField(source='run.run_date', read_only=True)
    class Meta:
        model = ProfileInfo
        fields = ['id', 'device', 'run', 'profile_file', 'profile_type', 'creation_date', 'used_class_samples', 'score', 'precision', 'recall', 'fscore']

class ProfileInfoSimpleSerializer(serializers.HyperlinkedModelSerializer):
    creation_date = serializers.DateTimeField(source='run.run_date', read_only=True)
    class Meta:
        model = ProfileInfo
        fields = ['id', 'creation_date']

class ProfileDataSerializer(serializers.ModelSerializer):
    profile_serialized = serializers.SerializerMethodField()
    support_serialized = serializers.SerializerMethodField()
    class Meta:
        model = ProfileInfo
        fields = ['profile_serialized', 'support_serialized', 'used_class_samples', 'score', 'precision', 'recall', 'fscore']

    def get_profile_serialized(self, obj):
        profile, _ = Services.ml_service().serialize_joblib(obj.profile_file)
        return profile

    def get_support_serialized(self, obj):
        _, support = Services.ml_service().serialize_joblib(obj.profile_file)
        return support

class AuthorizeDataSerializer(serializers.Serializer):
    device = serializers.PrimaryKeyRelatedField(queryset = Device.objects.all())
    profile_type = serializers.ChoiceField(choices = [tag.value for tag in ProfileInfo.ProfileType])
    sensor_data = serializers.CharField()
    
    def validate_sensor_data(self, obj):
        json_string = obj
        try:
            json_data = json.loads(json_string)
            if type(json_data) is not list:
                raise serializers.ValidationError("Invalid json structure")
            for json_row in json_data:
                if len(json_row) != 6*3 + 1:
                    raise serializers.ValidationError("Json should have 19 columns")
                if type(json_row) is not list:
                    raise serializers.ValidationError("Invalid json structure")
                for value in json_row:
                    if type(value) is not float and type(value) is not int:
                        raise serializers.ValidationError("Invalid json structure")
        except:
            raise serializers.ValidationError("Invalid data in sensor_data")
        return json_string
