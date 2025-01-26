from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from myapp.serializers import SuccessJsonResponse


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
        }
        return SuccessJsonResponse(data=content)
