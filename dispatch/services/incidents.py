from django.contrib.auth.models import User
from django.db.models import Q

from dispatch.models import Incident
from dispatch.services.duties import get_current_duties
from dispatch.services.messages import create_escalation_error_message_duty_not_opened, create_escalation_message
from dispatch.utils import now
from myapp.admin import user_has_group
from myapp.custom_groups import DispatchAdminManager
from myapp.utils import send_fcm_notification


def escalate_incident(incident: Incident):
    current_datetime = now()
    for i in range(min(incident.level + 1, 4), 5):
        if i == 4:
            create_escalation_message(incident, i, None)
            incident.level = i
            incident.is_critical = True
            incident.responsible_user = None
            continue

        duty_role = getattr(incident.point, f"level_{i}_role")
        if duty_role is None:
            continue
        duty = get_current_duties(current_datetime, role=duty_role).first()
        if duty is None:
            continue
        if not duty.is_opened:
            create_escalation_error_message_duty_not_opened(incident, i, duty)
            continue
        incident.level = i
        incident.responsible_user = duty.user
        if incident.responsible_user is not None:
            send_fcm_notification(incident.responsible_user, "Новый инцидент", incident.name)
        create_escalation_message(incident, i, duty)
        break

    incident.save()


def user_incidents(user: User):
    if user_has_group(user, DispatchAdminManager):
        return Incident.objects.all()

    return Incident.objects.filter(Q(author_id=user.id) | Q(responsible_user_id=user.id)).all()
