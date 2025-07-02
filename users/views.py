from django.contrib.auth import update_session_auth_hash, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import permissions, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from dispatch.serializers import UserSerializer
from users.serializers import ChangePasswordSerializer


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Старый пароль неправильный."]}, status=status.HTTP_400_BAD_REQUEST)
            new_password = serializer.validated_data['new_password']
            try:
                validate_password(new_password, user=user)
            except ValidationError as e:
                return Response(
                    {"error": e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(new_password)
            user.must_change_password = False
            user.save()
            update_session_auth_hash(request, user)
            return Response({"detail": "Пароль сменен успешно."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListAPIView(ListAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = get_user_model()._meta.ordering
