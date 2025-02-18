from dispatch.models import Notification


def create_notification(user, title, text):
    return Notification.objects.create(user=user, title=title, text=text)
