import logging
from datetime import timedelta

from django_cron import CronJobBase, Schedule

from dispatch.services.duties import get_current_duties, get_duty_point_by_duty_role
from dispatch.services.notification import create_and_notify, notify_point_admins
from dispatch.utils import now

logger = logging.getLogger(__name__)


class NeedToOpenNotification(CronJobBase):
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'dispatch.need_to_open_notification'

    def do(self):
        duties = get_current_duties(now(), start_offset=30)
        for duty in duties:
            if not duty.is_opened and duty.notification_duty_is_coming is None:
                title = "Вам назначено дежурство сегодня"
                text = f"Дежурство в роли: {duty.role.name}"
                duty.notification_duty_is_coming = create_and_notify(duty.user, title, text)
                duty.save()

            if not duty.is_opened and duty.notification_need_to_open is None \
                    and now() - duty.start_datetime > timedelta(minutes=15):
                duty.is_opened = True
                duty.is_forced_opened = True
                duty.notification_need_to_open = create_and_notify(duty.user, "Дежурство начато автоматически",
                                                                   f"Дежурство в роли: {duty.role.name}")
                duty.save()

                points = get_duty_point_by_duty_role(duty.role)
                for point in points:
                    notify_point_admins(point,
                                        f"Пользователь {duty.user.display_name} не начал дежурство",
                                        f"Пользователь {duty.user.display_name} не начал дежурство в роли {duty.role.name}, оно было открыто автоматически.")
