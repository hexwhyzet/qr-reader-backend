from datetime import date, timedelta, time

from django.contrib.auth.models import User

from dispatch.models import Duty, DutyRole


def get_duties_by_date(start_date: date, role: DutyRole = None):
    if role is None:
        return Duty.objects.filter(date__range=(start_date, start_date))
    return Duty.objects.filter(date__range=(start_date, start_date), role=role)


def get_duties_by_date_range(start_date: date, end_date: date):
    return Duty.objects.filter(date__range=(start_date, end_date))


def get_duties_assigned(start_date: date, duty_role: DutyRole):
    counter = 0
    current_date = start_date
    while counter < 100:
        if not Duty.objects.filter(date=current_date, role=duty_role).exists():
            break
        counter += 1
        current_date += timedelta(days=1)
    return counter


def get_current_duties(current_datetime, user: User = None, role: DutyRole = None):
    queryset = Duty.objects.none()
    if current_datetime.time() > time(18, 45):
        queryset = Duty.objects.filter(date=date)
    elif current_datetime.time() < time(7, 0):
        queryset = Duty.objects.filter(date=(current_datetime - timedelta(days=1)).date())
    if user is not None:
        queryset = queryset.filter(user=user)
    if role is not None:
        queryset = queryset.filter(role=role)
    return queryset
