# Generated by Django 5.0.4 on 2025-02-16 23:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0016_device'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='device', to='myapp.verboseuserdisplay'),
        ),
    ]
