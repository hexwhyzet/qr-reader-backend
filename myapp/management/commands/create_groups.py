from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create Managers group with permissions for myapp'

    def handle(self, *args, **options):
        app_name = 'myapp'
        group_name = 'Managers'

        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            self.stdout.write(f'Group "{group_name}" created')
        else:
            self.stdout.write(f'Group "{group_name}" already exists')

        content_types = ContentType.objects.filter(app_label=app_name)

        for content_type in content_types:
            if content_type.model in ['round', 'visit']:
                permissions = Permission.objects.filter(content_type=content_type).exclude(
                    codename__in=['delete_' + content_type.model,
                                  'change_' + content_type.model,
                                  'add_' + content_type.model])
            else:
                permissions = Permission.objects.filter(content_type=content_type)

            for permission in permissions:
                group.permissions.add(permission)

        self.stdout.write(f'Permissions added to group "{group_name}"')
