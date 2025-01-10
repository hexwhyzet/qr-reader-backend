from enum import Enum

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from myapp.custom_groups import (
    QRManager,
    QRGuard,
    UserManager,
    SeniorUserManager,
    CanteenManager,
    CanteenEmployee,
    CanteenAdminManager
)


class PermissionType(str, Enum):
    VIEW = 'view'
    DELETE = 'delete'
    CHANGE = 'change'
    ADD = 'add'


ALL_PERMISSIONS = (PermissionType.VIEW, PermissionType.DELETE, PermissionType.CHANGE, PermissionType.ADD)

roles = {
    QRManager: {
        'round': [PermissionType.VIEW],
        'visit': [PermissionType.VIEW],
        'message': ALL_PERMISSIONS,
        'point': ALL_PERMISSIONS,
        'guard': ALL_PERMISSIONS,
    },
    QRGuard: {
        # no access to admin panel
    },
    UserManager: {
        'user': ALL_PERMISSIONS,
    },
    SeniorUserManager: {
        'user': ALL_PERMISSIONS,
    },
    CanteenManager: {
        'dish': [PermissionType.VIEW],
        'order': [PermissionType.VIEW],
        'feedback': [PermissionType.VIEW]
    },
    CanteenAdminManager: {
        'dish': [PermissionType.VIEW],
        'order': [PermissionType.VIEW],
        'feedback': [PermissionType.VIEW]
    },
    CanteenEmployee: {
        'dish': ALL_PERMISSIONS,
        'order': [PermissionType.VIEW],
        'feedback': [PermissionType.ADD]
    },
}


class Command(BaseCommand):
    help = 'Create Managers group with permissions for myapp'

    def handle(self, *args, **options):
        for custom_group in roles.keys():
            group, _ = Group.objects.get_or_create(name=custom_group.name)

            for model_name in roles[custom_group].keys():
                content_type = ContentType.objects.get(model=model_name)

                for permission in roles[custom_group][model_name]:
                    codename = f'{permission.value}_{model_name}'

                    p = Permission.objects.get(codename=codename, content_type=content_type)
                    group.permissions.add(p)

                    self.stdout.write(f'Permission "{codename}" added to group "{custom_group.name}"')

            self.stdout.write(f'Permissions added to group "{custom_group.name}"')
