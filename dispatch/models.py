import os
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage

from myapp.models import VerboseUserDisplay
from myproject import settings


class S3MediaStorage(S3Boto3Storage):
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


class DutyPoint(models.Model):
    name = models.CharField(max_length=100, verbose_name='Имя точки дежурства')
    # level_0_role = models.ForeignKey(DutyRole, on_delete=models.SET_NULL, null=True, blank=True,
    #                                  verbose_name='Дежурный уровня 0', related_name='level_0_role')
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
    date = models.DateField(verbose_name='Дата дежурства')
    user = models.ForeignKey(VerboseUserDisplay, on_delete=models.CASCADE, verbose_name='Аккаунт дежурного')
    role = models.ForeignKey(DutyRole, on_delete=models.CASCADE, null=True, verbose_name='Роль дежурства')
    is_opened = models.BooleanField(default=False, verbose_name="Открыт ли")

    # Нотификация о том, что ответственный человек не принял дежурство
    notification_need_to_open = models.ForeignKey("Notification", on_delete=models.SET_NULL, null=True, blank=True)


    class Meta:
        verbose_name = "Дежурство"
        verbose_name_plural = "Дежурства"
        unique_together = ('date', 'role')

    def __str__(self):
        return f"{self.user} - {self.date} ({self.role})"


class Incident(models.Model):
    STATUS_CHOICES = [
        ('opened', 'В работе'),
        ('closed', 'Выполнено'),
        ('force_closed', 'Ненадлежащее выполнение'),
    ]

    name = models.CharField(max_length=255, verbose_name='Имя инцидента')
    description = models.TextField(verbose_name='Описание инцидента')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='opened', verbose_name='Статус')
    level = models.PositiveSmallIntegerField(default=0, verbose_name='Уровень')
    is_critical = models.BooleanField(default=False, verbose_name='Критичный', help_text='Автоматически выставляется, если ни один из уровней не справился с выполнением')
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='opened_incident', verbose_name='Автор')
    responsible_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='responsible_incidents', verbose_name='Ответственный дежурный')
    point = models.ForeignKey(DutyPoint, on_delete=models.SET_NULL, null=True, related_name='incidents', verbose_name='Точка диспетчеризации')

    class Meta:
        verbose_name = "Инцидент"
        verbose_name_plural = "Инциденты"

    def __str__(self):
        return f'{self.name} ({self.get_status_display()})'


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    text = models.TextField()
    is_sent = models.BooleanField(default=False)

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

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Отправитель")
    created_at = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Message from {self.user or 'system'} ({self.content_type}) at {self.created_at}"


def wrapped_upload_to_uuid(prefix):
    def upload_to_uuid(instance, filename):
        ext = filename.split('.')[-1]
        new_filename = f"{uuid.uuid4()}.{ext}"
        return os.path.join(f'{prefix}/', new_filename)

    return upload_to_uuid


class TextMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="text")
    text = models.TextField(verbose_name="Текст")

    def __str__(self):
        return f"{self.text}"


class PhotoMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="photo")
    photo = models.ImageField(storage=S3MediaStorage(), upload_to=wrapped_upload_to_uuid("photos"))


class VideoMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="video")
    video = models.FileField(storage=S3MediaStorage(), upload_to=wrapped_upload_to_uuid("videos"))


class AudioMessage(models.Model):
    message = models.OneToOneField(IncidentMessage, on_delete=models.CASCADE, related_name="audio")
    audio = models.FileField(storage=S3MediaStorage(), upload_to=wrapped_upload_to_uuid("audios"))
