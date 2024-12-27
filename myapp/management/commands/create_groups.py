from enum import Enum

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class PermissionType(str, Enum):
    VIEW = 'view'
    DELETE = 'delete'
    CHANGE = 'change'
    ADD = 'add'


ALL_PERMISSIONS = (PermissionType.VIEW, PermissionType.DELETE, PermissionType.CHANGE, PermissionType.ADD)

roles = {
    'QR Manager': {
        'round': [PermissionType.VIEW],
        'visit': [PermissionType.VIEW],
        'message': ALL_PERMISSIONS,
        'point': ALL_PERMISSIONS,
        'guard': ALL_PERMISSIONS,
    },
    'QR Guard': {
        # no access to admin panel
    },
    'Canteen Manager': {

    },
    'Canteen Employee': {},
    'User Manager': {
        'user': ALL_PERMISSIONS,
    }
}

def convert_to_lowercase(s):
    return s.lower().replace(' ', '_')


class Command(BaseCommand):
    help = 'Create Managers group with permissions for myapp'

    def handle(self, *args, **options):
        for group_name in roles.keys():
            group, _ = Group.objects.get_or_create(name=convert_to_lowercase(group_name))

            for model_name in roles[group_name].keys():
                content_type = ContentType.objects.get(model=model_name)

                for permission in roles[group_name][model_name]:
                    codename = f'{permission.value}_{model_name}'

                    p = Permission.objects.get(codename=codename, content_type=content_type)
                    group.permissions.add(p)

                    self.stdout.write(f'Permission "{codename}" added to group "{group_name}"')

            self.stdout.write(f'Permissions added to group "{group_name}"')
