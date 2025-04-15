from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from myapp.models import Device
from myapp.serializers import SuccessJsonResponse
from myapp.utils import send_fcm_notification


class UserInfo(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        extra = {}
        if user.guard_profile.exists():
            extra['guard_id'] = user.guard_profile.first().code
        content = {
            'id': user.id,
            'username': user.username,
            'groups': [group.name for group in user.groups.all()],
            'extra': extra,
            'must_change_password': user.must_change_password,
        }

        return SuccessJsonResponse(data=content)


class RegisterNotificationToken(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        notification_token = request.data.get('notification_token')

        if not notification_token:
            return Response({'error': 'Notification token is required'}, status=400)

        device, created = Device.objects.update_or_create(user=user, defaults={'notification_token': notification_token})

        return Response({'message': 'Notification token registered successfully'}, status=201)
