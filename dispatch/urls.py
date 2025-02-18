from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from .views import DutyViewSet, IncidentViewSet, DutyPointViewSet, IncidentMessageViewSet

router = DefaultRouter()
router.register(r"duties", DutyViewSet, basename="duty")
router.register(r"incidents", IncidentViewSet, basename="incident")
router.register(r"duty_points", DutyPointViewSet, basename="duty_point")
incidents_router = routers.NestedSimpleRouter(router, "incidents", lookup="incident")
incidents_router.register("messages", IncidentMessageViewSet, basename="incident-messages")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(incidents_router.urls)),
]
