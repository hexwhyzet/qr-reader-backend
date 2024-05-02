import random
from io import BytesIO

import pytz
import qrcode
from django.db import models
from django.http import HttpResponse
from django.utils.html import format_html
from django.core.files.base import ContentFile

from myproject import settings


def generate_six_digit_code():
    return f"{random.randint(100000, 999999)}"


def getTimezone():
    return pytz.timezone(settings.TIME_ZONE)


def pretty_datetime(dt):
    return f"{dt.astimezone(getTimezone()).date()} {dt.astimezone(getTimezone()).replace(microsecond=0).time()}"


class Guard(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, default=generate_six_digit_code, editable=False)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Охранник"
        verbose_name_plural = "Охранники"


class Point(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)  # Имя точки

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name = "Точка обхода"
        verbose_name_plural = "Точки обхода"

    def generate_qr_code(self):
        qr = qrcode.make(str(self.id), box_size=15)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f'{self.name}_qr.png')


class Round(models.Model):
    guard = models.ForeignKey(Guard, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.guard.name} начал обход {pretty_datetime(self.created_at)} (обход закончен: {'Нет' if self.is_active else 'Да'})"

    class Meta:
        verbose_name = "Обход"
        verbose_name_plural = "Обходы"


class Visit(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='visits')

    def __str__(self):
        return f"{self.round.guard.name} посетил {self.point.name} {pretty_datetime(self.created_at)}"

    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"
