from django.urls import path

from myapp.views.guards import GuardView
from myapp.views.rounds import StartRoundView, EndRoundView, RoundStatusView
from myapp.views.visits import VisitPointsView

urlpatterns = [
    path('auth/<int:guard_id>', GuardView.as_view(), name='guard'),

    path('guard/<int:guard_id>/start_round', StartRoundView.as_view(), name='start-round'),
    path('guard/<int:guard_id>/end_round', EndRoundView.as_view(), name='end-round'),
    path('guard/<int:guard_id>/round_status', RoundStatusView.as_view(), name='round-status'),

    path('guard/<int:guard_id>/visit_point/<int:point_id>', VisitPointsView.as_view(), name='visit-point'),
]
