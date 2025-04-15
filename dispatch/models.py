import enum
import os
import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import TruncDate
from django.utils.deconstruct import deconstructible
from storages.backends.s3boto3 import S3Boto3Storage

from myproject import settings
from myproject.settings import AUTH_USER_MODEL


class DispatchS3MediaStorage(S3Boto3Storage):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = 'dispatch_media'
    file_overwrite = False


class DutyRole(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя роли')

    class Meta:
        verbose_name = "Роль диспетчеризации"
        verbose_name_plural = "Роли диспетчеризации"

    def __str__(self):
        return f"{self.name}"


class ExploitationRole(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя роли')

    members = models.ManyToManyField(AUTH_USER_MODEL, related_name='exploitation_roles', verbose_name='Участники',
                                     blank=True)

    class Meta:
        verbose_name = "Роль эксплуатации"
        verbose_name_plural = "Роли эксплуатации"

    def __str__(self):
        return f"{self.name}"


class DutyPoint(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя точки дежурства')
    level_0_role = models.ForeignKey(ExploitationRole, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Эксплуатирующий персонал (уровень 0)', related_name='level_0_role')
    level_1_role = models.ForeignKey(DutyRole, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Дежурный уровня 1', related_name='level_1_role')
    level_2_role = models.ForeignKey(DutyRole, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Дежурный уровня 2', related_name='level_2_role')
    level_3_role = models.ForeignKey(DutyRole, on_delete=models.SET_NULL, null=True, blank=True,
                                     verbose_name='Дежурный уровня 3', related_name='level_3_role')

    class Meta:
        verbose_name = "Точка диспетчеризации"
        verbose_name_plural = "Точки диспетчеризации"

    def __str__(self):
        return f"{self.name}"


class Duty(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Аккаунт дежурного')
    role = models.ForeignKey(DutyRole, on_delete=models.CASCADE, null=True, verbose_name='Роль дежурства')
    is_opened = models.BooleanField(default=False, verbose_name='Открыт ли')

    start_datetime = models.DateTimeField(verbose_name='Начало дежурства', null=False, blank=False)
    end_datetime = models.DateTimeField(verbose_name='Окончание дежурства', null=False, blank=False)

    # Нотификация о том, что ответственный человек не принял дежурство
    notification_need_to_open = models.ForeignKey("Notification", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = "Дежурство"
        verbose_name_plural = "Дежурства"

        constraints = [
            UniqueConstraint(
                TruncDate('start_datetime'),
                'role',
                name='unique_start_date',
            ),
        ]

    @property
    def date(self):
        return self.start_datetime.date() if self.start_datetime else None

    def __str__(self):
        return f"{self.user} - {self.date} ({self.role})"


class IncidentStatusEnum(enum.Enum):
    OPENED = 'opened'
    CLOSED = 'closed'
    FORCE_CLOSED = 'force_closed'


class Incident(models.Model):
    STATUS_CHOICES = [
        (IncidentStatusEnum.OPENED.value, 'В работе'),
        (IncidentStatusEnum.CLOSED.value, 'Выполнено'),
        (IncidentStatusEnum.FORCE_CLOSED.value, 'Ненадлежащее выполнение'),
    ]

    name = models.CharField(max_length=255, verbose_name='Имя инцидента')
    description = models.TextField(verbose_name='Описание инцидента')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='opened', verbose_name='Статус')
    level = models.PositiveSmallIntegerField(default=0, verbose_name='Уровень')
    is_critical = models.BooleanField(default=False, verbose_name='Критичный',
                                      help_text='Автоматически выставляется, если ни один из уровней не справился с выполнением')
    author = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='opened_incident',
                               verbose_name='Автор')
    responsible_user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='responsible_incidents', verbose_name='Ответственный дежурный')
    point = models.ForeignKey(DutyPoint, on_delete=models.SET_NULL, null=True, related_name='incidents',
                              verbose_name='Точка диспетчеризации')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Инцидент"
        verbose_name_plural = "Инциденты"

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'


class Notification(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.TextField(max_length=255, null=True)
    text = models.TextField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"Уведомление для {self.user} - {'Отправлено' if self.is_sent else 'Не отправлено'}"


class IncidentMessage(models.Model):
    TEXT = "text"
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"

    MESSAGE_TYPES = [
        (TEXT, "Текст"),
        (PHOTO, "Фото"),
        (VIDEO, "Видео"),
        (AUDIO, "Аудио"),
    ]

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='messages')

    user = models.ForeignKey(AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name="Отправитель")
    created_at = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.user or 'system'} ({self.content_type}) at {self.created_at}"


@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        return os.path.join(self.path, filename)


class TextMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="text")
    text = models.TextField(verbose_name="Текст")

    def __str__(self):
        return f"{self.text}"


class PhotoMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="photo")
    photo = models.ImageField(storage=DispatchS3MediaStorage(), upload_to=PathAndRename("photos"))


class VideoMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="video")
    video = models.FileField(storage=DispatchS3MediaStorage(), upload_to=PathAndRename("videos"))


class AudioMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="audio")
    audio = models.FileField(storage=DispatchS3MediaStorage(), upload_to=PathAndRename("audios"))
