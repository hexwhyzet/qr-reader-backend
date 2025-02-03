from django.contrib.contenttypes.models import ContentType
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from myapp.admin import user_has_group
from myapp.custom_groups import DispatchAdminManager
from .models import IncidentMessage, Incident, Duty
from .serializers import MessageSerializer, TextMessageSerializer, PhotoMessageSerializer, VideoMessageSerializer, \
    AudioMessageSerializer, IncidentSerializer, DutySerializer
from .services.duties import get_duties_by_date, get_current_duties
from .services.incidents import escalate_incident
from .utils import now


class IncidentViewSet(viewsets.ViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    def list(self, request):
        incidents = Incident.objects.all()
        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        incident = Incident.objects.get(pk=pk)
        serializer = IncidentSerializer(incident)
        return Response(serializer.data)

    def create(self, request):
        serializer = IncidentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            incident = serializer.save()
            escalate_incident(incident)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        incident = Incident.objects.get(pk=pk)

        if incident.responsible_user != request.user and not user_has_group(request.user, DispatchAdminManager):
            return Response({"error": "Вы не являетесь ответственным за этот инцидент"}, status=403)

        new_status = request.data.get("status")

        if new_status in ["opened", "closed", "force_closed"]:
            return Response({"error": "Некорректный статус"}, status=400)

        if new_status in ["force_closed"] and not user_has_group(request.user, DispatchAdminManager):
            return Response({"error": "Принудительно закрыть может только dispatch_admin_manager"}, status=400)

        incident.status = new_status
        incident.save()

        serializer = IncidentSerializer(incident)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def escalate(self, request, pk=None):
        incident = Incident.objects.get(pk=pk)

        if incident.responsible_user != request.user and not user_has_group(request.user, DispatchAdminManager):
            return Response({"error": "Вы не являетесь ответственным за этот инцидент"}, status=403)

        escalate_incident(incident)

        serializer = IncidentSerializer(incident)
        return Response(serializer.data)


class DutyViewSet(viewsets.ReadOnlyModelViewSet):  # ReadOnly since no update/create
    # permission_classes = [IsAuthenticated]
    serializer_class = DutySerializer
    queryset = Duty.objects.all()
    filterset_fields = ['date', 'role', 'is_opened']

    def get_queryset(self):
        queryset = super().get_queryset()
        date_str = self.request.query_params.get('date')

        if date_str:
            date = parse_date(date_str)
            if date:
                queryset = get_duties_by_date(date)

        return queryset

    @action(detail=False, methods=['get'])
    def my_duties(self, request):
        serializer = DutySerializer(get_current_duties(now(), request.user), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def open(self, request, pk=None):
        duty = Duty.objects.get(pk=pk)

        if duty.user != request.user:
            return Response({"error": "Открыть дежурство может только сам дежурный"}, status=403)

        duty.is_opened = True

        serializer = DutySerializer(duty)
        return Response(serializer.data)


class IncidentMessageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def create(self, request):
        user = request.user if request.user.is_authenticated else None
        message_type = request.data.get("message_type")

        msg = IncidentMessage.objects.create(
            user=user,
            message_type=message_type,
            content_type=None,
            object_id=None
        )

        serializer_class = {
            IncidentMessage.TEXT: TextMessageSerializer,
            IncidentMessage.PHOTO: PhotoMessageSerializer,
            IncidentMessage.VIDEO: VideoMessageSerializer,
            IncidentMessage.AUDIO: AudioMessageSerializer,
        }.get(message_type)

        if not serializer_class:
            return Response({"error": "Invalid message type"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            content_obj = serializer.save(message=msg)
            msg.content_type = ContentType.objects.get_for_model(content_obj)
            msg.object_id = content_obj.id
            msg.save()
            return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)

        msg.delete()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request):
        messages = IncidentMessage.objects.all()
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            message = IncidentMessage.objects.get(pk=pk)
        except IncidentMessage.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(message)
        return Response(serializer.data)
