from django.contrib.auth.models import AbstractUser


def display_name(user):
    if len(user.first_name) > 0 and len(user.last_name) > 0:
        return user.first_name + ' ' + user.last_name
    elif len(user.first_name) > 0:
        return user.first_name
    elif len(user.last_name) > 0:
        return user.last_name
    return user.username


class User(AbstractUser):
    class Meta:
        db_table = 'auth_user'

    @property
    def display_name(self):
        return display_name(self)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.username})"
