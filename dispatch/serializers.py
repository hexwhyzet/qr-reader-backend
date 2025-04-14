from rest_framework import serializers

from myapp.models import display_name
from myproject.settings import AUTH_USER_MODEL
from .models import IncidentMessage, TextMessage, PhotoMessage, VideoMessage, AudioMessage, Incident, Duty, DutyRole, \
    DutyPoint


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = AUTH_USER_MODEL
        fields = ['id', 'username', 'first_name', 'last_name', 'display_name']

    def get_display_name(self, obj):
        return display_name(obj)


class DutyPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyPoint
        fields = ['id', 'name']


class IncidentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    responsible_user = UserSerializer(read_only=True)
    point = DutyPointSerializer(read_only=True)
    display_status = serializers.SerializerMethodField()

    point_id = serializers.PrimaryKeyRelatedField(
        queryset=DutyPoint.objects.all(), write_only=True, source='point'
    )

    def get_display_status(self, obj):
        for key, value in obj.STATUS_CHOICES:
            if key == obj.status:
                return value
        return "Неизвестен"

    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['id', 'status', 'is_critical', 'responsible_user']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.is_authenticated:
            validated_data['author'] = user
        return super().create(validated_data)


class DutyRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyRole
        fields = '__all__'


class DutySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = DutyRoleSerializer(read_only=True)
    date = serializers.SerializerMethodField()

    class Meta:
        model = Duty
        fields = '__all__'

    def get_date(self, obj):
        return obj.date


class TextMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextMessage
        fields = ["text"]


class PhotoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhotoMessage
        fields = ["photo"]


class VideoMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMessage
        fields = ["video"]


class AudioMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioMessage
        fields = ["audio"]


class IncidentMessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    content = serializers.SerializerMethodField()

    class Meta:
        model = IncidentMessage
        fields = ["id", "user", "message_type", "created_at", "content"]

    def get_content(self, obj):
        """Определяет, какой сериализатор использовать"""
        if obj.message_type == IncidentMessage.TEXT and obj.content_object:
            return TextMessageSerializer(obj.content_object).data
        elif obj.message_type == IncidentMessage.PHOTO and obj.content_object:
            return PhotoMessageSerializer(obj.content_object).data
        elif obj.message_type == IncidentMessage.VIDEO and obj.content_object:
            return VideoMessageSerializer(obj.content_object).data
        elif obj.message_type == IncidentMessage.AUDIO and obj.content_object:
            return AudioMessageSerializer(obj.content_object).data
        return None
