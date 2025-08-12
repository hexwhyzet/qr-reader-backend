from itertools import chain

from dispatch.models import Notification
from dispatch.services.access import dispatch_admins
from dispatch.services.duties import get_duty_point_by_duty_role
from myapp.utils import send_fcm_notification


def create_notification(user, title, text):
    return Notification.objects.create(user=user, title=title, text=text)


def create_and_notify(user, title, text):
    notification = create_notification(user, title, text)
    send_fcm_notification(user, notification.title, notification.text)
    return notification


def notify_users(users, title, text):
    notifications = []
    for point_admin in users:
        notification = create_notification(point_admin, title, text)
        send_fcm_notification(point_admin, notification.title, notification.text)
        notifications.append(notification)
    return notifications


def notify_point_admins(point, title, text):
    notify_users(chain(point.admins.all(), dispatch_admins()), title, text)


def notify_admins(title, text):
    notify_users(dispatch_admins(), title, text)
