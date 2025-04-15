from django.contrib.auth.models import AbstractUser
from django.db import models


def display_name(user):
    if len(user.first_name) > 0 and len(user.last_name) > 0:
        return user.last_name + ' ' + user.first_name
    elif len(user.first_name) > 0:
        return user.first_name
    elif len(user.last_name) > 0:
        return user.last_name
    return user.username


class User(AbstractUser):
    must_change_password = models.BooleanField(default=False, verbose_name="Необходимо сменить пароль при следующем входе в приложение")

    class Meta:
        db_table = 'auth_user'
        ordering = ['last_name']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    @property
    def display_name(self):
        return display_name(self)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"
