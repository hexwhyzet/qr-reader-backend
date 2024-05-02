from rest_framework import status
from rest_framework.views import APIView

from myapp.serializers import RoundSerializer, SuccessJsonResponse
from myapp.services.guards import get_guard
from myapp.services.rounds import deactivate_rounds, create_round, get_latest_round


class StartRoundView(APIView):
    def post(self, request, guard_id):
        guard = get_guard(guard_id)
        deactivate_rounds(guard)
        create_round(guard)
        return SuccessJsonResponse(status=status.HTTP_200_OK)


class EndRoundView(APIView):
    def post(self, request, guard_id):
        guard = get_guard(guard_id)
        deactivate_rounds(guard)
        return SuccessJsonResponse(status=status.HTTP_200_OK)


class RoundStatusView(APIView):
    def get(self, request, guard_id):
        guard = get_guard(guard_id)
        round = get_latest_round(guard)
        serializer = RoundSerializer(round)
        return SuccessJsonResponse(data=serializer.data, status=status.HTTP_200_OK)
