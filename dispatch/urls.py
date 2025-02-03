from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import IncidentMessageViewSet, DutyViewSet, IncidentViewSet

router = DefaultRouter()
router.register(r"incident_messages", IncidentMessageViewSet, basename="message")
# router.register(r"duties/(?P<date>.+)/", DutyViewSet, basename="duty")
router.register(r"duties", DutyViewSet, basename="duty")
router.register(r"incidents", IncidentViewSet, basename="incident")

urlpatterns = [
    path('', include(router.urls)),
]
