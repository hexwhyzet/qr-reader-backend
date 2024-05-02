from rest_framework import status
from rest_framework.views import APIView

from myapp.serializers import GuardSerializer, SuccessJsonResponse
from myapp.services.guards import get_guard


class GuardView(APIView):
    def get(self, request, guard_id):
        guard = get_guard(guard_id)
        serializer = GuardSerializer(guard)
        return SuccessJsonResponse(data=serializer.data, status=status.HTTP_200_OK)
