from rest_framework import status
from rest_framework.views import APIView

from myapp.serializers import SuccessJsonResponse
from myapp.services.guards import get_guard
from myapp.services.messages import create_message
from myapp.services.points import get_point
from myapp.services.rounds import get_latest_round
from myapp.services.visits import get_visit


class PointMessageView(APIView):
    def post(self, request, guard_id, point_id):
        try:
            guard = get_guard(guard_id)
            round = get_latest_round(guard)
            point = get_point(point_id)
            visit = get_visit(round, point)
            text = request.data.get('text')
            create_message(guard, visit, text)
            return SuccessJsonResponse(status=status.HTTP_200_OK)
        except (Exception,) as e:
            return SuccessJsonResponse(success=False, status=status.HTTP_400_BAD_REQUEST)
