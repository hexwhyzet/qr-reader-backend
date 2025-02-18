import logging

from django_cron import CronJobBase, Schedule

from dispatch.services.duties import get_current_duties
from dispatch.services.notification import create_notification
from dispatch.utils import now
from myapp.models import Device
from myapp.utils import send_fcm_notification

logger = logging.getLogger(__name__)


class NeedToOpenNotification(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dispatch.need_to_open_notification'

    def do(self):
        duties = get_current_duties(now())
        for duty in duties:
            if not duty.is_opened and duty.notification_need_to_open is None and Device.objects.filter(
                    user__id=duty.user.id).exists():
                title = "Необходимо открыть дежурство в приложении"
                text = f"Дежурство в роли: {duty.role.name}"
                notification = create_notification(duty.user, title, text)
                send_fcm_notification(duty.user, title, text)
                duty.notification_need_to_open = notification
                duty.save()
