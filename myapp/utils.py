import os

from pyfcm import FCMNotification

from myproject.settings import AUTH_USER_MODEL


def send_fcm_notification(user: AUTH_USER_MODEL, title, body, data=None):
    fcm = FCMNotification(service_account_file=os.getenv('PATH_TO_GOOGLE_OAUTH_TOKEN'),
                          project_id=os.getenv('FIREBASE_PROJECT_ID'))
    if user.device.notification_token is not None:
        result = fcm.notify(
            fcm_token=user.device.notification_token,
            notification_title=title,
            notification_body=body,
        )
        return result
