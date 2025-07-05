from django.db import models

class TelegramLoginToken(models.Model):
    token = models.CharField(max_length=64, unique=True)
    telegram_user_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
