from django.http import JsonResponse
from rest_framework import serializers
from .models import Round, Point, Visit, Guard

import time


class SuccessJsonResponse(JsonResponse):
    def __init__(self, data=None, success=True, *args, **kwargs):
        if data is None:
            data = {}
        data.setdefault('success', success)
        super().__init__(data, *args, **kwargs)


class GuardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guard
        fields = ['name', 'code']


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['name', 'point_type', 'expiration_date']


class VisitSerializer(serializers.ModelSerializer):
    point = PointSerializer()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Visit
        fields = ['point', 'created_at']

    def get_created_at(self, obj):
        return int(obj.created_at.timestamp())


class RoundSerializer(serializers.ModelSerializer):
    visits = VisitSerializer(many=True)

    class Meta:
        model = Round
        fields = ['is_active', 'visits']
