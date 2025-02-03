from dispatch.models import Incident
from dispatch.services.duties import get_current_duties
from dispatch.services.messages import create_escalation_error_message_duty_not_opened, create_escalation_message
from dispatch.utils import now


def escalate_incident(incident: Incident):
    current_datetime = now()
    for i in range(min(incident.level + 1, 4), 5):
        if i == 4:
            create_escalation_message(incident, i, None)
            incident.level = i
            incident.is_critical = True
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
        create_escalation_message(incident, i, duty)
        break

    incident.save()
