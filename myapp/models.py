import random
from io import BytesIO

import pytz
import qrcode
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Q

from myproject import settings


def generate_six_digit_code():
    return f"{random.randint(100000, 999999)}"


def getTimezone():
    return pytz.timezone(settings.TIME_ZONE)


def pretty_datetime(dt):
    return f"{dt.astimezone(getTimezone()).date()} {dt.astimezone(getTimezone()).replace(microsecond=0).time()}"


def display_name(user):
    if len(user.first_name) > 0 and len(user.last_name) > 0:
        return user.first_name + ' ' + user.last_name
    elif len(user.first_name) > 0:
        return user.first_name
    elif len(user.last_name) > 0:
        return user.last_name
    return user.username


class VerboseUserDisplay(User):
    class Meta:
        proxy = True

    @property
    def display_name(self):
        return display_name(self)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"


class Guard(models.Model):
    name_old = models.CharField(max_length=100, verbose_name='Имя', null=True, blank=True)
    code = models.CharField(max_length=6, unique=True, default=generate_six_digit_code, editable=False,
                            verbose_name='Код сотрудника')

    managers = models.ManyToManyField(User, limit_choices_to=Q(groups__name='Managers') | Q(groups__name='qr_manager'),
                                      default=None,
                                      related_name='guards', verbose_name='Менеджеры', blank=False)

    user = models.ForeignKey(VerboseUserDisplay, on_delete=models.CASCADE, related_name='guard_profile',
                             verbose_name='Аккаунт сотрудника', default=None, null=True, blank=False)

    @property
    def name(self):
        if not self.user:
            return f"{self.name_old} (Привяжите пользователя)"
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"


class Point(models.Model):
    class PointType(models.TextChoices):
        DEFAULT = 'default', 'Обычная точка'
        FIRE_EXTINGUISHER = 'fire_extinguisher', 'Огнетушитель'

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, verbose_name='Имя')  # Имя точки
    point_type = models.CharField(
        max_length=20,
        choices=PointType.choices,
        default=PointType.DEFAULT,
        verbose_name='Тип точки',
    )
    expiration_date = models.DateField(
        verbose_name='Дата истечения',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Точка обхода"
        verbose_name_plural = "Точки обхода"

    def generate_qr_code(self):
        qr = qrcode.make(str(self.id), box_size=15)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        buffer.seek(0)
        return ContentFile(buffer.read(), name=f'{self.name}_qr.png')

    def clean(self):
        if self.point_type == self.PointType.FIRE_EXTINGUISHER:
            if not self.expiration_date:
                raise ValidationError({'expiration_date': 'Дата истечения обязательна для огнетушителей.'})
        else:
            self.expiration_date = None
            self.has_fire_extinguisher = False


class Round(models.Model):
    guard = models.ForeignKey(Guard, on_delete=models.CASCADE, verbose_name=Guard._meta.verbose_name)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    is_active = models.BooleanField(default=True, verbose_name='Обход идет')

    def __str__(self):
        return f"{self.guard.name} начал обход {pretty_datetime(self.created_at)} (обход закончен: {'Нет' if self.is_active else 'Да'})"

    class Meta:
        verbose_name = "Обход"
        verbose_name_plural = "Обходы"


class Visit(models.Model):
    point = models.ForeignKey(Point, on_delete=models.CASCADE, verbose_name=Point._meta.verbose_name)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='visits',
                              verbose_name=Round._meta.verbose_name)

    def __str__(self):
        return f"{self.round.guard.name} посетил {self.point.name} {pretty_datetime(self.created_at)}"

    class Meta:
        verbose_name = "Посещение"
        verbose_name_plural = "Посещения"


class Message(models.Model):
    guard = models.ForeignKey(Guard, on_delete=models.CASCADE, verbose_name=Guard._meta.verbose_name)
    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, verbose_name=Visit._meta.verbose_name)
    text = models.CharField(null=False, blank=False, max_length=300)
    is_seen = models.BooleanField(default=False, verbose_name='Просмотрено')

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщение"


class Device(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='device')
    notification_token = models.CharField(max_length=255)
