from django.contrib.auth.models import User
from rest_framework import serializers

from .models import IncidentMessage, TextMessage, PhotoMessage, VideoMessage, AudioMessage, Incident, Duty, DutyRole


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'
        read_only_fields = ['id', 'status', 'is_critical', 'responsible_user']

    def create(self, validated_data):
        # user = self.context['request'].user
        # if user.is_authenticated:
        #     validated_data['author'] = user
        validated_data['author'] = User.objects.get(pk=7)
        return super().create(validated_data)



class DutyRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DutyRole
        fields = '__all__'


class DutySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = DutyRoleSerializer(read_only=True)

    class Meta:
        model = Duty
        fields = '__all__'


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


class MessageSerializer(serializers.ModelSerializer):
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
