import os

from django.contrib.auth.models import User
from pyfcm import FCMNotification


def send_fcm_notification(user: User, title, body, data=None):
    fcm = FCMNotification(service_account_file=os.getenv('PATH_TO_GOOGLE_OAUTH_TOKEN'),
                          project_id=os.getenv('FIREBASE_PROJECT_ID'))
    if user.device.notification_token is not None:
        result = fcm.notify(
            fcm_token=user.device.notification_token,
            notification_title=title,
            notification_body=body,
        )
        return result
